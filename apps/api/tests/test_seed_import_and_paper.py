"""核心链路测试：schema 校验 → 种子导入 → 对纲校验 → 组卷 → 换题。

跑法：cd 仓库根目录 && python -m pytest apps/api/tests -q
测试使用独立的临时数据库，绝不触碰 data/tiku.db。
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = tempfile.mkdtemp(prefix="tiku-test-")
os.environ["TIKU_DB_PATH"] = str(Path(_TMP) / "test.db")
os.environ["TIKU_DATA_DIR"] = _TMP

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "api"))

import json  # noqa: E402

import pytest  # noqa: E402
from sqlalchemy import func, select  # noqa: E402

from app.config import SEED_DIR  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.models import Book, Paper, Question  # noqa: E402
from app.schemas import PaperGenerate  # noqa: E402
from app.services import paper_builder  # noqa: E402
from app.services.bundle_import import import_bundle_file, validate_bundle  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def _db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture(scope="module")
def seeded():
    with SessionLocal() as db:
        for p in sorted(SEED_DIR.glob("*.json")):
            import_bundle_file(db, p)
        db.commit()
        yield db


def test_seed_bundles_validate():
    for p in sorted(SEED_DIR.glob("*.json")):
        kind = validate_bundle(json.loads(p.read_text(encoding="utf-8")))
        assert kind in ("catalog", "question")


def test_import_counts(seeded):
    books = seeded.scalars(select(Book)).all()
    assert len(books) == 4  # 2 纲 + 2 自编卷
    math = seeded.scalar(select(Book).where(Book.title == "自编卷·数学一年级上（第一单元）"))
    chinese = seeded.scalar(select(Book).where(Book.title == "自编卷·语文一年级上（第一、二单元）"))
    assert math and chinese
    assert seeded.scalar(select(func.count()).select_from(Question)
                         .where(Question.book_id == math.id)) == 55
    assert seeded.scalar(select(func.count()).select_from(Question)
                         .where(Question.book_id == chinese.id)) == 35


def test_scope_classification(seeded):
    """对纲校验：纲内题 ok；显式提优 extension；纲缺失才 pending。"""
    statuses = {s for (s,) in seeded.execute(select(Question.scope_status)).all()}
    assert "ok" in statuses
    assert "extension" in statuses  # 数学智慧挑战 3 题
    assert "pending" not in statuses
    ext = seeded.scalars(select(Question).where(Question.scope_status == "extension")).all()
    assert len(ext) == 3
    assert all(q.unit_id is not None for q in ext)  # extension 也应归属到提示单元


def test_generate_math_paper(seeded):
    textbook = seeded.scalar(select(Book).where(
        Book.title == "人教版数学一年级上册（2024）"))
    paper = paper_builder.generate_paper(seeded, PaperGenerate(
        textbook_id=textbook.id, unit_from=1, unit_to=1,
        counts={"口算": 10, "填空": 8, "连线": 1, "看图列式": 2, "应用": 2},
        total_score=100, duration_minutes=60, seed=7,
    ))
    seeded.commit()
    types = [it.snapshot["q_type"] for it in paper.items]
    assert types.count("口算") == 10
    assert types.count("填空") == 8
    assert sum(it.score for it in paper.items) == 100
    assert paper.title.startswith("1年级数学上册")
    stems = [it.snapshot["stem"] for it in paper.items]
    assert len(stems) == len(set(stems)), "同一张卷不应出现重复题干"


def test_generate_chinese_paper_with_extension(seeded):
    textbook = seeded.scalar(select(Book).where(
        Book.title == "统编版语文一年级上册（2024）"))
    paper = paper_builder.generate_paper(seeded, PaperGenerate(
        textbook_id=textbook.id, unit_from=1, unit_to=2,
        counts={"拼音": 4, "选择": 6, "连线": 2, "笔画": 3, "字谜": 1},
        total_score=100, duration_minutes=60, seed=3, include_extension=True,
    ))
    seeded.commit()
    assert len(paper.items) == 16
    assert sum(it.score for it in paper.items) == 100
    # 没勾 include_extension 时，extension 不入池
    paper2 = paper_builder.generate_paper(seeded, PaperGenerate(
        textbook_id=textbook.id, unit_from=1, unit_to=2,
        counts={"拼音": 4, "选择": 6, "连线": 2, "笔画": 3, "字谜": 1},
        total_score=100, duration_minutes=60, seed=3, include_extension=False,
    ))
    assert len(paper2.items) == 16  # 字谜/形近字本身在纲内（难度3），仍可出


def test_replace_question(seeded):
    paper = seeded.scalars(select(Paper)).first()
    item = paper.items[0]
    old_qid = item.question_id
    new_item = paper_builder.replace_question(seeded, paper, item.id)
    seeded.commit()
    assert new_item is not None
    assert new_item.question_id != old_qid
    assert new_item.snapshot["q_type"] == item.snapshot["q_type"]


def test_reimport_is_idempotent(seeded):
    """重复导入同一 bundle 不应产生重复题。"""
    p = SEED_DIR / "questions-自编卷-数学一年级上-第一单元.json"
    before = seeded.scalar(select(func.count()).select_from(Question))
    import_bundle_file(seeded, p)
    seeded.commit()
    after = seeded.scalar(select(func.count()).select_from(Question))
    assert before == after

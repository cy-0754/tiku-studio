"""tiku-studio API 入口。

- 开发：uvicorn app.main:app --app-dir apps/api --reload（前端另用 vite dev）
- 生产：uvicorn 直接挂载 apps/web/dist 的构建产物，单进程即可用
- 首次启动若库为空且 seed/ 有数据，自动导入种子题库
"""
import json
import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import SEED_DIR, WEB_DIST, ensure_dirs
from .db import SessionLocal, init_db
from .routers import books, ingest, meta, papers, questions

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("tiku-studio")

app = FastAPI(title="tiku-studio", version="0.1.0",
              description="小学题库与组卷系统：资料拆解入库 → 对纲校验 → 自动组卷导出 PDF")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(books.router)
app.include_router(questions.router)
app.include_router(papers.router)
app.include_router(ingest.router)
app.include_router(meta.router)


@app.on_event("startup")
def startup() -> None:
    ensure_dirs()
    init_db()
    _seed_if_empty()


def _seed_if_empty() -> None:
    from sqlalchemy import func, select
    from .models import Question
    from .services.bundle_import import import_bundle_file

    with SessionLocal() as db:
        n = db.scalar(select(func.count()).select_from(Question)) or 0
        if n > 0:
            return
        bundles = sorted(SEED_DIR.glob("*.json"))
        if not bundles:
            return
        log.info("空库：正在导入种子题库（%d 个 bundle）…", len(bundles))
        for path in bundles:
            try:
                result = import_bundle_file(db, path)
                log.info("seed %s -> %s", path.name, result)
            except Exception as e:  # 单个种子失败不阻断启动
                log.error("seed %s 导入失败: %s", path.name, e)
        db.commit()
        log.info("种子导入完成。")


if WEB_DIST.exists():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="web")
else:
    @app.get("/")
    def root():
        return {"app": "tiku-studio", "docs": "/docs",
                "hint": "前端未构建：cd apps/web && npm install && npm run build"}


def main() -> None:
    import uvicorn
    from .config import API_PORT

    uvicorn.run(app, host="0.0.0.0", port=API_PORT)


if __name__ == "__main__":
    main()

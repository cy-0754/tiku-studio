# tiku-studio · 小学题库与组卷系统

把"搜集资料 → 拆解归类 → 变成可复用的题库 → 为孩子出一张不超纲的卷子"这条流水线固化成代码。

**前后端分离**（FastAPI + Vue3）· **自带 SQLite 数据库** · **本地/线上均可部署** · **多端自适应**（平板/手机可直接访问）

```
家长的一天：
  ① 上传新课本/教辅（本地 Agent 拆解，或网页上传交给视觉模型） 
  ② 系统对纲校验：自动归类单元、标记疑似超纲，进待审核队列
  ③ 人工确认入池
  ④ 勾选「第 1~3 单元 · 题型配额」→ 一键组卷 → 导出 A4 可打印 PDF（题目卷 + 答案卷）
```

## 三分钟跑起来

1. 安装 [Python 3.10+](https://www.python.org/downloads/)（勾选 Add to PATH）和 [Node.js 18+](https://nodejs.org)
2. 克隆并双击启动：

```bash
git clone <本仓库> && cd tiku-studio
# Windows：双击 start.bat
# Linux / macOS：
./start.sh
```

3. 打开 **http://localhost:8100** —— 首次启动自动导入种子题库（人教版 2024 一年级上册数学/语文纲 + 90 道原创题）。

手机/平板访问：与电脑连同一 WiFi，浏览器打开 `电脑IP:8100`（如 `http://192.168.1.5:8100`）。

> 没装 Node？`start.bat` 会跳过前端构建，你可以把 `apps/web/dist` 从 GitHub Releases 下载解压到对应目录。

## 它能做什么

| 能力 | 说明 |
|---|---|
| **课本 = 纲** | 课本目录级拆解出「单元→知识点」映射，是全系统判定超纲的标尺 |
| **对纲校验** | 每道拆解入库的题自动比对纲：`范围内 / 提优拓展 / 疑似超纲（版本不符）`，疑似项进待审核队列并给出理由 |
| **自动组卷** | 绑定教材 + 单元范围（当前进度）+ 题型配额 → 抽题配分 → 总分精确配平；支持换题、固定随机种子复现 |
| **导出打印** | A4 打印视图（楷体、答题头、答案页分离），Playwright 一键 PDF，或浏览器直接打印 |
| **双拆解引擎** | ① 本地 Agent 模式（免费，见 `agent/AGENTS.md`）② 网页上传 PDF → 内置视觉模型拆解（配置自己的 API key，实验性） |
| **自编卷种子** | 内置两套全新原创卷（数学第一单元 55 题 / 语文一二单元 35 题），开箱即可试组卷 |

## 目录结构

```
apps/api        FastAPI 后端（模型、对纲校验、组卷引擎、PDF 渲染、LLM 拆解适配器）
apps/web        Vue3 + Vite 前端（题库/组卷/资料库/待审核/AI拆解/设置）
packages/schema 两套拆解产物 JSON Schema（两种引擎共用，Agent 与 API 产物可互换）
agent/          本地 Agent 拆解手册 + 可直接复制的提示词
seed/           开箱种子：2 本教材纲 + 90 道原创题（唯一公开的数据）
scripts/        import_bundle.py 等工具脚本
docs/           教程：本地部署 / Docker / Agent 拆解 / API 拆解 / 组卷
data/           你的私有数据（gitignored）：tiku.db、收件箱、题图库
```

## 教程

- [本地部署与日常使用](docs/本地部署.md)
- [Docker 部署（NAS / 云服务器）](docs/Docker部署.md)
- [把新课本教辅交给本地 Agent 拆解](docs/Agent拆解指南.md)
- [网页上传 PDF 自动拆解（LLM API）](docs/API拆解指南.md)
- [组卷与打印](docs/组卷指南.md)

## 版权与数据边界（重要）

- 本仓库**不含**任何受版权保护的课本/教辅扫描件；`seed/` 里的题目为原创，可公开。
- 你导入的教辅题目、拆解产物、题图全部存在本地 `data/`（gitignored），不会上传。
- 请仅对你合法拥有的资料做个人使用用途的拆解。

## 开发

```bash
# 后端测试（独立临时库，不碰开发数据）
.venv/Scripts/python -m pytest apps/api/tests -q

# 前端开发模式（热更新，代理 /api 到 8100）
cd apps/web && npm run dev

# API 文档
# http://localhost:8100/docs
```

## Roadmap

- [x] M1 仓库骨架 / 数据库 / Schema / 校验导入 / 种子题库
- [x] M2 题库检索与浏览
- [x] M3 自动组卷 + PDF 导出
- [x] M4 Agent 拆解手册与提示词
- [x] M5 内置 LLM 拆解流水线（实验性）
- [x] M6 Docker 与线上部署教程
- [ ] 在线练习 / 错题本（孩子在平板上答题）
- [ ] 数学公式渲染（LaTeX）与更丰富的图形题模板

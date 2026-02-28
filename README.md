# ResearcherZero - Claude-based AI Researcher

基于 Claude 的 AI 研究助手，具备自主学习和知识管理能力。

## 快速开始

### 1. 安装依赖

项目使用 [uv](https://github.com/astral-sh/uv) 管理依赖：

```bash
# 安装 uv (如果还没有)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

### 2. 使用学术搜索工具

```bash
# 搜索论文
uv run python skills/research-learn/scripts/semantic_scholar.py "Agent Memory" --limit 5

# 指定年份范围
uv run python skills/research-learn/scripts/semantic_scholar.py "MemGPT" --year 2024-2026 --limit 10

# 文本格式输出
uv run python skills/research-learn/scripts/semantic_scholar.py "LLM Agent" --format text
```

### 3. 配置 API Key（可选）

如果有 Semantic Scholar API key，可以在 `.env` 文件中配置：

```bash
cp .env.example .env
# 编辑 .env 文件，添加你的 API key
```

## 项目结构

```
researcher-zero/
├── skills/                    # AI 能力集
│   └── research-learn/        # 学习执行能力
│       └── scripts/
│           └── semantic_scholar.py
├── commands/                  # 用户交互命令
├── domains/                   # 知识存储
├── pyproject.toml            # 项目配置和依赖
├── uv.lock                   # 依赖锁定文件
└── .python-version           # Python 版本 (3.13)
```

## 详细文档

- [QUICKSTART.md](QUICKSTART.md) - 完整的使用指南
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - 详细设计规格

## 技术栈

- Python 3.13+
- uv - 快速的 Python 包管理器
- requests - HTTP 库
- Semantic Scholar API - 学术搜索

## License

MIT

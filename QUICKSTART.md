# ResearcherZero 快速开始

## 项目结构

```
researcher-zero/
├── .claude-plugin/
│   └── plugin.json                       # Claude Code plugin 配置
│
├── skills/                               # AI 研究员的能力集
│   ├── research-plan/                    # 任务规划能力
│   │   └── SKILL.md
│   ├── research-learn/                   # 学习执行能力
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── semantic_scholar.py       # 学术搜索工具
│   ├── research-memory/                  # 知识管理能力
│   │   └── SKILL.md
│   └── research-chat/                    # 认知对话能力
│       └── SKILL.md
│
├── commands/                             # 用户交互命令
│   ├── learn.md                          # /learn <学习目标>
│   ├── status.md                         # /status [领域]
│   └── init-domain.md                    # /init-domain <领域名>
│
└── domains/                              # 持久化知识存储
    └── _template/                        # 领域模板
        ├── basic_info.md
        ├── taxonomy.md
        ├── main_challenge.md
        ├── network.md
        ├── human_preference.md
        └── atomic_knowledge/
```

## 使用流程

### 1. 初始化新领域

```bash
/init-domain agent-memory
```

这会在 `domains/` 下创建一个新的领域目录，包含所有必要的知识文件模板。

### 2. 开始学习

```bash
/learn 建立对 Agent Memory 领域的基础认知
```

ResearcherZero 会：
1. 自动规划学习路径（调用 research-plan）
2. 搜索相关资料（论文、博客等）
3. 阅读和理解内容
4. 抽取结构化知识
5. 更新 domains/ 中的知识文件
6. 返回学习总结

### 3. 查看认知状态

```bash
/status agent-memory
```

查看 ResearcherZero 在该领域的当前认知覆盖度：
- 基础认知是否建立
- 核心挑战是否了解
- 有多少原子知识条目
- 最近更新了什么

### 4. 基于知识对话

直接提问，ResearcherZero 会基于已学习的知识回答：

```
用户: Agent Memory 的主要挑战是什么？
```

ResearcherZero 会：
- 加载相关知识（渐进式加载）
- 基于 domains/ 内容回答
- 标注信息来源
- 区分"已学"和"未学"

## 学习目标示例

### 建立基础认知
```bash
/learn 建立对 Agent Memory 领域的基础认知
/learn 了解 Quantum Computing 的基本概念和分类
```

### 深入特定主题
```bash
/learn 深入了解 MemGPT 的架构设计
/learn 学习 Transformer 的注意力机制
```

### 跟进最新进展
```bash
/learn 了解 Agent Memory 领域最近半年的进展
/learn 跟踪 LLM Agent 的最新研究
```

### 理解核心挑战
```bash
/learn 了解 Agent Memory 的核心挑战和 Benchmark
/learn 理解多模态学习的主要难点
```

## 核心特性

### 1. 自主规划
不需要人类拆分任务为微步骤，ResearcherZero 自己规划学习路径。

### 2. 持久化知识
所有学到的知识都结构化存储在 `domains/` 中，可以跨会话使用。

### 3. 渐进式加载
对话时不会一次性加载所有知识，而是根据需要逐步加载。

### 4. 诚实区分
明确区分"已学"和"未学"，不会在没有知识的情况下编造内容。

### 5. Context Fork 隔离
`/learn` 命令在独立上下文中执行，不会污染主会话。

## 知识文件说明

### basic_info.md
领域的基础定义和概述（不超过 500 字）

### taxonomy.md
领域的分类框架（树形结构）

### main_challenge.md
核心挑战列表（描述 + Benchmark + SOTA）

### network.md
概念间关系（递进、因果、演化、对比）

### human_preference.md
用户在该领域的学习偏好

### atomic_knowledge/*.md
具体的知识单元（论文、博客、技术等），每个文件包含：
- YAML frontmatter（类型、标题、来源、日期等）
- 结构化的知识内容

## 依赖安装

项目使用 `uv` 管理依赖，自动安装所有必需的包：

```bash
# 安装 uv (如果还没有)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖（自动创建虚拟环境）
uv sync
```

安装完成后，可以使用 `uv run` 运行任何脚本：

```bash
# 运行学术搜索工具
uv run python skills/research-learn/scripts/semantic_scholar.py --help
```

## 环境变量（可选）

如果有 Semantic Scholar API key，可以设置环境变量提高搜索速率限制：

```bash
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"
```

## 验收测试

按照以下步骤验证系统是否正常工作：

### 1. 初始化领域
```bash
/init-domain agent-memory
```
预期：成功创建 domains/agent-memory/ 及所有模板文件

### 2. 执行学习
```bash
/learn 建立对 Agent Memory 的基础认知
```
预期：自主规划、搜索、阅读、抽取、更新文件，返回学习总结

### 3. 查看状态
```bash
/status agent-memory
```
预期：展示认知覆盖度报告

### 4. 基于知识对话
```
Agent Memory 的主要挑战是什么？
```
预期：基于已学知识回答，标注来源

### 5. 继续学习
```bash
/learn 了解 Agent Memory 的核心挑战
```
预期：在已有认知基础上深入学习，更新相关文件

## 注意事项

1. **Context fork**: `/learn` 命令使用 `context: fork`，在独立上下文中执行
2. **知识格式**: 所有知识必须结构化，不能原文搬运
3. **渐进加载**: 对话时按需加载知识，避免过度加载
4. **诚实标注**: 不确定的内容要标注，不编造
5. **Human in the loop**: 人类给目标、评估结果，ResearcherZero 自主执行

## 下一步

1. 阅读 [IMPLEMENTATION.md](IMPLEMENTATION.md) 了解详细设计规格
2. 使用 `/init-domain` 创建你感兴趣的研究领域
3. 使用 `/learn` 开始学习之旅

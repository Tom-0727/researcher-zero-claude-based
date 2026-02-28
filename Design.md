---
title: "ResearcherZero 实现方案 -- 把 Claude Code 变成 AI 研究员"
---

# ResearcherZero 实现方案 -- 把 Claude Code 变成 AI 研究员

## Introduction

经过 [Context](https://www.tom-blogs.top/2026/02/01/researcher-zero/arch-design-context/)、[Memory](https://www.tom-blogs.top/2026/02/11/researcher-zero/arch-design-memory/)、[Learning](https://www.tom-blogs.top/2026/02/13/researcher-zero/arch-design-learning/) 三篇架构设计，ResearcherZero 的蓝图已经画完了。接下来该回答一个现实问题：**怎么实现它？**

最初的想法是自己搭一套 Agent 框架 —— 实现 Plan&Execute + React 的运转机制，自建工具调用链，管理上下文窗口，处理 subagent 的 fork 和 summary。做了一段时间后我意识到两件事：

1. **工程复杂度远超预期**。我造出来的东西，本质上就是在重新发明一个 Claude Code。
2. **核心运转机制无法完全自主控制**。Claude Code 有自己的 agent loop（本身就是 React）、自己的上下文压缩策略（自动 compaction）、自己的 todo/plan 管理。即使我在 Skill 里写了"请按我的 Plan&Execute 流程执行"，模型也只是被**引导**，不是被**控制**。Step 级的上下文压缩、精确的 Plan 重写触发 —— 这些在 Claude Code 的架构下不是确定性可实现的。

转念一想，我在 Learning 设计中做的那个决定 —— **克制全自动，转向 Human in the loop** —— 在这里反而变成了最大的架构优势。

> 人类做 Plan，Agent 做 Execute。每次 Execute 足够短，在一个 subagent 的 context window 内完成。

这就是 MVP 的核心策略：**不造框架，不对抗 Claude Code 的运行机制，完全接纳它，把精力放在注入研究者的灵魂上。**

## 为什么完全接纳 Claude Code？

> 对抗平台不如顺应平台。

### Claude Code 的运行机制到底是什么

Claude Code 的核心是一个 **model-driven agentic loop**：

```
用户输入 → [模型推理 → 工具调用 → 观察结果 → 模型推理 → ...] → 输出
```

几个关键事实：

- **它本身就是 React**。think → act → observe → repeat，模型自己决定下一步做什么。
- **上下文压缩是自动的**。context window 达到阈值时自动 compaction，用 summarization prompt 压缩历史，保留关键状态（文件修改、todo list）。你无法从 Skill 里控制何时触发、保留什么。
- **Plan 是模型行为，不是编程接口**。Claude Code 有 todo list 机制，会在 compaction 时持久化。但这是模型自己的行为模式，你只能引导不能强制。
- **Subagent 提供真正的 context 隔离**。独立 context window，执行完返回 summary。这是唯一和我原始设计真正对齐的机制。

### 原始设计 vs 实际可行性

| 原始 Learning 设计 | Claude Code 下能否实现 | MVP 策略 |
| --- | --- | --- |
| React（think→act→observe） | ✅ 天然就是 | 直接用 |
| Plan（任务拆解为 Steps） | ⚠️ 只能引导，不能强制 | **人类做 Plan** |
| Execute（按 Step 顺序执行） | ⚠️ 模型可能合并/跳步 | 每次 /learn 就是一个 Step |
| Step 级上下文压缩 | ❌ 无法主动控制 | 用 subagent fork 天然实现 |
| Plan 重写（灵活应对） | ⚠️ 模型可能自己做 | 人类根据结果调整下一步 |
| Human in the loop | ✅ 原生支持 | slash commands |

核心洞察：**把人类变成 Plan&Execute 的控制器，每次 /learn 就是一个 Step，每个 Step 在 subagent 的独立 context 里完成。** 这样：

- 不怕长程 compaction 丢失 context —— 因为每个任务足够短
- 不需要强制模型遵循 Plan —— 因为人类自己在做 Plan
- 完美契合"抽象之梯"—— 人类全程参与，每一步学到什么都是清楚的

## 整体架构

> 给 Claude Code 装上研究者的 Context。

### 核心理念

ResearcherZero MVP = **Claude Code + 一套研究者 Skills + 一个持续生长的知识文件系统**

- **Skills** 告诉 Claude 怎么做研究（搜索、阅读、抽取、存储、对话）
- **domains/** 是 Claude 的大脑（结构化知识持久存储）
- **Slash commands** 是人类与 Claude 的协作接口
- **Subagent** 是执行隔离层（独立 context，返回 summary）

### 目录结构

```
researcher-zero/                          # Plugin 根目录
├── .claude-plugin/
│   └── plugin.json                       # Plugin manifest
│
├── skills/
│   ├── research-learn/                   # 学习能力
│   │   ├── SKILL.md                      # 搜索 + 阅读 + 知识抽取的指令
│   │   └── scripts/
│   │       ├── semantic_scholar.py       # 学术搜索 API
│   │       └── tavily_search.py          # 通用搜索 API
│   │
│   ├── research-memory/                  # Memory 管理
│   │   └── SKILL.md                      # 知识的存储格式、读取规则、更新规则
│   │
│   └── research-chat/                    # 认知对话
│       └── SKILL.md                      # 如何加载 Context 并基于认知对话
│
├── commands/
│   ├── learn.md                          # /learn <任务> — 人类下达单步学习任务
│   ├── status.md                         # /status [领域] — 查看认知状态
│   └── init-domain.md                    # /init-domain <领域名> — 初始化新领域
│
└── domains/                              # Memory 文件系统
    └── _template/                        # 新领域模板
        ├── basic_info.md
        ├── taxonomy.md
        ├── main_challenge.md
        ├── network.md
        ├── human_preference.md
        └── atomic_knowledge/
            └── .gitkeep
```

相比之前的设计，做了几个简化：

1. **砍掉 research-read Skill**：阅读能力合并进 research-learn。MVP 阶段不需要独立拆分，保持 Skill 数量最少。
2. **砍掉 deep-learner subagent 定义**：直接在 /learn command 里用 `context: fork`。不额外定义 agent，减少概念层级。
3. **砍掉 /switch 和 /review**：MVP 先做一个领域跑通闭环，多领域切换和主动推荐放到后面。

### 工作流

一个典型的学习 session 长这样：

```
人类: /init-domain agent-memory
  → 从 _template/ 复制模板，创建 domains/agent-memory/

人类: /learn 搜索 Agent Memory 领域的 Survey 论文，找到最相关的 5 篇
  → [subagent fork] 调用 semantic_scholar.py 搜索
  → 返回 5 篇论文的标题、摘要、链接
  → [summary 返回主会话]

人类: /learn 精读第 2 篇 Survey，更新 basic_info 和 taxonomy
  → [subagent fork] 下载/阅读论文
  → 按 research-memory 的规则更新 domains/agent-memory/ 下的文件
  → [summary 返回主会话]

人类: /learn 搜索 Agent Memory Benchmarks，重点看最近一年的
  → [subagent fork] 搜索 + 筛选
  → 更新 main_challenge.md
  → 在 atomic_knowledge/ 下新增 benchmark 条目
  → [summary 返回主会话]

人类: /status agent-memory
  → 读取目录结构，汇报当前认知覆盖度

人类: （直接对话）Agent Memory 领域现在最大的挑战是什么？
  → research-chat 自动触发
  → 加载 domains/agent-memory/ 的 Context
  → 基于已有认知回答
```

注意这里的关键：**每次 /learn 是一个聚焦的小任务**。人类自己在做 Plan（决定学什么、学的顺序、学的深度），Agent 在 subagent 里做 Execute（搜索、阅读、抽取、存储）。这比让 Agent 自己做长程 Plan 可靠得多。

## 各模块设计

### 1. research-learn：学习引擎

```yaml
---
name: research-learn
description: >
  ResearcherZero 的学习引擎。当用户通过 /learn 下达学习任务时触发。
  负责搜索研究资料、阅读论文/网页、抽取结构化知识，并调用
  research-memory 将知识写入 domains/ 文件系统。
  Use when user gives a learning task via /learn command.
  Do NOT use for casual conversation or simple questions.
disable-model-invocation: true
allowed-tools: Bash(python *), Read, Write, Glob, Grep
---
```

`disable-model-invocation: true` 确保这个 Skill 只由人类通过 /learn 触发，不会被模型在对话中自动加载。

SKILL.md 正文包含：

- **搜索策略**：如何使用 semantic_scholar.py（学术搜索）和 tavily_search.py（通用搜索），query 的构造建议
- **阅读策略**：不同类型资料的阅读方式
  - Paper：重点抽取 Problem / Method / Metrics / Insights
  - Survey：重点抽取分类框架和高层认知
  - Benchmark：重点抽取它反映的能力挑战
  - Blog/News：重点抽取事实和工程实践
- **知识抽取规则**：学到的内容必须结构化后才能写入 Memory，不能原文搬运
- **调用 research-memory 的指引**：写入时遵循什么格式、更新时如何处理冲突

这个 Skill 合并了之前的 research-learn + research-read 的职责。在 MVP 阶段没必要拆分 —— 一个学习任务通常就是"搜索 + 阅读 + 存储"的连续动作，拆成两个 Skill 反而增加了模型协调的复杂度。

### 2. research-memory：Memory 管理

```yaml
---
name: research-memory
description: >
  管理 ResearcherZero 的知识文件系统（domains/ 目录）。
  定义知识的存储格式、读取规则和更新规则。
  Use when needing to store, retrieve, or update domain knowledge in domains/.
  Use when building context for research conversations.
  Do NOT load entire knowledge base at once — use progressive disclosure.
allowed-tools: Read, Write, Glob, Grep
---
```

SKILL.md 正文包含：

**存储规则 — 每种文件怎么写**

- `basic_info.md`：领域的基础定义，用自然语言段落描述，保持简洁（不超过 500 字）
- `taxonomy.md`：分类框架，用 Markdown 层级结构表示 Category → Concept 的树形关系
- `main_challenge.md`：核心挑战列表，每个挑战包含描述 + 相关 Benchmark + 当前 SOTA 状态
- `network.md`：概念间的关系，用自然语言描述递进/因果/演化关系
- `human_preference.md`：用户偏好（Research vs Engineering、novelty vs 可复现性等）
- `atomic_knowledge/*.md`：每个原子知识单元一个文件，YAML frontmatter 包含：
  ```yaml
  ---
  type: method | survey | benchmark | blog     # 类型
  title: "论文/文章标题"
  source: "来源 URL 或 DOI"
  date: 2026-01-15                              # 发表/发现日期
  categories: [Memory, Retrieval]               # 所属 Category
  concepts: [RAG, Long-term Memory]             # 相关 Concept
  ---
  ```

**读取规则 — 渐进式加载**

这部分是和 Claude Code 的 Progressive Disclosure 对齐的核心设计：

1. **轻量加载**（对话触发时默认）：只读 `basic_info.md` + `taxonomy.md` 的标题层级
2. **中量加载**（需要认知判断时）：追加 `main_challenge.md` + `network.md` + 浅层扫描 `atomic_knowledge/` 的 frontmatter
3. **深度加载**（讨论具体知识时）：按需读取特定的 `atomic_knowledge/*.md` 全文

**更新规则**

- 新增：直接创建新文件
- 修改：读取原文件 → 合并新信息 → 写回，保留原有内容不丢失
- 冲突：如果新信息和已有信息矛盾，标注冲突，不自动覆盖，等待人类 review

### 3. research-chat：认知对话

```yaml
---
name: research-chat
description: >
  基于已积累的领域知识进行对话。
  Auto-invoke when user discusses topics matching an existing domain in domains/.
  Loads domain context progressively and responds based on accumulated knowledge.
  Do NOT fabricate knowledge not present in domains/ — clearly distinguish
  "I know from my study" vs "I don't have this in my knowledge base".
allowed-tools: Read, Glob, Grep
---
```

SKILL.md 正文包含：

- **Context 加载流程**：对话开始时按 research-memory 的渐进式规则加载
- **回答策略**：
  - 如果问题在已有知识范围内：基于 domains/ 的内容回答，标注来源（哪个文件/哪篇论文）
  - 如果问题超出已有知识：明确说"这个我还没学到"，建议用 /learn 去学
  - 如果问题需要更深的知识：从轻量加载升级到深度加载
- **价值对齐**：读取 `human_preference.md`，调整回答风格

### Slash Commands 设计

#### /learn — 单步学习

```markdown
---
description: 下达一个聚焦的学习任务给 ResearcherZero
context: fork
allowed-tools: Bash(python *), Read, Write, Glob, Grep
---
你是 ResearcherZero，一个 AI 研究员。现在执行以下学习任务：

$ARGUMENTS

执行规则：
1. 先用 research-memory 加载当前领域的 Context（轻量加载即可）
2. 执行学习任务（搜索、阅读、抽取）
3. 按 research-memory 的存储规则将学到的知识写入 domains/
4. 最后输出一段简洁的学习总结，包括：学到了什么、更新了哪些文件、有什么发现值得后续深入
```

`context: fork` 是关键：每次 /learn 在独立的 subagent context 中执行。这意味着：
- 不污染主会话的 context
- 不用担心长程 compaction
- 返回给主会话的只是 summary
- 人类看到 summary 后决定下一步学什么

#### /status — 认知状态

```markdown
---
description: 查看 ResearcherZero 当前的领域认知状态
---
读取 domains/$ARGUMENTS/ 的结构，生成认知状态报告：

1. 基本语境：basic_info 和 taxonomy 是否已建立
2. 认知层：main_challenge 和 network 的覆盖程度
3. 原子知识：atomic_knowledge/ 下的文件数量和类型分布
4. 最近更新：最后修改的文件和时间

用简洁的方式呈现，帮助人类判断下一步该学什么。
```

#### /init-domain — 初始化领域

```markdown
---
description: 初始化一个新的研究领域
disable-model-invocation: true
---
在 domains/ 下创建新的研究领域目录：

1. 从 domains/_template/ 复制模板到 domains/$ARGUMENTS/
2. 确认目录结构完整
3. 提示人类可以开始用 /learn 进行学习
```

## 实现路线

> MVP 的哲学：先跑通闭环，再考虑优化。

### Phase 1：MVP — 一个领域的学习闭环

**目标**：选一个实际的研究领域（比如 Agent Memory），走通 "学习 → 存储 → 对话" 的完整闭环。

**实现清单**：

- [ ] `research-memory` SKILL.md — 知识存储格式和读写规则
- [ ] `research-learn` SKILL.md — 搜索 + 阅读 + 抽取的指令
- [ ] `research-chat` SKILL.md — 基于知识对话
- [ ] `semantic_scholar.py` — Semantic Scholar API wrapper
- [ ] `tavily_search.py` — Tavily Search API wrapper
- [ ] `/learn` command — 带 `context: fork`
- [ ] `/status` command
- [ ] `/init-domain` command
- [ ] `domains/_template/` — 领域模板
- [ ] `plugin.json` — Plugin manifest

**验收标准**：
1. `/init-domain agent-memory` 能创建目录
2. `/learn 搜索 Agent Memory Survey` 能搜索并返回结果
3. `/learn 阅读某篇论文并更新知识` 能正确写入 domains/
4. `/status agent-memory` 能展示当前认知状态
5. 直接对话能基于已有知识回答，区分"已学"和"未学"

**不做的事情**：多领域切换、遗忘机制、主动推荐、自动化 Plan

### Phase 2：体验优化

等 Phase 1 跑通后，根据实际使用体感来决定优化方向：

- 搜索质量不够 → 增加搜索引擎（Exa.ai、You.com 等）、优化 query 构造
- 知识存储混乱 → 优化存储格式、加强 taxonomy 管理
- 对话深度不够 → 优化 Context 加载策略、改进渐进式加载粒度
- 人类 Plan 太累 → 加一个 `/suggest-next` command，让 Claude 基于当前认知状态建议下一步学什么（仍由人类决定是否执行）

### Phase 3：认知增强

- 价值对齐层生效：human_preference 影响推荐和对话风格
- `/review` command：基于已有认知的增量更新推荐
- 遗忘机制：低频知识衰减
- 多领域支持：`/switch` command

## 关于 Plan&Execute + React 的取舍

> 最好的架构不是最完美的架构，而是最适合当前阶段的架构。

在 Learning 设计中，我提出了 Plan&Execute + React 的运转机制，它有四个优势：指令更遵循、路径更可控、Step 级上下文压缩、灵活应对。这些在自建框架下是确定性可实现的。

但在 Claude Code 下，经过严谨分析，结论是：

- **React** → 天然就是，不需要做任何事
- **Plan** → 人类来做，比让模型自动 Plan 更可靠
- **Execute** → 每次 /learn 就是一个 Step，在 subagent fork 里完成
- **Step 级压缩** → subagent 天然实现：独立 context，返回 summary

本质上，原始设计的四个优势在 MVP 中通过**人类介入 + subagent 隔离**的组合达成了，只是实现方式不同：

| 原始优势 | MVP 的实现方式 |
| --- | --- |
| 指令更遵循 | 每次 /learn 任务足够聚焦，不需要长程指令遵循 |
| 路径更可控 | 人类做 Plan，路径完全可控 |
| Step 级压缩 | subagent fork 天然隔离 |
| 灵活应对 | 人类看到每步 summary 后自由调整 |

这不是妥协，而是**用更少的工程成本达成了同等效果**。更重要的是，Learning 设计里那个"克制全自动，转向 Human in the loop"的决定，在这里被证明是对的 —— 人类参与不是退步，是让系统更可控的最实际的方式。

如果未来某天，人类做 Plan 变得太累了，我可以再加一层轻量的 orchestrator 脚本，把高频的 Plan 模式自动化。但那是 Phase 3 的事。

## Conclusion

ResearcherZero 的 MVP 策略可以用一句话概括：**不和平台对抗，把精力放在注入领域灵魂上。**

Claude Code 已经是一个成熟的 agent runtime。它的 React loop、上下文管理、subagent 隔离、文件系统操作 —— 这些都不需要我重新发明。我需要做的是定义好三件事：

1. **研究者的知识应该长什么样**（research-memory 的存储规则）
2. **研究者应该怎么学习**（research-learn 的搜索/阅读/抽取指令）
3. **研究者应该怎么和人交流**（research-chat 的对话策略）

这三件事，本质上就是给 Claude Code 写三份好的 SKILL.md。

从 GraphMemory 到 Markdown 文件系统，从自建 Agent 框架到 Claude Code Skills —— 每一次转向都在说同一件事：**不追求技术上的完备性，追求实现路径上的务实性。** 先让 ResearcherZero 活起来，再让它变强。
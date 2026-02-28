# ResearcherZero 实现规格

> 从设计到代码：ResearcherZero MVP 的技术规格文档

## 核心架构

ResearcherZero = **Claude Code + 研究者 Skills + 知识文件系统**

- **Skills**：定义研究者的能力（规划、学习、记忆、对话）
- **domains/**：持久化知识存储
- **Commands**：人类与 AI 的交互接口
- **Context fork**：执行隔离（通过 `context: fork` 实现）

## 目录结构

```
researcher-zero/
├── .claude-plugin/
│   └── plugin.json                       # Plugin manifest
│
├── skills/
│   ├── research-plan/
│   │   └── SKILL.md                      # 任务规划能力
│   │
│   ├── research-learn/
│   │   ├── SKILL.md                      # 学习执行能力
│   │   └── scripts/
│   │       ├── semantic_scholar.py       # 学术搜索
│   │
│   ├── research-memory/
│   │   └── SKILL.md                      # 知识管理能力
│   │
│   └── research-chat/
│       └── SKILL.md                      # 认知对话能力
│
├── commands/
│   ├── learn.md                          # /learn <目标>
│   ├── status.md                         # /status [领域]
│   └── init-domain.md                    # /init-domain <领域名>
│
└── domains/
    └── _template/                        # 领域模板
        ├── basic_info.md
        ├── taxonomy.md
        ├── main_challenge.md
        ├── network.md
        ├── human_preference.md
        └── atomic_knowledge/
            └── .gitkeep
```

## Skills 设计规格

### 1. research-plan

**frontmatter**:
```yaml
---
name: research-plan
description: >
  将高层学习目标拆解为可执行步骤。
  Auto-invoke when /learn command is executed.
allowed-tools: Read, Glob, Grep
---
```

**职责**:
- 理解用户的学习目标
- 评估当前认知状态（读取 domains/）
- 拆解为 2-5 个可执行步骤
- 输出简洁的执行计划

**典型规划模式**:

1. **建立基础认知**
   - 搜索 Survey 论文
   - 精读 1-2 篇
   - 抽取领域定义、分类框架
   - 更新 basic_info.md 和 taxonomy.md

2. **深入特定主题**
   - 搜索代表性工作
   - 阅读关键论文
   - 抽取技术细节
   - 创建 atomic_knowledge 条目，更新 network.md

3. **跟进最新进展**
   - 限定时间范围搜索（6-12个月）
   - 筛选高影响力工作
   - 对比已有认知
   - 更新相关文件

4. **理解核心挑战**
   - 搜索 Benchmark 工作
   - 识别能力边界
   - 关联 SOTA 进展
   - 更新 main_challenge.md

当然用户的需求不一定属于这上面四种，应该从第一性原理思考怎样学习路径最高效

**输出格式**:
```
学习目标：[用户目标]
当前状态：[已有认知概述]
执行步骤：
1. [步骤描述]
2. [步骤描述]
...
```

### 2. research-learn

**frontmatter**:
```yaml
---
name: research-learn
description: >
  ResearcherZero 的学习引擎。
  负责搜索、阅读、抽取知识，并写入 domains/。
  Use when user gives a learning task via /learn command.
disable-model-invocation: true
allowed-tools: Bash(python *), Read, Write, Glob, Grep
---
```

**职责**:
- 执行搜索（调用 semantic_scholar.py / claude code原生search）
- 阅读和理解资料
- 抽取结构化知识
- 调用 research-memory 写入 domains/

**搜索策略**:
- 学术搜索：semantic_scholar.py
- 通用搜索：Claude code 原生
- Query 构造：领域关键词 + 任务意图

**阅读策略**:
- **Paper**：Problem / Method / Metrics / Insights
- **Survey**：分类框架 + 高层认知
- **Benchmark**：能力挑战 + 评测方法
- **Blog/News**：事实 + 工程实践

**知识抽取规则**:
- 必须结构化，不能原文搬运
- 抽取完调用 research-memory 写入

### 3. research-memory

**frontmatter**:
```yaml
---
name: research-memory
description: >
  管理 domains/ 知识文件系统。
  定义存储格式、读取规则、更新规则。
  Use when storing/retrieving/updating domain knowledge.
allowed-tools: Read, Write, Glob, Grep
---
```

**存储格式**:

1. **basic_info.md**
   - 领域的基础定义
   - 自然语言段落
   - 不超过 500 字

2. **taxonomy.md**
   - 分类框架
   - Markdown 层级结构
   - Category → Concept 树形关系

3. **main_challenge.md**
   - 核心挑战列表
   - 每个挑战：描述 + Benchmark + SOTA 状态

4. **network.md**
   - 概念间关系
   - 递进/因果/演化关系描述

5. **human_preference.md**
   - 用户偏好
   - Research vs Engineering
   - Novelty vs 可复现性

6. **atomic_knowledge/*.md**
   - 每个原子知识单元一个文件
   - YAML frontmatter:
     ```yaml
     ---
     type: method | survey | benchmark | blog
     title: "标题"
     source: "URL 或 DOI"
     date: 2026-01-15
     categories: [Category1, Category2]
     concepts: [Concept1, Concept2]
     ---
     ```

**读取规则（渐进式加载）**:

1. **轻量加载**（默认）
   - basic_info.md
   - taxonomy.md 标题层级

2. **中量加载**（需要认知判断）
   - main_challenge.md
   - network.md
   - atomic_knowledge/ frontmatter 扫描

3. **深度加载**（讨论具体知识）
   - 特定 atomic_knowledge/*.md 全文

**更新规则**:
- 新增：直接创建
- 修改：读取 → 合并 → 写回
- 冲突：标注冲突，等待人类 review

### 4. research-chat

**frontmatter**:
```yaml
---
name: research-chat
description: >
  基于已有领域知识进行对话。
  Auto-invoke when user discusses topics matching existing domains.
  Clearly distinguish "I know" vs "I don't have this".
allowed-tools: Read, Glob, Grep
---
```

**职责**:
- 按 research-memory 的渐进式规则加载 Context
- 基于 domains/ 内容回答
- 区分"已学"和"未学"
- 读取 human_preference.md 调整回答风格

**回答策略**:
- 问题在已有知识范围内 → 基于 domains/ 回答，标注来源
- 问题超出已有知识 → 说"还没学到"，建议 /learn
- 需要更深知识 → 升级加载层级

## Commands 设计规格

### /learn

```markdown
---
description: 下达一个完整的学习目标给 ResearcherZero
context: fork
allowed-tools: Bash(python *), Read, Write, Glob, Grep
---

你是 ResearcherZero，一个 AI 研究员。执行以下学习任务：

$ARGUMENTS

执行规则：
1. 用 research-memory 加载当前领域 Context（轻量加载）
2. 调用 research-plan 规划学习路径：
   - 理解学习目标
   - 评估当前认知状态
   - 拆解为 2-5 个步骤
   - 输出执行计划
3. 按计划执行（可灵活调整）：
   - 搜索相关资料
   - 阅读和理解
   - 抽取结构化知识
   - 按 research-memory 规则写入 domains/
4. 输出学习总结：
   - 执行了哪些步骤
   - 学到了什么
   - 更新了哪些文件
   - 值得后续深入的发现
```

### /status

```markdown
---
description: 查看 ResearcherZero 当前的领域认知状态
---

读取 domains/$ARGUMENTS/ 的结构，生成报告：

1. 基本语境：basic_info 和 taxonomy 是否已建立
2. 认知层：main_challenge 和 network 的覆盖程度
3. 原子知识：atomic_knowledge/ 的文件数量和类型分布
4. 最近更新：最后修改的文件和时间

用简洁的方式呈现。
```

### /init-domain

```markdown
---
description: 初始化一个新的研究领域
disable-model-invocation: true
---

在 domains/ 下创建新领域：

1. 从 domains/_template/ 复制到 domains/$ARGUMENTS/
2. 确认目录结构完整
3. 提示可以开始用 /learn 学习
```

## 工作流示例

```
用户: /init-domain agent-memory
  → 创建 domains/agent-memory/

用户: /learn 建立对 Agent Memory 领域的基础认知
  → [fork 独立上下文]
  → 1. research-plan 规划：搜索 Survey → 精读 → 建立框架
  → 2. 执行：搜索 → 阅读 → 抽取 → 更新 basic_info.md 和 taxonomy.md
  → 3. 返回总结
  → [summary 返回主会话]

用户: /learn 深入了解核心挑战
  → [fork 独立上下文]
  → 规划 → 执行 → 更新 main_challenge.md
  → [summary 返回主会话]

用户: /status agent-memory
  → 展示当前认知覆盖度

用户: Agent Memory 的最大挑战是什么？
  → research-chat 触发
  → 加载 Context
  → 基于已有认知回答
```

## 实现清单

### Phase 1: MVP（核心闭环）

- [ ] **知识存储系统**
  - [ ] `domains/_template/` 模板目录
  - [ ] `research-memory` SKILL.md

- [ ] **任务规划能力**
  - [ ] `research-plan` SKILL.md

- [ ] **学习执行能力**
  - [ ] `research-learn` SKILL.md
  - [ ] `semantic_scholar.py`

- [ ] **认知对话能力**
  - [ ] `research-chat` SKILL.md

- [ ] **用户交互接口**
  - [ ] `/learn` command（带 `context: fork`）
  - [ ] `/status` command
  - [ ] `/init-domain` command

- [ ] **Plugin 配置**
  - [ ] `plugin.json`

### 验收标准

1. `/init-domain agent-memory` 能创建目录结构
2. `/learn 建立对 Agent Memory 的基础认知` 能自主规划并执行完整学习循环
3. `/learn 了解核心挑战` 能搜索 Benchmarks 并更新知识
4. `/status agent-memory` 能展示认知状态
5. 直接对话能基于已有知识回答，区分"已学"和"未学"

## 关键技术点

1. **Context fork 机制**
   - 在 command 的 frontmatter 中设置 `context: fork`
   - Claude Code 自动创建独立上下文
   - 执行完返回 summary 到主会话

2. **渐进式加载**
   - 默认轻量加载（basic_info + taxonomy 标题）
   - 需要时中量加载（challenge + network）
   - 讨论具体知识时深度加载

3. **Skills 协作**
   - research-plan 负责规划
   - research-learn 负责执行
   - research-memory 负责读写规则
   - research-chat 负责对话

4. **文件命名规范**
   - domains/ 下用领域名（小写，中划线分隔）
   - atomic_knowledge/ 下用清晰的描述性名称
   - 所有文件用 .md 后缀

## 注意事项

1. **不要过度设计**：MVP 阶段只做一个领域的学习闭环
2. **Skills 保持聚焦**：每个 Skill 职责单一清晰
3. **Context fork 是关键**：利用好独立上下文的隔离特性
4. **渐进式加载很重要**：避免一次性加载所有知识
5. **Human in the loop**：人类给目标，评估结果，决定方向

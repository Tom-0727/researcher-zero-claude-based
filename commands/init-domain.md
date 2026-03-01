---
description: 初始化一个新的研究领域
---

# /init-domain - 领域初始化命令

初始化一个新的研究领域，创建知识文件系统结构。

**领域名**: $ARGUMENTS

## 执行流程

### 1. 验证领域名

检查领域名是否符合规范:
- 使用小写字母
- 使用中划线分隔单词（不用下划线或空格）
- 只包含字母、数字和中划线

**示例**: ✅ `agent-memory`；❌ `Agent_Memory`（建议改为 `agent-memory`）

### 2. 检查领域是否已存在

使用 Glob 检查 `domains/$ARGUMENTS/` 是否已存在:
- 如果已存在，提示用户该领域已经创建
- 询问是否要查看状态（建议使用 `/status $ARGUMENTS`）
- 不要覆盖已有领域

### 3. 创建领域文件

如果领域不存在，创建目录结构并写入各文件内容:

```bash
mkdir -p domains/$ARGUMENTS/atomic_knowledge
touch domains/$ARGUMENTS/atomic_knowledge/.gitkeep
```

然后逐一创建以下文件（使用 Write 工具写入模板内容）:

**`domains/$ARGUMENTS/basic_info.md`**:
```markdown
# 基础信息

<!-- 此文件存储领域的基础定义和概述 -->
<!-- 用自然语言段落描述，不超过 500 字 -->

## 领域定义

[待补充：这个领域是什么？它研究什么问题？]

## 核心概念

[待补充：领域中的核心概念和术语]

## 应用场景

[待补充：这个领域的主要应用场景和价值]
```

**`domains/$ARGUMENTS/taxonomy.md`**:
```markdown
# 分类框架

<!-- 此文件存储领域的分类体系 -->
<!-- 使用 Markdown 层级结构表示 Category → Concept 的树形关系 -->

## [类别 1]

### [子类别 1.1]
- [概念 A]
- [概念 B]

### [子类别 1.2]
- [概念 C]

## [类别 2]

### [子类别 2.1]
- [概念 D]
- [概念 E]
```

**`domains/$ARGUMENTS/main_challenge.md`**:
```markdown
# 核心挑战

<!-- 此文件存储领域的核心挑战和难点 -->
<!-- 每个挑战包含：描述 + Benchmark + SOTA 状态 -->

## 挑战 1: [挑战名称]

**描述**: [挑战的具体描述]

**相关 Benchmark**:
- [Benchmark 名称]: [简要说明]

**SOTA 状态**:
- [当前最佳方法或性能水平]

---

## 挑战 2: [挑战名称]

**描述**: [挑战的具体描述]

**相关 Benchmark**:
- [Benchmark 名称]: [简要说明]

**SOTA 状态**:
- [当前最佳方法或性能水平]
```

**`domains/$ARGUMENTS/network.md`**:
```markdown
# 概念网络

<!-- 此文件存储概念之间的关系 -->
<!-- 描述递进、因果、演化等关系 -->

## 递进关系

- [概念 A] → [概念 B]: [关系描述]
- [概念 C] → [概念 D]: [关系描述]

## 因果关系

- [概念 X] 导致 [概念 Y]: [关系描述]

## 演化关系

- [早期方法] → [改进方法] → [最新方法]: [演化路径描述]

## 对比关系

- [方法 A] vs [方法 B]: [对比说明]
```

**`domains/$ARGUMENTS/human_preference.md`**:
```markdown
# 用户偏好

<!-- 此文件存储用户在该领域的学习偏好和关注点 -->

## 研究 vs 工程

- [ ] 偏向理论研究
- [ ] 偏向工程实践
- [ ] 两者平衡

## 内容深度

- [ ] 高层概览即可
- [ ] 需要技术细节
- [ ] 深入算法原理

## 新颖性 vs 可复现性

- [ ] 关注最新前沿进展
- [ ] 关注成熟可复现的方法
- [ ] 两者兼顾

## 特定关注点

[用户在这个领域特别关注的主题、问题或方向]
```

创建后应包含：basic_info.md, taxonomy.md, main_challenge.md, network.md, human_preference.md, atomic_knowledge/.gitkeep

### 4. 输出确认信息

```
✅ 领域 [$ARGUMENTS] 已成功初始化

创建的文件:
- domains/$ARGUMENTS/basic_info.md
- domains/$ARGUMENTS/taxonomy.md
- domains/$ARGUMENTS/main_challenge.md
- domains/$ARGUMENTS/network.md
- domains/$ARGUMENTS/human_preference.md
- domains/$ARGUMENTS/atomic_knowledge/

下一步:
1. 使用 `/learn 建立对 [领域] 的基础认知` 开始学习
2. 或者使用 `/learn [具体学习目标]` 进行针对性学习
```

示例：`/init-domain agent-memory` 成功时即输出上述格式。

## 示例执行

### 示例 1: 领域已存在
```
用户: /init-domain agent-memory

⚠️ 领域 [agent-memory] 已经存在

该领域已经创建过了。可以:
- 使用 `/status agent-memory` 查看当前认知状态
- 使用 `/learn [学习目标]` 继续学习该领域
- 如果确实需要重新初始化，请手动删除 domains/agent-memory/ 目录后再执行此命令
```

### 示例 2: 领域名不符合规范
```
用户: /init-domain Agent_Memory

❌ 领域名格式不符合规范

领域名应该:
- 使用小写字母
- 使用中划线分隔单词
- 只包含字母、数字和中划线

建议: 使用 `/init-domain agent-memory` 代替
```

**注意**：不要覆盖已存在的领域。

---
description: 查看 ResearcherZero 当前的领域认知状态
---

# /status - 认知状态查看命令

查看 ResearcherZero 在指定领域的当前认知状态。

**领域**: $ARGUMENTS

## 执行流程

### 1. 检查领域是否存在

使用 Glob 检查 `domains/$ARGUMENTS/` 是否存在:
- 如果不存在，提示用户该领域尚未初始化
- 建议使用 `/init-domain $ARGUMENTS` 创建领域

### 2. 读取领域结构

如果领域存在，读取以下信息:

#### 基本语境
- `basic_info.md`: 是否已建立？内容字数？
- `taxonomy.md`: 是否已建立？有多少个类别？

#### 认知层
- `main_challenge.md`: 是否已建立？记录了多少个挑战？
- `network.md`: 是否已建立？有多少条关系？

#### 原子知识
- `atomic_knowledge/`: 文件数量
- 类型分布: 统计 method / survey / benchmark / blog 的数量
- 时间分布: 最早和最新的知识条目日期

#### 最近更新
- 最后修改的文件名和时间（使用 `ls -lt` 排序）

### 3. 生成状态报告

用简洁的方式呈现认知状态:

```
# [领域名] 认知状态报告

## 📚 基本语境
- 基础信息: [已建立/未建立] ([字数] 字)
- 分类框架: [已建立/未建立] ([类别数] 个类别)

## 🎯 认知层
- 核心挑战: [已建立/未建立] ([挑战数] 个挑战)
- 概念网络: [已建立/未建立] ([关系数] 条关系)

## 📖 原子知识
- 总计: [总数] 个知识条目
- 类型分布:
  - Survey: [数量]
  - Method: [数量]
  - Benchmark: [数量]
  - Blog: [数量]
- 时间跨度: [最早日期] ~ [最新日期]

## 🕐 最近更新
- [文件名]: [更新时间]
- [文件名]: [更新时间]

## 💡 建议
[基于当前状态的学习建议]
```

## 示例输出

### 示例 1: 完整的认知状态
```
用户: /status agent-memory

# Agent Memory 认知状态报告

## 📚 基本语境
- 基础信息: 已建立 (458 字)
- 分类框架: 已建立 (4 个类别)

## 🎯 认知层
- 核心挑战: 已建立 (3 个挑战)
- 概念网络: 已建立 (12 条关系)

## 📖 原子知识
- 总计: 8 个知识条目
- 类型分布:
  - Survey: 2
  - Method: 4
  - Benchmark: 1
  - Blog: 1
- 时间跨度: 2024-06-15 ~ 2026-01-20

## 🕐 最近更新
- atomic_knowledge/memgpt-architecture.md: 2 hours ago
- network.md: 3 hours ago
- main_challenge.md: 1 day ago

## 💡 建议
认知状态良好。可以考虑:
- 深入了解某个具体方法的技术细节
- 跟进最近 3 个月的最新进展
```

### 示例 2: 初始化但未学习
```
用户: /status quantum-computing

# Quantum Computing 认知状态报告

## 📚 基本语境
- 基础信息: 未建立（使用模板）
- 分类框架: 未建立（使用模板）

## 🎯 认知层
- 核心挑战: 未建立
- 概念网络: 未建立

## 📖 原子知识
- 总计: 0 个知识条目

## 💡 建议
领域已初始化但尚未学习。建议:
- 使用 `/learn 建立对 Quantum Computing 的基础认知` 开始学习
```

### 示例 3: 领域不存在
```
用户: /status blockchain

该领域尚未初始化。

建议:
1. 使用 `/init-domain blockchain` 创建领域
2. 使用 `/learn 建立对 Blockchain 的基础认知` 开始学习
```

## 实现细节

### 统计 atomic_knowledge 类型分布
```bash
# 使用 grep 统计每种类型的数量
cd domains/$ARGUMENTS/atomic_knowledge
grep -h "^type:" *.md | sort | uniq -c
```

### 获取时间跨度
```bash
# 提取所有日期并排序
cd domains/$ARGUMENTS/atomic_knowledge
grep -h "^date:" *.md | sed 's/date: //' | sort
```

### 获取最近更新
```bash
# 列出最近修改的文件
cd domains/$ARGUMENTS
ls -lt *.md atomic_knowledge/*.md | head -3
```

### 统计文件状态
- 读取文件检查是否是模板内容（包含 [待补充] 等占位符）
- 统计字数: `wc -w basic_info.md`
- 统计类别数: 在 taxonomy.md 中统计 `##` 的数量

## 注意事项

1. **简洁呈现**: 信息要简洁清晰，不要过于冗长
2. **有用建议**: 根据当前状态给出合理的学习建议
3. **容错处理**: 如果某些文件不存在或格式错误，要能够处理
4. **可视化**: 使用 emoji 和格式让报告更易读

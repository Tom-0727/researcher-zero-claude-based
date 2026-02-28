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

**示例**:
- ✅ `agent-memory`
- ✅ `quantum-computing`
- ✅ `llm-agent`
- ❌ `Agent_Memory` (应该用小写和中划线)
- ❌ `agent memory` (不能有空格)

### 2. 检查领域是否已存在

使用 Glob 检查 `domains/$ARGUMENTS/` 是否已存在:
- 如果已存在，提示用户该领域已经创建
- 询问是否要查看状态（建议使用 `/status $ARGUMENTS`）
- 不要覆盖已有领域

### 3. 从模板复制创建

如果领域不存在，从 `domains/_template/` 复制:

```bash
cp -r domains/_template domains/$ARGUMENTS
```

### 4. 确认目录结构完整

检查以下文件是否都已创建:
- `basic_info.md`
- `taxonomy.md`
- `main_challenge.md`
- `network.md`
- `human_preference.md`
- `atomic_knowledge/.gitkeep`

### 5. 输出确认信息

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

## 示例执行

### 示例 1: 成功创建
```
用户: /init-domain agent-memory

✅ 领域 [agent-memory] 已成功初始化

创建的文件:
- domains/agent-memory/basic_info.md
- domains/agent-memory/taxonomy.md
- domains/agent-memory/main_challenge.md
- domains/agent-memory/network.md
- domains/agent-memory/human_preference.md
- domains/agent-memory/atomic_knowledge/

下一步:
1. 使用 `/learn 建立对 Agent Memory 的基础认知` 开始学习
2. 或者使用 `/learn [具体学习目标]` 进行针对性学习
```

### 示例 2: 领域已存在
```
用户: /init-domain agent-memory

⚠️ 领域 [agent-memory] 已经存在

该领域已经创建过了。可以:
- 使用 `/status agent-memory` 查看当前认知状态
- 使用 `/learn [学习目标]` 继续学习该领域
- 如果确实需要重新初始化，请手动删除 domains/agent-memory/ 目录后再执行此命令
```

### 示例 3: 领域名不符合规范
```
用户: /init-domain Agent_Memory

❌ 领域名格式不符合规范

领域名应该:
- 使用小写字母
- 使用中划线分隔单词
- 只包含字母、数字和中划线

建议: 使用 `/init-domain agent-memory` 代替
```

## 实现细节

### 验证领域名格式
```bash
# 检查是否只包含小写字母、数字和中划线
if [[ ! "$ARGUMENTS" =~ ^[a-z0-9-]+$ ]]; then
    echo "领域名格式不符合规范"
    exit 1
fi
```

### 检查领域是否存在
```bash
if [ -d "domains/$ARGUMENTS" ]; then
    echo "领域已存在"
    exit 1
fi
```

### 复制模板
```bash
cp -r domains/_template domains/$ARGUMENTS
```

### 验证文件完整性
```bash
# 检查所有必需文件是否存在
files=(
    "basic_info.md"
    "taxonomy.md"
    "main_challenge.md"
    "network.md"
    "human_preference.md"
    "atomic_knowledge/.gitkeep"
)

for file in "${files[@]}"; do
    if [ ! -f "domains/$ARGUMENTS/$file" ]; then
        echo "错误: 缺少文件 $file"
        exit 1
    fi
done
```

## 可选功能（未来扩展）

### 自定义模板
如果用户想为不同类型的领域使用不同模板:
- 创建 `domains/_template-research/` (偏向学术研究)
- 创建 `domains/_template-engineering/` (偏向工程实践)
- 命令支持 `--template` 参数

### 自动设置 human_preference
在初始化时询问用户偏好:
```
初始化 [agent-memory] 领域

请选择学习偏好:
1. 偏向理论研究
2. 偏向工程实践
3. 两者平衡

[等待用户选择，然后自动更新 human_preference.md]
```

## 注意事项

1. **不要覆盖**: 永远不要覆盖已存在的领域，避免丢失数据
2. **格式验证**: 确保领域名符合规范，避免文件系统问题
3. **完整性检查**: 确认所有必需文件都已创建
4. **清晰提示**: 告诉用户下一步该做什么

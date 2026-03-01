# Reasearcher Zero Claude Coded Based Implementation

> 本项目是对 [ResearcherZero](https://www.tom-blogs.top/2026/01/29/researcher-zero/intro-researcher-zero/) 的一个 Claude Code Based 的实现

具体实现设计可以[点击这里](https://www.tom-blogs.top/2026/02/28/researcher-zero/arch-design-claude-code-based-implementation/)阅读

## 安装步骤

1.	打开 Claude Code
2.	输入：
```
/plugin marketplace add Tom-0727/researcher-zero-claude-based
```
这会把你的 marketplace 加进去。 ￼
3. 再在 Claude code 中输入 `/plugin`，再tab到 "Marketplaces" 找到 researcher-zero 并探索安装

## 指令说明

- `/researcher-zero:init-domain your-learn-topic`：这个指令可以初始化一个遵循 [ResearcherZero - Context设计](https://www.tom-blogs.top/2026/02/01/researcher-zero/arch-design-context/) 的 workspace
- `/researcher-zero:learn`：你可以通过这个指令下达学习任务，ResearcherZero 将会自主拆机任务，寻找学习资料，完成学习任务，并将知识沉淀在 workspace
- `/researcher-zero:status`：你可以通过这个指令让 ResearcherZero 给你总结当前的学习状态
- 正常与 ResearcherZero 对话，它会富有知识内涵地与你交流
- 当然，你也可以利用沉淀的知识去做更多事情，比如用其搭建 Agent 阅读每天的新内容，并给你推荐更有品味和深度的讯息（这也是这个plugin的未来Todo）


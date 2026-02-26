# Usage Examples

[English](#english) | [中文](#chinese)

---

<a name="chinese"></a>
## 中文示例

### 📊 场景 1：自动问题跟踪

当团队成员遇到问题时，系统自动记录：

```
👤 成员 A: "我运行测试报错了，提示找不到模块"

🤖 Claude: [自动触发 usage-observer]
        "检测到你遇到了问题，我已自动记录：

        📋 自动识别信息：
        - 会话阶段: 调试
        - 问题描述: 运行测试报错，提示找不到模块
        - 问题类型: 执行失败
        - 相关文档: 未识别到具体文件

        需要我帮你解决这个问题吗？"

👤 成员 A: "是的，怎么解决？"

🤖 Claude: [帮助解决问题...]
        "解决方案是..."

👤 成员 A: "解决了，花了 15 分钟"

🤖 Claude: "已更新记录，标记为已解决。"
```

### 📝 场景 2：手动详细记录

需要记录更详细的信息时：

```
👤 成员 B: "记录这个问题"

🤖 Claude: "好的，我来记录。请告诉我：

        1. 当前处于什么阶段？
           （需求分析/代码编写/调试/测试/部署）

        2. 问题描述是什么？

        3. 问题类型？
           （工具错误/理解偏差/执行失败/性能问题/其他）

        4. 有解决方案吗？

        5. 大概花了多长时间？"

👤 成员 B: "代码编写阶段，Skill 没触发，应该是工具错误，
           花了 20 分钟，后来通过优化 description 解决了"

🤖 Claude: [调用 usage-recorder]
        "✅ 已记录到 2024-01-15.md

        | 时间戳 | 阶段 | 问题 | 类型 | 耗时 | 状态 |
        |--------|------|------|------|------|------|
        | 14:30 | 代码编写 | Skill 没触发 | 工具错误 | 20 | 已解决 |"
```

### 📈 场景 3：个人周报分析

个人查看使用情况：

```
👤 用户: "分析一下我本周的使用情况"

🤖 Claude: [调用 usage-analyst]
        "📊 个人使用周报 (2024-W03)

        数据概览：
        ├─ 记录数: 12
        ├─ 总耗时: 8.5 小时
        ├─ 日均: 1.7 小时
        └─ 解决率: 83%

        问题类型分布：
        工具错误    ████████░░  5 (42%)
        理解偏差    █████░░░░░  3 (25%)
        执行失败    ████░░░░░░  2 (17%)
        其他        ██░░░░░░░░  2 (17%)

        耗时分析：
        ├─ 平均解决时间: 21 分钟
        ├─ 最长耗时: 60 分钟 (调试问题)
        └─ 最短耗时: 5 分钟 (简单查询)

        本周亮点：
        ✓ 周三完成 5 个问题，效率最高
        ✓ Skill 使用熟练度提升

        改进机会：
        ⚠ 周四出现 3 个同类工具错误，建议查看相关文档
        ⚠ 测试类问题解决耗时较长，建议优化测试流程"
```

### 💭 场景 4：团队头脑风暴

团队一起优化 Claude 使用：

```
👤 团队负责人: "我们团队怎么优化 Claude 使用？"

🤖 Claude: [调用 usage-analyst 获取数据]
        [调用 usage-coach 组织讨论]

        "💭 团队头脑风暴 - Claude 使用优化

        【数据背景】
        基于过去一个月的数据：
        - 团队高频问题：Skill description 不清晰（18次）
        - 改进机会：解决率有 8% 提升空间

        【讨论主题】

        Q1: 为什么 Skill description 会成为高频问题？
           → 引导思考：是技能不足还是流程问题？

        Q2: 我们可以采取哪些措施？
           → 收集想法：培训？模板？Review机制？

        Q3: 哪些措施影响最大且最容易实施？
           → 优先级排序：影响力 vs 实施难度"

👤 成员 A: "我觉得是大家对如何写好 description 不熟悉"

👤 成员 B: "对，我们需要培训和模板"

👤 成员 C: "可以先创建一个 checklist"

🤖 Claude: "很好！总结一下大家的想法：

        📋 根因：缺乏 Skill description 编写规范

        💡 解决方案：
        1. 编写培训材料（成员B）
        2. 创建 description 模板（成员C）
        3. 建立 PR Review checklist（本周完成）

        下一步行动？"
```

### 🎯 场景 5：个人改进建议

基于数据获取个性化建议：

```
👤 用户: "看了我的使用数据，有什么建议吗？"

🤖 Claude: [调用 usage-analyst 分析数据]
        [调用 usage-coach 生成建议]

        "📊 基于你的数据分析，为你定制以下建议：

        【现状概览】
        - 两周记录 15 条，活跃度不错
        - 平均解决时间 28 分钟（团队平均 22 分钟）
        - 工具错误占比 40%（偏高）

        【改进建议】

        🎯 优先级 1: 减少工具错误
        根因分析: 可能是对工具参数不熟悉
        建议行动:
          1. 整理常用工具参数速查表
          2. 复杂操作先在小范围测试
          3. 参考 team wiki 中的工具指南
        预期效果: 工具错误率降至 20%

        🎯 优先级 2: 提高解决速度
        根因分析: 调试类问题耗时较长
        建议行动:
          1. 学习'分而治之'调试法
          2. 先缩小问题范围再深入
          3. 善用 Claude 的推理能力
        预期效果: 平均耗时降至 20 分钟

        【下周行动计划】
        □ 周一: 整理 Bash 命令速查表
        □ 周三: 练习分而治之调试法
        □ 周五: 回顾本周改进效果

        需要我详细解释任何建议吗？"
```

### 📚 场景 6：培训设计

为新成员设计培训：

```
👤 团队负责人: "给新成员设计一个 Claude 入门培训"

🤖 Claude: [调用 usage-analyst 分析能力差距]
        [调用 usage-coach 设计培训]

        "📚 新成员 Claude 入门培训方案

        【需求分析】
        基于使用数据分析，新成员需要提升：
        1. Skill description 编写能力
        2. 文件查找和导航技巧
        3. 调试和问题排查能力

        【培训大纲】

        Day 1: 初识 Claude (1小时)
        ├─ Claude Code 是什么，能做什么
        ├─ 基本交互方式和原则
        ├─ 第一个任务：熟悉环境
        └─ Q&A

        Day 2: 工具基础 (2小时)
        ├─ Read/Glob/Grep 三剑客
        ├─ Bash 命令执行
        ├─ Task 并行处理
        └─ 实践：项目导航

        Day 3: Skill 使用 (2小时)
        ├─ Skill 的概念和价值
        ├─ 如何发现和使用 Skill
        ├─ 常用 Skill 实战
        └─ 实践：用 Skill 完成文档任务

        Day 4: 高效协作 (2小时)
        ├─ 清晰表达需求
        ├─ 迭代优化技巧
        ├─ 常见错误避免
        └─ 实践：完成一个完整需求

        Day 5: 实战考核 (2小时)
        ├─ 模拟真实任务
        ├─ 导师观察指导
        ├─ 反馈和改进建议
        └─ 结业

        【配套资源】
        - 新人手册 PDF
        - 常用命令速查表
        - 内部 Skill 清单
        - FAQ 文档

        【考核标准】
        □ 能独立完成文件查找和编辑
        □ 会使用至少 5 个常用 Skill
        □ 工具错误率 < 30%
        □ 完成一个 mini project

        需要我展开某个模块的详细内容吗？"
```

---

<a name="english"></a>
## English Examples

### 📊 Scenario 1: Automatic Issue Tracking

When team members encounter problems, the system automatically records them:

```
👤 Member A: "I got an error running tests, module not found"

🤖 Claude: [Auto-trigger usage-observer]
        "Detected an issue. I've automatically recorded:

        📋 Auto-detected info:
        - Session stage: Debugging
        - Problem: Test error, module not found
        - Type: Execution failure
        - Related docs: None detected

        Would you like me to help solve this?"
```

### 📝 Scenario 2: Manual Detailed Recording

When detailed information needs to be recorded:

```
👤 Member B: "Record this issue"

🤖 Claude: "Sure, I'll record it. Please tell me:

        1. What stage are you at?
           (Analysis/Coding/Debugging/Testing/Deployment)

        2. What's the problem description?

        3. Problem type?
           (Tool error/Understanding/Execution/Performance/Other)

        4. Any solution?

        5. How long did it take?"
```

### 📈 Scenario 3: Personal Weekly Analysis

```
👤 User: "Analyze my weekly usage"

🤖 Claude: [Call usage-analyst]
        "📊 Personal Weekly Report (2024-W03)

        Overview:
        ├─ Records: 12
        ├─ Total time: 8.5 hours
        ├─ Daily average: 1.7 hours
        └─ Resolution rate: 83%

        Problem Distribution:
        Tool Error    ████████░░  5 (42%)
        Understanding █████░░░░░  3 (25%)
        Execution     ████░░░░░░  2 (17%)
        Other         ██░░░░░░░░  2 (17%)"
```

### 💭 Scenario 4: Team Brainstorming

```
👤 Team Lead: "How can we optimize Claude usage?"

🤖 Claude: [Get data via usage-analyst]
        [Facilitate via usage-coach]

        "💭 Brainstorming - Claude Usage Optimization

        [Data Background]
        Based on last month's data:
        - Top issue: Skill description unclear (18 times)
        - Improvement opportunity: 8% resolution rate gain

        [Discussion Topics]

        Q1: Why is Skill description a frequent issue?"
```

---

## More Examples

See the individual SKILL.md files for more detailed examples:
- [usage-observer/SKILL.md](skills/usage-observer/SKILL.md)
- [usage-recorder/SKILL.md](skills/usage-recorder/SKILL.md)
- [usage-analyst/SKILL.md](skills/usage-analyst/SKILL.md)
- [usage-coach/SKILL.md](skills/usage-coach/SKILL.md)

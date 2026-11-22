# ATTRIBUTION.md — 拿来说明

> 本项目遵循「拿来主义」原则：站在前人的肩膀上，但**如实说明借了什么、从哪借的、怎么用的**。
> 以下是 meeting-minutes-extractor 借鉴的来源清单。

---

## 一、方法论借鉴

| 来源 | 借鉴内容 | 如何用在本项目 |
|------|----------|----------------|
| AAR（After Action Review，行动后复盘） | 「预期 → 实际 → 差距 → 下次」的复盘闭环 | 移植为会议纪要的「目标 → 决策 → 行动项 → 未决 → 后续」闭环 |
| SMART 原则（管理学经典框架） | Specific/Measurable/Achievable/Relevant/Time-bound | 用于定义行动项四要素：行动 + 负责人 + 截止时间 + 状态 |
| 5 Why（丰田根因分析法） | 连续追问「为什么」找根因 | 用于 AI 日志中的 AAR 复盘与根因分析 |

---

## 二、技术规范借鉴

| 来源 | 借鉴内容 | 如何用在本项目 |
|------|----------|----------------|
| Anthropic / Claude Skill 开发文档 | `SKILL.md` frontmatter（name + description）结构、`.skill` 打包格式 | `SKILL.md` 的元信息与触发短语写法，`.skill`（zip）打包方式 |
| Python 标准库文档（argparse / pathlib / json / re） | 命令行参数解析、路径处理、JSON/文本解析的规范用法 | 核心脚本 `meeting_minutes_extractor.py` 的实现 |
| PEP 8（Python 代码风格指南） | snake_case 命名、docstring 约定 | 脚本与测试的代码风格 |

---

## 三、结构与交付规范借鉴

| 来源 | 借鉴内容 | 如何用在本项目 |
|------|----------|----------------|
| C5 挑战示例 wechat-doc-mapper（见 CHALLENGE.md） | `README.md / LICENSE / AI_LOG.md / ATTRIBUTION.md / .gitignore / SKILL.md / scripts / references / examples / tests` 的仓库结构 | 本仓库的目录组织直接参考该示例 |
| C4 参考技能 aar-report-generator（王春燕_C4_提交） | 「脚本驱动 + 指令驱动」双路径、零第三方依赖的设计、`脚本 + 参考框架` 的拆分 | 本技能的架构与「完整性自检」机制的设计思路 |
| GitHub 开源社区通用实践 | CONTRIBUTING.md、Issue/PR 模板、语义化版本、GitHub Actions CI | 社区要素的写法与 CI 配置 |
| MIT License 标准文本 | 开源协议原文 | LICENSE 文件 |

---

## 四、明确说明

1. 本项目**没有复制粘贴**任何被借鉴项目的代码；借鉴的是「方法论、结构、规范」，代码为 AI 辅助全新编写。
2. 核心脚本 `meeting_minutes_extractor.py` 由 DeepSeek 编码代理在人的指令下生成，并经真实运行调试（详见 AI_LOG.md）。
3. 若发现遗漏的借鉴来源，欢迎通过 Issue 或 PR 补充。

---

## 五、致谢

感谢以上所有方法论与规范的开源精神。本项目同样以 MIT 协议开放，欢迎引用、修改、分发。

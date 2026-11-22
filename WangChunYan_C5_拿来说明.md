# WangChunYan_C5_拿来说明

> 提交人：WangChunYan ｜ 项目：meeting-minutes-extractor
> 本文件对应仓库内 `ATTRIBUTION.md`，如实说明借鉴来源。

---

## 一、方法论借鉴

| 来源 | 借鉴内容 | 用在本项目 |
|------|----------|-----------|
| AAR（行动后复盘） | 预期→实际→差距→下次 的闭环 | 纪要的「目标→决策→行动→未决→后续」闭环 |
| SMART 原则 | 具体/可衡量/可达成/相关/有时限 | 行动项四要素：行动+负责人+截止时间+状态 |
| 5 Why（丰田根因法） | 连续追问找根因 | AI 日志的 AAR 复盘与根因分析 |

---

## 二、技术规范借鉴

| 来源 | 借鉴内容 | 用在本项目 |
|------|----------|-----------|
| Anthropic / Claude Skill 文档 | `SKILL.md` frontmatter、`.skill` 打包格式 | 技能元信息与触发短语 |
| Python 标准库文档（argparse/pathlib/json/re） | 参数解析、路径处理、JSON/文本解析规范 | 核心脚本实现 |
| PEP 8 | snake_case 命名、docstring 约定 | 脚本与测试代码风格 |

---

## 三、结构与交付规范借鉴

| 来源 | 借鉴内容 | 用在本项目 |
|------|----------|-----------|
| C5 示例 wechat-doc-mapper（CHALLENGE.md） | README/LICENSE/AI_LOG/ATTRIBUTION/.gitignore/SKILL/scripts/references/examples/tests 结构 | 仓库目录组织直接参考 |
| C4 技能 aar-report-generator | 脚本驱动+指令驱动双路径、零依赖设计 | 技能架构与完整性自检机制 |
| GitHub 开源社区通用实践 | CONTRIBUTING、Issue/PR 模板、语义化版本、Actions CI | 社区要素写法 |
| MIT License 标准文本 | 开源协议原文 | LICENSE 文件 |

---

## 四、明确说明

1. 本项目没有复制粘贴任何被借鉴项目的代码，借鉴的是「方法论、结构、规范」，代码为 AI 辅助全新编写。
2. 核心脚本 `meeting_minutes_extractor.py` 由 DeepSeek 编码代理在人（WangChunYan）的指令下生成，并经真实运行调试。
3. 若发现遗漏的借鉴来源，欢迎通过 Issue 或 PR 补充。

---

## 五、致谢

感谢以上来源的开源精神。本项目以 MIT 协议开放，欢迎引用、修改、分发。

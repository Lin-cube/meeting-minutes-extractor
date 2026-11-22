# AI_LOG.md — AI 生成日志

> 本日志如实记录 meeting-minutes-extractor 这个 GitHub 仓库在 C5 阶段的 AI 辅助开发过程：
> 用什么 AI、怎么指挥、迭代了几轮、我（人）做了什么、AI 做了什么、踩了什么坑、复盘了什么。

---

## 一、用了什么 AI

| 项 | 内容 |
|----|------|
| 模型 | DeepSeek（deepseek-v4-pro，经 DeepSeek Harness 编码代理调用） |
| 形态 | 编码代理（Coding Agent）——能读文件、写代码、跑命令、跑测试 |
| 辅助 | 无其他 AI 工具，单一代理完成 |

C5 要求交付一个「别人 clone 下来 5 分钟能跑」的仓库，需要**真的把文件结构搭出来、真的跑测试、真的 git 提交**，纯聊天 AI 无法验证可复现性，所以选编码代理。

---

## 二、我（人）做了什么 vs AI 做了什么

### 我做的（人的判断与决策）

1. **定方向**：决定把 C4 的 `meeting-minutes-extractor` 技能作为 C5 仓库的「实际项目」，而不是另起炉灶。
2. **定范围**：确认「先搭好本地仓库、稍后自己推送 GitHub」——本阶段不涉及真实公开仓库。
3. **验收**：逐项对照 C5 检查清单（README / License / .gitignore / AI_LOG / ATTRIBUTION / 社区要素 / CI），确认齐全。

### AI 做的（执行与生成）

1. 阅读 C5 的 `CHALLENGE.md`、`rubric.json`、`challenge.json`，提炼「必须/可选」要求。
2. 研究 CHALLENGE.md 里的 wechat-doc-mapper 示例，确定仓库结构。
3. 生成 README、LICENSE、.gitignore、.gitattributes、CONTRIBUTING、CHANGELOG、Issue/PR 模板、GitHub Actions CI。
4. 编写自动化测试并**真实运行**，发现并修复测试问题。
5. `git init` + 多次提交，搭建可推送的本地仓库。
6. 起草 C5 提交文件（repo 链接 / AI 日志 / 拿来说明）。

---

## 三、迭代记录（共 8 轮）

### 第 1 轮：读资料、拆需求

AI 先读 C5 资料，把要求拆成「必须 7 项（README/实际项目/使用说明/License/.gitignore/AI_LOG/ATTRIBUTION）+ 推荐/加分项（示例/CI/CHANGELOG/CONTRIBUTING）」，并对照 rubric 的 5 个评分维度（仓库质量/社区要素/产物完整性/AI 使用质量/复盘质量）。

### 第 2 轮：定仓库结构

按 CHALLENGE.md 的 wechat-doc-mapper 示例，确定：`SKILL.md` 放根目录，`scripts/`、`references/`、`examples/`、`tests/` 分目录，`.github/` 放 CI 和社区模板。

### 第 3 轮：写 README

严格套用 CHALLENGE.md 的 README 标准模板（一句话说明 / 解决什么问题 / 快速开始 / 示例 / 项目结构 / 技术栈 / AI 生成说明 / 借鉴来源 / License），把真实内容填进去。

### 第 4 轮：写 License 与 .gitignore

License 选 MIT（挑战推荐），版权署名 WangChunYan；.gitignore 排除 Python 缓存、编辑器文件、本地生成的模板/纪要产物；另加 `.gitattributes` 统一 LF 换行符。

### 第 5 轮：补社区要素

写 CONTRIBUTING.md、Issue 模板（bug/feature）、PR 模板、CHANGELOG——这些是 rubric「社区要素 20 分」的直接得分点。

### 第 6 轮：写测试 + CI

AI 写 `tests/test_meeting_minutes_extractor.py`（18 个用例，覆盖字段解析/行动项解析/文本与 JSON 解析/完整度自检/渲染/CLI）和 GitHub Actions CI（多 Python 版本矩阵）。**真实运行测试**时发现一个测试断言写错了（把「返回退出码 1」误写成「抛 SystemExit」），修复后 18 个用例全部通过。

### 第 7 轮：git 本地提交

`git init` 并按逻辑拆成多次 commit（核心代码 → 仓库文档 → 社区要素 → CI 与测试），保留清晰的提交历史。

### 第 8 轮：写 C5 提交文件

起草 `WangChunYan_C5_repo链接.md`、`WangChunYan_C5_AI日志.md`、`WangChunYan_C5_拿来说明.md`。

---

## 四、关键 prompt（节选，还原真实指令）

| 轮次 | 指令（大意） |
|------|------------|
| 拆需求 | 「读 C5 资料，把必须项和加分项列清楚，对照 rubric 五个维度」 |
| 结构 | 「照 wechat-doc-mapper 的结构，把 C4 技能包装成仓库」 |
| README | 「严格按标准模板写 README，一句话必须说清输入输出」 |
| 测试 | 「测试要真实跑通，别写跑不过的测试」 |
| 社区 | 「社区要素 20 分，把贡献指南、issue 模板、PR 模板都补上」 |

**指挥方式**：分轮推进、每轮验收，并要求「真实运行」作为验收标准——测试必须真跑过、git 必须真提交过。

---

## 五、真实失败经验（AAR 复盘）

| 维度 | 内容 |
|------|------|
| 目标 | 交付一个「别人 clone 后 5 分钟能跑」的专业开源仓库 |
| 过程 | 8 轮迭代，其中 1 轮是在修测试断言 |
| 结果 | 仓库结构齐全、测试 18/18 通过、可本地运行 |
| 根因 | 测试断言把「返回退出码」和「抛异常」搞混，属于「没跑就写」的典型问题 |
| 教训 | ① 测试必须真实运行，不能「写完就以为对」；② 可复现性是 C5 的生命线，任何一处「我以为能跑」都要用实际命令验证 |
| 行动 | 已把「测试真实跑通」写进贡献指南的测试约定；CI 会持续兜底 |

---

## 六、对「AI 使用质量」的自我评价

- ✅ **多轮迭代**：8 轮，而非一句话直接提交
- ✅ **prompt 优化**：从「搭个仓库」到「照示例结构 + 套模板 + 补社区要素 + 真实跑测试」逐步细化
- ✅ **工作流设计**：读资料 → 拆需求 → 定结构 → 写文档 → 补社区 → 测试 CI → git 提交 → 提交文件
- ✅ **可追溯**：本日志 + CHANGELOG + git 提交历史 + 测试记录

**最关键的体会**：C5 的本质不是「把文件放进一个文件夹」，而是「让一个陌生人 clone 下来、照着 README、5 分钟内跑起来」。AI 帮我做的最有价值的事，是**反复用「真实命令」验证可复现性**——测试真跑、示例真跑、git 真提交，这等价于提前替未来的使用者踩了一遍坑。

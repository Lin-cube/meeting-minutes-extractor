# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)（语义化版本）。

## [1.0.0] - 2026-02-20

### 新增

- 核心脚本 `meeting_minutes_extractor.py`：输入会议记录，输出结构化 Markdown 会议纪要。
- 支持两种输入：JSON 文件、以及「标签: 值」纯文本（照顾非程序员）。
- 行动项自动拆分为「行动 / 负责人 / 截止时间 / 状态」四字段。
- 输出「会议纪要完整度自检」（6 维度自动打分）。
- 命令：`--sample`（内置示例）、`--template`（生成空白模板）、`-o`（写入文件）、`--version`。
- Claude Skill 形态：`SKILL.md` + `references/meeting_minutes_framework.md`（指令路径）。
- 自动化测试 `tests/test_meeting_minutes_extractor.py` + GitHub Actions CI。
- 社区要素：贡献指南、Issue 模板、PR 模板。

### 修复

- 修复 Windows 记事本保存的 UTF-8（带 BOM）文件首行字段被静默丢弃的问题（改用 `utf-8-sig` 读取）。

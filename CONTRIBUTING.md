# 贡献指南（Contributing）

感谢你愿意为 meeting-minutes-extractor 贡献！无论是提 Issue、改文档、还是写代码，都很欢迎。

## 如何贡献

### 报告 Bug

1. 先搜索已有 [Issues](../../issues)，确认是否已有人报告。
2. 用 **Bug 报告** 模板新建 Issue，尽量附上：复现步骤、期望结果、实际结果、运行环境（Python 版本、操作系统）。
3. 如果涉及报错，请贴出完整报错信息。

### 提出新功能

用 **功能请求** 模板新建 Issue，说明：这个功能解决什么问题、期望的输入输出是什么。

### 提交代码（Pull Request）

1. Fork 本仓库并 clone 到本地。
2. 新建一个分支：`git checkout -b feat/你的功能`。
3. 修改代码，并确保现有测试通过（见下）。
4. 提交：`git commit -m "feat: 一句话说明改动"`。
5. 推送并提交 PR，描述清楚「改了什么、为什么这么改」。

## 本地开发

本仓库**零第三方依赖**，环境要求只有 Python 3.8+。

```bash
# 跑一遍内置示例
python scripts/meeting_minutes_extractor.py --sample

# 跑自动化测试
python -m unittest discover -s tests -v
```

## 测试约定

- 核心逻辑（输入解析、纪要渲染、完整度自检）都要有测试覆盖，见 `tests/`。
- 新增功能请同步新增测试。
- 提交前请保证 `python -m unittest discover -s tests` 全部通过。

## 代码风格

- 遵循 PEP 8。
- 变量、函数用 snake_case；注释用中文，说清「为什么」而不仅是「是什么」。
- 只使用 Python 标准库，**不要引入第三方依赖**（这是本项目的核心设计约束）。

## 行为准则

- 对事不对人，友好、建设性地交流。
- 尊重不同经验水平的贡献者，欢迎「新手友好」的提问。

再次感谢你的贡献！

# meeting-minutes-extractor

一句话描述：**输入**一份散乱的会议记录（JSON 或「标签: 值」纯文本），**输出**一份分章节、可执行、可追溯的 Markdown 会议纪要 + 完整度自检。

> 一个零依赖、开箱即用的「会议纪要提取器」，同时也是可安装的 Claude Skill。

---

## 解决什么问题

开会最贵的成本不是时间，而是「会后没人记得结论、没人认领行动」。散乱的会议记录（聊天刷屏、语音转写、随手笔记）一旦没人整理，就变成一堆再也找不回来的文字。

**没有它之前**：要么不记（结论靠脑子，三天全忘），要么记成流水账（只记「谁说了什么」，不提炼「定了什么、谁去做什么」）。

**有了它之后**：把会议记录一键整理成结构化纪要，强制覆盖完整闭环：

```
目标 → 摘要 → 关键决策 → 行动项 → 未决问题 → 风险 → 下次会议
```

并自动输出「会议纪要完整度自检」，客观判断这份纪要记全了没有。

---

## 快速开始

### 安装

```bash
git clone https://github.com/WangChunYan/meeting-minutes-extractor.git
cd meeting-minutes-extractor
# 无需安装任何依赖，仅需 Python 3.8+
```

> 本工具**零第三方依赖**，只用 Python 标准库，不需要 `pip install`。

### 使用

```bash
# 1. 生成空白模板（JSON）
python scripts/meeting_minutes_extractor.py --template -o 我的会议.json

# 2. 填好模板后，生成纪要
python scripts/meeting_minutes_extractor.py 我的会议.json -o 我的会议纪要.md

# 3. 或用「标签: 值」纯文本输入（非程序员也能写）
python scripts/meeting_minutes_extractor.py 我的会议.txt -o 我的会议纪要.md

# 4. 快速看效果（内置示例）
python scripts/meeting_minutes_extractor.py --sample
```

也可以把它当作 **Claude Skill** 安装：直接把本仓库放到技能目录（或解压 `.skill` 包），然后对 Claude 说「帮我把这段会议聊天记录整理成纪要」，无需碰代码。

---

## 示例

### 输入（纯文本，`标签: 值` 格式）

```text
标题: 班级读书会筹备会
日期: 2026-03-02
参会人:
- 王春燕
- 刘洋
- 孙悦
会议目标: 敲定第一期读书会的书目、时间和分工
会议纪要: 大家投票选了《被讨厌的勇气》作为第一期书目……
关键决策:
- 第一期书目定为《被讨厌的勇气》
行动项:
- 借到能坐 20 人的场地 | 刘洋 | 2026-03-09 | 进行中
- 完成导读 PPT 初稿 | 孙悦 | 2026-03-12 | 待开始
```

### 输出（Markdown 会议纪要，节选）

```markdown
# 会议纪要：班级读书会筹备会

> 会议日期：2026-03-02 ｜ 参会人：王春燕、刘洋、孙悦 ｜ 时长：20 分钟

## 三、关键决策

1. 第一期书目定为《被讨厌的勇气》

## 四、行动项

| 行动 | 负责人 | 截止时间 | 状态 |
|------|--------|----------|------|
| 借到能坐 20 人的场地 | 刘洋 | 2026-03-09 | 进行中 |
| 完成导读 PPT 初稿 | 孙悦 | 2026-03-12 | 待开始 |

## 会议纪要完整度自检（自动生成）

**完整度得分：6 / 6**
```

完整示例输入输出见 [`examples/`](./examples/)（含 JSON 与纯文本两种路径的完整输出）。

---

## 项目结构

```
meeting-minutes-extractor/
├── README.md               ← 项目说明（你在看这里）
├── LICENSE                 ← MIT 开源协议
├── AI_LOG.md               ← AI 生成日志
├── ATTRIBUTION.md          ← 拿来说明（借鉴来源）
├── CHANGELOG.md            ← 版本更新记录
├── CONTRIBUTING.md         ← 贡献指南
├── SKILL.md                ← Claude Skill 主指令（可直接安装）
├── .gitignore
├── .gitattributes
├── .github/
│   ├── workflows/ci.yml    ← GitHub Actions 自动测试
│   ├── ISSUE_TEMPLATE/     ← Issue 模板
│   └── PULL_REQUEST_TEMPLATE.md
├── scripts/
│   └── meeting_minutes_extractor.py   ← 核心引擎（零依赖）
├── references/
│   └── meeting_minutes_framework.md   ← 纪要框架（指令路径使用）
├── examples/               ← 示例输入输出
└── tests/
    └── test_meeting_minutes_extractor.py  ← 自动化测试
```

---

## 技术栈

- 语言：Python 3.8+（仅标准库，零第三方依赖）
- 输入格式：JSON / 「标签: 值」纯文本
- 输出格式：Markdown 会议纪要
- 形态：命令行脚本 + Claude Skill（双路径）
- 测试：Python `unittest` + GitHub Actions CI

---

## AI 生成说明

本项目使用 AI 辅助开发（DeepSeek 编码代理），覆盖「需求澄清 → 架构设计 → 代码编写 → 测试 → 调试 → 文档」全流程。详见 [AI_LOG.md](./AI_LOG.md)。

---

## 借鉴来源

本项目的结构与方法论参考了 AAR（行动后复盘）框架、SMART 原则，以及 Claude Skill 的标准规范。详见 [ATTRIBUTION.md](./ATTRIBUTION.md)。

---

## License

[MIT](./LICENSE) © 2026 WangChunYan

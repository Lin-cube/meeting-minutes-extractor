#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meeting_minutes_extractor.py — 会议纪要提取器（meeting-minutes-extractor）

一句话说明：
    输入一份会议记录（JSON 或「标签: 值」纯文本），
    输出一份结构化的 Markdown 会议纪要，把散乱的记录提炼成
    「目标 / 摘要 / 关键决策 / 行动项 / 未决问题 / 风险 / 下次会议」，
    并自动生成「会议纪要完整度自检」。

特性：
    * 零第三方依赖（仅用 Python 标准库），开箱即用；
    * 支持两种输入：JSON 文件 或 「标签: 值」纯文本文件；
    * 行动项自动拆成「行动 / 负责人 / 截止时间 / 状态」四字段；
    * 输出「会议纪要完整度自检」，判断纪要是否覆盖关键信息；
    * 提供 --template / --sample，降低上手门槛。

用法：
    python meeting_minutes_extractor.py 会议记录.json            # 生成纪要（打印到终端）
    python meeting_minutes_extractor.py 会议记录.json -o 纪要.md  # 生成纪要并写入文件
    python meeting_minutes_extractor.py --template                # 输出空白 JSON 模板
    python meeting_minutes_extractor.py --template -o 模板.json   # 将模板写入文件
    python meeting_minutes_extractor.py --sample                  # 使用内置示例运行一次
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

__version__ = "1.0.0"

# 行动项状态的可选值（用于自检时判断是否规范）
ACTION_STATUSES = ("待开始", "进行中", "已完成", "已阻塞")


def _force_utf8():
    """让 stdout/stderr 使用 UTF-8，避免 Windows 控制台 GBK 编码报错。"""
    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


_force_utf8()

# 可出现在输入里的字段及其中文标签（用于纯文本解析）
STR_FIELDS = ("title", "date", "objective", "summary", "duration", "next_meeting")
LIST_FIELDS = ("attendees", "decisions", "action_items", "open_questions", "risks")

FIELD_LABELS = {
    "title": "会议标题",
    "date": "日期",
    "attendees": "参会人",
    "duration": "时长",
    "objective": "会议目标",
    "summary": "会议纪要",
    "decisions": "关键决策",
    "action_items": "行动项",
    "open_questions": "未决问题",
    "risks": "风险",
    "next_meeting": "下次会议",
}

# 兼容英文标签
FIELD_ALIASES = {
    "title": ("标题", "会议标题", "主题", "title"),
    "date": ("日期", "会议日期", "date"),
    "attendees": ("参会人", "与会人", "参加人", "attendees"),
    "duration": ("时长", "会议时长", "duration"),
    "objective": ("会议目标", "目标", "objective", "议题"),
    "summary": ("会议纪要", "摘要", "过程", "纪要", "summary", "内容"),
    "decisions": ("关键决策", "决策", "结论", "decisions"),
    "action_items": ("行动项", "行动计划", "待办", "行动", "action_items", "下一步"),
    "open_questions": ("未决问题", "待定事项", "开放问题", "未决", "open_questions", "遗留问题"),
    "risks": ("风险", "阻塞", "阻碍", "风险点", "risks"),
    "next_meeting": ("下次会议", "后续安排", "下次安排", "next_meeting"),
}


# --------------------------------------------------------------------------- #
# 输入解析
# --------------------------------------------------------------------------- #
def load_json(path: Path) -> dict:
    """读取 JSON 文件并返回 dict。"""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 解析失败：{exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("JSON 顶层必须是对象（{}），例如 {\"title\": \"...\"}")
    return data


def load_text(path: Path) -> dict:
    """解析「标签: 值」纯文本，列表项用 '- ' 或 '* ' 开头。"""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    data: dict = {}
    current = None  # 当前正在填充的列表字段

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # 列表项（以 - 或 * 或 • 开头），追加到当前列表字段
        if line.startswith(("-", "*", "•")) and current:
            item = line.lstrip("-*• ").strip()
            if item:
                if current == "action_items":
                    data.setdefault(current, []).append(_parse_action(item))
                else:
                    data.setdefault(current, []).append(item)
            continue

        # 「标签: 值」行
        if ":" in line or "：" in line:
            parts = re.split(r"[:：]", line, maxsplit=1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ""
            field = _resolve_field(key)
            if field is None:
                continue  # 忽略无法识别的标签
            if field in STR_FIELDS:
                data[field] = value
                current = None
            elif field in LIST_FIELDS:
                current = field
                if value:  # 标签行自身也可能带一个值
                    if field == "action_items":
                        data.setdefault(field, []).append(_parse_action(value))
                    else:
                        data.setdefault(field, []).append(value)
                else:
                    data.setdefault(field, [])
            continue

        # 无标签的连续文本行 → 追加到当前列表字段（容错）
        if current:
            data.setdefault(current, []).append(line)

    return data


def _resolve_field(label: str):
    """把中文/英文标签解析成标准字段名，失败返回 None。"""
    label_l = label.lower().strip()
    for field, aliases in FIELD_ALIASES.items():
        if label_l in [a.lower() for a in aliases]:
            return field
    return None


def _parse_action(text: str) -> dict:
    """把「行动 | 负责人 | 截止时间 | 状态」解析成结构化行动项。"""
    parts = [p.strip() for p in text.split("|")]
    return {
        "action": parts[0] if parts[0] else "（未填写）",
        "owner": parts[1] if len(parts) > 1 and parts[1] else "未指派",
        "deadline": parts[2] if len(parts) > 2 and parts[2] else "—",
        "status": parts[3] if len(parts) > 3 and parts[3] else "待开始",
    }


def load_input(path: str) -> dict:
    """按内容自动选择 JSON 或纯文本解析。"""
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"找不到输入文件：{path}")
    raw = p.read_text(encoding="utf-8-sig", errors="replace").lstrip()
    if raw.startswith("{"):
        return load_json(p)
    return load_text(p)


# --------------------------------------------------------------------------- #
# 会议纪要完整度自检
# --------------------------------------------------------------------------- #
def completeness_check(data: dict) -> dict:
    """评估一份会议纪要的完整度，返回每个维度的 (评级, 说明)。"""
    def has_str(key, min_len=4):
        v = data.get(key)
        return isinstance(v, str) and len(v.strip()) >= min_len

    def has_list(key):
        v = data.get(key)
        return isinstance(v, list) and len(v) > 0

    checks = {}

    basic_ok = has_str("title", 1) and has_str("date", 1) and has_list("attendees")
    checks["基本信息"] = (basic_ok, "是否写清标题、日期、参会人")

    checks["目标明确"] = (has_str("objective"), "是否写清了会议目标")
    checks["纪要记录"] = (has_str("summary", 10), "是否记录了会议核心内容")
    checks["决策清晰"] = (has_list("decisions"), "是否提炼出关键决策")

    action_ok = has_list("action_items") and all(
        isinstance(a, dict) and a.get("action") and a.get("owner") != "未指派" and a.get("deadline") != "—"
        for a in data["action_items"]
    )
    checks["行动落地"] = (action_ok, "行动项是否含负责人/截止时间")

    checks["后续明确"] = (
        has_str("next_meeting") or has_list("open_questions"),
        "是否有下次会议安排或未决问题",
    )
    return checks


def _rate(ok: bool) -> str:
    return "✅" if ok else "❌"


# --------------------------------------------------------------------------- #
# 纪要渲染
# --------------------------------------------------------------------------- #
def render(data: dict) -> str:
    title = (data.get("title") or "未命名会议").strip()
    d = data.get("date") or date.today().isoformat()
    attendees = data.get("attendees") or []
    duration = (data.get("duration") or "（未填写）").strip()
    objective = (data.get("objective") or "（未填写）").strip()
    summary = (data.get("summary") or "（未填写）").strip()

    decisions = data.get("decisions") or []
    actions = data.get("action_items") or []
    open_questions = data.get("open_questions") or []
    risks = data.get("risks") or []
    next_meeting = (data.get("next_meeting") or "").strip()

    lines = []
    add = lines.append

    attendee_str = "、".join(attendees) if attendees else "（未填写）"

    add(f"# 会议纪要：{title}")
    add("")
    add(f"> 会议日期：{d} ｜ 参会人：{attendee_str} ｜ 时长：{duration}")
    add(f"> 生成工具：meeting-minutes-extractor v{__version__}")
    add("")

    add("## 一、会议目标")
    add(objective)
    add("")

    add("## 二、会议纪要（摘要）")
    add(summary)
    add("")

    add("## 三、关键决策")
    add("")
    if decisions:
        for i, item in enumerate(decisions, 1):
            add(f"{i}. {item}")
    else:
        add("- （未提炼关键决策）")
    add("")

    add("## 四、行动项")
    add("")
    if actions:
        add("| 行动 | 负责人 | 截止时间 | 状态 |")
        add("|------|--------|----------|------|")
        for a in actions:
            if isinstance(a, dict):
                add(
                    f"| {_cell(a.get('action', ''))} | {_cell(a.get('owner', '未指派'))} "
                    f"| {_cell(a.get('deadline', '—'))} | {_cell(a.get('status', '待开始'))} |"
                )
            else:
                add(f"| {_cell(str(a))} | 未指派 | — | 待开始 |")
    else:
        add("- （未填写行动项）")
    add("")

    add("## 五、未决问题")
    add("")
    if open_questions:
        for q in open_questions:
            add(f"- {q}")
    else:
        add("- （无未决问题记录）")
    add("")

    add("## 六、风险与阻塞")
    add("")
    if risks:
        for r in risks:
            add(f"- {r}")
    else:
        add("- （未识别风险或阻塞）")
    add("")

    add("## 七、下次会议")
    add("")
    add(next_meeting if next_meeting else "（未安排下次会议）")
    add("")

    add("## 八、一句话总结")
    add("")
    add(_one_liner(data))
    add("")

    # —— 会议纪要完整度自检 ——
    add("---")
    add("")
    add("## 会议纪要完整度自检（自动生成）")
    add("")
    checks = completeness_check(data)
    add("| 维度 | 评级 | 说明 |")
    add("|------|------|------|")
    ok_count = 0
    for name, (ok, desc) in checks.items():
        if ok:
            ok_count += 1
        add(f"| {name} | {_rate(ok)} | {desc} |")
    add("")
    total = len(checks)
    add(f"**完整度得分：{ok_count} / {total}**")
    if ok_count == total:
        add("")
        add("✅ 这份纪要信息完整（基本信息→目标→纪要→决策→行动→后续），可直接用于执行与追溯。")
    elif ok_count >= total - 2:
        add("")
        add("⚠️ 纪要基本完整，但仍有缺口：补齐缺失维度会让后续执行更有依据。")
    else:
        add("")
        add("❌ 纪要信息不足，建议补全目标、决策、行动项后再定稿。")
    add("")

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# 小工具
# --------------------------------------------------------------------------- #
def _cell(s) -> str:
    """转义 Markdown 表格里的竖线，避免破坏表格。"""
    return str(s).replace("|", "\\|").replace("\n", " ").strip() or "—"


def _action_texts(actions):
    out = []
    for a in actions:
        if isinstance(a, dict) and a.get("action"):
            out.append(a["action"])
        elif isinstance(a, str):
            out.append(a)
    return out


def _one_liner(data: dict) -> str:
    """自动生成一句话总结。"""
    title = (data.get("title") or "本次会议").strip()
    decisions = data.get("decisions") or []
    actions = _action_texts(data.get("action_items") or [])
    parts = [f"「{title}」的会议结论是"]
    if decisions:
        parts.append(f"关键决策：{'；'.join(decisions[:2])}")
    if actions:
        parts.append(f"行动项：{'；'.join(actions[:2])}")
    return "，".join(parts) + "。"


# --------------------------------------------------------------------------- #
# 模板 & 示例
# --------------------------------------------------------------------------- #
TEMPLATE = {
    "title": "在这里填写会议标题",
    "date": date.today().isoformat(),
    "attendees": ["张三", "李四", "王五"],
    "duration": "1 小时",
    "objective": "本次会议要达成什么？",
    "summary": "会议讨论的核心内容，按议题或时间顺序概括。",
    "decisions": ["已经拍板的关键决策 1", "已经拍板的关键决策 2"],
    "action_items": [
        {"action": "具体要做的下一步", "owner": "张三", "deadline": "YYYY-MM-DD", "status": "待开始"}
    ],
    "open_questions": ["尚未达成一致、需要后续跟进的问题"],
    "risks": ["可能影响进度的风险或阻塞"],
    "next_meeting": "下次会议时间与主题（如：2026-03-01 复盘进度）",
}

SAMPLE = {
    "title": "读书会小程序 v2 需求评审会",
    "date": "2026-02-18",
    "attendees": ["王春燕", "李雷", "韩梅梅", "林一"],
    "duration": "45 分钟",
    "objective": "对齐 v2 版本要做什么、不做什么，并明确每个人的分工与截止时间。",
    "summary": (
        "会上先过了一遍 v1 的用户反馈：大家最想要的是「读书打卡提醒」和「共读小组」。"
        "围绕这两个需求讨论了实现成本，李雷提出可以用系统通知实现打卡提醒，"
        "韩梅梅担心通知太频繁会打扰用户，最终决定做成「用户可自定义频率」。"
        "共读小组功能复杂度高，决定先做 MVP（仅支持创建小组 + 邀请好友），暂不做话题讨论区。"
    ),
    "decisions": [
        "v2 聚焦「打卡提醒 + 共读小组 MVP」两个功能",
        "打卡提醒频率由用户自定义，默认每天一次",
        "共读小组只做「创建 + 邀请」，话题讨论区推迟到 v3",
    ],
    "action_items": [
        {"action": "输出 v2 产品需求文档（PRD）", "owner": "王春燕", "deadline": "2026-02-21", "status": "进行中"},
        {"action": "开发打卡提醒后端接口", "owner": "李雷", "deadline": "2026-02-25", "status": "待开始"},
        {"action": "设计共读小组交互稿", "owner": "韩梅梅", "deadline": "2026-02-24", "status": "待开始"},
        {"action": "调研系统通知的到达率与限制", "owner": "林一", "deadline": "2026-02-22", "status": "待开始"},
    ],
    "open_questions": [
        "共读小组的「小组人数上限」暂未确定",
        "打卡提醒是否需要在用户静音时段静默",
    ],
    "risks": [
        "系统通知可能被部分机型拦截，到达率存疑",
        "四人中两人是兼职投入，排期偏紧",
    ],
    "next_meeting": "2026-02-26 14:00 评审 PRD 与交互稿",
}


# --------------------------------------------------------------------------- #
# 入口
# --------------------------------------------------------------------------- #
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="会议纪要提取器：输入会议记录，输出结构化 Markdown 会议纪要。",
        epilog="示例：python meeting_minutes_extractor.py 会议.json -o 会议纪要.md",
    )
    parser.add_argument("input", nargs="?", help="输入文件（.json 或「标签: 值」纯文本）")
    parser.add_argument("-o", "--output", help="输出 Markdown 文件路径（缺省打印到终端）")
    parser.add_argument("--template", action="store_true", help="输出空白 JSON 模板")
    parser.add_argument("--sample", action="store_true", help="使用内置示例运行一次")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    try:
        if args.template:
            report = json.dumps(TEMPLATE, ensure_ascii=False, indent=2)
            _emit(report + "\n", args.output)
            return 0

        if args.sample:
            data = SAMPLE
        elif args.input:
            data = load_input(args.input)
        else:
            parser.print_help(sys.stderr)
            return 1

        report = render(data)
        _emit(report, args.output)
        return 0

    except (FileNotFoundError, ValueError) as exc:
        print(f"[错误] {exc}", file=sys.stderr)
        print("提示：可用 `--template` 生成空白模板，或用 `--sample` 查看示例。", file=sys.stderr)
        return 1


def _emit(text: str, output):
    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"✅ 纪要已写入：{output}", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    raise SystemExit(main())

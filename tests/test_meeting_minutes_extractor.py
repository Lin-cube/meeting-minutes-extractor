#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meeting-minutes-extractor 的自动化测试。

运行方式：
    python -m unittest discover -s tests -v
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

# 让测试能导入 scripts 目录下的核心模块
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import meeting_minutes_extractor as mme  # noqa: E402


class TestFieldResolution(unittest.TestCase):
    """标签解析测试。"""

    def test_chinese_label(self):
        self.assertEqual(mme._resolve_field("标题"), "title")
        self.assertEqual(mme._resolve_field("会议目标"), "objective")
        self.assertEqual(mme._resolve_field("关键决策"), "decisions")

    def test_english_label(self):
        self.assertEqual(mme._resolve_field("title"), "title")
        self.assertEqual(mme._resolve_field("action_items"), "action_items")

    def test_unknown_label(self):
        self.assertIsNone(mme._resolve_field("不存在的标签"))


class TestActionParsing(unittest.TestCase):
    """行动项解析测试。"""

    def test_full_action(self):
        a = mme._parse_action("开发接口 | 李雷 | 2026-02-25 | 进行中")
        self.assertEqual(a["action"], "开发接口")
        self.assertEqual(a["owner"], "李雷")
        self.assertEqual(a["deadline"], "2026-02-25")
        self.assertEqual(a["status"], "进行中")

    def test_action_missing_parts(self):
        a = mme._parse_action("只写了行动")
        self.assertEqual(a["action"], "只写了行动")
        self.assertEqual(a["owner"], "未指派")
        self.assertEqual(a["deadline"], "—")
        self.assertEqual(a["status"], "待开始")


class TestTextParsing(unittest.TestCase):
    """纯文本输入解析测试。"""

    def _write(self, content: str, bom: bool = False) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )
        if bom:
            tmp.write("\ufeff")  # 模拟 Windows 记事本的 BOM
        tmp.write(content)
        tmp.close()
        return Path(tmp.name)

    def test_basic_fields(self):
        p = self._write("标题: 一次会议\n日期: 2026-03-01\n会议目标: 对齐进度\n")
        data = mme.load_text(p)
        self.assertEqual(data["title"], "一次会议")
        self.assertEqual(data["date"], "2026-03-01")
        self.assertEqual(data["objective"], "对齐进度")
        p.unlink()

    def test_list_fields_and_action(self):
        content = (
            "标题: 筹备会\n"
            "关键决策:\n"
            "- 决策一\n"
            "行动项:\n"
            "- 借场地 | 刘洋 | 2026-03-09 | 进行中\n"
        )
        p = self._write(content)
        data = mme.load_text(p)
        self.assertEqual(data["decisions"], ["决策一"])
        self.assertEqual(data["action_items"][0]["owner"], "刘洋")
        self.assertEqual(data["action_items"][0]["status"], "进行中")
        p.unlink()

    def test_bom_first_field_not_dropped(self):
        """带 BOM 的文件，首行字段不应被丢弃（回归测试）。"""
        p = self._write("标题: 一次简短的碰头\n日期: 2026-03-05\n", bom=True)
        data = mme.load_text(p)
        self.assertEqual(data["title"], "一次简短的碰头")
        p.unlink()


class TestJsonParsing(unittest.TestCase):
    """JSON 输入解析测试。"""

    def test_valid_json(self):
        raw = '{"title": "评审会", "decisions": ["决策A"]}'
        p = Path(tempfile.NamedTemporaryFile(suffix=".json", delete=False).name)
        p.write_text(raw, encoding="utf-8")
        data = mme.load_json(p)
        self.assertEqual(data["title"], "评审会")
        self.assertEqual(data["decisions"], ["决策A"])
        p.unlink()

    def test_invalid_json_raises(self):
        p = Path(tempfile.NamedTemporaryFile(suffix=".json", delete=False).name)
        p.write_text("{not valid json", encoding="utf-8")
        with self.assertRaises(ValueError):
            mme.load_json(p)
        p.unlink()

    def test_top_level_must_be_object(self):
        p = Path(tempfile.NamedTemporaryFile(suffix=".json", delete=False).name)
        p.write_text("[1, 2, 3]", encoding="utf-8")
        with self.assertRaises(ValueError):
            mme.load_json(p)
        p.unlink()


class TestCompletenessCheck(unittest.TestCase):
    """完整度自检测试。"""

    def test_complete_record_scores_full(self):
        data = {
            "title": "评审会",
            "date": "2026-02-18",
            "attendees": ["张三", "李四"],
            "objective": "对齐 v2 要做什么",
            "summary": "会上讨论了需求范围和实现成本……",
            "decisions": ["聚焦两个功能"],
            "action_items": [
                {"action": "输出 PRD", "owner": "张三", "deadline": "2026-02-21", "status": "进行中"}
            ],
            "next_meeting": "2026-02-26 评审",
        }
        checks = mme.completeness_check(data)
        self.assertTrue(all(ok for ok, _ in checks.values()))

    def test_incomplete_record_scores_low(self):
        data = {"title": "碰头", "objective": "同步进度"}
        checks = mme.completeness_check(data)
        ok_count = sum(1 for ok, _ in checks.values() if ok)
        self.assertLess(ok_count, 4)


class TestRender(unittest.TestCase):
    """纪要渲染测试。"""

    def _sample(self):
        return mme.SAMPLE

    def test_render_contains_key_sections(self):
        report = mme.render(self._sample())
        for section in (
            "# 会议纪要：",
            "## 一、会议目标",
            "## 三、关键决策",
            "## 四、行动项",
            "## 会议纪要完整度自检（自动生成）",
        ):
            self.assertIn(section, report)

    def test_render_escapes_pipe(self):
        self.assertEqual(mme._cell("a|b"), "a\\|b")


class TestCLI(unittest.TestCase):
    """命令行入口测试。"""

    def test_sample_output(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = mme.main(["--sample"])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("# 会议纪要：", out)
        self.assertIn("完整度得分", out)

    def test_template_output(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = mme.main(["--template"])
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        self.assertIn("title", data)
        self.assertIn("action_items", data)

    def test_missing_input_returns_nonzero(self):
        self.assertEqual(mme.main([]), 1)


if __name__ == "__main__":
    unittest.main()

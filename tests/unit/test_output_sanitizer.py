"""Tests for the LLM output sanitizer."""

import json

import pytest
from pydantic import BaseModel

from enterprise_skills_lib.llm.output_sanitizer import (
    _escape_control_chars_in_strings,
    _extract_json_block,
    _strip_schema_metadata,
    normalize_answer_content,
    parse_llm_json,
    sanitize_llm_json,
)


class SimpleSchema(BaseModel):
    answer: str


class ListSchema(BaseModel):
    items: list[str]


class TestSanitizeLlmJson:
    def test_clean_json_passthrough(self):
        raw = '{"answer": "hello"}'
        assert sanitize_llm_json(raw) == raw

    def test_strips_markdown_fences(self):
        raw = '```json\n{"answer": "hello"}\n```'
        result = sanitize_llm_json(raw)
        assert '"answer"' in result
        assert "```" not in result

    def test_strips_thinking_tags(self):
        raw = '<think>reasoning here</think>{"answer": "hello"}'
        result = sanitize_llm_json(raw)
        assert "<think>" not in result
        assert '"answer"' in result

    def test_replaces_unicode_whitespace(self):
        raw = '{"answer":\u00a0"hello"}'
        result = sanitize_llm_json(raw)
        assert "\u00a0" not in result

    def test_removes_zero_width_chars(self):
        raw = '{"answer": "he\u200bllo"}'
        result = sanitize_llm_json(raw)
        assert "\u200b" not in result

    def test_empty_input(self):
        assert sanitize_llm_json("") == ""
        assert sanitize_llm_json("   ") == "   "


class TestExtractJsonBlock:
    def test_extracts_object_from_preamble(self):
        text = 'Here is the result: {"answer": "test"} and some postamble'
        result = _extract_json_block(text)
        parsed = json.loads(result)
        assert parsed["answer"] == "test"

    def test_extracts_array(self):
        text = 'Result: [1, 2, 3] done'
        result = _extract_json_block(text)
        assert json.loads(result) == [1, 2, 3]

    def test_starts_with_brace(self):
        text = '{"key": "value"}'
        assert _extract_json_block(text) == text

    def test_no_json(self):
        text = "no json here"
        assert _extract_json_block(text) == text

    def test_nested_objects(self):
        text = '{"outer": {"inner": "value"}}'
        result = _extract_json_block(text)
        parsed = json.loads(result)
        assert parsed["outer"]["inner"] == "value"


class TestStripSchemaMetadata:
    def test_removes_schema_keys(self):
        parsed = {
            "answer": "hello",
            "$defs": {},
            "properties": {},
            "title": "MySchema",
            "type": "object",
        }
        result = _strip_schema_metadata(parsed, SimpleSchema)
        assert "answer" in result
        assert "$defs" not in result
        assert "properties" not in result

    def test_no_metadata_passthrough(self):
        parsed = {"answer": "hello"}
        result = _strip_schema_metadata(parsed, SimpleSchema)
        assert result == parsed


class TestParseLlmJson:
    def test_valid_json(self):
        raw = '{"answer": "hello world"}'
        result = parse_llm_json(raw, SimpleSchema)
        assert result.answer == "hello world"

    def test_with_markdown_fences(self):
        raw = '```json\n{"answer": "hello"}\n```'
        result = parse_llm_json(raw, SimpleSchema)
        assert result.answer == "hello"

    def test_invalid_json_raises(self):
        raw = "not json at all"
        with pytest.raises(ValueError):
            parse_llm_json(raw, ListSchema)

    def test_answer_fallback(self):
        raw = "Just a plain text answer without JSON"
        result = parse_llm_json(raw, SimpleSchema)
        assert len(result.answer) > 0


class TestEscapeControlChars:
    def test_escapes_newlines_in_strings(self):
        text = '{"key": "line1\nline2"}'
        result = _escape_control_chars_in_strings(text)
        assert "\\n" in result

    def test_leaves_newlines_outside_strings(self):
        text = '{\n"key": "value"\n}'
        result = _escape_control_chars_in_strings(text)
        assert result.count("\n") == 2  # Newlines outside strings preserved


class TestNormalizeAnswerContent:
    def test_fixes_double_escaped_newlines(self):
        text = "line1\\nline2"
        result = normalize_answer_content(text)
        assert result == "line1\nline2"

    def test_empty_input(self):
        assert normalize_answer_content("") == ""
        assert normalize_answer_content(None) is None

    def test_collapses_excessive_newlines(self):
        text = "a\n\n\n\n\nb"
        result = normalize_answer_content(text)
        assert result == "a\n\nb"

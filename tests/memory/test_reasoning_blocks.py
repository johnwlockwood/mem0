import json
import re

from mem0.memory.utils import isolate_json_object


def test_isolate_json_object_with_reasoning_blocks():
    """Test that isolate_json_object correctly extracts JSON from text with reasoning blocks."""
    # Test with reasoning blocks before JSON
    input_with_reasoning = '<think>\nOkay, let\'s see. The user mentioned having a Turkish Van cat that loves water.\n</think>\n\n{"facts": ["Having a Turkish Van cat that loves water would be fascinating"]}'
    result = isolate_json_object(input_with_reasoning)
    assert result == {"facts": ["Having a Turkish Van cat that loves water would be fascinating"]}


def test_isolate_json_object_with_code_blocks():
    """Test that isolate_json_object correctly extracts JSON from code blocks."""
    # Test with code blocks
    input_with_code_blocks = '```json\n{"facts": ["Prefers Pepsi over Coke"]}\n```'
    result = isolate_json_object(input_with_code_blocks)
    assert result == {"facts": ["Prefers Pepsi over Coke"]}


def test_isolate_json_object_with_mixed_content():
    """Test that isolate_json_object correctly extracts JSON from mixed content."""
    # Test with both reasoning blocks and code blocks
    input_mixed = '<think>\nAnalyzing preferences...\n</think>\n\n```json\n{"facts": ["Prefers tea over coffee"]}\n```'
    result = isolate_json_object(input_mixed)
    assert result == {"facts": ["Prefers tea over coffee"]}


def test_isolate_json_object_with_multiple_json_objects():
    """Test that isolate_json_object correctly extracts the first valid JSON object."""
    # Test with multiple JSON objects
    input_multiple = '{"first": "value"} {"second": "value"}'
    result = isolate_json_object(input_multiple)
    assert result == {"first": "value"}


def test_isolate_json_object_with_invalid_json():
    """Test that isolate_json_object returns None for invalid JSON."""
    # Test with invalid JSON
    input_invalid = "This is not JSON"
    result = isolate_json_object(input_invalid)
    assert result is None


def test_remove_code_blocks_vs_isolate_json_object():
    """
    Test that demonstrates the bug in the original remove_code_blocks function
    and how isolate_json_object fixes it.
    """

    # Define a function that simulates the old behavior
    def remove_code_blocks(content: str) -> str:
        pattern = r"^```[a-zA-Z0-9]*\n([\s\S]*?)\n```$"
        match = re.match(pattern, content.strip())
        return match.group(1).strip() if match else content.strip()

    # Input with reasoning blocks
    input_with_reasoning = '<think>\nOkay, let\'s see. The user mentioned having a Turkish Van cat that loves water.\n</think>\n\n{"facts": ["Having a Turkish Van cat that loves water would be fascinating"]}'

    # The old function would not handle reasoning blocks
    old_result = remove_code_blocks(input_with_reasoning)

    try:
        # This would fail with the old function
        json.loads(old_result)
        old_success = True
    except json.JSONDecodeError:
        old_success = False

    # The new function handles reasoning blocks correctly
    new_result = isolate_json_object(input_with_reasoning)

    # Verify that the old function fails but the new one succeeds
    assert old_success is False, "The old function should fail to parse JSON with reasoning blocks"
    assert new_result is not None, "The new function should successfully parse JSON with reasoning blocks"
    assert new_result == {"facts": ["Having a Turkish Van cat that loves water would be fascinating"]}

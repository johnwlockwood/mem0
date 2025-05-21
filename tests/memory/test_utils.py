import pytest

from mem0.memory.utils import process_message_for_memory


@pytest.fixture
def base_metadata():
    return {"user_id": "test_user", "agent_id": "test_agent"}

class TestProcessMessageForMemory:
    def test_valid_message_with_actor(self, base_metadata):
        """Test processing valid message with actor name"""
        message = {
            "role": "user", 
            "content": "Test message",
            "name": "test_actor"
        }
        result = process_message_for_memory(message, base_metadata)
        assert result is not None
        content, metadata = result
        assert content == "Test message"
        assert metadata["role"] == "user"
        assert metadata["actor_id"] == "test_actor"
        assert metadata["user_id"] == "test_user"

    def test_valid_message_no_actor(self, base_metadata):
        """Test processing valid message without actor name"""
        message = {
            "role": "assistant",
            "content": "Test reply"
        }
        result = process_message_for_memory(message, base_metadata)
        assert result is not None
        content, metadata = result
        assert content == "Test reply"
        assert metadata["role"] == "assistant"
        assert "actor_id" not in metadata

    def test_system_message(self, base_metadata):
        """Test system messages are filtered out"""
        message = {
            "role": "system",
            "content": "System prompt"
        }
        result = process_message_for_memory(message, base_metadata)
        assert result is None

    def test_invalid_message_missing_role(self, base_metadata):
        """Test message missing required role field"""
        message = {
            "content": "Invalid message"
        }
        result = process_message_for_memory(message, base_metadata)
        assert result is None

    def test_invalid_message_missing_content(self, base_metadata):
        """Test message missing required content field"""
        message = {
            "role": "user"
        }
        result = process_message_for_memory(message, base_metadata)
        assert result is None

    def test_empty_content(self, base_metadata):
        """Test message with empty content"""
        message = {
            "role": "user",
            "content": ""
        }
        result = process_message_for_memory(message, base_metadata)
        assert result is None

    def test_none_content(self, base_metadata):
        """Test message with None content"""
        message = {
            "role": "user",
            "content": None
        }
        result = process_message_for_memory(message, base_metadata)
        assert result is None

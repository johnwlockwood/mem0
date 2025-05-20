import hashlib
import json
import logging
from unittest.mock import MagicMock

import pytest
from qdrant_client.http.models.models import Record, ScoredPoint

from mem0.memory.main import AsyncMemory, Memory


def _setup_mocks(mocker):
    """Helper to setup common mocks for both sync and async fixtures"""
    mock_embedder = mocker.MagicMock()
    mock_embedder.return_value.embed.return_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    mocker.patch("mem0.utils.factory.EmbedderFactory.create", mock_embedder)

    mock_vector_store = mocker.MagicMock()
    mock_vector_store.return_value.search.return_value = []
    mocker.patch(
        "mem0.utils.factory.VectorStoreFactory.create", side_effect=[mock_vector_store.return_value, mocker.MagicMock()]
    )

    mock_llm = mocker.MagicMock()
    mocker.patch("mem0.utils.factory.LlmFactory.create", mock_llm)

    mocker.patch("mem0.memory.storage.SQLiteManager", mocker.MagicMock())

    return mock_llm, mock_vector_store


def get_vector_payload(memory_payload, vector_id):
    """Helper to get payload from memory_payload dict"""
    return memory_payload.get(vector_id)


def update_mock_record(memory_payload, vector_id, vector, payload):
    """Update a mock Record object for vector_store.update"""
    old_payload = get_vector_payload(memory_payload, vector_id)
    if old_payload:
        old_payload.update(payload)
        return Record(id=vector_id, payload=old_payload, vector=vector, shard_key=None, order_value=None)
    return None


def insert_mock_record(memory_payload, vectors, ids, payloads):
    """Insert a mock Record object for vector_store.insert
    Args:
        memory_payload: The memory payload to insert.
        vectors: The vectors to insert.
        ids: The IDs to insert.
        payloads: The payloads to insert.
    """
    if vectors and ids and payloads:
        return Record(id=ids[0], payload=payloads[0], vector=vectors[0], shard_key=None, order_value=None)
    return None


def create_mock_record(memory_payload, vector_id):
    """Create a mock Record object for vector_store.get"""
    payload = get_vector_payload(memory_payload, vector_id)
    if payload:
        return Record(id=vector_id, payload=payload, vector=None, shard_key=None, order_value=None)
    return None


def create_mock_scored_point(memory_payload, vector_id):
    """Create a mock ScoredPoint object for vector_store.search"""
    payload = get_vector_payload(memory_payload, vector_id)
    if payload:
        return ScoredPoint(
            id=vector_id, version=57, score=0.9, payload=payload, vector=None, shard_key=None, order_value=None
        )
    return None


@pytest.fixture
def base_memory_scenario():
    """Returns a complete test scenario for memory operations including:
    - Pre-existing memories
    - LLM responses
    - ID mapping
    - User input
    - Expected results

    Returns tuple of:
    1. relevant_existing_memories: Dict of memory UUIDs to their payload data
    2. fact_extraction_response: Mock LLM response for fact extraction phase
    3. memory_actions_response: Mock LLM response for memory actions phase
    4. id_mapping: Dict mapping simple IDs (0,1,2) to actual UUIDs
    5. message_from_user: Input message that triggers the memory operations
    6. expected_add_results: Expected results from memory.add()
    7. expected_update_call_values: Expected vector store update calls
    8. expected_delete_call_values: Expected vector store delete calls
    9. expected_insert_call_values: Expected vector store insert calls

    The ID mapping serves an important purpose:
    1. UUIDs are permanent identifiers in the vector store
    2. LLMs may generate invalid UUIDs during processing
    3. Mapping provides stable reference between simple IDs and UUIDs

    Workflow:
    1. Fact extraction: LLM extracts facts from user message
    2. Vector store query: Finds relevant existing memories
    3. ID mapping: Replaces UUIDs with simple IDs for LLM processing
    4. Memory actions: LLM determines UPDATE/DELETE/ADD operations
    5. Execution: Operations performed using original UUIDs
    """
    relevant_existing_memories = {
        "5e6c2501-095c-49b4-8e59-348cf6745f1d": {
            "user_id": "default_user",
            "data": "I like rice and beans",
            "hash": hashlib.md5("I like rice and beans".encode()).hexdigest(),
            "created_at": "2025-05-07T00:21:28.118301-07:00",
        },
        "f179d243-6875-4a91-a278-5d153e2ca193": {
            "user_id": "default_user",
            "data": "Likes rice",
            "hash": hashlib.md5("Likes rice".encode()).hexdigest(),
            "created_at": "2025-05-07T00:21:28.118301-07:00",
        },
        "27b6bd28-2e23-4c2e-9715-1a46b00362cd": {
            "user_id": "default_user",
            "data": "I like basmati rice",
            "hash": hashlib.md5("I like basmati rice".encode()).hexdigest(),
            "created_at": "2025-05-07T00:21:28.118301-07:00",
        },
        "43d356c7-6833-4c27-abff-2876cc37b144": {
            "user_id": "default_user",
            "data": "I like acro yoga, surfing, swimming, and paddle boarding.",
            "hash": hashlib.md5("I like acro yoga, surfing, swimming, and paddle boarding.".encode()).hexdigest(),
            "created_at": "2025-05-07T00:21:28.118301-07:00",
        },
        "be6c8333-2e75-4177-a9b6-6a2a5d75dd32": {
            "user_id": "default_user",
            "data": "Likes pizza",
            "hash": hashlib.md5("Likes pizza".encode()).hexdigest(),
            "created_at": "2025-05-07T00:21:28.118301-07:00",
        },
    }

    # ids are generated by enumerating existing memory payloads
    # and replacing the UUIDs with simple numeric strings.
    # This is mainly shown here to show the relationship
    # between the llm responses and the existing memory.
    id_mapping = {
        "0": "5e6c2501-095c-49b4-8e59-348cf6745f1d",
        "1": "f179d243-6875-4a91-a278-5d153e2ca193",
        "2": "27b6bd28-2e23-4c2e-9715-1a46b00362cd",
        "3": "43d356c7-6833-4c27-abff-2876cc37b144",
        "4": "be6c8333-2e75-4177-a9b6-6a2a5d75dd32",
    }

    message_from_user = "I like rice and beans and cheese. I like tacos"
    # The LLM is asked to extract facts from the input message
    # and perform memory actions based on the extracted facts.

    # There are two phases of prompting the LLM when adding memory:
    # 1. Fact extraction: The LLM is asked to extract facts from the input message
    # 2. Memory actions: The LLM is asked to perform memory actions based on the extracted facts
    # The LLM responses are mocked here to simulate the expected behavior
    # of the LLM in both phases.
    # The first response is a JSON string with the extracted facts
    #   * The extracted facts are used to query the vector store, which returns the relevant existing memories
    #   * The relevant memory ids are mapped temporarily to simple numeric strings
    #   * The LLM is then asked to perform memory actions based on the extracted facts
    #       given the relevant existing memories with the temporary numeric ids.
    # The second response is a JSON string with the memory actions
    #   * The memory actions are then performed on the vector store
    #       using the original UUIDs, new facts are given a new UUID
    #       and the relevant existing memories are updated or deleted
    fact_extraction_response = '{"facts": ["I like rice and beans and cheese", "Likes tacos"]}'
    memory_actions_response = json.dumps(
        {
            "memory": [
                {
                    "id": "0",
                    "text": "I like rice and beans and cheese",
                    "event": "UPDATE",
                    "old_memory": "I like rice and beans",
                },
                {"id": "1", "text": "Likes rice", "event": "NONE"},
                {"id": "2", "text": "I like basmati rice", "event": "NONE"},
                {
                    "id": "3",
                    "text": "I like acro yoga, surfing, swimming, and paddle boarding.",
                    "event": "NONE",
                },
                {"id": "4", "text": "Likes pizza", "event": "DELETE"},
                {"id": "5", "text": "Likes tacos", "event": "ADD"},
                {"id": "6", "text": "Likes Tuesdays", "event": "ADD"},
                {"id": "7", "text": "Likes T-Shirts", "event": "ADD"},
                {"id": "8", "text": "Likes Potatoes", "event": "ADD"},
                {"id": "9", "text": "Likes Pineapple", "event": "ADD"},
            ]
        }
    )

    expected_add_results = [
        {
            "id": "5e6c2501-095c-49b4-8e59-348cf6745f1d",
            "memory": "I like rice and beans and cheese",
            "event": "UPDATE",
            "previous_memory": "I like rice and beans",
        },
        {"memory": "Likes pizza", "event": "DELETE", "id": "be6c8333-2e75-4177-a9b6-6a2a5d75dd32"},
        {"memory": "Likes tacos", "event": "ADD"},
        {"memory": "Likes Tuesdays", "event": "ADD"},
        {"memory": "Likes Potatoes", "event": "ADD"},
        {"memory": "Likes Pineapple", "event": "ADD"},
        {"memory": "Likes T-Shirts", "event": "ADD"},
    ]

    expected_update_call_values = [
        {
            "vector_id": "5e6c2501-095c-49b4-8e59-348cf6745f1d",
            "data": "I like rice and beans and cheese",
            "hash": hashlib.md5("I like rice and beans and cheese".encode()).hexdigest(),
        }
    ]
    expected_delete_call_values = [
        "be6c8333-2e75-4177-a9b6-6a2a5d75dd32",
    ]
    expected_insert_call_values = [
        {
            "data": "Likes tacos",
            "hash": hashlib.md5("Likes tacos".encode()).hexdigest(),
        },
        {
            "data": "Likes Pineapple",
            "hash": hashlib.md5("Likes Pineapple".encode()).hexdigest(),
        },
        {
            "data": "Likes Potatoes",
            "hash": hashlib.md5("Likes Potatoes".encode()).hexdigest(),
        },
        {
            "data": "Likes T-Shirts",
            "hash": hashlib.md5("Likes T-Shirts".encode()).hexdigest(),
        },
        {
            "data": "Likes Tuesdays",
            "hash": hashlib.md5("Likes Tuesdays".encode()).hexdigest(),
        },
    ]

    return (
        relevant_existing_memories,
        fact_extraction_response,
        memory_actions_response,
        id_mapping,
        message_from_user,
        expected_add_results,
        expected_update_call_values,
        expected_delete_call_values,
        expected_insert_call_values,
    )


class TestMemoryLLMCalls:
    """Tests that verify direct LLM calls without mocking response methods"""

    @pytest.fixture
    def memory_for_llm_tests(self, mocker):
        """Fixture that returns a Memory instance with minimal mocks"""
        mock_llm, mock_vector_store = _setup_mocks(mocker)

        memory = Memory()
        memory.config = mocker.MagicMock()
        memory.config.custom_fact_extraction_prompt = None
        memory.config.custom_update_memory_prompt = None
        memory.api_version = "v1.1"

        return memory

    @pytest.fixture
    def async_memory_for_llm_tests(self, mocker):
        """Fixture that returns an AsyncMemory instance with minimal mocks"""
        mock_llm, mock_vector_store = _setup_mocks(mocker)

        memory = AsyncMemory()
        memory.config = mocker.MagicMock()
        memory.config.custom_fact_extraction_prompt = None
        memory.config.custom_update_memory_prompt = None
        memory.api_version = "v1.1"

        return memory

    def test_generate_fact_retrieval_response_calls_llm(self, memory_for_llm_tests):
        """Test that _generate_fact_retrieval_response calls llm.generate_response"""
        system_prompt = "Test system prompt"
        user_prompt = "Test user prompt"

        # Call the method
        memory_for_llm_tests._generate_fact_retrieval_response(system_prompt, user_prompt)

        # Verify llm.generate_response was called correctly
        memory_for_llm_tests.llm.generate_response.assert_called_once_with(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"},
        )

    def test_generate_memory_actions_response_calls_llm(self, memory_for_llm_tests):
        """Test that _generate_memory_actions_response calls llm.generate_response"""
        function_calling_prompt = "Test function calling prompt"

        # Call the method
        memory_for_llm_tests._generate_memory_actions_response(function_calling_prompt)

        # Verify llm.generate_response was called correctly
        memory_for_llm_tests.llm.generate_response.assert_called_once_with(
            messages=[{"role": "user", "content": function_calling_prompt}], response_format={"type": "json_object"}
        )

    @pytest.mark.asyncio
    async def test_async_generate_fact_retrieval_response_calls_llm(self, async_memory_for_llm_tests):
        """Test that _generate_fact_retrieval_response calls llm.generate_response in async mode"""
        system_prompt = "Test system prompt"
        user_prompt = "Test user prompt"

        # Call the method
        await async_memory_for_llm_tests._generate_fact_retrieval_response(system_prompt, user_prompt)

        # Verify llm.generate_response was called correctly
        async_memory_for_llm_tests.llm.generate_response.assert_called_once_with(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"},
        )

    @pytest.mark.asyncio
    async def test_async_generate_memory_actions_response_calls_llm(self, async_memory_for_llm_tests):
        """Test that _generate_memory_actions_response calls llm.generate_response in async mode"""
        function_calling_prompt = "Test function calling prompt"

        # Call the method
        await async_memory_for_llm_tests._generate_memory_actions_response(function_calling_prompt)

        # Verify llm.generate_response was called correctly
        async_memory_for_llm_tests.llm.generate_response.assert_called_once_with(
            messages=[{"role": "user", "content": function_calling_prompt}], response_format={"type": "json_object"}
        )


def assert_add_result(add_result, expected_add_results):
    """Helper to assert the add result against expected add results"""
    assert add_result is not None
    assert "results" in add_result
    results = add_result["results"]
    unordered_results = []
    for result in results:
        testing_result = {"memory": result["memory"], "event": result["event"]}
        if result["event"] == "UPDATE":
            testing_result["previous_memory"] = result["previous_memory"]
            testing_result["id"] = result["id"]
        if result["event"] == "DELETE":
            testing_result["id"] = result["id"]
        unordered_results.append(testing_result)

    assert len(unordered_results) == len(expected_add_results)
    assert sorted(unordered_results, key=lambda x: x["event"] + x["memory"]) == sorted(
        expected_add_results, key=lambda x: x["event"] + x["memory"]
    )


def assert_expected_updates(mock_memory, expected_update_call_values):
    """Helper to assert the update calls against expected values"""
    # Check update calls unordered
    actual_update_calls = [call[1] for call in mock_memory.vector_store.update.call_args_list]
    actual_update_call_values = [
        {
            "vector_id": call_params["vector_id"],
            "data": call_params["payload"]["data"],
            "hash": call_params["payload"]["hash"],
        }
        for call_params in actual_update_calls
    ]
    assert len(actual_update_calls) == len(expected_update_call_values)
    assert sorted(actual_update_call_values, key=lambda x: x["hash"]) == sorted(
        expected_update_call_values, key=lambda x: x["hash"]
    )


def assert_expected_deletes(mock_memory, expected_delete_call_values):
    """Helper to assert the delete calls against expected values"""
    # Check delete calls unordered
    actual_delete_calls = [call[1] for call in mock_memory.vector_store.delete.call_args_list]
    actual_delete_call_values = [call_params["vector_id"] for call_params in actual_delete_calls]
    assert len(actual_delete_calls) == len(expected_delete_call_values)
    assert sorted(actual_delete_call_values) == sorted(expected_delete_call_values)


def assert_expected_inserts(mock_memory, expected_insert_call_values):
    """Helper to assert the insert calls against expected values"""
    # Check insert calls unordered
    actual_insert_calls = [call[1] for call in mock_memory.vector_store.insert.call_args_list]
    actual_insert_call_values = [
        {
            "data": call_params["payloads"][0]["data"],
            "hash": call_params["payloads"][0]["hash"],
        }
        for call_params in actual_insert_calls
    ]
    assert len(actual_insert_calls) == len(expected_insert_call_values)
    assert sorted(actual_insert_call_values, key=lambda x: x["hash"]) == sorted(
        expected_insert_call_values, key=lambda x: x["hash"]
    )


class TestAddMemory:
    @pytest.fixture
    def mock_memory(self, mocker):
        """Fixture that returns a Memory instance with mocker-based mocks"""
        mock_llm, mock_vector_store = _setup_mocks(mocker)

        memory = Memory()
        memory.config = mocker.MagicMock()
        memory.config.custom_fact_extraction_prompt = None
        memory.config.custom_update_memory_prompt = None
        memory.api_version = "v1.1"

        # Mock response generation methods but make them flexible
        memory._generate_fact_retrieval_response = mocker.MagicMock()
        memory._generate_memory_actions_response = mocker.MagicMock()

        return memory

    def test_valid_llm_responses_memory_add_updates(self, mock_memory, caplog, base_memory_scenario):
        """Test valid response from LLM during fact extraction"""
        (
            memory_payload,
            fact_extraction_response,
            memory_actions_response,
            id_mapping,
            message_from_user,
            expected_add_results,
            expected_update_call_values,
            expected_delete_call_values,
            expected_insert_call_values,
        ) = base_memory_scenario

        from functools import partial

        mock_get = partial(create_mock_record, memory_payload)
        mock_search = partial(create_mock_scored_point, memory_payload)
        mock_update = partial(update_mock_record, memory_payload)
        mock_insert = partial(insert_mock_record, memory_payload)
        mock_memory.vector_store.insert.side_effect = mock_insert

        mock_memory.vector_store.get.side_effect = mock_get
        mock_memory.vector_store.search.return_value = [mock_search(key) for key in memory_payload.keys()]
        mock_memory.vector_store.update.side_effect = mock_update

        mock_memory._generate_fact_retrieval_response.return_value = fact_extraction_response
        mock_memory._generate_memory_actions_response.return_value = memory_actions_response

        with caplog.at_level(logging.ERROR):
            add_result = mock_memory.add(
                messages=[{"role": "user", "content": message_from_user}],
                user_id="default_user",
                agent_id="test_agent",
                metadata={},
                infer=True,
            )
        assert_add_result(add_result, expected_add_results)

        assert mock_memory._generate_fact_retrieval_response.call_count == 1
        assert mock_memory._generate_memory_actions_response.call_count == 1
        assert_expected_updates(mock_memory, expected_update_call_values)

        # Check delete calls unordered
        assert_expected_deletes(mock_memory, expected_delete_call_values)

        # Check insert calls unordered
        assert_expected_inserts(mock_memory, expected_insert_call_values)

    def test_generate_fact_retrieval_response_called(self, mock_memory, base_memory_scenario):
        """Test that _generate_fact_retrieval_response is called with expected arguments"""
        (
            memory_payload,
            fact_extraction_response,
            memory_actions_response,
            id_mapping,
            message_from_user,
            expected_add_results,
            expected_update_call_values,
            expected_delete_call_values,
            expected_insert_call_values,
        ) = base_memory_scenario

        mock_memory._generate_fact_retrieval_response.return_value = fact_extraction_response
        mock_memory._generate_memory_actions_response.return_value = memory_actions_response

        mock_memory.add(
            messages=[{"role": "user", "content": message_from_user}],
            user_id="default_user",
            agent_id="test_agent",
            metadata={},
            infer=True,
        )

        # Verify method was called once with expected arguments
        mock_memory._generate_fact_retrieval_response.assert_called_once()
        args, _ = mock_memory._generate_fact_retrieval_response.call_args
        assert isinstance(args[0], str)  # system_prompt
        assert isinstance(args[1], str)  # user_prompt
        assert "Input:" in args[1]  # Verify user prompt contains input

    def test_generate_memory_actions_response_called(self, mock_memory, base_memory_scenario):
        """Test that _generate_memory_actions_response is called with expected arguments"""
        (
            memory_payload,
            fact_extraction_response,
            memory_actions_response,
            id_mapping,
            message_from_user,
            expected_add_results,
            expected_update_call_values,
            expected_delete_call_values,
            expected_insert_call_values,
        ) = base_memory_scenario

        mock_memory._generate_fact_retrieval_response.return_value = fact_extraction_response
        mock_memory._generate_memory_actions_response.return_value = memory_actions_response

        mock_memory.add(
            messages=[{"role": "user", "content": message_from_user}],
            user_id="default_user",
            agent_id="test_agent",
            metadata={},
            infer=True,
        )

        # Verify method was called once with expected arguments
        mock_memory._generate_memory_actions_response.assert_called_once()
        args, _ = mock_memory._generate_memory_actions_response.call_args
        assert isinstance(args[0], str)  # function_calling_prompt
        assert "memory" in args[0]  # Verify prompt contains memory context

    def test_empty_llm_response_memory_actions(self, mock_memory, caplog, base_memory_scenario):
        """Test empty response in AsyncMemory.add.
        Sometimes the LLM doesn't return a valid JSON response
        and we need to handle that gracefully.
        """
        (
            memory_payload,
            fact_extraction_response,
            memory_actions_response,
            id_mapping,
            message_from_user,
            expected_add_results,
            expected_update_call_values,
            expected_delete_call_values,
            expected_insert_call_values,
        ) = base_memory_scenario

        from functools import partial

        mock_get = partial(create_mock_record, memory_payload)
        mock_search = partial(create_mock_scored_point, memory_payload)
        mock_memory.vector_store.get.side_effect = mock_get
        mock_memory.vector_store.search.return_value = [mock_search(key) for key in memory_payload.keys()]

        mock_memory._generate_fact_retrieval_response.return_value = ""
        mock_memory._generate_memory_actions_response.return_value = ""

        with caplog.at_level(logging.ERROR):
            add_result = mock_memory.add(
                messages=[{"role": "user", "content": message_from_user}],
                user_id="default_user",
                agent_id="test_agent",
                metadata={},
                infer=True,
            )

        assert mock_memory._generate_fact_retrieval_response.call_count == 1
        assert mock_memory._generate_memory_actions_response.call_count == 1
        assert add_result is not None
        assert "results" in add_result
        results = add_result["results"]
        assert results == []
        assert "Invalid JSON response" in caplog.text
        assert "Error in new_retrieved_facts:" in caplog.text
        assert mock_memory.vector_store.update.call_count == 0
        assert mock_memory.vector_store.insert.call_count == 0


@pytest.mark.asyncio
class TestAsyncAddMemory:
    @pytest.fixture
    def mock_async_memory(self, mocker):
        """Fixture for AsyncMemory with mocker-based mocks"""
        _, mock_vector_store = _setup_mocks(mocker)

        memory = AsyncMemory()
        memory.config = mocker.MagicMock()
        memory.config.custom_fact_extraction_prompt = None
        memory.config.custom_update_memory_prompt = None
        memory.api_version = "v1.1"

        # Mock the new async response generation methods
        memory._generate_fact_retrieval_response = mocker.AsyncMock()
        memory._generate_memory_actions_response = mocker.AsyncMock()

        return memory

    @pytest.mark.asyncio
    async def test_valid_llm_responses_memory_add_updates(
        self, mock_async_memory, caplog, mocker, base_memory_scenario
    ):
        """Test valid response in AsyncMemory.add"""
        (
            memory_payload,
            fact_extraction_response,
            memory_actions_response,
            id_mapping,
            message_from_user,
            expected_add_results,
            expected_update_call_values,
            expected_delete_call_values,
            expected_insert_call_values,
        ) = base_memory_scenario

        from functools import partial

        mock_get = partial(create_mock_record, memory_payload)
        mock_search = partial(create_mock_scored_point, memory_payload)
        mock_update = partial(update_mock_record, memory_payload)
        mock_insert = partial(insert_mock_record, memory_payload)
        mock_async_memory.vector_store.insert.side_effect = mock_insert

        mock_async_memory.vector_store.get.side_effect = mock_get
        mock_async_memory.vector_store.search.return_value = [mock_search(key) for key in memory_payload.keys()]
        mock_async_memory.vector_store.update.side_effect = mock_update

        mock_async_memory._generate_fact_retrieval_response.return_value = fact_extraction_response
        mock_async_memory._generate_memory_actions_response.return_value = memory_actions_response

        with caplog.at_level(logging.ERROR):
            add_result = await mock_async_memory.add(
                messages=[{"role": "user", "content": message_from_user}],
                user_id="default_user",
                agent_id="test_agent",
                metadata={},
                infer=True,
            )

        assert_add_result(add_result, expected_add_results)

        assert mock_async_memory._generate_fact_retrieval_response.call_count == 1
        assert mock_async_memory._generate_memory_actions_response.call_count == 1
        assert_expected_updates(mock_async_memory, expected_update_call_values)

        assert_expected_updates(mock_async_memory, expected_update_call_values)

        # Check delete calls unordered
        assert_expected_deletes(mock_async_memory, expected_delete_call_values)

        # Check insert calls unordered
        assert_expected_inserts(mock_async_memory, expected_insert_call_values)

    @pytest.mark.asyncio
    async def test_async_generate_fact_retrieval_response_called(self, mock_async_memory, base_memory_scenario):
        """Test that _generate_fact_retrieval_response is called with expected arguments in async mode"""
        (
            memory_payload,
            fact_extraction_response,
            memory_actions_response,
            id_mapping,
            message_from_user,
            expected_add_results,
            expected_update_call_values,
            expected_delete_call_values,
            expected_insert_call_values,
        ) = base_memory_scenario

        mock_async_memory._generate_fact_retrieval_response.return_value = fact_extraction_response
        mock_async_memory._generate_memory_actions_response.return_value = memory_actions_response

        await mock_async_memory.add(
            messages=[{"role": "user", "content": message_from_user}],
            user_id="default_user",
            agent_id="test_agent",
            metadata={},
            infer=True,
        )

        # Verify method was called once with expected arguments
        mock_async_memory._generate_fact_retrieval_response.assert_called_once()
        args, _ = mock_async_memory._generate_fact_retrieval_response.call_args
        assert isinstance(args[0], str)  # system_prompt
        assert isinstance(args[1], str)  # user_prompt
        assert "Input:" in args[1]  # Verify user prompt contains input

    @pytest.mark.asyncio
    async def test_async_generate_memory_actions_response_called(self, mock_async_memory, base_memory_scenario):
        """Test that _generate_memory_actions_response is called with expected arguments in async mode"""
        (
            memory_payload,
            fact_extraction_response,
            memory_actions_response,
            id_mapping,
            message_from_user,
            expected_add_results,
            expected_update_call_values,
            expected_delete_call_values,
            expected_insert_call_values,
        ) = base_memory_scenario

        mock_async_memory._generate_fact_retrieval_response.return_value = fact_extraction_response
        mock_async_memory._generate_memory_actions_response.return_value = memory_actions_response

        await mock_async_memory.add(
            messages=[{"role": "user", "content": message_from_user}],
            user_id="default_user",
            agent_id="test_agent",
            metadata={},
            infer=True,
        )

        # Verify method was called once with expected arguments
        mock_async_memory._generate_memory_actions_response.assert_called_once()
        args, _ = mock_async_memory._generate_memory_actions_response.call_args
        assert isinstance(args[0], str)  # function_calling_prompt
        assert "memory" in args[0]  # Verify prompt contains memory context

    @pytest.mark.asyncio
    async def test_async_empty_llm_response_memory_actions(
        self, mock_async_memory, caplog, mocker, base_memory_scenario
    ):
        """Test empty response in AsyncMemory.add.
        Sometimes the LLM doesn't return a valid JSON response
        and we need to handle that gracefully.
        """
        (
            memory_payload,
            fact_extraction_response,
            memory_actions_response,
            id_mapping,
            message_from_user,
            expected_add_results,
            expected_update_call_values,
            expected_delete_call_values,
            expected_insert_call_values,
        ) = base_memory_scenario
        from functools import partial

        mock_get = partial(create_mock_record, memory_payload)
        mock_search = partial(create_mock_scored_point, memory_payload)
        mock_async_memory.vector_store.get.side_effect = mock_get
        mock_async_memory.vector_store.search.return_value = [mock_search(key) for key in memory_payload.keys()]

        mocker.patch("mem0.utils.factory.EmbedderFactory.create", return_value=MagicMock())
        mock_async_memory._generate_fact_retrieval_response.return_value = ""
        mock_async_memory._generate_memory_actions_response.return_value = ""

        with caplog.at_level(logging.ERROR):
            add_result = await mock_async_memory.add(
                messages=[{"role": "user", "content": message_from_user}],
                user_id="default_user",
                agent_id="test_agent",
                metadata={},
                infer=True,
            )
        assert mock_async_memory._generate_fact_retrieval_response.call_count == 1
        assert mock_async_memory._generate_memory_actions_response.call_count == 1
        assert add_result is not None
        assert "results" in add_result
        results = add_result["results"]
        assert results == []
        assert "Invalid JSON response" in caplog.text
        assert "Error in new_retrieved_facts:" in caplog.text
        assert mock_async_memory.vector_store.update.call_count == 0
        assert mock_async_memory.vector_store.insert.call_count == 0

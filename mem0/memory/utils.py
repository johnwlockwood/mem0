import json
from typing import Any

from mem0.configs.prompts import FACT_RETRIEVAL_PROMPT


def get_fact_retrieval_messages(message):
    return FACT_RETRIEVAL_PROMPT, f"Input:\n{message}"


def parse_messages(messages):
    response = ""
    for msg in messages:
        if msg["role"] == "system":
            response += f"system: {msg['content']}\n"
        if msg["role"] == "user":
            response += f"user: {msg['content']}\n"
        if msg["role"] == "assistant":
            response += f"assistant: {msg['content']}\n"
    return response


def format_entities(entities):
    if not entities:
        return ""

    formatted_lines = []
    for entity in entities:
        simplified = f"{entity['source']} -- {entity['relatationship']} -- {entity['destination']}"
        formatted_lines.append(simplified)

    return "\n".join(formatted_lines)


def isolate_json_object(content: str) -> Any | None:
    """
    Isolates and parses the first valid JSON object or array found within a string.

    Handles JSON embedded within other text, code blocks, or reasoning blocks.

    Args:
        content: The input string potentially containing a JSON object or array.

    Returns:
        The parsed JSON object/array if found and valid, otherwise None.
    """
    content = content.strip()

    # Find the first potential start of a JSON object or array
    first_brace = content.find("{")
    first_bracket = content.find("[")

    start_index = -1
    start_char = ""

    if first_brace == -1 and first_bracket == -1:
        return None  # No JSON object/array start found
    elif first_brace == -1:
        start_index = first_bracket
        start_char = "["
    elif first_bracket == -1:
        start_index = first_brace
        start_char = "{"
    else:
        start_index = min(first_brace, first_bracket)
        start_char = "{" if start_index == first_brace else "["

    end_char = "}" if start_char == "{" else "]"

    brace_level = 0
    in_string = False
    escape_next = False

    for i in range(start_index, len(content)):
        char = content[i]

        if in_string:
            if escape_next:
                escape_next = False
            elif char == "\\":
                escape_next = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == start_char:
            brace_level += 1
        elif char == end_char:
            brace_level -= 1
            if brace_level == 0:
                # Found the potential end of the JSON object/array
                potential_json = content[start_index : i + 1]
                try:
                    return json.loads(potential_json)
                except json.JSONDecodeError:
                    # If parsing fails, it might not be the correct end, continue searching
                    # Or it could be invalid JSON, in which case we'll eventually return None
                    pass  # Continue the loop to find a potentially larger valid JSON

    # If we reach here, no valid JSON object/array was found and parsed
    return None


def get_image_description(image_obj, llm, vision_details):
    """
    Get the description of the image
    """

    if isinstance(image_obj, str):
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "A user is providing an image. Provide a high level description of the image and do not include any additional text.",
                    },
                    {"type": "image_url", "image_url": {"url": image_obj, "detail": vision_details}},
                ],
            },
        ]
    else:
        messages = [image_obj]

    response = llm.generate_response(messages=messages)
    return response


def parse_vision_messages(messages, llm=None, vision_details="auto"):
    """
    Parse the vision messages from the messages
    """
    returned_messages = []
    for msg in messages:
        if msg["role"] == "system":
            returned_messages.append(msg)
            continue

        # Handle message content
        if isinstance(msg["content"], list):
            # Multiple image URLs in content
            description = get_image_description(msg, llm, vision_details)
            returned_messages.append({"role": msg["role"], "content": description})
        elif isinstance(msg["content"], dict) and msg["content"].get("type") == "image_url":
            # Single image content
            image_url = msg["content"]["image_url"]["url"]
            try:
                description = get_image_description(image_url, llm, vision_details)
                returned_messages.append({"role": msg["role"], "content": description})
            except Exception:
                raise Exception(f"Error while downloading {image_url}.")
        else:
            # Regular text content
            returned_messages.append(msg)

    return returned_messages

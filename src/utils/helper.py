import json
from pydantic_ai.messages import ModelResponse

# Filter out the latest response


def to_chat_message(messages: list, role: str):
    for m in messages:
        if isinstance(m, ModelResponse):
            first_part = m.parts[0]
            content = None

            # First try to get content from args if available
            if hasattr(first_part, "args") and first_part.args:
                if hasattr(first_part.args, "args_json"):
                    try:
                        content = json.loads(first_part.args.args_json)["question"]
                    except (json.JSONDecodeError, KeyError):
                        pass

            # If no content yet, try direct content attribute
            if not content and hasattr(first_part, "content"):
                content = first_part.content

            # If still no content, try string representation
            if not content:
                content = str(first_part)

            return {"role": role, "content": content}

    return {"role": role, "content": "No content available"}

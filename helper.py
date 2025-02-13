import json
from pydantic_ai.messages import ModelResponse

# Filter out the latest response


def to_chat_message(messages: list, role: str):
    for m in messages:
        if isinstance(m, ModelResponse):
            first_part = m.parts[0]
            content = None
            if hasattr(first_part, "args") and first_part.args:
                try:
                    content = json.loads(first_part.args.args_json)["question"]
                except (json.JSONDecodeError, KeyError):
                    pass

            # Fall back to direct content if ModelResponse is not of custom class
            if not content and hasattr(first_part, "content"):
                content = first_part.content

            return {
                "role": role,
                "timestamp": m.timestamp.isoformat(),
                "content": content,
            }

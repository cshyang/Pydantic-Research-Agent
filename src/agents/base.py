"""Base configuration and setup for all agents."""

from pydantic_ai import Agent
from src.core.config import DEFAULT_MODEL


def create_agent(*args, model=DEFAULT_MODEL, **kwargs) -> Agent:
    """Factory function to create agents with common configuration.

    Args:
        *args: Positional arguments to pass to Agent
        model: Model to use, defaults to config.DEFAULT_MODEL
        **kwargs: Keyword arguments to pass to Agent
    """
    # Allow overriding the model if specified in args
    if args and isinstance(args[0], str) and args[0].startswith("openai:"):
        model = args[0]
        args = args[1:]

    return Agent(model, *args, **kwargs)

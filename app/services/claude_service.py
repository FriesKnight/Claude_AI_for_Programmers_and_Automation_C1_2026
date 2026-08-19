# route/service -> ClaudeService -> Anthropic SDK
# input -> build one Claude request -> send request -> receive response -> return result
# Goal -> decide what to do -> choose tool

from dataclasses import dataclass

from anthropic import AsyncAnthropic

from app.config import get_settings


class ClaudeConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class ClaudeTextResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int


class ClaudeService:
    def __init__(self) -> None:
        settings = get_settings()

        if settings.anthropic_api_key is None:
            raise ClaudeConfigurationError(
                "ANTHROPIC_API_KEY is not configured."
            )

        api_key = (
            settings.anthropic_api_key
            .get_secret_value()
            .strip()
        )

        if not api_key:
            raise ClaudeConfigurationError(
                "ANTHROPIC_API_KEY is empty."
            )

        if not settings.claude_model:
            raise ClaudeConfigurationError(
                "CLAUDE_MODEL is not configured."
            )

        self.model = settings.claude_model

        self.client = AsyncAnthropic(
            api_key=api_key,
            timeout=settings.claude_timeout_seconds,
            max_retries=settings.claude_max_retries,
        )

    async def generate_text(
        self,
        user_message: str,
        *,
        max_tokens: int = 300,
        system: str | None = None,
    ) -> ClaudeTextResult:
        request = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
        }

        if system:
            request["system"] = system

        message = await self.client.messages.create(
            **request
        )

        text_parts = [
            block.text
            for block in message.content
            if block.type == "text"
        ]

        text = "\n".join(text_parts).strip()

        return ClaudeTextResult(
            text=text,
            model=message.model,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )

    async def close(self) -> None:
        await self.client.close()

from app.prompts.generate_response import (
    GENERATE_RESPONSE_SYSTEM_PROMPT,
)
from app.services.claude_service import (
    ClaudeService,
    ClaudeTextResult,
)


class ResponseService:
    def __init__(
        self,
        claude_service: ClaudeService,
    ) -> None:
        self.claude_service = claude_service

    async def generate_response(
        self,
        message: str,
    ) -> ClaudeTextResult:
        user_prompt = (
            "Customer support message:\n"
            + message
        )

        return await self.claude_service.generate_text(
            user_prompt,
            system=GENERATE_RESPONSE_SYSTEM_PROMPT,
            max_tokens=300,
        )

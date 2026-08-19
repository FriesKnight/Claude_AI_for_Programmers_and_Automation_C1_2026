from pydantic import Field

from app.schemas.common import StrictModel


class AIUsage(StrictModel):
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)

from pydantic import BaseModel, Field

# What the client sends
class SummariseRequest(BaseModel):
    text: str = Field(
        min_length=20,
        max_length=5000,
    )

# What our API returns
class SummariseResponse(BaseModel):
    summary: str
    model: str
    input_tokens: int
    output_tokens: int
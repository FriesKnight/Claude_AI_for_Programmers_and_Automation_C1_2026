from pydantic import Field, model_validator

from app.schemas.common import (
    Priority,
    Sentiment,
    StrictModel,
    TicketCategory,
)
from app.schemas.usage import AIUsage


class SummariseRequest(StrictModel):
    text: str = Field(
        min_length=20,
        max_length=5000,
    )


class SummariseResponse(StrictModel):
    summary: str
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)


class AnalyseRequest(StrictModel):
    message: str = Field(
        min_length=5,
        max_length=5000,
    )


class TicketAnalysis(StrictModel):
    summary: str = Field(
        min_length=5,
        max_length=300,
    )

    category: TicketCategory
    sentiment: Sentiment
    priority: Priority

    needs_order_lookup: bool
    needs_faq_lookup: bool
    needs_human_review: bool

    faq_query: str | None = Field(
        default=None,
        max_length=200,
    )

    human_review_reason: str | None = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def validate_dependencies(
        self,
    ) -> "TicketAnalysis":
        if self.needs_faq_lookup and not self.faq_query:
            raise ValueError(
                "faq_query is required when "
                "needs_faq_lookup is true"
            )

        if (
            self.needs_human_review
            and not self.human_review_reason
        ):
            raise ValueError(
                "human_review_reason is required when "
                "needs_human_review is true"
            )

        return self


class AnalyseResponse(StrictModel):
    analysis: TicketAnalysis
    usage: AIUsage


class GenerateResponseRequest(StrictModel):
    message: str = Field(
        min_length=5,
        max_length=5000,
    )


class GenerateResponseResponse(StrictModel):
    draft_response: str
    usage: AIUsage

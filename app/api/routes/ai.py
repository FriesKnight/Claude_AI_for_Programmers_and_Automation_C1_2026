from fastapi import APIRouter

from app.prompts.summarise import (
    SUMMARISE_SYSTEM_PROMPT
)
from app.schemas.ai import (
    SummariseRequest,
    SummariseResponse,
    AnalyseRequest,
    AnalyseResponse
)

from app.schemas.usage import AIUsage
from app.services.analysis_service import AnalysisService

from app.services.claude_service import ClaudeService

router = APIRouter(tags=["ai"])

@router.post(
    "/summarise",
    response_model=SummariseResponse,
)
async def summarise_text(
    request: SummariseRequest,
) -> SummariseResponse:
    claude_service = ClaudeService()

    try: 
        result = await claude_service.generate_text(
            request.text,
            system=SUMMARISE_SYSTEM_PROMPT,
            max_tokens=150,
        )
    finally:
        await claude_service.close()

    return SummariseResponse(
        summary=result.text,
        model=result.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )


@router.post(
    "/analyse",
    response_model=AnalyseResponse,
)
async def analyse_ticket(
    request: AnalyseRequest,
) -> AnalyseResponse:
    claude_service = ClaudeService()
    analyse_service = AnalysisService(
        claude_service
    )

    try: 
        result = await analyse_service.analyse(
            request.message
        )
    finally:
        await claude_service.close()

    return AnalyseResponse(
        analysis=result.data,
        usage=AIUsage(
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )
    )

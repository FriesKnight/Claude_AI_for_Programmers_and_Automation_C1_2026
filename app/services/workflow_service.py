from dataclasses import dataclass
from datetime import datetime, timezone

from app.repositories.faq_repository import FAQRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.common import TicketStatus
from app.schemas.ticket import TicketCreateRequest, TicketResponse
from app.schemas.usage import AIUsage
from app.schemas.workflow import (
    ProcessTicketRequest,
    WorkflowStep,
)
from app.services.analysis_service import AnalysisService
from app.services.response_service import ResponseService
from app.services.ticket_service import TicketService


# One result object represents the outcome of the entire workflow.
@dataclass(frozen=True)
class WorkflowProcessResult:
    ticket: TicketResponse
    executed_steps: list[WorkflowStep]
    analysis_usage: AIUsage
    response_usage: AIUsage


# This service does not replace the existing services/repositories.
# It coordinates them in an application-owned sequence.
class WorkflowService:
    def __init__(
        self,
        *,
        analysis_service: AnalysisService,
        response_service: ResponseService,
        ticket_service: TicketService,
        order_repository: OrderRepository,
        faq_repository: FAQRepository,
    ) -> None:
        # Dependencies are injected so this service does not create its own
        # Claude client or MongoDB connection.
        self.analysis_service = analysis_service
        self.response_service = response_service
        self.ticket_service = ticket_service
        self.order_repository = order_repository
        self.faq_repository = faq_repository

    async def process(
        self,
        request: ProcessTicketRequest,
    ) -> WorkflowProcessResult:
        executed_steps: list[WorkflowStep] = []

        # 1. ANALYSIS — always runs; nothing else can be decided without it.
        analysis_result = await self.analysis_service.analyse(
            request.message
        )
        analysis = analysis_result.data
        executed_steps.append(WorkflowStep.ANALYSIS)

        # 2. ORDER_LOOKUP — only if required AND an order_id was actually given.
        order_context = None
        order_lookup_unresolved = False

        if analysis.needs_order_lookup:
            if request.order_id:
                order_context = (
                    await self.order_repository
                    .get_order_for_customer(
                        request.customer_id,
                        request.order_id,
                    )
                )
                executed_steps.append(WorkflowStep.ORDER_LOOKUP)

                if order_context is None:
                    order_lookup_unresolved = True
            else:
                # Analysis says an order matters, but nothing to look up.
                # Never invent an order_id — treat as unresolved.
                order_lookup_unresolved = True

        # 3. FAQ_LOOKUP — only if required.
        faq_context: list = []
        faq_lookup_unresolved = False

        if analysis.needs_faq_lookup:
            faq_context = await self.faq_repository.search(
                analysis.faq_query,
                limit=3,
            )
            executed_steps.append(WorkflowStep.FAQ_LOOKUP)

            if not faq_context:
                faq_lookup_unresolved = True

        # 4. DATABASE_INSERT — persist before generating a response, so an
        # audit record exists even if response generation fails downstream.
        ticket = await self.ticket_service.create(
            TicketCreateRequest(
                customer_id=request.customer_id,
                order_id=request.order_id,
                message=request.message,
            ),
            analysis,
        )
        executed_steps.append(WorkflowStep.DATABASE_INSERT)

        # 5. RESPONSE_GENERATION — always runs, using only verified context.
        response_result = await self.response_service.generate_draft(
            request.message,
            order_context=order_context,
            faq_context=faq_context,
        )
        executed_steps.append(WorkflowStep.RESPONSE_GENERATION)

        # 6. Final status — application-owned, never Claude's decision.
        final_status = ticket.status

        if (
            order_lookup_unresolved
            or faq_lookup_unresolved
        ):
            final_status = TicketStatus.NEEDS_HUMAN_REVIEW
        elif final_status == TicketStatus.ANALYSED:
            final_status = TicketStatus.PROCESSED

        # 7. DATABASE_UPDATE — always runs, persists the final state.
        updated_ticket = ticket.model_copy(
            update={
                "order_context": order_context,
                "faq_context": faq_context,
                "draft_response": response_result.text,
                "status": final_status,
                "updated_at": datetime.now(timezone.utc),
            }
        )
        ticket = await self.ticket_service.save(updated_ticket)
        executed_steps.append(WorkflowStep.DATABASE_UPDATE)

        return WorkflowProcessResult(
            ticket=ticket,
            executed_steps=executed_steps,
            analysis_usage=AIUsage(
                model=analysis_result.model,
                input_tokens=analysis_result.input_tokens,
                output_tokens=analysis_result.output_tokens,
            ),
            response_usage=AIUsage(
                model=response_result.model,
                input_tokens=response_result.input_tokens,
                output_tokens=response_result.output_tokens,
            ),
        )

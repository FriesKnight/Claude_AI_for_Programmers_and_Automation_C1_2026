from dataclasses import dataclass

from app.repositories.faq_repository import FAQRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.ticket import TicketResponse
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
        # Exercise 01: participants build the orchestration here.
        raise NotImplementedError

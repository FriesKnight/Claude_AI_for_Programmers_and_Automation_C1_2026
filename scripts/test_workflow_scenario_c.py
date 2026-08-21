import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import connect_to_database, close_database, get_database
from app.repositories.faq_repository import FAQRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.workflow import ProcessTicketRequest
from app.services.analysis_service import AnalysisService
from app.services.claude_service import ClaudeService
from app.services.response_service import ResponseService
from app.services.ticket_service import TicketService
from app.services.workflow_service import WorkflowService


async def main():
    await connect_to_database()
    db = get_database()
    claude_service = ClaudeService()

    workflow = WorkflowService(
        analysis_service=AnalysisService(claude_service),
        response_service=ResponseService(claude_service),
        ticket_service=TicketService(TicketRepository(db)),
        order_repository=OrderRepository(db),
        faq_repository=FAQRepository(db),
    )

    # Scenario C — missing trusted information.
    # ORD-1001 is a real seeded order, but it belongs to CUST-101, not
    # CUST-102. The customer/order pairing will not resolve, forcing the
    # order_lookup_unresolved branch that Scenario A never touched.
    request = ProcessTicketRequest(
        customer_id="CUST-102",
        order_id="ORD-1001",
        message=(
            "Can you check the status of my order? I want to know "
            "when it will be delivered."
        ),
    )

    try:
        result = await workflow.process(request)
    finally:
        await claude_service.close()

    print("executed_steps:", [s.value for s in result.executed_steps])
    print("final status:", result.ticket.status.value)
    print("order_context used:", result.ticket.order_context)
    print("faq_context used:", result.ticket.faq_context)
    print("draft_response:", result.ticket.draft_response)
    print("analysis_usage:", result.analysis_usage)
    print("response_usage:", result.response_usage)

    await close_database()


if __name__ == "__main__":
    asyncio.run(main())

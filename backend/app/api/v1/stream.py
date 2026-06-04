"""
File: app/api/v1/stream.py
Purpose: Server-Sent Events (SSE) endpoint for real-time agent progress.
Responsibilities:
  - Stream report status changes to the frontend as agents complete
  - Authenticate via JWT query parameter (EventSource doesn't support headers)
  - Push one SSE event per agent state change (PENDING → RUNNING → COMPLETED/FAILED)
  - Send a final {"type": "done"} event when all 11 agents finish
  - Auto-close the stream after 10 minutes (safety timeout)
Dependencies:
  - fastapi (StreamingResponse, Query)
  - app.core.security (decode_access_token)
  - app.core.database (AsyncSessionLocal)
  - app.models.report (Report, ReportStatus)
"""

import asyncio
import json
import uuid

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import decode_access_token
from app.models.idea import Idea
from app.models.report import Report

router = APIRouter(prefix="/ideas", tags=["Stream"])

# Total number of agents in the pipeline
TOTAL_AGENTS = 11

# Maximum stream duration in seconds before auto-close (safety net)
STREAM_TIMEOUT_SECONDS = 600   # 10 minutes

# How frequently the server checks for DB changes (seconds)
POLL_INTERVAL_SECONDS = 0.5


@router.get(
    "/{idea_id}/stream",
    summary="Stream real-time agent progress via Server-Sent Events",
    response_class=StreamingResponse,
)
async def stream_idea_progress(
    idea_id: uuid.UUID,
    token: str = Query(..., description="JWT access token (Bearer not supported by EventSource)"),
) -> StreamingResponse:
    """
    Purpose: Open a persistent SSE connection that pushes agent report updates
      as they arrive in the database. The frontend subscribes with EventSource
      instead of polling every 3 seconds.

    Authentication:
      JWT is passed as a query parameter because the browser's EventSource API
      does not support setting custom Authorization headers. The token is
      validated server-side before streaming begins.

    Event format (each line):
      data: {"agent_type": "MARKET_RESEARCH", "status": "COMPLETED", ...}
      (blank line terminates the event)

    Final event:
      data: {"type": "done"}

    Parameters:
      idea_id: UUID of the idea to stream progress for.
      token: JWT access token from localStorage.
    Returns:
      StreamingResponse with media_type="text/event-stream".
    Raises:
      401: If token is missing or invalid.
      404: If the idea doesn't belong to this user.
    """
    # ── Validate JWT ────────────────────────────────────────────────────────────
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user_id = uuid.UUID(payload["sub"])

    # ── Verify idea ownership (one-shot DB check before streaming begins) ───────
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Idea).where(Idea.id == idea_id, Idea.user_id == user_id)
        )
        idea = result.scalar_one_or_none()
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found",
            )

    # ── Return the SSE stream ───────────────────────────────────────────────────
    return StreamingResponse(
        _event_generator(idea_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Disable Nginx buffering for SSE
            "Connection": "keep-alive",
        },
    )


async def _event_generator(idea_id: uuid.UUID):
    """
    Purpose: Async generator that yields SSE-formatted strings as agents complete.
      Polls the reports table every POLL_INTERVAL_SECONDS for status changes.
      Yields an event whenever a report's status changes.
      Terminates when all agents are in a terminal state or timeout is reached.

    Parameters:
      idea_id: UUID of the idea whose reports to stream.
    Yields:
      str: SSE-formatted data string ending with double newline.
    """
    # Track last-seen status per agent so we only push on changes
    last_seen: dict[str, str] = {}

    max_iterations = int(STREAM_TIMEOUT_SECONDS / POLL_INTERVAL_SECONDS)

    for _ in range(max_iterations):
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Report).where(Report.idea_id == idea_id)
                )
                reports = result.scalars().all()

            # ── Yield an event for every status change ─────────────────────────
            for report in reports:
                key = report.agent_type.value
                current = report.status.value

                if last_seen.get(key) != current:
                    last_seen[key] = current

                    event_data = {
                        "agent_type": key,
                        "status": current,
                        "execution_time_ms": report.execution_time_ms,
                        "reasoning_summary": report.reasoning_summary,
                        "error_message": report.error_message,
                        # Only send output when the agent is done (saves bandwidth)
                        "output": report.output if current == "COMPLETED" else None,
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"

            # ── Check if all agents are in a terminal state ────────────────────
            terminal = {"COMPLETED", "FAILED"}
            all_done = (
                len(reports) == TOTAL_AGENTS
                and all(r.status.value in terminal for r in reports)
            )

            if all_done:
                yield 'data: {"type":"done"}\n\n'
                return

        except Exception as exc:
            # Non-fatal: log and keep retrying
            print(f"⚠️  SSE generator error for {idea_id}: {exc}")

        await asyncio.sleep(POLL_INTERVAL_SECONDS)

    # ── Timeout — close gracefully ─────────────────────────────────────────────
    yield 'data: {"type":"timeout"}\n\n'

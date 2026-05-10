from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json
from typing import Dict, Any
from db.session import get_db
from core.security import verify_gateway_psk

router = APIRouter(
    prefix="/webhooks", tags=["webhooks"], dependencies=[Depends(verify_gateway_psk)]
)


@router.post("/auth", status_code=status.HTTP_200_OK)
async def handle_auth_webhook(
    payload: Dict[str, Any], session: AsyncSession = Depends(get_db)
):
    """
    Handle Supabase Auth Webhooks for authentication events.
    Captures login/signup events and writes them to the audit log.
    """
    event_type = payload.get("type", "UNKNOWN_AUTH_EVENT")
    record = payload.get("record", {})
    user_id = record.get("id")

    # We use auth.users as the table name
    record_id = user_id if user_id else "00000000-0000-0000-0000-000000000000"

    stmt = text("""
        INSERT INTO public.audit_log (table_name, record_id, action, new_data, changed_by)
        VALUES (:table_name, :record_id, :action, :new_data, :changed_by)
    """)

    await session.execute(
        stmt,
        {
            "table_name": "auth.users",
            "record_id": record_id,
            "action": event_type,
            "new_data": json.dumps(record),
            "changed_by": user_id,
        },
    )
    await session.commit()

    return {"status": "ok"}

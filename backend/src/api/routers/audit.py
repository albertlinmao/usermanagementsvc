from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Any
import json

from db.session import get_db
from models.schemas import PaginatedAuditLogResponse, AuditLogResponse
from core.security import verify_gateway_psk

router = APIRouter(
    prefix="/audit", tags=["audit"], dependencies=[Depends(verify_gateway_psk)]
)


class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_audit_logs(
        self, cursor: Optional[str] = None, limit: int = 50
    ) -> dict:
        # Simple cursor based pagination using created_at/changed_at
        query = """
            SELECT id, table_name, record_id, action, old_data, new_data, changed_by, changed_at
            FROM public.audit_log
        """
        params = {"limit": limit + 1}

        if cursor:
            query += " WHERE changed_at < :cursor"

        # Add to params safely
        if cursor:
            params_with_cursor = dict(params)
            params_with_cursor["cursor"] = cursor
            params = params_with_cursor

        query += " ORDER BY changed_at DESC LIMIT :limit"

        stmt = text(query)
        result = await self.session.execute(stmt, params)
        rows = result.fetchall()

        has_more = len(rows) > limit
        data_rows = rows[:limit]

        data = []
        for row in data_rows:
            data.append(
                AuditLogResponse(
                    id=row.id,
                    table_name=row.table_name,
                    record_id=row.record_id,
                    action=row.action,
                    old_data=row.old_data if row.old_data else None,
                    new_data=row.new_data if row.new_data else None,
                    changed_by=row.changed_by,
                    changed_at=row.changed_at,
                )
            )

        next_cursor = None
        if has_more and data:
            next_cursor = data[-1].changed_at.isoformat()

        return {"data": data, "next_cursor": next_cursor, "has_more": has_more}


def get_audit_service(session: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(session)


@router.get("/", response_model=PaginatedAuditLogResponse)
async def get_audit_logs(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: AuditService = Depends(get_audit_service),
):
    """
    Retrieve a paginated list of audit logs.
    """
    return await service.get_audit_logs(cursor, limit)

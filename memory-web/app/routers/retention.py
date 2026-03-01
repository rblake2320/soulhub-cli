"""Retention control API routes."""

from fastapi import APIRouter, Body, Query
from pydantic import BaseModel
from typing import Optional

from ..schemas import PurgeRequest, RetentionResult
from ..services import retention as ret_svc

router = APIRouter(prefix="/api/retain", tags=["retention"])


class RetentionBody(BaseModel):
    reason: Optional[str] = None


@router.delete("/day/{date}", summary="Tombstone all data for a date (YYYY-MM-DD)")
def tombstone_day(date: str, body: RetentionBody = Body(default=RetentionBody())):
    return ret_svc.tombstone_by_date(date, reason=body.reason)


@router.delete("/domain/{domain}", summary="Tombstone all segments tagged with domain")
def tombstone_domain(domain: str, body: RetentionBody = Body(default=RetentionBody())):
    return ret_svc.tombstone_by_domain(domain, reason=body.reason)


@router.delete("/conversation/{conversation_id}", summary="Tombstone entire conversation")
def tombstone_conversation(
    conversation_id: int,
    body: RetentionBody = Body(default=RetentionBody()),
):
    return ret_svc.tombstone_conversation(conversation_id, reason=body.reason)


@router.get("/tombstoned", summary="Count tombstoned records")
def list_tombstoned():
    return ret_svc.list_tombstoned()


@router.post("/restore/{target_type}/{target_id}", summary="Restore (un-tombstone) a record")
def restore(target_type: str, target_id: int):
    return ret_svc.restore(target_type, target_id)


@router.post("/purge", summary="Hard-delete old tombstoned records")
def purge(body: PurgeRequest):
    return ret_svc.purge_tombstoned(
        older_than_days=body.older_than_days,
        dry_run=body.dry_run,
    )

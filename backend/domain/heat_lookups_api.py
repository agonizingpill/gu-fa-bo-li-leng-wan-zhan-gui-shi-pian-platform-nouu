from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import heat_lookups_service as service
from domain.heat_lookups_model import heat_lookups
from domain.heat_lookups_schemas import ConfirmHeatLookup, CreateHeatLookup

router = APIRouter()

@router.get('/heat_lookups')
def list_heat_lookups(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, heat_lookups)


@router.post('/heat_lookups/lookup')
def create_lookup(data: CreateHeatLookup, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.create_lookup(conn, user, data)
        record(conn, user, 'heat_lookups.lookup')
        return output


@router.post('/heat_lookups/confirm')
def confirm_lookup(data: ConfirmHeatLookup, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.confirm_lookup(conn, user, data)
        record(conn, user, 'heat_lookups.confirm')
        return output

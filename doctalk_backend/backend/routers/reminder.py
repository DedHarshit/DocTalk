from fastapi import APIRouter, HTTPException
from models.reminder import ReminderCreate, ReminderUpdate, ReminderResponse
from utils.helpers import generate_id, utc_now_iso, error_response
from utils.logger import get_logger

router = APIRouter(prefix="/reminder", tags=["Reminder"])
logger = get_logger("routers.reminder")

# In-memory store (replace with a real DB in production)
_reminders: dict[str, dict] = {}


def _to_response(r: dict) -> ReminderResponse:
    return ReminderResponse(
        id=r["id"],
        medicine_name=r["medicine_name"],
        dosage=r["dosage"],
        frequency=r["frequency"],
        times=r["times"],
        start_date=r["start_date"],
        end_date=r.get("end_date"),
        notes=r.get("notes"),
        active=r["active"],
        created_at=r["created_at"],
    )


@router.post("", response_model=ReminderResponse, status_code=201)
async def create_reminder(data: ReminderCreate):
    try:
        reminder_id = generate_id()
        reminder = {
            "id": reminder_id,
            **data.model_dump(),
            "created_at": utc_now_iso(),
        }
        _reminders[reminder_id] = reminder
        logger.info(f"Reminder created: {reminder_id}")
        return _to_response(reminder)
    except Exception as e:
        logger.error(f"Create reminder error: {e}")
        raise HTTPException(status_code=500, detail=error_response(str(e), "CREATE_ERROR"))


@router.get("", response_model=list[ReminderResponse])
async def list_reminders(active_only: bool = False):
    reminders = list(_reminders.values())
    if active_only:
        reminders = [r for r in reminders if r.get("active", True)]
    return [_to_response(r) for r in reminders]


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(reminder_id: str):
    r = _reminders.get(reminder_id)
    if not r:
        raise HTTPException(
            status_code=404,
            detail=error_response("Reminder not found", "NOT_FOUND"),
        )
    return _to_response(r)


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(reminder_id: str, data: ReminderUpdate):
    r = _reminders.get(reminder_id)
    if not r:
        raise HTTPException(
            status_code=404,
            detail=error_response("Reminder not found", "NOT_FOUND"),
        )
    updates = data.model_dump(exclude_unset=True)
    r.update(updates)
    _reminders[reminder_id] = r
    return _to_response(r)


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: str):
    if reminder_id not in _reminders:
        raise HTTPException(
            status_code=404,
            detail=error_response("Reminder not found", "NOT_FOUND"),
        )
    del _reminders[reminder_id]
    return {"deleted": True, "id": reminder_id}


@router.patch("/{reminder_id}/toggle", response_model=ReminderResponse)
async def toggle_reminder(reminder_id: str):
    r = _reminders.get(reminder_id)
    if not r:
        raise HTTPException(
            status_code=404,
            detail=error_response("Reminder not found", "NOT_FOUND"),
        )
    r["active"] = not r["active"]
    return _to_response(r)

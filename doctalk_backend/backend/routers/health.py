from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone

from models.health import MetricLog, MetricResponse, MetricSummary, MetricAlert, NORMAL_RANGES
from utils.helpers import generate_id, utc_now_iso, error_response
from utils.logger import get_logger

router = APIRouter(prefix="/health", tags=["Health Metrics"])
logger = get_logger("routers.health")

# In-memory store (replace with a real DB in production)
_metrics: dict[str, dict] = {}


def _to_response(m: dict) -> MetricResponse:
    return MetricResponse(
        id=m["id"],
        metric_type=m["metric_type"],
        value=m["value"],
        unit=m.get("unit"),
        notes=m.get("notes"),
        recorded_at=m["recorded_at"],
        created_at=m["created_at"],
    )


def _generate_alerts(metric_type: str, value: float, recorded_at: str) -> list[MetricAlert]:
    alerts = []
    ranges = NORMAL_RANGES.get(metric_type)
    if not ranges:
        return alerts

    lo = ranges.get("min")
    hi = ranges.get("max")
    unit = ranges.get("unit", "")

    if lo is not None and value < lo:
        severity = "critical" if value < lo * 0.85 else "warning"
        alerts.append(
            MetricAlert(
                metric_type=metric_type,
                value=value,
                message=f"{metric_type.replace('_', ' ').title()} is LOW: {value} {unit} (normal ≥ {lo} {unit})",
                severity=severity,
                recorded_at=recorded_at,
            )
        )
    elif hi is not None and value > hi:
        severity = "critical" if value > hi * 1.2 else "warning"
        alerts.append(
            MetricAlert(
                metric_type=metric_type,
                value=value,
                message=f"{metric_type.replace('_', ' ').title()} is HIGH: {value} {unit} (normal ≤ {hi} {unit})",
                severity=severity,
                recorded_at=recorded_at,
            )
        )
    return alerts


@router.post("/log", response_model=MetricResponse, status_code=201)
async def log_metric(data: MetricLog):
    try:
        metric_id = generate_id()
        now = utc_now_iso()
        recorded_at = (
            data.recorded_at.isoformat()
            if data.recorded_at
            else now
        )
        metric = {
            "id": metric_id,
            "metric_type": data.metric_type,
            "value": data.value,
            "unit": data.unit or NORMAL_RANGES.get(data.metric_type, {}).get("unit"),
            "notes": data.notes,
            "recorded_at": recorded_at,
            "created_at": now,
        }
        _metrics[metric_id] = metric
        logger.info(f"Metric logged: {data.metric_type}={data.value} [{metric_id}]")
        return _to_response(metric)
    except Exception as e:
        logger.error(f"Log metric error: {e}")
        raise HTTPException(status_code=500, detail=error_response(str(e), "LOG_ERROR"))


@router.get("/metrics", response_model=list[MetricResponse])
async def get_metrics(
    metric_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    all_metrics = list(_metrics.values())

    if metric_type:
        all_metrics = [m for m in all_metrics if m["metric_type"] == metric_type]

    all_metrics.sort(key=lambda m: m["recorded_at"], reverse=True)
    all_metrics = all_metrics[:limit]

    return [_to_response(m) for m in all_metrics]


@router.get("/summary", response_model=list[MetricSummary])
async def get_summary():
    from collections import defaultdict

    grouped: dict[str, list[float]] = defaultdict(list)
    latest: dict[str, dict] = {}

    for m in _metrics.values():
        mtype = m["metric_type"]
        grouped[mtype].append(m["value"])
        if mtype not in latest or m["recorded_at"] > latest[mtype]["recorded_at"]:
            latest[mtype] = m

    summaries = []
    for mtype, values in grouped.items():
        latest_m = latest.get(mtype)
        summaries.append(
            MetricSummary(
                metric_type=mtype,
                count=len(values),
                average=round(sum(values) / len(values), 2) if values else None,
                min_value=min(values) if values else None,
                max_value=max(values) if values else None,
                latest_value=latest_m["value"] if latest_m else None,
                latest_recorded_at=latest_m["recorded_at"] if latest_m else None,
            )
        )
    return summaries


@router.get("/alerts", response_model=list[MetricAlert])
async def get_alerts():
    alerts = []
    for m in _metrics.values():
        generated = _generate_alerts(m["metric_type"], m["value"], m["recorded_at"])
        alerts.extend(generated)

    alerts.sort(key=lambda a: a.recorded_at, reverse=True)
    return alerts

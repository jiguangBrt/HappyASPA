from datetime import datetime, timezone, timedelta

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except Exception:  # pragma: no cover - fallback for older Python
    ZoneInfo = None
    ZoneInfoNotFoundError = Exception


UTC = timezone.utc
if ZoneInfo:
    try:
        APP_TZ = ZoneInfo("Asia/Shanghai")
    except ZoneInfoNotFoundError:
        APP_TZ = timezone(timedelta(hours=8))
else:
    APP_TZ = timezone(timedelta(hours=8))


def utcnow_naive():
    return datetime.utcnow()


def ensure_aware(dt, assume_tz=UTC):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=assume_tz)
    return dt


def ensure_naive_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(UTC).replace(tzinfo=None)


def to_beijing(dt, assume_tz=UTC):
    aware = ensure_aware(dt, assume_tz)
    return aware.astimezone(APP_TZ) if aware is not None else None


def is_system_tz_beijing():
    local_offset = datetime.now().astimezone().utcoffset()
    return local_offset == timedelta(hours=8)

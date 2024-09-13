from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .db import sqlalchemy_models as models


async def calculate_service_downtime(db: AsyncSession, service_id: int,
                                     start_date: datetime,
                                     end_date: datetime) -> dict[str, Any]:
    # Получаем все записи о статусах сервиса за указанный интервал
    result = await db.execute(
        select(models.ServiceHistory).where(
            models.ServiceHistory.service_id == service_id,
            models.ServiceHistory.timestamp >= start_date,
            models.ServiceHistory.timestamp <= end_date))
    history_records = result.scalars().all()

    total_downtime: timedelta = timedelta()
    last_status: str | None = None
    last_status_time: datetime | None = None

    # Проходим по всем записям и считаем время простоя
    for record in history_records:
        if last_status:
            if last_status == 'down' and (record.status == 'up'
                                          or record.status == 'unstable'):
                # Если был статус 'down' и теперь 'up'/'unstable', добавляем время простоя
                downtime_duration: timedelta = record.timestamp - last_status_time
                total_downtime += downtime_duration

        # Обновляем последний статус и его время
        last_status = record.status
        last_status_time = record.timestamp

    # Расчет SLA
    total_time: timedelta = end_date - start_date
    if total_time.total_seconds() > 0:
        sla = (1 - (total_downtime.total_seconds() /
                    total_time.total_seconds())) * 100
    else:
        sla: int | float = 0

    return {
        "total_downtime": str(total_downtime),
        "sla_percentage": round(sla, 3)
    }

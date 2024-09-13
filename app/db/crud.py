from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import sqlalchemy_models as models
from .sqlalchemy_models import Service
from ..models import pydantic_models as schemas


async def create_service(db: AsyncSession,
                         service: schemas.Service) -> models.Service:
    service_exist_check = await db.execute(
        select(models.Service).where(models.Service.name == service.name))
    existing_service = service_exist_check.scalars().first()
    if existing_service:  # если сервис с таким названием уже существует, то обновляем его данные
        # 1) записываем существующие данные в историю
        history_entry = models.ServiceHistory(
            service_id=existing_service.id,
            status=existing_service.status,
            description=existing_service.description)
        db.add(history_entry)

        # 2) обновляем актуальные данные о сервисе
        existing_service.status = service.status
        existing_service.description = service.description
        await db.commit()
        await db.refresh(existing_service)
        return existing_service
    else:  # иначе добавляем новый сервис в БД
        service = models.Service(**service.model_dump())
        db.add(service)
        await db.commit()
        await db.refresh(service)
        return service


async def read_services(db: AsyncSession) -> list[models.Service]:  ## ##
    services = await db.execute(select(models.Service))
    return services.scalars().all()


async def read_service_history_by_name(
        db: AsyncSession,
        service_name: str) -> Optional[list[models.ServiceHistory]]:
    service = await db.execute(
        select(models.Service).where(models.Service.name == service_name))
    service = service.scalar_one_or_none()

    if not service:
        return None

    history_entries = await db.execute(
        select(models.ServiceHistory).where(
            models.ServiceHistory.service_id == service.id))

    return history_entries.scalars().all()

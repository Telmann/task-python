from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime
from .SLA_calculation import calculate_service_downtime

from .models.pydantic_models import Service, ServiceHistory
from .db.database import get_db
from .db.crud import create_service, read_services, read_service_history_by_name

app = FastAPI()


@app.post("/services", response_model=dict)
async def post_service(
    service: Service, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    new_service = await create_service(db=db, service=service)
    if new_service:
        return {"message": "service created/updated successfully!"}
    return {"message": "service is NOT created/updated successfully!"}  #


@app.get("/services", response_model=list[Service] | dict[str, str])
async def get_services(db: AsyncSession = Depends(get_db)) -> list[Service] | dict[str, str]:
    services = await read_services(db=db)
    if services:
        return services
    return {"message": "There are no services in the database"}


@app.get("/services/{service_name}/history",
         response_model=list[ServiceHistory] | dict)
async def get_service_history(
    service_name: str, db: AsyncSession = Depends(get_db)
) -> list[ServiceHistory] | dict[str, str]:
    history_entries = await read_service_history_by_name(db, service_name)
    if not history_entries:
        return {
            "message":
            "Service not found OR Service doesn't have a history yet."
        }
    return history_entries


@app.get("/services/{service_id}/SLA_downtime_info", response_model=dict)
async def get_service_history(
    service_id: int,
    start_date: datetime,
    end_date: datetime,
    db: AsyncSession = Depends(get_db)) -> dict:
    try:
        # Вызываем функцию для расчета времени простоя|SLA
        time_data = await calculate_service_downtime(db=db,
                                                     service_id=service_id,
                                                     start_date=start_date,
                                                     end_date=end_date)
        return time_data
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")

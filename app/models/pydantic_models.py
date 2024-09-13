from pydantic import BaseModel


class Service(BaseModel):
    name: str
    status: str
    description: str


class ServiceHistory(BaseModel):
    id: int
    service_id: int
    status: str
    description: str

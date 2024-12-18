from pydantic import BaseModel
from datetime import datetime

class ReportCreateSchema(BaseModel):
    address: str
    password: str
    name: str
    date: datetime

class ReportInfoSchema(BaseModel):
    password: str
    address: str
    receive: bool
    reportId: int
    name: str
    date: datetime

class UpdateReceiveSchema(BaseModel):
    receive: bool

    class Config:
        orm_mode = True

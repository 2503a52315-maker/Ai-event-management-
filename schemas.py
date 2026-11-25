from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str


class EventCreate(BaseModel):
    title: str
    description: str | None = None
    date: str
    time: str
    location: str


class RegistrationCreate(BaseModel):
    user_id: int
    event_id: int
class AttendanceCreate(BaseModel):
    registration_id: int
    status: str
class LoginRequest(BaseModel):
    email: str
    password: str
class NotificationCreate(BaseModel):
    user_id: int
    event_id: int
    message: str
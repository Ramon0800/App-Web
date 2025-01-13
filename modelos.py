from pydantic import BaseModel, Field
from typing import Optional
import datetime


class Recorder(BaseModel):
    id: int
    path: str = Field(max_length=200, default="output.mp4")
    interval: int = Field(ge=0, le=180, default=5)
    frames: float = Field(ge=0, le=15, default=10.0)
    width: int = Field(ge=1024, le=3840, default=1770)
    heigth: int = Field(ge=720, le=2160, default=720)
    time_out_monitor: int = Field(ge=0, le=20)
    time_out_wait: int = Field(ge=0, le=20)
    url: str = Field(
        max_length=100, default="https://www.flightradar24.com/23.42,-79.95/6"
    )


class User(BaseModel):
    id: int
    email: str = Field(max_length=200)
    password: str = Field(max_length=8)

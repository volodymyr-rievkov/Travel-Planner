from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import date


class PlaceBase(BaseModel):
    external_id: int
    notes: Optional[str] = None
    is_visited: bool = False

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None

class PlaceRead(PlaceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
   

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    # Дозволяємо створювати проект одразу з місцями
    places: Optional[List[PlaceCreate]] = Field(default=[], max_items=10)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectRead(ProjectBase):
    id: int
    is_completed: bool
    places: List[PlaceRead]

    model_config = ConfigDict(from_attributes=True)

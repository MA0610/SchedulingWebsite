from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

class Class(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias='_id')
    class_name: str = Field(..., description="The name of the class")
    class_time: str = Field(..., description="The time the class is held, e.g. '10:00 AM - 11:30 AM'")
    class_days: List[str] = Field(..., description="Days the class is held, e.g. ['Monday', 'Wednesday']")
    coreqs: Optional[List[str]] = Field(None, description="List of corequisite class IDs, if any")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "class_name": "Calculus 1",
                "class_time": "10:00 AM - 11:30 AM",
                "class_days": ["Monday", "Wednesday"],
                "coreqs": ["12345"]
            }
        }   

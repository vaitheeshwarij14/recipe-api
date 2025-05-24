from pydantic import BaseModel
from typing import Optional, Dict

class RecipeBase(BaseModel):
    title: str
    cuisine: str
    rating: Optional[float]
    prep_time: Optional[int]
    cook_time: Optional[int]
    total_time: Optional[int]
    description: str
    nutrients: Dict
    serves: str

    class Config:
        orm_mode = True

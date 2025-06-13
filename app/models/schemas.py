from pydantic import BaseModel
from typing import List, Optional

class Link(BaseModel):
    url: str
    text: str

class QuestionResponse(BaseModel):
    answer: str
    links: List[Link]

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None 
from typing import List, Dict, Union
from pydantic import BaseModel


class Question:
    def __init__(self, fact, statement: str, options: List[str], answer_mode: int):
        self.statement = statement
        self.options = options
        self.answer_mode = answer_mode  # 1 unique - 2 multiple,
        self.fact = fact


class Quiz:
    def __init__(self, questions: List[Question]):
        self.questions = questions


class QuizAnswers(BaseModel):
    condition: str
    answers: Dict[str, Union[str, int]]


class AuthDto(BaseModel):
    email: str
    password: str


class SessionData(BaseModel):
    to_save: List[str]
    user_id: str

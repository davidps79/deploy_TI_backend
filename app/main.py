import json
from typing import List

import uvicorn
from fastapi import FastAPI

from app.dtos import QuizAnswers, AuthDto, SessionData
from config.authMethods import login_user, register_user
from config.getSessions import get_user_sessions
from experts.experts import get_quiz, get_analysis
from fastapi.middleware.cors import CORSMiddleware
from config.supabaseConfig import get_supabase_client

supabase = get_supabase_client()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/quiz/{condition}")
async def quiz(condition: str):
    return get_quiz(condition)


@app.post("/analyze/")
async def analyze(answer: QuizAnswers):
    return get_analysis(answer)


@app.post("/login/")
async def login(user_data: AuthDto):
    return login_user(user_data.email, user_data.password)


@app.post("/signup/")
async def login(user_data: AuthDto):
    return register_user(user_data.email, user_data.password)


@app.get("/session/{user_id}")
async def session(user_id: str):
    return get_user_sessions(user_id)


@app.post("/save_data/")
def save_session_data(data: SessionData):
    session_data = {
        'data': json.dumps(data.to_save),
        'user_id': data.user_id
    }
    supabase.table('sessions').insert(session_data).execute()


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)

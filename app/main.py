import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from julia import load_model

MODEL_PATH=os.getenv("JULIA_MODEL_PATH","/models/Julia-1")
DEVICE=os.getenv("JULIA_DEVICE","cpu")
engine=None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    engine=load_model(MODEL_PATH,device=DEVICE,strict_encoding=True,max_length=8192,head_length=512)
    yield

app=FastAPI(title="Julia-1 API",version="1.0.0",lifespan=lifespan)

class Question(BaseModel):
    type: str
    instructions: str
    criteria: dict | list | None = None

class Request(BaseModel):
    state: str=Field(min_length=1)
    questions: dict[str,Question]=Field(min_length=1)

@app.get("/")
def root():
    return {"name":"julia-1-api","model":"SupersonicLabs/Julia-1","docs":"/docs"}

@app.get("/health")
def health():
    return {"status":"ok" if engine else "starting","model_loaded":engine is not None,"device":DEVICE}

@app.post("/v1/decide")
def decide(payload: Request):
    if engine is None:
        raise HTTPException(503,"Model is still loading.")
    questions={k:v.model_dump(exclude_none=True) for k,v in payload.questions.items()}
    try:
        return engine.predict(state=payload.state,questions=questions)
    except Exception as exc:
        raise HTTPException(400,str(exc)) from exc

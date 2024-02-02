from fastapi import FastAPI
from .routers.users import users
from .routers.papers import papers

app = FastAPI()

@app.get("/")
async def home():
    return "Welcome to Arxiv Hunter"

app.include_router(users, prefix="/users", tags=["users"])
app.include_router(papers, prefix="/papers", tags=["papers"])
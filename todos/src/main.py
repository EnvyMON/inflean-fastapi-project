from fastapi import FastAPI
from api import todo, user

app = FastAPI()
app.include_router(todo.router)
app.include_router(user.router)

@app.get("/")
def index():
    return {"hello": "fastapi"}


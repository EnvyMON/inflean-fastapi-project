from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

app = FastAPI()

todo_data = {
    1: {
        "id": 1,
        "contents": "hello fastatpi 1",
        "is_done": True
    },
    2: {
        "id": 2,
        "contents": "hello fastatpi 2",
        "is_done": False
    },
    3: {
        "id": 3,
        "contents": "hello fastatpi 3",
        "is_done": True
    }
}

class CreateToDoRequest(BaseModel):
    id: int
    contents: str
    is_done: bool

@app.get("/")
def index():
    return {"hello": "fastapi"}

@app.get("/todos", status_code=200)
def get_todos_handler(order: str | None = None):
    ret = list(todo_data.values())
    if order and order == "DESC":
        return ret[::-1]
    else:
        return ret

@app.get("/todos/{todo_id}", status_code=200)
def get_todo_handler(todo_id: int):
    if todo_id in todo_data:
        return todo_data[todo_id]
    else:
        raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/todos", status_code=201)
def create_todo_handler(req_body: CreateToDoRequest):
    if req_body.id in todo_data:
        raise HTTPException(status_code=404, detail="Already todo data")
    else:
        todo_data[req_body.id] = req_body.dict()
        return todo_data[req_body.id]

@app.patch("/todos/{todo_id}", status_code=200)
def update_todo_handler(todo_id: int, is_done: bool = Body(..., embed=True)):
    if todo_id in todo_data:
        todo_data[todo_id]["is_done"] = is_done
        return todo_data[todo_id]
    else:
        raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo_handler(todo_id: int):
    if todo_id in todo_data:
        todo_data.pop(todo_id)
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
from typing import List

from fastapi import FastAPI, HTTPException, Body, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.orm import ToDo
from database.repository import get_todos, get_todo_by_todo_id, create_todo, update_todo, delete_todo
from schema.request import CreateToDoRequest
from schema.response import ToDoListSchema, ToDoSchema

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

@app.get("/")
def index():
    return {"hello": "fastapi"}

@app.get("/todos", status_code=200)
def get_todos_handler(
        order: str | None = None,
        session : Session = Depends(get_db)
) -> ToDoListSchema:
    todos: List[ToDo] = get_todos(session=session)
    if order and order == "DESC":
        return ToDoListSchema(
            todos = [
                ToDoSchema.from_orm(todo) for todo in todos[::-1]
            ]
        )
    else:
        return ToDoListSchema(
            todos = [
                ToDoSchema.from_orm(todo) for todo in todos
            ]
        )

@app.get("/todos/{todo_id}", status_code=200)
def get_todo_handler(
        todo_id: int,
        session: Session = Depends(get_db)
) -> ToDoSchema:
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)

    if todo:
        return ToDoSchema.from_orm(todo)
    else:
        raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/todos", status_code=201)
def create_todo_handler(
        req_body: CreateToDoRequest,
        session: Session = Depends(get_db)
) -> ToDoSchema:
    todo_orm: ToDo = ToDo.create(request=req_body)
    todo: ToDo = create_todo(session=session, todo= todo_orm)
    return ToDoSchema.from_orm(todo)

@app.patch("/todos/{todo_id}", status_code=200)
def update_todo_handler(
        todo_id: int,
        is_done: bool = Body(..., embed=True),
        session: Session = Depends(get_db)
) -> ToDoSchema:
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)

    if todo:
        # update
        if is_done:
            todo.done()
        else:
            todo.undone()
        todo: ToDo = update_todo(session=session, todo=todo)
        return ToDoSchema.from_orm(todo)
    else:
        raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo_handler(
        todo_id: int,
        session: Session = Depends(get_db)
):
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)

    if todo:
        # delete
        delete_todo(session=session, todo_id=todo_id)
    else: 
        raise HTTPException(status_code=404, detail="Todo not found")
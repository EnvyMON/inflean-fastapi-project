from typing import List

from fastapi import Depends, HTTPException, Body, APIRouter
from sqlalchemy.orm import Session

from database.connection import get_db
from database.orm import ToDo
from database.repository import ToDoRepository
from schema.request import CreateToDoRequest
from schema.response import ToDoListSchema, ToDoSchema


router = APIRouter(prefix="/todos")


@router.get("", status_code=200)
def get_todos_handler(
        order: str | None = None,
        todo_repo: ToDoRepository = Depends(ToDoRepository)
) -> ToDoListSchema:
    todos: List[ToDo] = todo_repo.get_todos()
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


@router.get("/{todo_id}", status_code=200)
def get_todo_handler(
        todo_id: int,
        todo_repo: ToDoRepository = Depends(ToDoRepository)
) -> ToDoSchema:
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id)

    if todo:
        return ToDoSchema.from_orm(todo)
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.post("", status_code=201)
def create_todo_handler(
        req_body: CreateToDoRequest,
        todo_repo: ToDoRepository = Depends(ToDoRepository)
) -> ToDoSchema:
    todo_orm: ToDo = ToDo.create(request=req_body)
    todo: ToDo = todo_repo.create_todo(todo= todo_orm)
    return ToDoSchema.from_orm(todo)


@router.patch("/{todo_id}", status_code=200)
def update_todo_handler(
        todo_id: int,
        is_done: bool = Body(..., embed=True),
        todo_repo: ToDoRepository = Depends(ToDoRepository)
) -> ToDoSchema:
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)

    if todo:
        # update
        if is_done:
            todo.done()
        else:
            todo.undone()
        todo: ToDo = todo_repo.update_todo(todo=todo)
        return ToDoSchema.from_orm(todo)
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.delete("/{todo_id}", status_code=204)
def delete_todo_handler(
        todo_id: int,
        todo_repo: ToDoRepository = Depends(ToDoRepository)
):
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)

    if todo:
        # delete
        todo_repo.delete_todo(todo_id=todo_id)
    else:
        raise HTTPException(status_code=404, detail="Todo not found")

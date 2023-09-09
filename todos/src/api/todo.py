from typing import List

from fastapi import Depends, HTTPException, Body, APIRouter
from sqlalchemy.orm import Session

from database.connection import get_db
from database.orm import ToDo, User
from database.repository import ToDoRepository, UserRepository
from schema.request import CreateToDoRequest
from schema.response import ToDoListSchema, ToDoSchema
from security import get_access_token
from service.user import UserService

router = APIRouter(prefix="/todos")


@router.get("", status_code=200)
def get_todos_handler(
        access_token: str = Depends(get_access_token),
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends(),
        order: str | None = None,
        todo_repo: ToDoRepository = Depends(ToDoRepository)
) -> ToDoListSchema:

    # access token 을 통해서 username 획득
    username: str = user_service.decode_jwt(access_token= access_token)

    # username 을 통해서 user 조회
    user: User = user_repo.get_user_by_username(username= username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # user.todos = user orm 에 todo 테이블을 조인 시켜놓은 상태이기 때문에 획득 가능해짐
    todos: List[ToDo] = user.todos
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

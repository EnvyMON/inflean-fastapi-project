from database.orm import ToDo, User
from database.repository import ToDoRepository, UserRepository
from service.user import UserService


def test_get_todos(client, mocker):
    access_token: str = UserService().create_jwt(username= "test")
    headers: dict = {
        "Authorization": f"Bearer {access_token}"
    }

    user = User(id= 1, username= "test", password= "hashed")
    user.todos = [
        ToDo(id=1, contents="FastAPI test 01", is_done=True),
        ToDo(id=2, contents="FastAPI test 02", is_done=False)
    ]

    mocker.patch.object(
        UserRepository,
        "get_user_by_username",
        return_value= user
    )

    # order = ASC
    ret = client.get("/todos", headers= headers)
    assert ret.status_code == 200

    # order = DESC
    ret = client.get("/todos?order=DESC", headers= headers)
    assert ret.status_code == 200


def test_get_todo(client, mocker):
    mocker.patch.object(
        ToDoRepository,
        "get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="FastAPI test 01", is_done=True)
    )
    # 200
    ret = client.get("/todos/1")
    assert ret.status_code == 200
    assert ret.json() == {"id": 1, "contents": "FastAPI test 01", "is_done": True}

    # 404
    mocker.patch.object(
        ToDoRepository,
        "get_todo_by_todo_id",
        return_value=None
    )
    ret = client.get("/todos/1")
    assert ret.status_code == 404
    assert ret.json() == {"detail" : "Todo not found"}

def test_create_todo(client, mocker):
    create_spy = mocker.spy(ToDo, "create")
    mocker.patch.object(
        ToDoRepository,
        "create_todo",
        return_value=ToDo(id=1, contents="FastAPI test 01", is_done=True)
    )

    body = {
        "contents" : "test",
        "is_done" : False
    }

    # 200
    ret = client.post("/todos", json=body)

    assert create_spy.spy_return.id is None
    assert create_spy.spy_return.contents == "test"
    assert create_spy.spy_return.is_done is False

    assert ret.status_code == 201
    assert ret.json() == {"id": 1, "contents": "FastAPI test 01", "is_done": True}

def test_update_todo(client, mocker):
    mocker.patch.object(
        ToDoRepository,
        "get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="FastAPI test 01", is_done=True)
    )

    undone = mocker.patch.object(ToDo, "undone")

    mocker.patch.object(
        ToDoRepository,
        "update_todo",
        return_value=ToDo(id=1, contents="FastAPI test 01", is_done=False)
    )

    # 200
    ret = client.patch("/todos/1", json={"is_done": False})

    undone.assert_called_once_with()

    assert ret.status_code == 200
    assert ret.json() == {"id": 1, "contents": "FastAPI test 01", "is_done": False}

    # 404
    mocker.patch.object(
        ToDoRepository,
        "get_todo_by_todo_id",
        return_value=None
    )
    ret = client.patch("/todos/1", json={"is_done": True})
    assert ret.status_code == 404
    assert ret.json() == {"detail": "Todo not found"}

def test_delete_todo(client, mocker):
    mocker.patch.object(
        ToDoRepository,
        "get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="FastAPI test 01", is_done=True)
    )
    mocker.patch.object(
        ToDoRepository,
        "delete_todo",
        return_value=None
    )
    # 204
    ret = client.delete("/todos/1")
    assert ret.status_code == 204

    # 404
    mocker.patch.object(
        ToDoRepository,
        "get_todo_by_todo_id",
        return_value=None
    )
    ret = client.delete("/todos/1")
    assert ret.status_code == 404
    assert ret.json() == {"detail": "Todo not found"}

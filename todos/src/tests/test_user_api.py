def test_user_sign_up(client):
    ret = client.post("/users/sign-up")
    assert ret.status_code == 200
    assert ret.json() is True
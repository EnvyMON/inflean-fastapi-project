def test_health_check(client):
    ret = client.get("/")
    assert ret.status_code == 200
    assert ret.json() == {"hello": "fastapi"}

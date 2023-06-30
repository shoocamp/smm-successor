import io

from fastapi.testclient import TestClient

from smm_successor.models.user import BaseUser
from smm_successor.models.video import VideoInDB, VideoEdit, VideoInfo
from smm_successor.server import app

client = TestClient(app)


def test_sign_up():
    username = "test_user_1"
    password = "my_secret_password"
    email = "test_user_1@gmail.com"

    response = client.post('/api/v1/users/signup', data={
        'username': username,
        'password': password,
        'email': email,
    }, allow_redirects=False)

    # redirect to sign in page
    assert response.status_code == 307, response.content


def test_log_in():
    username = "test_user_1"
    password = "my_secret_password"
    email = "test_user_1@gmail.com"

    response = client.post('/api/v1/users/signin', data={
        'username': username,
        'password': password,
    })

    assert response.status_code == 200
    access_token = response.json()['access_token']

    response = client.get("/api/v1/users/info")
    assert response.status_code == 401

    response = client.get("/api/v1/users/info", headers={"Authorization": f"Bearer {access_token}"})
    user = BaseUser(**response.json())
    assert user.username == username
    assert user.email == email
    assert user.id is not None


def test_upload_video(authorized_client, current_user):
    test_video = {
        "title": "test_video",
        "description": "test video description",
    }
    files = {'file': io.BytesIO()}

    response = authorized_client.post("/api/v1/videos/",
                                      data=test_video,
                                      files=files)

    assert response.status_code == 200, response.content

    video_in_db_raw = response.json()
    video_in_db = VideoInDB(**video_in_db_raw)

    assert video_in_db.info.title == test_video["title"]
    assert video_in_db.info.description == test_video["description"]
    assert video_in_db.owner_id == current_user.id

    response = authorized_client.get(f"/api/v1/videos/{video_in_db.id}")

    assert response.status_code == 200, response.content

    video_in_db_raw = response.json()
    video_in_db = VideoInDB(**video_in_db_raw)

    assert video_in_db.info.title == test_video["title"]
    assert video_in_db.info.description == test_video["description"]
    assert video_in_db.owner_id == current_user.id


def test_edit_video(authorized_client):
    test_video = {
        "title": "test_video",
        "description": "test video description",
    }
    files = {'file': io.BytesIO()}

    response = authorized_client.post("/api/v1/videos/",
                                      data=test_video,
                                      files=files)

    assert response.status_code == 200, response.content

    video_in_db_raw = response.json()
    video_in_db = VideoInDB(**video_in_db_raw)

    new_info = VideoEdit(
        info=VideoInfo(
            title="new_title",
            description="new description"
        )
    )

    response = authorized_client.put(f"/api/v1/videos/{video_in_db.id}", data=new_info.json())
    assert response.status_code == 200, response.content

    new_video_raw = response.json()
    new_video = VideoInDB(**new_video_raw)

    assert new_video.info.title == new_info.info.title
    assert new_video.info.description == new_info.info.description

    response = authorized_client.get(f"/api/v1/videos/{video_in_db.id}")

    assert response.status_code == 200, response.content
    new_video_raw = response.json()
    new_video = VideoInDB(**new_video_raw)

    assert new_video.info.title == new_info.info.title
    assert new_video.info.description == new_info.info.description

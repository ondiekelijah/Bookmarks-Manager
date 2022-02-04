import pytest
from jose import jwt
from app import schemas
from app.config import settings


def test_get_all_bookmarks(authorized_client, test_bookmarks):
    res = authorized_client.get("bookmarks/")

    def validate(bookmark):
        """
        Bookmark validation using a schema, takes a
        list of dict >> a list of schema models
        """
        return schemas.Bookmark(**bookmark)

    mapped_bookmarks = map(validate, res.json())
    bookmarks_list = list(mapped_bookmarks)

    # Remember here we only get posts of the authorized user -> test_client
    assert len(res.json()) == len(test_bookmarks)-1
    assert res.status_code == 200


def test_get_one_bookmark(authorized_client, test_bookmarks):
    res = authorized_client.get(f"bookmarks/{test_bookmarks[0].id}")
    assert res.status_code == 200

    bookmark = schemas.Bookmark(**res.json())

    # Refer to scchemas
    assert bookmark.id == test_bookmarks[0].id
    assert bookmark.body == test_bookmarks[0].body
    assert bookmark.url == test_bookmarks[0].url


def test_get_one_bookmark_not_exist(authorized_client, test_bookmarks):
    res = authorized_client.get(f"/bookmarks/234")
    assert res.status_code == 404


@pytest.mark.parametrize(
    "body, url",
    [
        ("Github", "https://github.com/Elie"),
        ("Twitter 2", "https://twitter.com/elie"),
        ("Twitter 3", "https://twitter.com/dev"),
        ("Twitter 4", "https://twitter.com/deve")

    ],
)
def test_create_bookmark(
    authorized_client, test_user, test_bookmarks, url, body
):
    res = authorized_client.post(
        "/bookmarks/", json={"url": url, "body": body}
    )

    new_bookmark = schemas.BookmarkOut(**res.json()) 

    assert res.status_code == 201
    assert new_bookmark.url == url
    assert new_bookmark.body == body


def test_create_bookmark_unauthorized_user(client, test_user, test_bookmarks):
    res = client.post(
        "/bookmarks/",
        json={
            "url": "https://github.com/Dev-Elie",
            "body": "Twitter",

        },
    )

    assert res.status_code == 401


def test_delete_bookmark_unauthorized_user(client, test_user, test_bookmarks):
    res = client.delete(f"/bookmarks/{test_bookmarks[0].id}")
    assert res.status_code == 401


def test_delete_bookmark_authorized_user(authorized_client, test_user, test_bookmarks):
    res = authorized_client.delete(f"/bookmarks/{test_bookmarks[0].id}")
    assert res.status_code == 204


def test_delete_bookmark_non_exist(authorized_client, test_user, test_bookmarks):
    res = authorized_client.delete(f"/bookmarks/8000000")

    assert res.status_code == 404

def test_delete_other_user_bookmark(authorized_client, test_user, test_bookmarks):
    res = authorized_client.delete(
        f"/bookmarks/{test_bookmarks[3].id}")
    assert res.status_code == 403

def test_update_post(authorized_client, test_user, test_bookmarks):
    data = {
        "url": "https://www.linkedin.com/in/ondiek-elijah-2aaba4198/",
        "body": "Dev Elie's Profile",
        "id": test_bookmarks[0].id
    }

    res = authorized_client.put(f"/bookmarks/{test_bookmarks[0].id}", json=data)
    updated_bookmark = models.Bookmarks(**res.json())

    assert res.status_code == 200
    assert updated_bookmark.url == data['url']
    assert updated_bookmark.body == data['body']


def test_update_other_user_bookmark(authorized_client, test_user, test_user2, test_bookmarks):
    data = {
        "url": "https://www.linkedin.com/in/ondiek-elijah-2aaba4198/",
        "body": "Linkedin Profile Updated",
        "id": test_bookmarks[3].id

    }
    res = authorized_client.put(f"/bookmarks/{test_bookmarks[3].id}", json=data)
    assert res.status_code == 403


def test_update_bookmark_unauthorized_user(client, test_user, test_bookmarks):
    res = client.put(
        f"/bookmarks/{test_bookmarks[0].id}")
    assert res.status_code == 401


def test_update_bookmark_non_exist(authorized_client, test_user, test_bookmarks):
    data = {
        "url": "https://www.linkedin.com/in/ondiek-elijah-2aaba4198/",
        "body": "Still Linkedin",
        "id": test_bookmarks[3].id

    }
    res = authorized_client.put(
        f"/bookmarks/000000", json=data)

    assert res.status_code == 404
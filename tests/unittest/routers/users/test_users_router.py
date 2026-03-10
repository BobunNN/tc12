def test_get_user(client, normal_user_token_headers, superuser_token_headers):
    res1 = client.get(
        "/v1/users/non-existent-user@example.com", headers=superuser_token_headers
    )
    res2 = client.get("/v1/users/user@example.com", headers=normal_user_token_headers)
    res3 = client.get("/v1/users/user@example.com", headers=superuser_token_headers)
    assert res1.status_code == 404
    assert res2.status_code == 403
    assert res3.status_code == 200


def test_read_users_me(client, normal_user_token_headers):
    response = client.get("/v1/users/me", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["first_name"] == "Regular"
    assert data["is_superuser"] is False


def test_read_all_users_as_superuser(client, superuser_token_headers):
    response = client.get("/v1/users", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # Should return at least two fixture users


def test_read_all_users_as_regular_user_forbidden(client, normal_user_token_headers):
    response = client.get("/v1/users", headers=normal_user_token_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges"


def test_signup(client):
    response = client.post(
        "/v1/users/signup",
        json={
            "email": "newuser@example.com",
            "password": "securepassword",
            "first_name": "New",
            "last_name": "User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"


def test_signup_existing_email_fails(client):
    response = client.post(
        "/v1/users/signup",
        json={
            "email": "user@example.com",  # Already exists in fixture
            "password": "securepassword",
            "first_name": "Clone",
            "last_name": "User",
        },
    )
    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "The user with this email already exists in the system."
    )


def test_update_user_me(client, normal_user_token_headers):
    response = client.patch(
        "/v1/users/me",
        headers=normal_user_token_headers,
        json={"first_name": "UpdatedName", "last_name": "User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "UpdatedName"


def test_update_password_me(client, normal_user_token_headers):
    response = client.patch(
        "/v1/users/me/password",
        headers=normal_user_token_headers,
        json={"current_password": "userpass", "new_password": "newsecurepassword123"},
    )
    assert response.status_code == 200
    assert response.json() == "Password updated successfully"


def test_delete_user_me(client, normal_user_token_headers):
    response = client.delete("/v1/users/me", headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json() == "User deleted successfully"


def test_delete_user_me_superuser_forbidden(client, superuser_token_headers):
    response = client.delete("/v1/users/me", headers=superuser_token_headers)
    assert response.status_code == 403
    assert (
        response.json()["detail"] == "Super users are not allowed to delete themselves"
    )


def test_self_deletion_wrong_endpoint(client, superuser_token_headers):
    response = client.delete(
        "v1/users/admin@example.com", headers=superuser_token_headers
    )
    assert response.status_code == 400

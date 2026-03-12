def test_create_training_session(
    client, superuser_token_headers, training_session_payload
):
    response = client.post(
        "/v1/training-sessions",
        json=training_session_payload,
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Leo Lagrange"


def test_create_training_session_forbidden(
    client, normal_user_token_headers, training_session_payload
):
    response = client.post(
        "/v1/training-sessions",
        json=training_session_payload,
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403 or response.status_code == 401


def test_get_training_session(
    client, superuser_token_headers, training_session_payload
):
    post = client.post(
        "/v1/training-sessions",
        json=training_session_payload,
        headers=superuser_token_headers,
    )
    session_id = post.json()["id"]
    response = client.get(
        f"/v1/training-sessions/{session_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == session_id


def test_get_all_training_sessions(
    client, superuser_token_headers, training_session_payload
):
    client.post(
        "/v1/training-sessions",
        json=training_session_payload,
        headers=superuser_token_headers,
    )
    response = client.get("/v1/training-sessions", headers=superuser_token_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_training_session(
    client, superuser_token_headers, training_session_payload
):
    post = client.post(
        "/v1/training-sessions",
        json=training_session_payload,
        headers=superuser_token_headers,
    )
    session_id = post.json()["id"]
    response = client.patch(
        f"/v1/training-sessions/{session_id}",
        json={"location": "Alain Mimoun"},
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["location"] == "Alain Mimoun"


def test_delete_training_session(
    client, superuser_token_headers, training_session_payload
):
    post = client.post(
        "/v1/training-sessions",
        json=training_session_payload,
        headers=superuser_token_headers,
    )
    session_id = post.json()["id"]
    response = client.delete(
        f"/v1/training-sessions/{session_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Deleted successfully"


def test_create_training_session_overlap(
    client, superuser_token_headers, training_session_payload, training_session_payload2
):
    client.post(
        "/v1/training-sessions",
        json=training_session_payload,
        headers=superuser_token_headers,
    )
    overlap_payload = training_session_payload.copy()
    overlap_payload["session_start"] = "10:30:00"
    response = client.post(
        "/v1/training-sessions",
        json=overlap_payload,
        headers=superuser_token_headers,
    )
    assert response.status_code == 409 or response.status_code == 422

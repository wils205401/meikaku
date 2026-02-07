import uuid

from fastapi.testclient import TestClient


class TestWorkspace:
    workspace_name = "Test User's Workspace"

    def test_create_workspace(
        self, client: TestClient, user_a_token_headers: dict[str, str]
    ) -> None:
        """
        Test create workspace.
        """
        response = client.post(
            "/workspaces",
            json={"name": self.workspace_name},
            headers=user_a_token_headers,
        )

        assert response.status_code == 201
        created_workspace = response.json()

        assert set(created_workspace.keys()) == {"id", "name", "created_at"}
        assert created_workspace["name"] == self.workspace_name

    def test_create_workspace_duplicate_name(
        self, client: TestClient, user_a_token_headers: dict[str, str]
    ) -> None:
        """
        Test that creating two workspaces with the same name raises an error.
        """
        # First workspace
        client.post(
            "/workspaces",
            json={"name": self.workspace_name},
            headers=user_a_token_headers,
        )

        # Second workspace
        response = client.post(
            "/workspaces",
            json={"name": self.workspace_name},
            headers=user_a_token_headers,
        )

        assert response.status_code == 409
        assert (
            response.json()["message"]
            == "The workspace you are trying to create already exists"
        )

    def test_get_workspaces(
        self, client: TestClient, user_a_token_headers: dict[str, str]
    ) -> None:
        """
        Test that all workspaces for a user is returned.

        NOTE:
        A default workspace is already created upon registration, therefore
        after we create a new workspace, we expect the number of workspaces to be 2
        """
        # Create a workspace
        client.post(
            "/workspaces",
            json={"name": self.workspace_name},
            headers=user_a_token_headers,
        )

        # Get workspaces
        response = client.get("/workspaces", headers=user_a_token_headers)

        assert response.status_code == 200

        workspaces = response.json()

        assert len(workspaces) == 2

        workspace_names = {workspace["name"] for workspace in workspaces}
        assert workspace_names == {
            "My Workspace",
            self.workspace_name,
        }  # "My Workspace" is the default workspace created

    def test_get_workspace(
        self, client: TestClient, user_a_token_headers: dict[str, str]
    ) -> None:
        """
        Given a workspace_id, test that the correct workspace for a user is returned.
        """
        # Create a workspace
        workspace_id = client.post(
            "/workspaces",
            json={"name": self.workspace_name},
            headers=user_a_token_headers,
        ).json()["id"]

        # Get workspace
        response = client.get(
            f"/workspaces/{workspace_id}", headers=user_a_token_headers
        )

        assert response.status_code == 200
        assert response.json()["name"] == self.workspace_name

    def test_get_workspace_not_found(
        self, client: TestClient, user_a_token_headers: dict[str, str]
    ) -> None:
        """
        Given a workspace_id, test that the correct workspace for a user is returned.
        """
        # Create a workspace
        workspace_id = client.post(
            "/workspaces",
            json={"name": self.workspace_name},
            headers=user_a_token_headers,
        ).json()["id"]

        # Get workspace for a random id
        random_id = uuid.uuid4()
        # The chance of ids being the same is pretty much 0, but oh well
        # lets prevent any flakiness
        assert random_id != workspace_id

        response = client.get(f"/workspaces/{random_id}", headers=user_a_token_headers)

        assert response.status_code == 404
        assert response.json()["message"] == f"Workspace {random_id} not found"

    def test_get_workspace_no_permission(
        self,
        client: TestClient,
        user_a_token_headers: dict[str, str],
        user_b_token_headers: dict[str, str],
    ) -> None:
        """
        Test that User A cannot access User B's workspace.

        - User A is the test user defined in the user_a_token_headers fixture
        - User B is the test user defined in the user_b_token_headers fixture
        """
        # Create a workspace for User A
        workspace_id = client.post(
            "/workspaces",
            json={"name": self.workspace_name},
            headers=user_a_token_headers,
        ).json()["id"]

        # Try to access User A's workspace as User B
        response = client.get(
            f"/workspaces/{workspace_id}", headers=user_b_token_headers
        )

        assert response.status_code == 403
        assert (
            response.json()["message"]
            == "You are unauthorized to access this workspace"
        )

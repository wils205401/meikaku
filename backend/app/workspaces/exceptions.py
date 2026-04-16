from uuid import UUID

from app.exceptions import AppBaseException


class WorkspaceAlreadyExists(AppBaseException):
    def __init__(self):
        super().__init__(
            status_code=409,
            error="Workspace Already Exists",
            message="The workspace you are trying to create already exists",
        )


class WorkspaceNotFound(AppBaseException):
    def __init__(self, workspace_id: UUID):
        super().__init__(
            status_code=404,
            error="Workspace Not Found",
            message=f"Workspace {workspace_id} not found",
        )


class WorkspaceForbidden(AppBaseException):
    def __init__(self):
        super().__init__(
            status_code=403,
            error="Workspace Forbidden",
            message="You are unauthorized to access this workspace",
        )

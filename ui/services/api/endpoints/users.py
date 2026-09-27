# ui/services/api/endpoints/users.py
from config.settings import settings
from services.api.client import ApiClient

class UsersAPI:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def hello_world(self) -> str:
        # En tu API: router.get("/") con prefix "/users"
        return self.client.get("/users/")

users_api = UsersAPI(ApiClient(settings.api_base_url, settings.api_timeout))

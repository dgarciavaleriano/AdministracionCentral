# ACFrontEnd/services/api/endpoints/users_api.py
from services.api.client import ApiClient
from config.settings import API_BASE_URL, API_TIMEOUT


class UsersAPI:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def hello_world(self) -> str:
        # En tu API: router.get("/") con prefix "/users"
        return self.client.get("/users/")


users_api = UsersAPI(ApiClient(API_BASE_URL, API_TIMEOUT))
# ui/services/api/endpoints/users.py
import os
from dotenv import load_dotenv
from services.api.client import ApiClient

load_dotenv()

class UsersAPI:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def hello_world(self) -> str:
        # En tu API: router.get("/") con prefix "/users"
        return self.client.get("/users/")

API_BASE_URL = os.getenv("API_BASE_URL")
API_TIMEOUT = float(os.getenv("API_TIMEOUT"))
users_api = UsersAPI(ApiClient(API_BASE_URL, API_TIMEOUT))
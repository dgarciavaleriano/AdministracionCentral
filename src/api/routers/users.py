from fastapi import APIRouter, status

from models.user import UserCreate

router: APIRouter = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # Logica de creacion de usuario
    return {
        "message": "Endpoint de creacion de usuario",
        "user": user,
    }


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: str):

    # Logica de borrado de usuario
    return {
        "message": "Endpoint de borrado de usuario",
        "user_id": user_id,
    }
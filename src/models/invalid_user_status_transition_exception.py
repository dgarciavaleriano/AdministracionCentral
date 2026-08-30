from user_status import UserStatus

class InvalidUserStatusTransition(Exception):
    def __init__(self, from_status: UserStatus, to_status: UserStatus):
        super().__init__(
            f'No se puede pasar del estado "{from_status.value}" al estado "{to_status.value}"'
        )

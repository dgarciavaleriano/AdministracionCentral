from enum import Enum

class UserStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"

    def can_transition_to(self, target: "UserStatus") -> bool:
        transitions = {
            UserStatus.ACTIVE: {UserStatus.SUSPENDED, UserStatus.DEACTIVATED},
            UserStatus.SUSPENDED: {UserStatus.ACTIVE, UserStatus.DEACTIVATED},
            UserStatus.DEACTIVATED: set(),
        }
        return target in transitions[self]
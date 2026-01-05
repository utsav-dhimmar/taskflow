from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class ProjectStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class ProjectPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

from contextvars import ContextVar


user_id: ContextVar[str] = ContextVar("lingominer_user_id")

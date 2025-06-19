from asyncio import Condition, Lock


class TaskContext:
    condition = Condition()
    lock = Lock()

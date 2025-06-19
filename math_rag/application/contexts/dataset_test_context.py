from asyncio import Condition, Lock


class DatasetTestContext:
    condition = Condition()
    lock = Lock()

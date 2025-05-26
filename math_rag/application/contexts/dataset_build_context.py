from asyncio import Condition, Lock


class DatasetBuildContext:
    condition = Condition()
    lock = Lock()

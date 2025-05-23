from asyncio import Condition, Lock


class IndexBuildContext:
    condition = Condition()
    lock = Lock()

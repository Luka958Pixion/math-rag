from abc import ABC, abstractmethod


class BaseMathArticleParserService(ABC):
    @abstractmethod
    def parse(self):
        pass

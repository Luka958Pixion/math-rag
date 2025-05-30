from abc import ABC, abstractmethod

from mcp.server.fastmcp import FastMCP


class BaseResource(ABC):
    @abstractmethod
    def add(self, mcp: FastMCP):
        pass

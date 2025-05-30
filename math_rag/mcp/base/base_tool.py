from abc import ABC, abstractmethod

from mcp.server.fastmcp import FastMCP


class BaseTool(ABC):
    @abstractmethod
    def add(self, mcp: FastMCP):
        pass

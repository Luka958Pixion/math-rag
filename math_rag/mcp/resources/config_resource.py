from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources import Resource

from math_rag.mcp.base import BaseResource


class _ConfigResource(Resource):
    async def read(self) -> str | bytes:
        return 'this is some resource content'


class ConfigResource(BaseResource):
    def add(self, mcp: FastMCP):
        mcp.add_resource(
            _ConfigResource(
                uri='config://default',
                name='default-config',
                description='A static config resource for testing.',
                mime_type='text/plain',
            )
        )

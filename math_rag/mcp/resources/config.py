from dependency_injector.wiring import Provide, inject
from mcp.server.fastmcp.resources import Resource

from math_rag.application.containers import ApplicationContainer


class ConfigResource(Resource):
    async def read(self) -> str | bytes:
        return 'this is some resource content'


CONFIG_RESOURCE = ConfigResource(
    uri='config://default',
    name='default-config',
    description='A static config resource for testing.',
    mime_type='text/plain',
)

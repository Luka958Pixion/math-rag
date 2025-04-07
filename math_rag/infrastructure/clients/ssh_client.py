from logging import getLogger

from asyncssh import (
    ConnectionLost,
    DisconnectError,
    SSHClientConnection,
    connect,
    read_private_key,
)
from asyncssh.misc import async_context_manager
from backoff import expo, on_exception


logger = getLogger(__name__)


class SSHClient:
    def __init__(self, host: str, user: str, passphrase: str):
        self.host = host
        self.user = user
        self.private_key = read_private_key('/.ssh/id_ed25519', passphrase)

    @async_context_manager
    async def connect(self) -> SSHClientConnection:
        return await connect(
            self.host, username=self.user, client_keys=[self.private_key]
        )

    async def connect_retry(self) -> SSHClientConnection:
        return await on_exception(expo, (ConnectionLost, DisconnectError), max_tries=4)(
            self.connect
        )()

    async def run(self, command: str) -> str:
        async with await self.connect_retry() as connection:
            result = await connection.run(command, check=False)
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            logger.info(
                f'Command `{command}` in `{self.run.__name__}` '
                f'returned stdout: {stdout}'
            )

            if stderr:
                logger.error(
                    f'Command `{command}` in `{self.run.__name__}` '
                    f'returned stderr: {stderr}'
                )

            if result.exit_status != 0:
                raise Exception(
                    f'Command `{command}` failed with status {result.exit_status}'
                )

            return stdout

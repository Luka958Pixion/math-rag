from logging import getLogger

from asyncssh import (
    ChannelOpenError,
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
        self._private_key = read_private_key('/.ssh/id_ed25519', passphrase)
        self._connection: SSHClientConnection | None = None

    @async_context_manager
    async def connect(self) -> SSHClientConnection:
        return await connect(self.host, username=self.user, client_keys=[self._private_key])

    async def connect_retry(self) -> SSHClientConnection:
        # NOTE: max_tries=None sets unlimited retries
        return await on_exception(
            expo, (ConnectionLost, DisconnectError, ChannelOpenError), max_tries=None, max_value=60
        )(self.connect)()

    async def _get_connection(self) -> SSHClientConnection:
        if self._connection is None or self._connection.is_closed():
            try:
                if self._connection is not None:
                    self._connection.close()

            except Exception:
                pass

            self._connection = await self.connect_retry()

        return self._connection

    async def run(self, command: str) -> str:
        try:
            connection = await self._get_connection()
            result = await connection.run(command, check=False)

        except (ConnectionLost, DisconnectError):
            self._connection = None
            connection = await self._get_connection()
            result = await connection.run(command, check=False)

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        # logger.info(f'Command `{command}` in `{self.run.__name__}` ' f'returned stdout: {stdout}')

        if stderr:
            logger.error(
                f'Command `{command}` in `{self.run.__name__}` ' f'returned stderr: {stderr}'
            )

        if result.exit_status != 0:
            raise Exception(f'Command `{command}` failed with status {result.exit_status}')

        return stdout

import logging

from asyncssh import ConnectionLost, SSHClientConnection, connect, read_private_key
from asyncssh.misc import async_context_manager
from backoff import expo, on_exception


class SSHClient:
    def __init__(self, host: str, user: str, passphrase: str):
        self.host = host
        self.user = user
        self.private_key = read_private_key('/.ssh/id_ed25519', passphrase)

    @async_context_manager
    @on_exception(expo, (OSError, ConnectionLost), max_tries=4)
    async def connect(self) -> SSHClientConnection:
        return await connect(
            self.host, username=self.user, client_keys=[self.private_key]
        )

    async def run(self, command: str) -> str:
        async with await self.connect() as connection:
            result = await connection.run(command, check=True)
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            logging.info(
                f'Running `{command}` in `{self.run.__name__}` resulted in: {stdout}'
            )

            if stderr:
                logging.error(
                    f'Error while running `{command}` in `{self.run.__name__}`: {stderr}'
                )
                raise Exception(stderr)

            return stdout

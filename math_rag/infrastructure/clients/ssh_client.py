import logging

from asyncssh import ConnectionLost, Error, connect, read_private_key
from backoff import expo, on_exception


class SSHClient:
    def __init__(self, host: str, user: str, passphrase: str):
        self.host = host
        self.user = user
        self.private_key = read_private_key('/.ssh/id_ed25519', passphrase=passphrase)

    @on_exception(expo, (OSError, ConnectionLost), max_tries=4)
    async def run(self, command: str) -> str:
        try:
            async with await connect(
                self.host, username=self.user, client_keys=[self.private_key]
            ) as connection:
                result = await connection.run(command, check=False)

                if result.exit_status != 0:
                    logging.error(
                        f'SSH process with command {result.command},\n'
                        f'completed with status {result.exit_status},\n'
                        f'STDOUT: {result.stderr},\n'
                        f'STDERR: {result.stderr}'
                    )
                    raise Exception(
                        f'SSH process completed with status {result.exit_status}'
                    )

                return result.stdout.strip()

        except Error:
            raise

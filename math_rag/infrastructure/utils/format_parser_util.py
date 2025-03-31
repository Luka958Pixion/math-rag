from datetime import datetime, timedelta


class FormatParserUtil:
    @staticmethod
    def parse_memory(value: str) -> int:
        base10 = {'b': 1, 'kb': 10**3, 'mb': 10**6, 'gb': 10**9, 'tb': 10**12}
        base2 = {
            'kib': 1024,
            'mib': 1024**2,
            'gib': 1024**3,
            'tib': 1024**4,
            'k': 1024,
            'm': 1024**2,
            'g': 1024**3,
            't': 1024**4,
        }
        units = {**base2, **base10}

        value = value.strip().lower()

        for unit in sorted(units, key=len, reverse=True):
            if value.endswith(unit):
                number = value.removesuffix(unit)

                return int(float(number) * units[unit])

        raise ValueError(f'Invalid memory format: {value}')

    @staticmethod
    def parse_timedelta(value: str) -> timedelta:
        if value == '0':
            return timedelta(seconds=0)

        if value.count(':') == 1:
            value += ':00'

        return value

    @staticmethod
    def parse_datetime(value: str) -> timedelta:
        return datetime.strptime(value, '%a %b %d %H:%M:%S %Y')

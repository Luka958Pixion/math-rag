from datetime import timedelta


class HPCParserUtil:
    @staticmethod
    def parse(value: str) -> dict[str, str]:
        result: dict[str, str] = {}
        collected: list[str] = []
        buffer = ''

        for line in value.splitlines():
            line = line.rstrip('\n')

            if line.startswith('Job Id:'):
                result['Job_Id'] = line.split(':', 1)[1].strip()
                continue

            stripped = line.lstrip('\t')
            is_continuation = stripped.lstrip().startswith('=')
            eq_index = stripped.find(' = ')
            is_new_entry = eq_index != -1 and eq_index < 40 and not is_continuation

            if is_new_entry:
                if buffer:
                    collected.append(buffer)

                buffer = stripped.strip()

            else:
                buffer += stripped.strip()

        if buffer:
            collected.append(buffer)

        for entry in collected:
            if ' = ' in entry:
                key, value = entry.split(' = ', 1)
                result[key.strip()] = value.strip()

        result = {key.lower(): value for key, value in result.items()}

        return result

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
    def parse_time(value: str) -> timedelta:
        if value == '0':
            return timedelta(seconds=0)

        if value.count(':') == 1:
            value += ':00'

        return value

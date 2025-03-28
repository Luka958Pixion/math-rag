class PBSProValidator:
    @staticmethod
    def parse_memory(value: str) -> int:
        units = {'b': 1, 'kb': 1024, 'mb': 1024**2, 'gb': 1024**3, 'tb': 1024**4}
        value = value.strip().lower()

        for unit in units:
            if value.endswith(unit):
                number = value.removesuffix(unit)

                return int(float(number) * units[unit])

        raise ValueError(f'Invalid memory format: {value}')

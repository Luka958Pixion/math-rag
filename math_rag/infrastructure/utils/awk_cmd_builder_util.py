class AwkCmdBuilderUtil:
    @staticmethod
    def build(
        num_records: int, fields: list[int], operator: str = '==', separator: str = ', '
    ) -> str:
        print_args = separator.join(f'${i}' for i in fields).strip()

        return f"awk 'NR{operator}{num_records} {{print {print_args}}}'"

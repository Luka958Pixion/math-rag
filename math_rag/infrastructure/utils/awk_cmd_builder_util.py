from collections.abc import Iterable


class AwkCmdBuilderUtil:
    """
    GNU awk simple command builder utility

    Reference:
        https://savannah.gnu.org/git/?group=gawk
    """

    @staticmethod
    def build(
        *,
        row_number: int,
        col_numbers: Iterable[int],
        operator: str = '==',
        separator: str = ', ',
    ) -> str:
        print_args = separator.join(f'${i}' for i in col_numbers).strip()

        return f"awk 'NR{operator}{row_number} {{print {print_args}}}'"

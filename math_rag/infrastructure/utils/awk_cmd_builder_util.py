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

    @staticmethod
    def build_wall_times() -> str:
        return (
            "awk -F'= ' "
            "'/Resource_List.walltime/ { walltime = $2 } "
            '/resources_used.walltime/ { used = $2 } '
            'END { print walltime "\\n" used }\''
        )

from re import match


class LabelInstructionBuilderUtil:
    @staticmethod
    def build(text: str) -> str:
        """
        Convert any multiline string into HTML by:
        - Wrapping non-numbered lines in <p>...</p>
        - Grouping contiguous lines starting with '1.', '2.', etc. into <ol><li>...</li></ol>
        """
        html_lines = []
        in_list = False

        for line in text.splitlines():
            if match(r'^\s*\d+\.', line):
                if not in_list:
                    html_lines.append('<ol>')
                    in_list = True

                html_lines.append(f'  <li>{line}</li>')

            else:
                if in_list:
                    html_lines.append('</ol>')
                    in_list = False

                html_lines.append(f'<p>{line}</p>')

        if in_list:
            html_lines.append('</ol>')

        return '\n'.join(html_lines)

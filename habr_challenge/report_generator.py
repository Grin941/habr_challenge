__all__ = ['ReportGenerator']


class ReportGenerator:
    """Generate and show crawler result report.

    Attributes:
        _report_data_dict (dict):
            dictionary containing report data.
            Example:
                {
                    ('01-01-2000', '07-07-2000'): 'noun1 noun2 noun3'
                }
        _report_header (tuple): tuple with report header titles.
        _report_columns_width (tuple): tuple with column width.
        _table_width (int): table total width.
        _report_format_string (str): string represents report skeleton.
        _columns_separator (str): string character separating
            columns in a report.
        _rows_separator (str): string character separating rows in a report.

    """

    def __init__(self, report_data_dict):
        self._report_data_dict = report_data_dict
        self._report_header = (
            'Начало недели', 'Конец недели', 'Популярные слова'
        )

        self._report_columns_width = self._get_report_columns_width()
        self._table_width = sum(
            self._report_columns_width
        ) + 3  # Keep in mind 3 column separators

        self._report_format_string = (
            '{week_begin:{week_begin_col_width}}{sep}'
            '{week_end:^{week_end_col_width}}{sep}'
            '{popular_words:^{popular_words_col_width}}{sep}'
        )
        self._columns_separator = '|'
        self._rows_separator = '-'

    def _get_report_columns_width(self):
        """Estimate width of each report columns.

        Popular words column width equals
        a length of the longest string in a report_data.values().

        Returns:
            (tuple): (int, int, int) - estimated columns width.

        """
        week_begin_col_width = len(
            self._report_header[0]
        ) + 1  # Note one whitespace at the end
        week_end_col_width = len(
            self._report_header[1]
        ) + 2  # Note two whitespaces at the left and right
        popular_words_col_width = len(
            max(self._report_data_dict.values(), key=len)
        ) + 2  # Note two whitespaces at the left and right

        return (
            week_begin_col_width,
            week_end_col_width,
            popular_words_col_width
        )

    def _print_header(self):
        """Print report header.
        """
        header = self._report_format_string.format(
            week_begin=self._report_header[0],
            week_begin_col_width=self._report_columns_width[0],
            week_end=self._report_header[1],
            week_end_col_width=self._report_columns_width[1],
            popular_words=self._report_header[2],
            popular_words_col_width=self._report_columns_width[2],
            sep=self._columns_separator
        )
        print(self._rows_separator * self._table_width)
        print(header)
        print(self._rows_separator * self._table_width)

    def _print_body(self):
        """Print report body.
        """
        for week, popular_words in self._report_data_dict.items():
            body = self._report_format_string.format(
                week_begin=week[0],
                week_begin_col_width=self._report_columns_width[0],
                week_end=week[1],
                week_end_col_width=self._report_columns_width[1],
                popular_words=popular_words,
                popular_words_col_width=self._report_columns_width[2],
                sep=self._columns_separator
            )
            print(body)
        print(self._rows_separator * self._table_width)

    def print_report(self):
        """Public interface to print a report.
        """
        self._print_header()
        self._print_body()

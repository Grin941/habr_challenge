import collections

from habr_challenge.common import cached_property


__all__ = ['ReportGenerator']


ReportTemplate = collections.namedtuple(
    'ReportTemplate',
    ['body', 'rows_separator', 'columns_separator']
)


class ReportGenerator:
    """Generate and show crawler result report.

    Attributes:
        _report_data_dict (dict):
            dictionary containing report data.
            Example:
                {
                    ('01-01-2000', '07-07-2000'): 'noun1 noun2 noun3'
                }

    """

    REPORT_TEMPLATE = ReportTemplate(
        body=(
            '{col_data[0]:{col_width[0]}}{col_sep}'
            '{col_data[1]:^{col_width[1]}}{col_sep}'
            '{col_data[2]:^{col_width[2]}}{col_sep}'
        ),
        rows_separator='-',
        columns_separator='|'
    )

    REPORT_HEADER = ('Начало недели', 'Конец недели', 'Популярные слова')

    def __init__(self, report_data_dict):
        self._report_data_dict = report_data_dict

    @cached_property
    def columns_width(self):
        """Estimate width of each report columns.

        Popular words column width equals
        a length of the longest string in a report_data.values().

        Returns:
            (tuple): (int, int, int) - estimated columns width.

        """
        week_begin_col_width = len(
            self.REPORT_HEADER[0]
        ) + 1  # Note one whitespace at the end
        week_end_col_width = len(
            self.REPORT_HEADER[1]
        ) + 2  # Note two whitespaces at the left and right
        popular_words_col_width = len(
            max(self._report_data_dict.values(), key=len)
        ) + 2  # Note two whitespaces at the left and right

        return (
            week_begin_col_width,
            week_end_col_width,
            popular_words_col_width
        )

    @cached_property
    def table_width(self):
        return sum(
            self.columns_width
        ) + 3  # Keep in mind 3 column separators

    def _print_boarder(self):
        print(self.REPORT_TEMPLATE.rows_separator * self.table_width)

    def _print_header(self):  # pragma: no cover
        """Print report header.
        """
        header = self.REPORT_TEMPLATE.body.format(
            col_data=self.REPORT_HEADER,
            col_width=self.columns_width,
            col_sep=self.REPORT_TEMPLATE.columns_separator
        )
        self._print_boarder()
        print(header)
        self._print_boarder()

    def _print_body(self):  # pragma: no cover
        """Print report body.
        """
        for (
            week_begin, week_end
        ), popular_words in self._report_data_dict.items():
            body = self.REPORT_TEMPLATE.body.format(
                col_data=(week_begin, week_end, popular_words),
                col_width=self.columns_width,
                col_sep=self.REPORT_TEMPLATE.columns_separator
            )
            print(body)
        self._print_boarder()

    def print_report(self):  # pragma: no cover
        """Public interface to print a report.
        """
        self._print_header()
        self._print_body()

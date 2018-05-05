class ReportGenerator:

    def __init__(self, report_data_json):
        self._report_data_json = report_data_json
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
        week_begin_col_width = len(self._report_header[0]) + 1
        week_end_col_width = len(self._report_header[1]) + 2
        popular_words_col_width = len(
            max(self._report_data_json.values(), key=len)
        ) + 2

        return (
            week_begin_col_width,
            week_end_col_width,
            popular_words_col_width
        )

    def _print_header(self):
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
        for week, popular_words in self._report_data_json.items():
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
        self._print_header()
        self._print_body()

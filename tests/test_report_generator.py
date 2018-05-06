import pytest

from habr_challenge.report_generator import ReportGenerator


@pytest.fixture
def report_generator():
    report_data_dict = {
        ('01-01-2000', '07-07-2000'): 'пример решение проблема',
        ('01-01-2010', '07-07-2010'): 'окно менеджер задача',
    }
    return ReportGenerator(report_data_dict)


def test_report_column_width(report_generator):
    assert report_generator._get_report_columns_width() == (
        len('{0} '.format(report_generator._report_header[0])),
        len(' {0} '.format(report_generator._report_header[1])),
        len(' пример решение проблема ')
    )

import pytest

from habr_challenge.report_generator import ReportGenerator


@pytest.fixture(scope="module")
def report_generator():
    report_data_dict = {
        ('01-01-2000', '07-07-2000'): 'пример решение проблема',
        ('01-01-2010', '07-07-2010'): 'окно менеджер задача',
    }
    return ReportGenerator(report_data_dict)

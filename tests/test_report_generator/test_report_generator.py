def test_report_column_width(report_generator):
    assert report_generator.columns_width == (
        len('{0} '.format(report_generator.REPORT_HEADER[0])),
        len(' {0} '.format(report_generator.REPORT_HEADER[1])),
        len(' пример решение проблема ')
    )

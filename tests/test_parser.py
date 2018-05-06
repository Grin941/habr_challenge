import pytest
import collections


from habr_challenge.parser import ParserDataCollector, Parser


@pytest.fixture
def parser_data_collector():
    return ParserDataCollector()


@pytest.fixture
def article_data():
    article_publication_datetime = '1 января 2010'
    title = '(Законы Акина) законы космической инженерии'

    return Parser.ARTICLE_DATA(title, article_publication_datetime)


def test_data_collector_normalizes_publication_datetime(
    parser_data_collector, article_data
):
    """Tuple with start and end week days should be returned.
    And also article publication datetime should be parsed correctly.
    """
    assert parser_data_collector._normalize_publication_datetime(
        article_data.publication_datetime
    ) == ('28-12-2009', '03-01-2010')


def test_data_collector_normalizes_article_title(
    parser_data_collector, article_data
):
    assert parser_data_collector._normalize_title(
        article_data.title) == \
        collections.Counter({'закон': 2, 'инженерия': 1})


def test_data_collector_updating_in_realtime(
    parser_data_collector, article_data
):
    # There is no data yet
    assert parser_data_collector._parser_result == {}

    # Collect some data
    parser_data_collector.collect(article_data)
    parser_data_collector._parser_result = {
        ('28-12-2009', '03-01-2010'): collections.Counter(
            {'закон': 2, 'инженерия': 1}
        )
    }


def test_data_collector_result_dict(
    parser_data_collector, article_data
):
    parser_data_collector.collect(article_data)
    assert parser_data_collector.result_dict == {
        ('28-12-2009', '03-01-2010'): 'закон инженерия'
    }

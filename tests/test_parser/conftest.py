import pytest

from habr_challenge import parser
from habr_challenge.parser_data_collector import ParserDataCollector


@pytest.fixture(scope="module")
def parser_data_collector():
    return ParserDataCollector()


@pytest.fixture(scope="module")
def article_data():
    article_publication_datetime = '1 января 2010'
    title = '(Законы Акина) законы космической инженерии'

    return parser.ARTICLE_DATA(title, article_publication_datetime)

import pytest

from habr_challenge.parser import ParserDataCollector, Parser


@pytest.fixture(scope="module")
def parser_data_collector():
    return ParserDataCollector()


@pytest.fixture(scope="module")
def article_data():
    article_publication_datetime = '1 января 2010'
    title = '(Законы Акина) законы космической инженерии'

    return Parser.ARTICLE_DATA(title, article_publication_datetime)

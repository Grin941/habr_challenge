import pymorphy2
import string
import datetime
import argparse
import requests
import bs4
import collections
import dateparser

from tqdm import tqdm as progress_bar


class Selector:

    SELECTOR_PARSE_SIGNATURE = collections.namedtuple(
        'SELECTOR_PARSE_SIGNATURE', ['name', 'css_kwargs']
    )

    def __init__(self, selector, class_=None, id_=None):
        self.name = selector
        self.class_ = class_
        self.id_ = id_

    def to_bs4_parse_signature(self):
        return self.SELECTOR_PARSE_SIGNATURE(
            self.name,
            {
                'class_': self.class_,
                'id': self.id_,
            }
        )


class SiteConfig:

    SITE_CONFIG = {
        'habr': {
            'url': 'https://habr.com/all/',
            'pagination': 'page{page}/',
            'article': Selector(
                'article', class_="post post_preview"
            ),
            'article_publication_datetime': Selector(
                'span', class_="post__time"
            ),
            'article_title': Selector(
                'a', class_="post__title_link"
            ),
        },
    }

    def __init__(self, site_name):
        self._site_config = self._get_site_config(site_name)

    def __getattr__(self, selector_name):
        selector = self._site_config.get(selector_name)
        if selector is None:
            raise AttributeError(
                '"{selector_name}" selector not defined in {site_url} config'.format(
                    site_url=self._site_config['url'],
                    selector_name=selector_name
                )
            )

        return selector

    def _get_site_config(self, site_name):
        site_config = self.SITE_CONFIG.get(site_name)
        if site_config is None:
            raise Exception(
                'Please provide {site_name} site configuration'.format(
                    site_name=site_name
                )
            )

        return site_config

    @property
    def articles_list_url(self):
        return '{url}{pagination}'.format(
            url=self._site_config['url'],
            pagination=self._site_config.get('pagination', '')
        )


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return start


class ParserDataCollector:

    def __init__(self, args):
        self._parser_result = collections.defaultdict(collections.Counter)
        self._parser_data_collector = self._collect()

    def _normalize_publication_datetime(self, article_publication_datetime):
        datetime_parsed = dateparser.parse(article_publication_datetime)
        week_start = datetime_parsed - datetime.timedelta(
            days=datetime_parsed.weekday()
        )
        week_end = week_start + datetime.timedelta(days=6)

        return (
            week_start.strftime('%d-%m-%Y'),
            week_end.strftime('%d-%m-%Y')
        )

    def _normalize_title(self, article_title):
        morph = pymorphy2.MorphAnalyzer()
        title_words = article_title.lower().strip(
            string.punctuation + "«»"
        ).split(' ')
        title_morphs = (morph.parse(word)[0] for word in title_words)
        title_nouns = filter(
            lambda word_morph: 'NOUN' in word_morph.tag, title_morphs
        )
        return collections.Counter(
            map(lambda noun: noun.normal_form, title_nouns)
        )

    @coroutine
    def _collect(self):
        while True:
            article_data = (yield)
            article_title_words = self._normalize_title(article_data.title)
            article_week_range = self._normalize_publication_datetime(
                article_data.publication_datetime
            )

            self._parser_result[article_week_range].update(article_title_words)

    def collect(self, article_data):
        self._parser_data_collector.send(article_data)

    @property
    def result(self):
        result = {}
        for k, v in self._parser_result.items():
            result[k] = ' '.join(map(lambda x: x[0], v.most_common(3)))
        return result


class Parser:

    ARTICLE_DATA = collections.namedtuple(
        'ARTICLE_DATA', ['title', 'publication_datetime']
    )

    def __init__(self, site_config):
        self.article_selector = self._get_selector('article', site_config)
        self.article_title_selector = self._get_selector(
            'article_title', site_config
        )
        self.article_publication_datetime_selector = self._get_selector(
            'article_publication_datetime', site_config
        )

    def _get_selector(self, selector_name, site_config):
        selector = getattr(site_config, selector_name)
        return selector.to_bs4_parse_signature()

    def parse_articles(self, articles_list):
        soup = bs4.BeautifulSoup(articles_list, 'html.parser')
        for article_preview in soup.find_all(
            self.article_selector.name,
            **self.article_selector.css_kwargs
        ):
            article_publication_datetime = article_preview.find(
                self.article_publication_datetime_selector.name,
                **self.article_publication_datetime_selector.css_kwargs
            ).text
            article_title = article_preview.find(
                self.article_title_selector.name,
                **self.article_title_selector.css_kwargs
            ).text

            yield self.ARTICLE_DATA(
                article_title, article_publication_datetime
            )


class Crawler:

    REQUEST_HEADERS = {
        'User-Agent': ("Mozilla/5.0"
                       "(Macintosh; Intel Mac OS X 10_10_1)"
                       "AppleWebKit/537.36"
                       "(KHTML, like Gecko)"
                       "Chrome/39.0.2171.95"
                       "Safari/537.36"),
    }

    def __init__(self, site_name):
        self._site_config = SiteConfig(site_name)

    def _crawl_articles(self, pages_range):
        articles_list_url = self._site_config.articles_list_url
        for page in pages_range:
            articles_list = requests.get(
                articles_list_url.format(page=page),
                headers=self.REQUEST_HEADERS
            )
            yield articles_list.text

    def crawl(self, user_settings):
        parser = Parser(self._site_config)
        parser_data_collector = ParserDataCollector(user_settings)
        show_progress = progress_bar if \
            user_settings.show_progress else lambda x: x
        for articles_list in self._crawl_articles(
            pages_range=show_progress(range(1, user_settings.pages + 1))
        ):
            for article_data in parser.parse_articles(articles_list):
                parser_data_collector.collect(article_data)

        return parser_data_collector.result


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Print 3 most popular nouns.'
    )
    parser.add_argument(
        '--pages', type=int, default=10,
        help="""How many feed pages do you like to parse
                (default: %(default)s)?"""
    )
    parser.add_argument(
        '--show-progress', action='store_false',
        help='do you want to see progress bar?'
    )
    user_settings = parser.parse_args()
    assert user_settings.pages > 0, "Please pass --pages > 10"

    articles_data = Crawler('habr').crawl(user_settings)
    ReportGenerator(articles_data).print_report()

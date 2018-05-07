import bs4
import collections
import dateparser
import datetime
import pymorphy2
import string

from habr_challenge.common import coroutine


__all__ = ['Parser']


class ParserDataCollector:
    """Coroutine collecting Parser result in a real time.

    Attributes:
        _parser_result (defaultdict(<class 'collections.Counter'>, {})):
            container collecting Parser results
        _parser_data_collector (function): coroutine itself

    """

    def __init__(self, user_settings=None):
        """
        Args:
            user_settings (ArgumentParser):
               user arguments passed to the program.

        Note:
            user_settings are not used now.
            They are needed to make Collector more customable and
            user friendly in a future.

        """
        self._parser_result = collections.defaultdict(collections.Counter)
        self._parser_data_collector = self._collect()

    def _normalize_publication_datetime(self, article_publication_datetime):
        """Normalize article publication datetime.

        Estimate the start and the and of the week\
        when article has been published.

        Args:
            article_publication_datetime (str): crawled publication datetime.

        Returns:
            (str, str) - formatted dates of week start and end.

        """
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
        """Normalize article title.

        - lowercase title
        - remove punctuation marks from title
        - filter only nouns
        - normalize nouns
        - count each noun occurance in the title

        Args:
            article_title (str): article title.

        Returns:
            collections.Counter - count each noun occurance in the title.

        """
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
        """Collect parsed articles in a real time.

        Normalize and store parsed data.

        """
        while True:
            article_data = (yield)
            article_title_words = self._normalize_title(article_data.title)
            article_week_range = self._normalize_publication_datetime(
                article_data.publication_datetime
            )

            self._parser_result[article_week_range].update(article_title_words)

    def collect(self, article_data):
        """Public interface to send data to the coroutine.

        Args:
            article_data (collections.namedtuple(
                str:title, str:publication_datetime)
            ):
                webpage parsed data.

        """
        self._parser_data_collector.send(article_data)

    @property
    def result_dict(self):
        """ParserDataCollector results in a user defined format.

        Show only 3 most common words for a week interval.

        Example:
            {
                ('01-01-2000', '07-07-2000'): 'noun1 noun2 noun3'
            }

        Returns:
            (dict): result dictionary

        """
        result = {}
        for k, v in self._parser_result.items():
            result[k] = ' '.join(map(lambda x: x[0], v.most_common(3)))
        return result


class Parser:  # pragma: no cover
    """Parse crawled webpage.

    Implemented with BeautifulSoup4.

    Attributes:
        _parser_data_collector (ParserDataCollector):
            collect parsed data in a real time.
        _article_selector (collections.namedtuple(str, dict)):
            selector to parse article preview.
        _article_title_selector (collections.namedtuple(str, dict)):
            selector to parse article title.
        _article_publication_datetime_selector (
            collections.namedtuple(str, dict)
        ):
            selector to parse article publication datetime.

    """

    ARTICLE_DATA = collections.namedtuple(
        'ARTICLE_DATA', ['title', 'publication_datetime']
    )

    def __init__(self, site_config, user_settings):
        """
        Args:
            user_settings (ArgumentParser):
               user arguments passed to the program.
            site_config (SiteConfig):
               get selectors from config

        """
        self._parser_data_collector = ParserDataCollector(user_settings)

        self._article_selector = self._get_selector('article', site_config)
        self._article_title_selector = self._get_selector(
            'article_title', site_config
        )
        self._article_publication_datetime_selector = self._get_selector(
            'article_publication_datetime', site_config
        )

    def _get_selector(self, selector_name, site_config):
        """Get selector in a format useful for bs4 parsing.

        Args:
            selector_name (str): selector name to get.
            site_config (SiteConfig): selectors are declared in the config.

        Returns:
            collections.namedtuple(str, dict)
        """
        selector = getattr(site_config, selector_name)
        return selector.to_bs4_parse_signature()

    def _parse_articles(self, articles_list):
        """Parsing method.

        Parse pages with bs4 using Selectors declared in the SiteConfig.

        Args:
            articles_list (list): list of webpages crawled.

        """
        soup = bs4.BeautifulSoup(articles_list, 'html.parser')
        for article_preview in soup.find_all(
            self._article_selector.name,
            **self._article_selector.css_kwargs
        ):
            article_publication_datetime = article_preview.find(
                self._article_publication_datetime_selector.name,
                **self._article_publication_datetime_selector.css_kwargs
            ).text
            article_title = article_preview.find(
                self._article_title_selector.name,
                **self._article_title_selector.css_kwargs
            ).text

            article_data = self.ARTICLE_DATA(
                article_title, article_publication_datetime
            )
            self._parser_data_collector.collect(article_data)

    def parse(self, articles_list_pagination_gen):
        """Parser interface to parse webpages crawled.

        Crawler passes crawled web pages to a Parser
        that returns Parser result dictionary.

        Args:
            articles_list_pagination_gen (genirator):
                generator of strings representing artiles list paginated.

        Returns:
            (dict): parsed data dict.

        """
        for articles_list_from_page in articles_list_pagination_gen:
            self._parse_articles(articles_list_from_page)

        return self.result_dict

    @property
    def result_dict(self):
        """Parser results.

        Returns:
            (dict): ParserDataCollector result

        """
        return self._parser_data_collector.result_dict

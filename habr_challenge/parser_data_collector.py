import collections
import dateparser
import datetime
import pymorphy2
import string

from habr_challenge.common import coroutine


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

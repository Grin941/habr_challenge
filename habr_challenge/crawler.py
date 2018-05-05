import requests

from tqdm import tqdm as progress_bar

from habr_challenge.site_config import SiteConfig
from habr_challenge.parser import Parser


__all__ = ['Crawler']


class Crawler:
    """Crawle webpages and return parser result.

    Attributes:
       _site_config (SiteConfig): config of the site to be crawled.

    """

    REQUEST_HEADERS = {
        'User-Agent': ("Mozilla/5.0"
                       "(Macintosh; Intel Mac OS X 10_10_1)"
                       "AppleWebKit/537.36"
                       "(KHTML, like Gecko)"
                       "Chrome/39.0.2171.95"
                       "Safari/537.36"),
    }

    def __init__(self, site_name):
        """
        Args:
            site_name (str): Name of the site to be crawled

        Note:
            site_name should be equal the one defined in a SiteConfig

        """
        self._site_config = SiteConfig(site_name)

    def _crawl_articles(self, pages_range):
        """Crawl each webpage with articles during pagination.

        Args:
            pages_range (
              tqdm(range) or range
            ): iterable over the site pages with pretty statusbar.

        Yields:
           (str): webpage crawled.

        """
        articles_list_url = self._site_config.articles_list_url
        for page in pages_range:
            articles_list = requests.get(
                articles_list_url.format(page=page),
                headers=self.REQUEST_HEADERS
            )
            yield articles_list.text

    def crawl(self, user_settings):
        """Crawler interface to crawl webpages.

        Crawler passes crawled web pages to a Parser
        and returns Parser result dictionary.

        Args:
            user_settings (ArgumentParser):
               user arguments passed to the program.

        Returns:
            (dict): parsed data dict.

        """
        parser = Parser(self._site_config, user_settings)
        show_progress = progress_bar if \
            user_settings.show_progress else lambda x: x

        for articles_list in self._crawl_articles(
            pages_range=show_progress(range(1, user_settings.pages + 1))
        ):
            parser.parse_articles(articles_list)

        return parser.result_dict

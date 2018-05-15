import requests

from tqdm import tqdm as progress_bar


__all__ = ['RequestsCrawler']


class BaseCrawler:  # pragma: no cover
    """Crawle webpages and return parser result.

    Attributes:
       _site_config (SiteConfig): config of the site to be crawled.
       _user_settings (ArgumentParser):
           user arguments passed to the program.

    """

    REQUEST_HEADERS = {
        'User-Agent': ("Mozilla/5.0"
                       "(Macintosh; Intel Mac OS X 10_10_1)"
                       "AppleWebKit/537.36"
                       "(KHTML, like Gecko)"
                       "Chrome/39.0.2171.95"
                       "Safari/537.36"),
    }

    def __init__(self, site_config, user_settings):
        self._site_config = site_config
        self._user_settings = user_settings

    @staticmethod
    def _get_pagination_range(user_settings):
        """Get pagination range from user_settings.

        Return pretty shown pagination range.

        Args:
            user_settings (ArgumentParser):
                user arguments passed to the program.

        Returns:
            pages_range (
              tqdm(range) or range
            ): iterable over the site pages with pretty statusbar.


        """

        pages_range = range(1, user_settings.pages + 1)
        show_progress = progress_bar if \
            user_settings.show_progress else lambda x: x

        return show_progress(pages_range)

    def _crawl_articles(self, pages_range):
        """Crawl each webpage with articles during pagination.

        Args:
            pages_range (
              tqdm(range) or range
            ): iterable over the site pages with pretty statusbar.

        Yields:
           (str): webpage crawled.

        """
        raise NotImplementedError(
            'You are free to use every crawler you want'
        )

    def crawl(self):
        """Crawler interface to crawl webpages.

        Crawler crawles site through pagination.

        Yields:
            (str): crawlerd articles list webpage.

        """
        pages_range = self._get_pagination_range(self._user_settings)
        for articles_list in self._crawl_articles(pages_range):
            yield articles_list


class RequestsCrawler(BaseCrawler):
    """Crawl web weth Python requests library.
    """
    def _crawl_articles(self, pages_range):
        articles_list_url = self._site_config.articles_list_url
        for page in pages_range:
            articles_list = requests.get(
                articles_list_url.format(page=page),
                headers=self.REQUEST_HEADERS
            )
            yield articles_list.text

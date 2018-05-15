import requests

from tqdm import tqdm as progress_bar


REQUEST_HEADERS = {
    'User-Agent': ("Mozilla/5.0"
                   "(Macintosh; Intel Mac OS X 10_10_1)"
                   "AppleWebKit/537.36"
                   "(KHTML, like Gecko)"
                   "Chrome/39.0.2171.95"
                   "Safari/537.36"),
}


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


def _crawl_articles(articles_list_url, pages_range):
    """Crawl each webpage with articles during pagination.

    Args:
        articles_list_url (str): url to crawl articles from.
        pages_range (
          tqdm(range) or range
        ): iterable over the site pages with pretty statusbar.

    Yields:
       (str): webpage crawled.

    """
    for page in pages_range:
        articles_list = requests.get(
            articles_list_url.format(page=page),
            headers=REQUEST_HEADERS
        )
        yield articles_list.text


def crawl(site_config, user_settings):
    """Crawler interface to crawl webpages.

    Crawler crawles site through pagination.

    Args:
       site_config (SiteConfig): config of the site to be crawled.
       user_settings (ArgumentParser):
           user arguments passed to the program.

    Yields:
        (str): crawlerd articles list webpage.

    """
    pages_range = _get_pagination_range(user_settings)
    for articles_list in _crawl_articles(
        site_config.articles_list_url, pages_range
    ):
        yield articles_list

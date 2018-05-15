import bs4
import collections

from habr_challenge.parser_data_collector import ParserDataCollector


ARTICLE_DATA = collections.namedtuple(
    'ARTICLE_DATA', ['title', 'publication_datetime']
)


def _get_selectors_from_config(site_config, *selector_names):
    """Get selectors in a format useful for bs4 parsing.

    Args:
        selector_name (str): selector name to get.

    Returns:
        {str: collections.namedtuple(str, dict)}

    """
    selectors = {}
    for selector_name in selector_names:
        selector = getattr(site_config, selector_name)
        selectors[selector_name] = selector.to_bs4_parse_signature()
    return selectors


def _parse_articles(articles_list, **selectors):
    """Parsing method.

    Parse pages with bs4 using Selectors declared in the SiteConfig.

    Args:
        articles_list (list): list of webpages crawled.

    """
    article_selector = selectors['article']
    article_publication_datetime_selector = selectors[
        'article_publication_datetime'
    ]
    article_title_selector = selectors['article_title']

    soup = bs4.BeautifulSoup(articles_list, 'html.parser')
    for article_preview in soup.find_all(
        article_selector.name,
        **article_selector.css_kwargs
    ):
        article_publication_datetime = article_preview.find(
            article_publication_datetime_selector.name,
            **article_publication_datetime_selector.css_kwargs
        ).text
        article_title = article_preview.find(
            article_title_selector.name,
            **article_title_selector.css_kwargs
        ).text

        article_data = ARTICLE_DATA(
            article_title, article_publication_datetime
        )
        yield article_data


def parse(articles_list_pagination_gen, site_config, user_settings):
    """Parser interface to parse webpages crawled.

    Crawler passes crawled web pages to a Parser
    that returns Parser result dictionary.

    Args:
        articles_list_pagination_gen (genirator):
            generator of strings representing artiles list paginated.
        site_config (SiteConfig):
           get selectors from config
        user_settings (ArgumentParser):
           user arguments passed to the program.

    Returns:
        (dict): parsed data dict.

    """
    parser_data_collector = ParserDataCollector(user_settings)
    site_selectors = _get_selectors_from_config(
        site_config,
        *('article', 'article_publication_datetime', 'article_title')
    )

    for articles_list_from_page in articles_list_pagination_gen:
        for article_data in _parse_articles(
            articles_list_from_page, **site_selectors
        ):
            parser_data_collector.collect(article_data)

    return parser_data_collector.result_dict

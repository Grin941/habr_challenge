import argparse
import requests
import bs4
import collections


class Selector:

    SELECTOR_PARSE_SIG = collections.namedtuple(
        'SELECTOR_PARSE_SIG', ['name', 'css_kwargs']
    )

    def __init__(self, selector, class_=None, id_=None):
        self.name = selector
        self.class_ = class_
        self.id_ = id_

    def to_bs4_parse_signature(self):
        return self.SELECTOR_PARSE_SIG(
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
            'article_publication_date': Selector(
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
                '"{selector_name}" selector not defined for {site_url}'.format(
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

    def _get_selector(self, selector_name):
        selector = getattr(self._site_config, selector_name)
        return selector.to_bs4_parse_signature()

    def crawl(self, pages=1):
        articles_list_url = self._site_config.articles_list_url
        article_selector = self._get_selector('article')
        article_title_selector = self._get_selector('article_title')
        article_publication_date_selector = self._get_selector(
            'article_publication_date'
        )

        for page in range(1, pages + 1):
            articles_list = requests.get(
                articles_list_url.format(page=page),
                headers=self.REQUEST_HEADERS
            )
            soup = bs4.BeautifulSoup(articles_list.text, 'html.parser')
            for article_preview in soup.find_all(
                article_selector.name,
                **article_selector.css_kwargs
            ):
                article_publication_date = article_preview.find(
                    article_publication_date_selector.name,
                    **article_publication_date_selector.css_kwargs
                ).text
                article_title = article_preview.find(
                    article_title_selector.name,
                    **article_title_selector.css_kwargs
                ).text
                print(article_title, article_publication_date)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Print 3 most popular nouns.'
    )
    parser.add_argument(
        '--pages', type=int, default=10,
        help="""How many feed payges do you like to parse
                (default: %(default)s)?"""
    )
    args = parser.parse_args()

    Crawler('habr').crawl(pages=args.pages)

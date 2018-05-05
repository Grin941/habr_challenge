import collections


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
                '"{selector_name}" not defined in {site_url} config'.format(
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

import collections


class Selector:
    """Represent the rules how a web element may be found.

    Attributes:
        name (str): selector name.
            Example: 'span', 'div', ...
        class_ (str or None): class identifying a web element.
        id_ (str or None): id identifying a web element.

    """

    SELECTOR_PARSE_SIGNATURE = collections.namedtuple(
        'SELECTOR_PARSE_SIGNATURE', ['name', 'css_kwargs']
    )

    def __init__(self, selector, class_=None, id_=None):
        self.name = selector
        self.class_ = class_
        self.id_ = id_

    def to_bs4_parse_signature(self):
        """Return Selector in a bs4 usable representation.

        Returns:
            collections.namedtuple(str, dict)

        """
        return self.SELECTOR_PARSE_SIGNATURE(
            self.name,
            {
                'class_': self.class_,
                'id': self.id_,
            }
        )


class SiteConfig:
    """Declare site crawling configuration.

    Attributes:
        _site_config (dict)

    """

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
        """
        Args:
            site_name (string): name of the site to get config for.

        """
        self._site_config = self._get_site_config(site_name)

    def __getattr__(self, selector_name):
        """Get config values by keys.

        Args:
            selector_name (str): key to get config value upon.

        Returns:
            (dict value): selector representation.

        Raises:
            AttributeError: selector is not defined in a config,
                key does not exist.

        """
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
        """There may be many different sites which its own configs.
        Get the one by site name.

        Args:
            site_name (str): site name to get config for.

        Returns:
            (dict): specific site config.

        Raises:
            Exception: site config is not defined,
                key does not exist.

        """
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
        """Return article list url to parse.
        """
        return '{url}{pagination}'.format(
            url=self._site_config['url'],
            pagination=self._site_config.get('pagination', '')
        )

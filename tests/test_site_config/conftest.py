import pytest

from habr_challenge.site_config import Selector, SiteConfig


@pytest.fixture(scope="module")
def selector():
    return Selector('div', class_='test', id_='me')


@pytest.fixture(scope="module")
def site_config():
    SiteConfig.SITE_CONFIG['test'] = {
        'url': 'http://test.com/',
        'pagination': 'pages{page}/',
        'div': Selector('div', class_='test_me'),
    }
    return SiteConfig('test')

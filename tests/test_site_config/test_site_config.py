import pytest

from habr_challenge.site_config import Selector, SiteConfig


def test_selector_to_bs4_parse_signature(selector):
    selector_parse_signature = selector.to_bs4_parse_signature()
    assert selector_parse_signature.name == selector.name
    assert selector_parse_signature.css_kwargs == {
        'class_': selector.class_,
        'id': selector.id_,
    }


def test_site_config_getattr_to_get_selector(site_config):
    # Selector declared in the config
    assert site_config.div == Selector('div', class_='test_me')

    # Selector is not defined in the config
    with pytest.raises(AttributeError):
        site_config.span


def test_get_site_config_by_name():
    # Method raises KeyError if config not found by site name
    with pytest.raises(KeyError):
        SiteConfig._get_site_config('NOT_EXIST')


def test_article_list_url_property(site_config):
    assert site_config.articles_list_url == \
        'http://test.com/pages{page}/'

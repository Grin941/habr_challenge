import argparse

from habr_challenge import \
    SiteConfig, \
    ReportGenerator, \
    crawler, \
    parser


def parse_user_settings():
    parser = argparse.ArgumentParser(
        description='Print 3 most popular nouns from Habr feed article titles.'
    )
    parser.add_argument(
        '--pages', type=int, default=10,
        help="""How many feed pages do you like to parse
                (default: %(default)s)?"""
    )
    parser.add_argument(
        '--show-progress', action='store_false',
        help='do you want to see progress bar?'
    )
    return parser.parse_args()


def main():
    user_settings = parse_user_settings()
    assert user_settings.pages > 0, "Please pass --pages > 0"

    site_config = SiteConfig('habr')
    articles_list_pagination_gen = crawler.crawl(
        site_config, user_settings
    )
    articles_data = parser.parse(
        articles_list_pagination_gen, site_config, user_settings
    )
    ReportGenerator(articles_data).print_report()


if __name__ == '__main__':
    main()

import argparse

import habr_challenge as hc


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

    site_config = hc.SiteConfig('habr')
    articles_list_pagination_gen = hc.Crawler(
        site_config, user_settings
    ).crawl()
    articles_data = hc.Parser(
        site_config, user_settings
    ).parse(articles_list_pagination_gen)
    hc.ReportGenerator(articles_data).print_report()


if __name__ == '__main__':
    main()

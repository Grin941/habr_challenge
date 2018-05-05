# -*- coding: utf-8 -*-
import argparse

from habr_challenge.crawler import Crawler
from habr_challenge.report_generator import ReportGenerator


if __name__ == '__main__':
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
    user_settings = parser.parse_args()
    assert user_settings.pages > 0, "Please pass --pages > 0"

    articles_data = Crawler('habr').crawl(user_settings)
    ReportGenerator(articles_data).print_report()

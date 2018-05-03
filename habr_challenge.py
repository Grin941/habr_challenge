import argparse
import requests
import bs4


class Selector:
    def __init__(self, selector, class_=None, id_=None):
        self.selector = selector
        self.class_ = class_
        self.id_ = id_

    def to_bs4(self):
        return self.selector, {
            'class_': self.class_,
            'id_': self.id_,
        }


HabrConfig = {
    'url': 'https://habr.com/all/',
    'pagination': 'page{page}/',
    'article': 'article class="post post_preview"',
    'article_publication_date': 'span class="post__time"',
    'article_header': 'a class="post__title_link"',
}


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

    articles_list_request_url = '{url}{pagination}'.format(
        url=HabrConfig['url'], pagination=HabrConfig['pagination']
    )
    for page in range(1, args.pages + 1):
        # TODO: Heder User-Agent
        articles_list = requests.get(
            articles_list_request_url.format(page=page)
        )

        soup = bs4.BeautifulSoup(articles_list.text, 'html.parser')
        for article_preview in soup.find_all(
            'article', class_='post post_preview'
        ):
            article_publication_date = article_preview.find(
                'span', class_='post__time'
            ).text
            article_header = article_preview.find(
                'a', class_='post__title_link'
            ).text
            print(article_header, article_publication_date)

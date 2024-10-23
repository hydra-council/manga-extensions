from enum import Enum

import requests
from bs4 import BeautifulSoup

###########################################################################################################################################################################################################################
###########################################################################################################################################################################################################################
###########################################################################################################################################################################################################################
# book metadata

BOOK_IMAGE_SELECTOR = 'body > div.body-site > div.container.container-main > div.container-main-left > div.panel-story-info > div.story-info-left > span.info-image > img'


def get_book_image(document: BeautifulSoup):
    img = document.select_one(BOOK_IMAGE_SELECTOR)
    return img.get("src")


TITLE_SELECTOR = 'body > div.body-site > div.container.container-main > div.container-main-left > div.panel-story-info > div.story-info-right > h1'
ALTERNATE_TITLE_SELECTOR = 'body > div.body-site > div.container.container-main > div.container-main-left > div.panel-story-info > div.story-info-right > table > tbody > tr:nth-child(1) > td.table-value > h2'


def get_title(document: BeautifulSoup):
    select = document.select_one(TITLE_SELECTOR)
    alt_select = document.select_one(ALTERNATE_TITLE_SELECTOR)
    return select.text.strip(), alt_select.text.strip().split(';')


BOOK_STATUS_SELECTOR = 'body > div.body-site > div.container.container-main > div.container-main-left > div.panel-story-info > div.story-info-right > table > tbody > tr:nth-child(3) > td.table-value'


def get_status(document: BeautifulSoup):
    select = document.select_one(BOOK_STATUS_SELECTOR)
    return select.text.strip()


GENRE_SELECTOR = 'body > div.body-site > div.container.container-main > div.container-main-left > div.panel-story-info > div.story-info-right > table > tbody > tr:nth-child(4) > td.table-value'


def get_genres(document: BeautifulSoup):
    genres = []
    select = document.select_one(GENRE_SELECTOR)
    for genre in select.select('.a-h'):
        genres.append(genre.text.strip())
    return genres


DESCRIPTION_SELECTOR = '#panel-story-info-description'


def get_description(document: BeautifulSoup):
    select = document.select_one(DESCRIPTION_SELECTOR)
    tmp = select.text.strip().lstrip('Description').replace('\n', '').strip()
    return tmp.lstrip(':')


CHAPTER_LIST_SELECTOR = 'body > div.body-site > div.container.container-main > div.container-main-left > div.panel-story-chapter-list > ul'


def get_chapters(document: BeautifulSoup):
    chapters = []
    for element in document.select_one(CHAPTER_LIST_SELECTOR).select('ul .a-h'):
        link = element.find('a')
        if link:
            date_released = element.select_one('.chapter-time').get('title').strip()
            href = link.get('href')
            chapter = link.text.strip()
            chapters.append({'name': chapter, 'link': href, 'date': date_released})
    return chapters


# example manga-uh998064
def get_book_metadata(book_url):
    req = requests.get(book_url)
    soup = BeautifulSoup(req.text, features="html.parser")

    title, alt_title = get_title(soup)
    image = get_book_image(soup)
    status = get_status(soup)
    genres = get_genres(soup)
    description = get_description(soup)
    chapters = get_chapters(soup)

    return {
        'title': title,
        'alt_title': alt_title,
        'image': image,
        'status': status,
        'genres': genres,
        'description': description,
        'chapters': chapters,
    }


########################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################
###########################################################################################################################################################################################################################
# chapter selector

CHAPTER_SELECTOR = 'body > div.body-site > div.container-chapter-reader'


def get_chapter_images(chapter_link):
    all_links = []
    req = requests.get(chapter_link)
    soup = BeautifulSoup(req.text, features="html.parser")
    elem = soup.select_one(CHAPTER_SELECTOR)
    all_img = elem.find_all('img')
    for img in all_img:
        link = img.get('src')
        all_links.append(link)

    headers = {
        "Referer": 'https://chapmanganato.to/'
    }

    return all_links, headers


###########################################################################################################################################################################################################################
###########################################################################################################################################################################################################################
###########################################################################################################################################################################################################################
# search page parser
def parse_results_page(document: BeautifulSoup, selector_class):
    story_items = document.find_all(class_=selector_class)

    search_results = []
    # Loop through the found items
    for item in story_items:
        book_link = (item.find('a')).get('href')
        img = (item.find('img')).get('src')
        book_title = item.find('h3').text.strip()
        search_results.append({
            'title': book_title,
            'link': book_link,
            'img': img,
        })

    return search_results


def search_page(search_query, page=1):
    url = f'https://manganato.com/search/story/{search_query}/?page={page}'
    req = requests.get(url)
    soup = BeautifulSoup(req.text, features="html.parser")
    results = parse_results_page(soup, 'search-story-item')
    return results


class Status(Enum):
    LATEST = 'p'
    HOT = 'a'
    POPULAR = 'i'


# future stuff add genres
def home_page(filter_books: Status = Status.POPULAR, page=1):
    url = ''
    if filter_books == Status.POPULAR:
        url = f'https://manganato.com/genre-all/{page}'
    elif filter_books == Status.HOT:
        url = f'https://manganato.com/genre-all/{page}?type=topview'
    elif filter_books == Status.LATEST:
        url = f'https://manganato.com/genre-all/{page}?type=newest'
    assert (url != '')

    req = requests.get(url)
    soup = BeautifulSoup(req.text, features="html.parser")
    results = parse_results_page(soup, 'content-genres-item')
    return results


if __name__ == '__main__':
    # search_page('isekai')
    # home_page(Status.LATEST)
    # get_chapter_images('https://chapmanganato.to/manga-ri994991/chapter-11')

    # get_book_metadata("https://chapmanganato.to/manga-ri994991/")
    pass
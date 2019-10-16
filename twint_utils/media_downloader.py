from pathlib import Path
from re import compile
from time import sleep
from urllib.parse import urlparse

import youtube_dl
from bs4 import BeautifulSoup
from requests import get


def get_soup(html):
    if html is not None:
        soup = BeautifulSoup(html, 'lxml')
        return soup
    else:
        return


def photo_downloader(urls, download_location):
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/74.0.3729.169 Safari/537.36'}
    for tweet in urls:
        try:
            result = get(tweet, headers)
        except Exception as e:
            continue
        if result.status_code is 200:
            content = result.content
            soup = get_soup(content)
            for link in soup.findAll('img', attrs={'src': compile("^https://pbs.twimg.com/media")}):
                photo_url = link['src']
                url_obj = urlparse(photo_url)
                file_name = url_obj.path.replace("/media/", "")
                path = str(Path(download_location, file_name))
                if not Path(path).is_file():
                    with open(path, "wb") as file:
                        file.write(get(photo_url).content)
        else:
            continue


def video_downloader(urls, download_location):
    for tweet in urls:
        try:
            download_path = str(Path(download_location, "%(id)s.%(ext)s"))
            ydl_opts = {
                "outtmpl": download_path,
                "quiet": True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([tweet, ])
        except Exception as e:
            continue
        if len(urls) > 200:
            sleep(2)


def sorter(tweets_obj):
    photo_urls = []
    video_urls = []
    for item in tweets_obj:
        url = "https://twitter.com/statuses/{0}".format(item.id)
        if item.photos:
            photo_urls.append(url)
        if item.video:
            video_urls.append(url)
    return photo_urls, video_urls


def get_photo_urls(tweets_obj):
    photo_urls = []
    for item in tweets_obj:
        url = "https://twitter.com/statuses/{0}".format(item.id)
        if item.photos:
            photo_urls.append(url)
    return photo_urls


def get_video_urls(tweets_obj):
    video_urls = []
    for item in tweets_obj:
        url = "https://twitter.com/statuses/{0}".format(item.id)
        if item.video:
            video_urls.append(url)
    return video_urls


def download_photos(tweets_obj, download_location):
    photo_urls = get_photo_urls(tweets_obj)
    photo_downloader(photo_urls, download_location)


def download_videos(tweets_obj, download_location):
    video_urls = get_video_urls(tweets_obj)
    video_downloader(video_urls, download_location)

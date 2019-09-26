# WIP

import os
import signal
import sys
from pathlib import Path
from pickle import dump
from pickle import load
from queue import Queue
from re import compile
from threading import Thread
from time import sleep
from urllib.parse import urlparse

import requests
import twint
import youtube_dl
from blessings import Terminal
from bs4 import BeautifulSoup
from progressbar import ProgressBar

working_dir = os.getcwd()
term = Terminal()


class Writer(object):
    def __init__(self, location):
        self.location = location

    def write(self, string):
        with term.location(*self.location):
            print(string)

    def flush(self):
        pass


def write_to_screen(x_pos, y_pos, string):
    location = (x_pos, y_pos)
    w = Writer(location)
    w.write(string)


class Twitter(object):
    def __init__(self, usernames, location, get_videos=True, get_photos=True,
                 ignore_errors=True, sleep_timer=1, output=True):
        self.get_photos = get_photos
        self.get_videos = get_videos
        self.queue = Queue()
        self.crawling = True
        self.usernames = usernames
        self.ignore_errors = ignore_errors
        self.download_folder = Path(location, "twitter")
        self.writer = Writer((0, 4))
        self.output = output
        self.sleeptimer = sleep_timer

    @staticmethod
    def get_soup(html):
        if html is not None:
            soup = BeautifulSoup(html, 'lxml')
            return soup
        else:
            return

    def get_tweets(self, target):
        c = twint.Config()
        c.Username = target
        c.Resume = str(Path(working_dir, "resume", "{0}_history_ids.txt".format(target)))
        c.Store_object = True
        c.Hide_output = True
        c.Media = True
        if self.output is True:
            write_to_screen(0, 0, "Twitter crawler:")
            write_to_screen(0, 1, "crawling {0}".format(target))
        twint.run.Search(c)
        tweets = twint.output.tweets_list

        photo_url = []
        video_url = []
        for item in tweets:
            url = "https://twitter.com/statuses/{0}".format(item.id)
            if item.photos:
                photo_url.append(url)
            if item.video:
                video_url.append(url)

        tweets.clear()

        return target, photo_url, video_url

    def download_photos(self, target, urls):
        if urls:
            location = Path(self.download_folder, target)
            photo_location = Path(location, "photos")
            if not location.is_dir():
                location.mkdir()
            if not photo_location.is_dir():
                photo_location.mkdir()
            prefix_msg = "{0}: Downloading photos ".format(target)
            with ProgressBar(max_value=len(urls), fd=self.writer, prefix=prefix_msg) as pbar:
                current_len = 0
                headers = {
                    'User-Agent':
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/74.0.3729.169 Safari/537.36'}
                for tweet in urls:
                    result = requests.get(tweet, headers)
                    if result.status_code is 200:
                        content = result.content
                        soup = self.get_soup(content)
                        for link in soup.findAll('img', attrs={'src': compile("^https://pbs.twimg.com/media")}):
                            photo_url = link['src']
                            url_obj = urlparse(photo_url)
                            file_name = url_obj.path.replace("/media/", "")
                            path = str(Path(photo_location, file_name))
                            if not os.path.isfile(path):
                                with open(path, "wb") as file:
                                    file.write(requests.get(photo_url).content)
                    else:
                        print("Error requesting the webpage: {0}".format(result.status_code))
                        if self.ignore_errors is False:
                            exit(1)
                    if self.output is True:
                        current_len += 1
                        pbar.update(current_len)
                        write_to_screen(0, 3, "Twitter downloader:")

    def download_videos(self, target, urls):
        if urls:
            location = Path(self.download_folder, target)
            video_location = Path(location, "videos")
            if not location.is_dir():
                location.mkdir()
            if not video_location.is_dir():
                video_location.mkdir()
            prefix_msg = "{0}: Downloading videos ".format(target)
            with ProgressBar(max_value=len(urls), fd=self.writer, prefix=prefix_msg) as pbar:
                current_len = 0
                for tweet in urls:
                    try:
                        download_path = str(Path(video_location, "%(id)s.%(ext)s"))
                        ydl_opts = {"outtmpl": download_path, "quiet": True}
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([tweet, ])
                    except youtube_dl.utils.DownloadError as y:
                        print(y)
                        if self.ignore_errors is False:
                            exit(1)
                    if self.output is True:
                        current_len += 1
                        pbar.update(current_len)
                        write_to_screen(0, 3, "Twitter downloader:")
                    if len(urls) > 200:
                        sleep(self.sleeptimer)

    def sigterm_handler(self, signal, frame):
        self.dump_queue()
        sys.exit(0)

    def dump_queue(self):
        with open("queue", "w") as file:
            dump(self.queue, file, protocol=4, fix_imports=False)

    def load_queue(self):
        with open("queue", "r") as file:
            self.queue = load(file, fix_imports=False, encoding="bytes")

    def downloader(self):
        if not self.download_folder.is_dir():
            self.download_folder.mkdir()
        while not self.queue.empty() or self.crawling:
            tweets = self.queue.get()
            if self.get_photos is True:
                self.download_photos(tweets[0], tweets[1])
            if self.get_videos is True:
                self.download_videos(tweets[0], tweets[2])
        if self.output is True:
            write_to_screen(0, 4, "Done downloading!")

    def crawler(self):
        if not os.path.exists("resume"):
            os.mkdir("resume")
        for username in self.usernames:
            tweets = self.get_tweets(username)
            self.queue.put(tweets)
        self.crawling = False
        if self.output is True:
            write_to_screen(0, 1, "Done crawling!")

    def start(self):
        os.system("clear")
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        Thread(target=self.downloader).start()
        self.crawler()

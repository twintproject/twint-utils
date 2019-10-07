import logging
import signal
import sys
from os import getcwd
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
from bs4 import BeautifulSoup

working_dir = getcwd()


class Twitter(object):
    def __init__(self, usernames, location, get_videos=True, keep_log=True,
                 ignore_errors=True, get_photos=True, logger=""):
        self.get_photos = get_photos
        self.get_videos = get_videos
        self.queue = Queue()
        self.crawling = True
        self.usernames = usernames
        self.ignore_errors = ignore_errors
        self.download_folder = Path(location, "twitter")
        self.logging = keep_log
        if self.logging:
            self.logger = logging.getLogger(logger)

    @staticmethod
    def get_soup(html):
        if html is not None:
            soup = BeautifulSoup(html, 'lxml')
            return soup
        else:
            return

    @staticmethod
    def get_tweets(target):
        c = twint.Config()
        c.Username = target
        c.Resume = str(Path(working_dir, "resume", "{0}_history_ids.txt".format(target)))
        c.Store_object = True
        c.Hide_output = True
        c.Media = True
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
            headers = {
                'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/74.0.3729.169 Safari/537.36'}
            for tweet in urls:
                try:
                    result = requests.get(tweet, headers)
                except Exception as e:
                    self.logger.error(e)
                    if not self.ignore_errors:
                        exit(1)
                    continue
                if result.status_code is 200:
                    content = result.content
                    soup = self.get_soup(content)
                    for link in soup.findAll('img', attrs={'src': compile("^https://pbs.twimg.com/media")}):
                        photo_url = link['src']
                        url_obj = urlparse(photo_url)
                        file_name = url_obj.path.replace("/media/", "")
                        path = str(Path(photo_location, file_name))
                        if not Path(path).is_file():
                            with open(path, "wb") as file:
                                file.write(requests.get(photo_url).content)
                else:
                    self.logger.error("Error requesting the webpage: {0}".format(result.status_code))
                    if not self.ignore_errors:
                        exit(1)

    def download_videos(self, target, urls):
        if urls:
            location = Path(self.download_folder, target)
            video_location = Path(location, "videos")
            if not location.is_dir():
                location.mkdir()
            if not video_location.is_dir():
                video_location.mkdir()
            for tweet in urls:
                try:
                    download_path = str(Path(video_location, "%(id)s.%(ext)s"))
                    ydl_opts = {
                        "outtmpl": download_path,
                        "quiet": True,
                        "logger": self.logger,
                        "ignoreerrors:": self.ignore_errors
                    }
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([tweet, ])
                except Exception as y:
                    self.logger.error(y)
                    if not self.ignore_errors:
                        exit(1)
                if len(urls) > 200:
                    sleep(2)

    def sigterm_handler(self):
        """
        possible parameters: signal, frame
        """
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
            if self.logging:
                if not tweets[1] and not tweets[2]:
                    pass
                elif not tweets[1] and tweets[2]:
                    self.logger.info("{0}: downloading {1} videos".format(tweets[0], len(tweets[2])))
                elif not tweets[2] and tweets[1]:
                    self.logger.info("{0}: downloading {1} photos".format(tweets[0], len(tweets[1])))
                else:
                    self.logger.info(
                        "{0}: downloading {1} photos and {2} videos".format(tweets[0], len(tweets[1]), len(tweets[2])))
            if self.get_photos:
                self.download_photos(tweets[0], tweets[1])
                if self.logging:
                    if not tweets[1]:
                        pass
                    else:
                        self.logger.info("{0}: photo download complete!".format(tweets[0]))
            if self.get_videos:
                self.download_videos(tweets[0], tweets[2])
                if self.logging:
                    if not tweets[2]:
                        pass
                    else:
                        self.logger.info("{0}: video download complete!".format(tweets[0]))
            if self.queue.qsize() > 0:
                self.logger.info("{0} items left in the download queue".format(self.queue.qsize()))
        if self.logging:
            self.logger.info("Done downloading!")

    def crawler(self):
        resume_location = Path(working_dir, "resume")
        if not resume_location.is_dir():
            resume_location.mkdir()
        counter = len(self.usernames)
        for username in self.usernames:
            if self.logging:
                self.logger.info("crawling {0}".format(username))
            tweets = self.get_tweets(username)
            self.queue.put(tweets)
            counter -= 1
            if self.logging:
                self.logger.info("{0} items left in crawler queue".format(counter))
        self.crawling = False
        if self.logging:
            self.logger.info("Done crawling!")

    def start(self):
        if self.logging:
            self.logger.info("Starting twitter module with a queue size of {0}".format(len(self.usernames)))
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        Thread(target=self.downloader).start()
        self.crawler()


def worker(usernames, location):
    t = Twitter(usernames=usernames, location=location, logger="SMDL.Twitter")
    t.start()

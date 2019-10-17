import twint

from twint_utils.tweets import media_downloader

account = "twitter"


def get_tweets(target):
    c = twint.Config()
    c.Username = target
    c.Store_object = True
    c.Hide_output = False
    c.Media = True
    twint.run.Search(c)
    return twint.output.tweets_list


if __name__ == "__main__":
    # media_downloader.download_photos(get_tweets(account), ".")
    media_downloader.download_videos(get_tweets(account), ".")

# twint-utils
These are utilizations of Twint. Please check out our collaboration guidelines to contribute to these.

## Mutuals Detector
Mufos.py uses Twint to detect a given seed accounts mutual followers. It can be incorporated into other more elaborate pipelines for social networks or millieu detection. It is too slow to be useful right now for accounts with massive follower/Following. Here is a [hosted version](https://colab.research.google.com/drive/1AOXQxkOWbq7KEHWVBRiOrYhTOSg3QTqq) that you can open in playground mode to play with.

## Media Downloader
accepts twint.output.tweets_list as an argument. 
```python
from twint_utils import media_downloader

tweets = twint.output.tweets_list                              
location = "./"
media_downloader.download_photos(get_tweets(tweets), location)
media_downloader.download_videos(get_tweets(tweets), location)
```

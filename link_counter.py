#This code takes a list of twitter usernames, iterates over them to find tweets where they shared links,
#and then sums up the base URLs of everyones links combined and turns it into a matplotlib graph.
#I put a bunch of code documentation in and it really will help you use this.
#the code does take a bit to run depending on your tweet limit and how many accounts you pull

import pandas as pd
import re

from urllib.parse import urlparse
from urllib.request import urlopen

import csv

import twint #you may need to install this first if you haven't!

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

import csv
import os

#this prevents async problems/ runtime errors
#https://markhneedham.com/blog/2019/05/10/jupyter-runtimeerror-this-event-loop-is-already-running/
import nest_asyncio
nest_asyncio.apply()

#put accounts in between the brackets, comma seperated, without the @sign. ie ["jack", "realDonaldtrump", "Blacksocialists"]
sourceAccounts= ["PUT YOUR ACCOUNTS HERE" , "DIRECTIONS ABOVE"]



if not os.path.isfile('all_urls.csv'):
    with open('all_urls.csv', 'wb') as f:
        pass

for username in sourceAccounts:
    c = twint.Config()
    print("pulling tweets for " + str(username) + "...")
    c.Username = username
    c.Hide_output = True #makes the command line less noisy
    c.Limit = 500 #maximum number of tweets to pull per account
    c.Store_object = True
    #only selects tweets that have links
    c.Links = "include"


    baseURLs = []
    twint.run.Search(c)
    tweets = twint.output.tweets_list
    for tweet in tweets:
        #urls is a class in the twint tweet objects to see all classes: dir(tweet)
        for URL in tweet.urls:

            parsed_uri = urlparse(URL)
            baseURL = str('{uri.netloc}'.format(uri=parsed_uri)) #gets the base URL
            if baseURL[:7] == 'twitter': #ignores RTs as links
                pass
            elif baseURL[:4] == "www.": #strips www for a e s t h e t i c
                baseURLs.append([username, baseURL[4:]])
            else:
                baseURLs.append([username, baseURL])


    # I added this in case it gets slow in pulling the list so you can stop at any point and then just
    #edit your sourceAccounts list to get rid of the one's you've already done.
    with open('all_urls.csv','a', newline='') as f:
        for baseURL in baseURLs:
            writer = csv.writer(f)
            writer.writerow(baseURL)



all_urls = pd.read_csv('all_urls.csv', names = ['username','URL'])

print("total tweets pulled: " + str(len(all_urls)))


labels = ['Base URL', 'Frequency']
countedURLs = all_urls['URL'].value_counts()
countedURLs.to_csv('countedURLs.csv')

top_urls = countedURLs.iloc[:10]
top_urls = top_urls[::-1] #makes it descending

y_pos = np.arange(len(top_urls))
performance = top_urls
print(performance)
baseURLs =  top_urls.index
print(baseURLs)
plt.barh(y_pos, performance, align='center', alpha=0.5)
plt.yticks(y_pos, baseURLs)
plt.xlabel('Frequency of Links')
plt.title('Most Frequent External Links of all Handles Tested')

plt.show()

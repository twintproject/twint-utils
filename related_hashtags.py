# Related Hashtags Detector

#This notebook finds other hashtags that are most commonly found with a given hashtag
#and creates a bar graph of them. This can be used to track how disinformation campaigns
#or stories are happening. Be patient. It takes a bit to pull the tweets especially
#if you have a high limit.

seed_hashtag = "#Elections2019"   #change this to whatever seed hashtag you want.
limit = 500   #This changes the number of tweets to pull

import twint #may need to install first
import heapq
import matplotlib.pyplot as plt


print("pulling tweets.... please wait...espera por favor...")
c = twint.Config()
c.Hide_output = True #makes the command line less noisy
c.Limit = limit #maximum number of tweets to pull per account
c.Store_object = True
c.Search = seed_hashtag
twint.run.Search(c)
tweets = twint.output.tweets_list

#counts occurrence of hashtags
hashtags_dict = {}
for tweet in tweets:
  for hashtag in tweet.hashtags:
    if hashtag in hashtags_dict:
      hashtags_dict[hashtag] += 1
    else:
      hashtags_dict[hashtag] = 1

del hashtags_dict[seed_hashtag] #gets rid of seed hashtag
top_hashtags = heapq.nlargest(10, hashtags_dict, key=hashtags_dict.get) #gets highest hashtags

#makes dictionary of just highest ones
hashtags_ranked = {}
for hashtag in top_hashtags:
  hashtags_ranked[hashtag] = hashtags_dict[hashtag]

print("There will now be a pop-up with the bar chart.")
plt.barh(range(len(hashtags_ranked)), list(hashtags_ranked.values()), align='center', color = 'maroon')
plt.yticks(range(len(hashtags_ranked)), list(hashtags_ranked.keys()))
plt.gca().invert_yaxis() #just to have the highest bar at the top
plt.title("Most Related Hashtags to " + seed_hashtag)
plt.show()

#this function detects mutual followers for a seed twitter account and
#can be incporated into other more elaborate pipelines for social networks or millieu detection.
#this is too slow to be useful right now for accounts with massive follower/Following
#here is a hosted version that you can open in playground mode to play with
#https://colab.research.google.com/drive/1AOXQxkOWbq7KEHWVBRiOrYhTOSg3QTqq

#install twint: pip3 install twint
#write seed username below
import twint

username = "CHOOSE TARGET USERNAME HERE NO @ SIGN"

def mutuals(username):
  c = twint.Config()
  c.Hide_output = True
  c.Username = username
  c.Pandas = True
  print("finding followers...(ignore errors)")

  twint.run.Followers(c)

  Followers_df = twint.storage.panda.Follow_df
  list_of_followers = Followers_df['followers'][username]
  print("finding following...(ignore errors)")

  c.Pandas = True
  twint.run.Following(c)

  Following_df = twint.storage.panda.Follow_df
  list_of_following = Following_df['following'][username]
  print("finding mutuals...")
  def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

  mufos = intersection(list_of_followers, list_of_following)
  return mufos

mufos = mutuals(username)

print(str(username)+ " account has " + str(len(mufos)) + " mutual followers. Here they are:")
print(mufos)

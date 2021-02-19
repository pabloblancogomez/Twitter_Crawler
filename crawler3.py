import tweepy
import csv
import time
from collections import Counter
from collections import defaultdict
import nltk
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from nltk import WordNetLemmatizer
from nltk.tokenize.toktok import ToktokTokenizer
#import numpy as np
#import pandas as pd
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

toktok=ToktokTokenizer()

def get_hashtag(filename):
    hashtag = []
    with open(filename, mode='r') as hashtag_file:
        for a_hashtag in hashtag_file:
            hashtag.append(a_hashtag.split()[0])
    return hashtag

consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''
tweetsPerQry = 100
maxTweets = 1000000
hashtag = get_hashtag('/home/pi/Twitter/hashtags.txt')  # read hashtags

authentication = tweepy.OAuthHandler(consumer_key, consumer_secret)
authentication.set_access_token(access_token, access_secret)
api = tweepy.API(authentication, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
maxId = -1
tweetCount = 0

with open('/home/pi/Twitter/registro_Tweets.csv', "w", newline='') as csv_file:
	csv_add = csv.writer(csv_file, dialect='unix', delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	csv_add.writerow(['created_at', 'hashtag', 'id', 'text'])
	#for hasht in hashtag:
	while tweetCount < maxTweets:
		#print(hasht)
		if(maxId <= 0):
			for hasht in hashtag:
				newTweets = api.search(q=hasht, count=tweetsPerQry, result_type="recent", tweet_mode="extended")
				for tweet in newTweets:
					print(tweet.full_text.encode('utf-8'))	
					char1 = 'Status(full_text='
					char2 = ', truncated'
					mystr =tweet.full_text
					csv_add.writerow([tweet.created_at, hasht, tweet.id, mystr[mystr.find(char1)+1 : mystr.find(char2)]])
					print("#####")
		else:
			for hasht in hashtag:
				newTweets = api.search(q=hasht, count=tweetsPerQry, max_id=str(maxId - 1), result_type="recent", tweet_mode="extended")
				for tweet in newTweets:
					print(tweet.full_text.encode('utf-8'))
					char1 = 'Status(full_text='
					char2 = ', truncated'
					mystr =tweet.full_text.encode('utf-8')
					csv_add.writerow([tweet.created_at, hasht, tweet.id, mystr[mystr.find(char1)+1 : mystr.find(char2)]])
					print("#####")
		if not newTweets:
			print("No hay Tweets nuevos")
			break
		
		tweetCount += len(newTweets)	
		maxId = newTweets[-1].id
csv_file.close()
time.sleep(5)
print('Extrayendo palabras clave del registro de Tweets')
words= []
with open('/home/pi/Twitter/registro_Tweets.csv','r') as csvfile:
	reader = csv.reader(csvfile,delimiter='|')
	next(reader)
	for row in reader:
		csvwords = row[3].split(" ")
		tokens=toktok.tokenize(csvwords)
		# Remove the punctuations
		tokens=[word for word in tokens if word.isalpha()]
		# Lower the tokens
		tokens=[word.lower() for word in tokens]
		# Remove stopword
		tokens=[word for word in tokens if not word in stopwords.words("spanish")]
		# Lemmatize
		lemma=WordNetLemmatizer()
		tokens=[lemma.lemmatize(word, pos = "v") for word in tokens]
		tokens=[lemma.lemmatize(word, pos = "n") for word in tokens]
		for i in tokens:
			words.append(i)
print('Guardando palabras clave en archivo csv')
words2= []
for i in words:	
	if i not in words2:
		words2.append(i)
words_counted= []
for i in words2:		
	x = words.count(i)
	words_counted.append((i,x))
#write this to a csv file
with open('/home/pi/Twitter/frecuencia_palabras.csv', 'w', newline='') as f:
	writer = csv.writer(f)	
	writer.writerows(words_counted)
print('Generando nube de palabras')
with open('/home/pi/Twitter/registro_Tweets.csv','r') as csvfile:
	df = csv.reader(csvfile,delimiter='|')
	for row in reader:
		text = row[3]
	# lower max_font_size, change the maximum number of word and lighten the background:
	wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text)
	plt.figure()
	plt.imshow(wordcloud, interpolation="bilinear")
	plt.axis("off")
	plt.show()
	# Save the image in the img folder:
	wordcloud.to_file("/home/pi/Twitter/img/Tweetcloud_plot.png")
print('Tarea finalizada')

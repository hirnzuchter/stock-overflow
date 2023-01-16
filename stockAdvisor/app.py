import math
import numpy as np 
import pandas as pd 
import requests
import os
import json
import random
from datetime import datetime
import time
import matplotlib
matplotlib.use('WebAgg')
import matplotlib.pyplot as plt,mpld3
import tweepy
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, subjectivity
from nltk.classify import NaiveBayesClassifier
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import threading
import yfinance as yf 
from cleanco import basename

'''For backtesting, take the user's favorited assets, and load only the data for these.
This would mean, of course, that the user may only incorporate these in the strategy to be
backtested. However, we are assuming that the user already tracks the assets with which
they plan to center strategies around. For expected strategy return, there are two values:
one for which we have made the ceteris paribus assumption, and the other stemming from
averaging the results of Monte Carlo simulations. Include all of our rebalancing strategies
as presets for the backtesting, naïve, and Monte Carlo methods.'''

#We've registered lots of emails with AlphaVantage to get these keys
keys = [
    'WWF2YGNBXK210E9A', 
    '3BJBPEWCJ3I05F0Q', 
    '495VY7LZMRER61EG', 
    'P4FVS1NXV78E3QWS', 
    'FIH76AALZDALNEYK',
    'GSSKOADRRQ3NFR23',
    'H7ROJYZACU81ZE53',
    'THODG184BTEDCGEJ',
    '0XHYPMSWV1Z09N6I',
    'OGYMYNYOT42R0IMC',
    'UJBHAKP3O2OGJ9JA',
]

twitter_api_key = "9ynDMEqpA30ASFyVF6UMrm0Dm"
twitter_secret_api_key = "EJQZosqpLehGh7jilj72wvLCDO70FQiLfnC9GhXm939voSh18Y"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAB3VlAEAAAAAone1Vhobtx1lJzIHPrn8bpE89VU%3DZ9HqfieQFrRFMsYEiahJg0XHGA3lskbUhxZh7gGeYlvdRydJZ9"

'''Returns the probability density of a normal distribution given mean and standard deviation
at a point x'''
def normal_dist(x , mean , sd):
    prob_density = (np.pi*sd) * np.exp(-0.5*((x-mean)/sd)**2)
    return prob_density

'''Returns the contribution of all outcomes above 0 to the expected value'''
def pcm(dist, *args, **kwargs):
    mean = kwargs.get('mean', None)
    stdev = kwargs.get('stdev', None)
    area = 0
    step = 0.0001
    upper_limit = 1
    steps_in_one = 1/step
    num_steps = upper_limit*int(steps_in_one)
    if dist == normal_dist:
        for i in range(0, num_steps):
            area += (i*step)*normal_dist(i*step, mean, stdev)*step
    return area

'''Applies a softmax operation to an array'''
def softmax(array):
    total = 0
    for i in range(len(array)):
        array[i] = math.exp(array[i])
        total += array[i]
    array /= total
    return array

'''Used to randomize the key used in each request,
and to simplify the amount of code required for the get request.'''
def get(function, ticker):
    #AlphaVantage API Keys
    random.seed(datetime.now().timestamp())
    api_token = keys[random.randrange(0, len(keys))]
    api_url = f'https://www.alphavantage.co/query?function={function}&symbol={ticker}&apikey={api_token}'
    data = requests.get(api_url)
    if '5 calls per minute and 500 calls per day' in data.text:
        get(function, ticker)
    else:
        return data

'''Calculates the mean and standard deviation of an asset's last 30-Day's returns'''
def returns(ticker):
    temp = []
    temper = np.array([])
    function = 'TIME_SERIES_DAILY_ADJUSTED'
    request = get(function, ticker)
    while request == None:
            request = get(function, ticker)
    all_data = json.loads(request.text)
    # time series data accessed from endpoint
    data = all_data["Time Series (Daily)"]
    i = 0
    for date in data:
        if i > 30:
            break
        date = data[date]
        closing_val = float(date["4. close"])
        temp.append(closing_val)
        i+=1   
    for i in range(30, 0, -1):
        temper = np.append(temper, temp[i-1] - temp[i]) / temp[i]
    mean = np.mean(temper)
    stdev = np.std(temper)
    return [mean, stdev]

'''Returns graphs of the last 30 days' returns'''
def return_plot(ticker):
    function = 'TIME_SERIES_DAILY_ADJUSTED'
    temp = []
    request = get(function, ticker)
    while request == None:
            request = get(function, ticker)
    all_data = json.loads(request.text)
    # time series data accessed from endpoint
    data = all_data["Time Series (Daily)"]
    i = 0
    # Sums up the closing stock value of every day and divides by 30 to find the monthly average
    for date in data:
        if i >= 100:
            break
        date = data[date]
        temp.insert(0, float(date["4. close"]))
        i+=1    
    fig, ax = plt.subplots()
    plt.xlabel('The Last 100 Days')
    plt.ylabel('Closing Price($)')
    plt.title(ticker)
    plt.plot(temp)        
    return (mpld3.fig_to_html(fig, d3_url=None, mpld3_url=None, no_extras=False, template_type='general', figid=None, use_http=False))
    

'''Returns a portfolio based off of balancing the risk of each asset'''
def balance_risk(symbols, budget):
    out = np.array([])
    for symbol in symbols:
        [alpha, beta] = returns(symbol)
        if alpha / (beta)**2 < 0:
            out = np.append(out, 0)
        else:
            out = np.append(out, alpha / (beta)**2)
    out /= np.sum(out)
    out = { x:{"dollar_amount": round(budget*y, 2), "percentage_of_portfolio": round(100*y, 2)} for (x, y) in zip(symbols, out) }
    out = { "assets": out, "strategy": "Risk Allocation Strategy"}
    return out

'''Uses the thirty daily growth rates to normalize by
probability of daily returns being positive;
uses a normal distribution for probability;
note that lognormal is for price and normal is for returns'''
def expected_returns(symbols, budget):
    out = np.array([])
    for symbol in symbols:
        [alpha, beta] = returns(symbol)
        out = np.append(out, pcm(normal_dist, mean=alpha, stdev=beta))
    out /= np.sum(out)
    out = { x:{"dollar_amount": round(budget*y, 2), "percentage_of_portfolio": round(100*y, 2)} for (x, y) in zip(symbols, out) }
    out = { "assets": out, "strategy": "Expected Returns Strategy"}
    return out

'''
Fetches the general data specific to the parameter (ticker) that the user requests
Ticker is the stock symbol
Returns a json object with all data
Calculates the the 30 day moving average by accessing the data of a stock at the close time of each day
'''
def moving_average(ticker): 
    function = 'TIME_SERIES_DAILY_ADJUSTED'
    request = get(function, ticker)
    while request == None:
            request = get(function, ticker)
    all_data = json.loads(request.text)
    # time series data accessed from endpoint
    data = all_data["Time Series (Daily)"]
    i = 0
    total = 0.0
    # Sums up the closing stock value of every day and divides by 30 to find the monthly average
    for date in data:
        if i >= 30:
            break
        date = data[date]
        closing_val = float(date["4. close"])
        total += closing_val
        i+=1      
    return total/30.0

'''Returns the percent growth of the 30-Day moving average,
based off of last month's 30-Day moving average,
and today's 30-Day moving average'''
def momentum(ticker): 
    function = 'TIME_SERIES_DAILY_ADJUSTED'
    request = get(function, ticker)
    while request == None:
            request = get(function, ticker)
    all_data = json.loads(request.text)
    # time series data accessed from endpoint
    data = all_data["Time Series (Daily)"]
    i = 0
    total_new = 0.0
    total_old = 0.0
    # Sums up the closing stock value of every day and divides by 30 to find the monthly average
    for date in data:
        if i >= 60:
            break
        date = data[date]
        closing_val = float(date["4. close"])
        if i < 30:
            total_new += closing_val
        else:
            total_old += closing_val
        i+=1   
    return (total_new - total_old) / total_old

'''Returns a portfolio based off of assets percent returns, 
and then applies softmax to determine allocation'''
def momentum_strategy(symbols, budget):
    out = np.zeros(len(symbols))
    temp = np.array([])
    for symbol in symbols:
        temp = np.append(temp, momentum(symbol))
    out = softmax(temp*10)
    out = { x:{"dollar_amount": round(budget*y, 2), "percentage_of_portfolio": round(100*y, 2)} for (x, y) in zip(symbols, out) }
    out = { "assets": out, "strategy": "Momentum Investing Strategy"}
    return out

'''Returns data from the "quote" endpoint'''
def quote(symbols):
    function = 'GLOBAL_QUOTE'
    out = []
    for symbol in symbols:
        data = get(function, symbol)
        while request == None:
            request = get(function, ticker)
        data = data.json()
        out.append([symbol, data])
    return out

def result_bar(strategy):
    asset_name = strategy['assets'].keys()
    dollar_amount = [x for x in strategy['assets'].values()]
    for i in range(len(dollar_amount)):
        dollar_amount[i] = dollar_amount[i]['dollar_amount']
    fig = plt.figure()
    ax = pd.Series(dollar_amount).plot(kind="bar")
    ax.set_title("Dollar Amount by Asset")
    ax.set_ylabel("Dollar Amount($)")
    ax.set_xticklabels(asset_name)
    rects = ax.patches
    labels = [f'{x}: ${y}' for (x, y) in zip(asset_name, dollar_amount)]
    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2, height + 5, label, ha="center", va="bottom"
        )
    plt.bar(asset_name, dollar_amount, color ='maroon')
    return (mpld3.fig_to_html(fig, d3_url=None, mpld3_url=None, no_extras=False, template_type='general', figid=None, use_http=False))

def result_pie(strategy):
    asset_name = strategy['assets'].keys()
    percentage = [x for x in strategy['assets'].values()]
    explode = []
    for i in range(len(percentage)):
        percentage[i] = percentage[i]['percentage_of_portfolio']
        explode.append(0.05)
    fig, ax = plt.subplots()
    plt.axis('off')
    ax.set_title("Percentage of Portfolio by Asset")
    plt.pie(percentage, labels = asset_name, explode = explode, shadow = True, autopct='%1.0f%%', labeldistance=0.8)
    return (mpld3.fig_to_html(fig, d3_url=None, mpld3_url=None, no_extras=False, template_type='general', figid=None, use_http=False))

'''Loading Twitter Data'''
client = tweepy.Client(os.getenv("bearer_token"))
update_interval = 60.0
tweets_folder = "data/tweets"
companies = set()
company_ratings = {}
def load_companies():
    file = open("data/companies.txt", "rt")
    for company in file:
        companies.add(str(company).strip())
    file.close()
#TO-DO Make a service to run this function every interval
def refresh_data():
    file = open("data/stock_influencers.txt")
    for line in file:        
        user = client.get_user(username=str(line).strip())
        if user.data == None:
            continue
        userid = user.data.id
        thread = threading.Thread(target=write_data, args=(userid, str(line).strip()))
        thread.start()
    file.close()
def parse_data(influencer):
    file = open(tweets_folder + "/" + influencer + ".json")
    tweet_data = json.loads(file.read())
    file.close()
    tweets = tweet_data["tweets"]
    for tweet in tweets:
        company_keywords = tweet["company_keywords"]
        rating = tweet["rating"]
        write_company_rating(company_keywords, rating)
def write_data(userid, username):
    tweets = client.get_users_tweets(id=userid, max_results=100, tweet_fields=['id', 'text', 'created_at', 'context_annotations'], exclude="replies")
    if tweets.data==None:
        print(username, "is banned or doesn't have any tweets available")
        return
    json_array = []
    last_updated = int(time.time())
    for tweet in tweets.data:
        created_at = int(round(tweet.created_at.timestamp()))
        text = tweet.text
        company_keywords = get_company_keywords(text.replace("@", ""))

        if len(company_keywords) == 0:
            continue
        sid = SentimentIntensityAnalyzer()
        score_set = sid.polarity_scores(text)
        write_company_rating(company_keywords, score_set["compound"])
        json_array.append(
            {
                "created_at": created_at,
                "text": text,
                "rating": score_set["compound"],
                "company_keywords": list(company_keywords)
            }
        )
    file = open(tweets_folder + "/" + username + ".json", "w")
    file.write(
        json.dumps({ 
            "last_updated": last_updated,
            "tweets": list(json_array)
        }, indent=4)
    )
    file.close()
    print("done for", username)
def get_company_keywords(text):
    list = de_noise(text)
    i = 0   
    keywords = set()
    for word in list:        
        
        if word.lower() in companies:
            keywords.add(word.lower()) 
    return keywords
def de_noise(text):
    list = word_tokenize(text)
    filtered_list = []
    stop_words = set(stopwords.words("english"))
    for word in list:
        if word not in stop_words:
            filtered_list.append(word)
    return filtered_list
def load_local_data():
    for file_name in os.listdir(tweets_folder):
        parse_data(file_name[:-5])
def write_company_rating(company_keywords, score):
    for company_keyword in company_keywords:
        sum = score
        count = 1
        if company_keyword in company_ratings:
            rating = company_ratings[company_keyword]
            sum += rating["sum"]
            count += rating["count"]
        company_ratings.update(
            { 
                company_keyword: {
                    "sum": sum,
                    "count": count
                }
            }
        )

'''Performs a sentiment analysis using twitter data. Make sure to refresh the database every so often.'''
def sentiment_analysis(symbols, budget):
    average_ratings = []
    for symbol in symbols:        
        stock = yf.Ticker(symbol.upper())
        company_name = basename(stock.info["shortName"]).lower()
        if company_name not in company_ratings:
            average_ratings.append(0.0)
            continue
        total = company_ratings[company_name]["sum"]
        count = company_ratings[company_name]["count"]
        
        average_ratings.append(total/count)
    ratings = average_ratings
    out = softmax(np.array(ratings))
    out = { x:{"dollar_amount": round(budget*y, 2), "percentage_of_portfolio": round(100*y, 2)} for (x, y) in zip(symbols, out) }
    out = { "assets": out, "strategy": "Sentiment Analysis Strategy"}
    return out
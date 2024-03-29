#!/usr/bin/python
import RPi.GPIO as GPIO
import io
import json
import sys
import time
import facebook
import pytumblr
import tweepy
from time import sleep
from threading import Thread

consumer_key = 'xdbXxjbzCkABXdlrhX3XNQ'
consumer_secret = 'XGYGTU5CYlh6ObaotzRIZywOyGvn8xXBB2tsrvuZ6pU'
access_token = '1857778609-G1o40hMrTEc9u4jOyLsDVr9mKrxSJXLAenmne5E'
access_token_secret = 'olmHCWTMvEXdbNIgeXNaaQrwue6bBLPbfe3I3bckA'

GPIO.setmode(GPIO.BOARD)
GPIO.setup(15,GPIO.OUT)

class GPIOPort():

    def blink(self):
        print "Blink"
        GPIO.output(15,GPIO.HIGH) # Outputs through GPIO Pin 22
        time.sleep(1)
        GPIO.output(15,GPIO.LOW)
        return True


class TumblrListener(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.gpio_port = GPIOPort()
        pass

    def run(self):
        tumblr_consumer_key = '08rMqbhTHyPqXGHSwTQWXaBhgjojRtQktJf4uHTbr4IYD90YOy'
        tumblr_consumer_secret = 'UI0Dh6v5zCILf3KhFEJny4Dcj2Ol191x2oMg0TlNLge0CzgFhY'
        tumblr_oauth_token = 'DcPeq6ZtmwzQwXHxTKebVZJhML4Zfv0H1cOi9Yw7AXRTLpMqGt'
        tumblr_oauth_secret = 'CUIHItHRGpA6TAkxNxXtCyNIbFgwM3TagyAJulfQ0Vc6grgJrU'
        client = pytumblr.TumblrRestClient(tumblr_consumer_key, tumblr_consumer_secret, tumblr_oauth_token, tumblr_oauth_secret)
        previous_tumblr_followers = client.followers('likeordidnthappen')['total_users']

        print 'Initial followers on Tumblr: ', previous_tumblr_followers
        while True:
            current_tumblr_followers = client.followers('likeordidnthappen')['total_users']
            if current_tumblr_followers > previous_tumblr_followers:
                print 'A person has just followed the Tumblr blog!', current_tumblr_followers
                previous_tumblr_followers = current_tumblr_followers
                self.gpio_port.blink()
            else:
                print 'Tumblr followers: ',current_tumblr_followers,'. There are no new followers.'
            time.sleep(10)


class FacebookListener(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.gpio_port = GPIOPort()
        pass

    def run(self):
        graph = facebook.GraphAPI('CAAUZAeC7fPDgBAEquwHQAxgDjtO4g57xzUAxuZBT8QKwuCEjYCJIkS65ndwFKfOEAZCQqjTDICNJfafTYGpEMcjmMYEf59i8REUbIrSn60WTo5epyzEj77ToNoSpiN1ExdSfly6ZBm6dPZCZBNi9JEdujzZC89zlZCYvzFlHoLCNOeOS29PBy6BUx5u7nD5eZAX5EqgXep9cOMcx2iPKtuAo7')
        previous_fb_likes = graph.get_object('345921298869077')['likes']
        print 'Initial likes on Facebook: ', previous_fb_likes

        while True:
            page = graph.get_object('345921298869077')
            current_fb_likes = page['likes']
            if current_fb_likes > previous_fb_likes:
                print 'A new person has liked the page [',current_fb_likes,']!'
                previous_fb_likes = current_fb_likes
                self.gpio_port.blink()
            else:
                print 'Facebook likes: ',current_fb_likes,'. No new likes on Facebook.'
            sleep(1.1)


class StreamListener(tweepy.StreamListener):
    def __init__(self):
        self.gpio_port = GPIOPort()

    def on_data(self, status):
        try:
            decoded = json.loads(status)
            user = decoded['user']['screen_name']
            tweet = decoded['text']
            date = decoded['user']['created_at']
            print  "@%s twitted: \"%s\" on %s." %(user,tweet,date)
            logtext = "@%s,%s,%s\n" %(user,tweet,date)
            with open("log.txt","a") as logfile:
                logfile.write(logtext)
            logfile.close()
            self.gpio_port.blink()
        except Exception, e:
            print >> sys.stderr, 'Exception:', e
            pass

    def on_error(self, status_code):
        print >> sys.stderr, 'Error:', status_code
        return True

    def on_timeout(self):
        print >> sys.stderr, 'Timeout'
        return True


if __name__ == '__main__':
    facebook_thread = FacebookListener()
    facebook_thread.daemon = True
    tumblr_thread = TumblrListener()
    tumblr_thread.daemon = True
    
    try:
        tumblr_thread.start()
        facebook_thread.start()
        l = StreamListener()
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        stream = tweepy.Stream(auth, l)
        stream.filter(track=['likeordidnthappen'])
    except(KeyboardInterrupt, SystemExit):
        print 'Interrupted by user. Quitting...'
        GPIO.cleanup()
        exit(1)

    print 'Main terminating'
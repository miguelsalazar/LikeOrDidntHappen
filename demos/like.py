#!/usr/bin/python

#Missing:
#3. The application must run as a process.
#4. Save stats.
#5. User FB OAuth
#6. Add logic

#import RPi.GPIO as GPIO
import facebook
import io
import json
import pytumblr
import sys
import time
import tweepy
from time import sleep
from threading import Thread


class GPIOPort():
    
    def __init__(self):
        pass

    def blink(self):
        print "Blink"
        GPIO.output(22,GPIO.HIGH) # Outputs through GPIO Pin 22
        time.sleep(1)
        GPIO.output(22,GPIO.LOW)
        return True


class TumblrListener(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        consumer_key = '08rMqbhTHyPqXGHSwTQWXaBhgjojRtQktJf4uHTbr4IYD90YOy'
        consumer_secret = 'UI0Dh6v5zCILf3KhFEJny4Dcj2Ol191x2oMg0TlNLge0CzgFhY'
        oauth_token = 'DcPeq6ZtmwzQwXHxTKebVZJhML4Zfv0H1cOi9Yw7AXRTLpMqGt'
        oauth_secret = 'CUIHItHRGpA6TAkxNxXtCyNIbFgwM3TagyAJulfQ0Vc6grgJrU'
        self.gpio_port = GPIOPort()
        self.client = pytumblr.TumblrRestClient(consumer_key, consumer_secret, oauth_token, oauth_secret)
        self.previous_tumblr_followers = self.client.followers('likeordidnthappen')['total_users']
        print('Initial followers on Tumblr: ',self.previous_tumblr_followers)
        pass

    def run(self):
        while True:
            current_tumblr_followers = self.client.followers('likeordidnthappen')['total_users']
            if current_tumblr_followers > self.previous_tumblr_followers:
                print('A person has just followed the Tumblr blog! ', current_tumblr_followers)
                self.previous_tumblr_followers = current_tumblr_followers
                self.gpio_port.blink()
            else:
                print('Tumblr followers: ',current_tumblr_followers,'. There are no new followers.')
            time.sleep(10)


class FacebookListener(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.gpio_port = GPIOPort()
        self.graph = facebook.GraphAPI()
        self.previous_fb_likes = self.graph.get_object('345921298869077')['likes']
        print('Initial likes on Facebook: ',self.previous_fb_likes)
        print 
        pass

    def run(self):
        while True:
            page = self.graph.get_object('345921298869077')
            current_fb_likes = page['likes']
            if current_fb_likes > self.previous_fb_likes:
                print('A new person has liked the page [',current_fb_likes,']!')
                self.previous_fb_likes = current_fb_likes
                self.gpio_port.blink()
            else:
                print('Facebook likes: ',current_fb_likes,'. No new likes on Facebook.')
            sleep(1.1)


class StreamListener(tweepy.StreamListener):
    def __init__(self):
        self.gpio_port = GPIOPort()

    def on_status(self, status):
        try:
            user = status.user.screen_name
            tweet = status.text
            date = status.user.created_at
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

class TwitterListener():
    def __init__(self):
        consumer_key = 'xdbXxjbzCkABXdlrhX3XNQ'
        consumer_secret = 'XGYGTU5CYlh6ObaotzRIZywOyGvn8xXBB2tsrvuZ6pU'
        access_key = '1857778609-G1o40hMrTEc9u4jOyLsDVr9mKrxSJXLAenmne5E'
        access_secret = 'olmHCWTMvEXdbNIgeXNaaQrwue6bBLPbfe3I3bckA'
        
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_key, access_secret)
        self.api = tweepy.API(self.auth)

    def start(self):
        twl = StreamListener()
        stream = tweepy.streaming.Stream(self.auth,twl, secure=True)
        stream.filter(follow=None, track=['likeordidnthappen'])

if __name__ == '__main__':
    facebook_thread = FacebookListener()
    tumblr_thread = TumblrListener()
    facebook_thread.daemon = True
    tumblr_thread.daemon = True
    
    try:
        TwitterListener().start()
        facebook_thread.start()
        tumblr_thread.start()
    except(KeyboardInterrupt, SystemExit):
        print 'Interrupted by user. Quitting...'
        exit(1)

    print('Main terminating')
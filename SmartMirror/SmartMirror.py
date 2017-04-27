import logging
import redis
from flask import Flask
from flask_ask import Ask, request, session, question, statement
import os


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
r = redis.from_url("redis://h:p06b10c763b6d7785f6c7c7f27b6152493b47abef3a0a76619cc8951b22b5f92e@ec2-34-204-242-91.compute-1.amazonaws.com:19749")

@app.route("/test")
def test():
    return "Successs"

@ask.intent('HelloWorldIntent')
def hello_world():
    speech_text = 'Hello world'
    r.publish('hello','new message from me')
    return statement(speech_text).simple_card('HelloWorld', speech_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('NavigateIntent', 
        mapping={'route': 'Route'})
def navigate(route):
    speech_text = str(route)
    r.publish('navigation',route)
    print("NAVIGATING")
    return statement(speech_text).simple_card('Routing to',speech_text)


@ask.intent('CreateProfileIntent')
def create_profile():
    speech_text = "Let's get started. What is your name?"
    reprompt_speech_text = "May I please have your name?"
    return question(speech_text).reprompt(reprompt_speech_text)

@ask.intent('MyNameIsIntent')
def my_name_is(firstname):
    speech_text= "Hi {}, please position your face at the center of mirror".format(firstname)
    return statement(speech_text)

@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=PORT)

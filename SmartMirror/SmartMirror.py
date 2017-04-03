import logging
import redis
from flask import Flask
from flask_ask import Ask, request, session, question, statement
import os


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
# r = redis.StrictRedis(host='localhost',port=6379, db=0)

# @ask.launch
# def launch():
#     speech_text = 'Welcome to the Alexa Skills Kit, you can say hello'
#     return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)


@ask.intent('HelloWorldIntent')
def hello_world():
    speech_text = 'Hello world'
    # r.publish('hello','new message from me')
    return statement(speech_text).simple_card('HelloWorld', speech_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('NavigateIntent', 
        mapping={'route': 'Route'})
def navigate(route):
    speech_text = str(route)
    return statement(speech_text).simple_card('Routing to',speech_text)

@ask.session_ended
def session_ended():
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)

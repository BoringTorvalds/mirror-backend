import logging
from flask import Flask
from flask_ask import Ask, request, session, question, statement
import os
import requests


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
SERVER_URL = "http://localhost:9000"

@ask.intent('HelloWorldIntent')
def hello_world():
    speech_text = 'Hello world'
    return statement(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)


@ask.intent('TurnOnOffIntent', 
        mapping={'status': 'Status'})
def navigate(status):
    speech_text = "Mirror is going to " + str(status)
    err_speech_text = "There's an issue with " + str(status)
    r = requests.get(SERVER_URL + "/navigate/" + status)
    if r.status_code == 200:
        return statement(speech_text).simple_card("Routing to ", speech_text)
    else:
        return statement(err_speech_text).simple_card(err_speech_text)

@ask.intent('NavigateIntent', 
        mapping={'route': 'Route'})
def navigate(route):
    speech_text = "Mirror is going to " + str(route)
    err_speech_text = "There's an issue with " + str(route)
    r = requests.get(SERVER_URL + "/navigate/" + route)
    if r.status_code == 200:
        return statement(speech_text).simple_card("Routing to ", speech_text)
    else:
        return statement(err_speech_text).simple_card(err_speech_text)



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

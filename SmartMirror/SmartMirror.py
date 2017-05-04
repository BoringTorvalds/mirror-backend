import logging
from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement
import os
import requests


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
#SERVER_URL = "http://184.73.147.177:9001"
SERVER_URL= "http://localhost:9001"
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
    speech_text = render_template('turn_off')
    if str(status) == 'on':
        speech_text = render_template('turn_on') 

    r = requests.get(SERVER_URL + "/navigate/" + status)
    err_speech_text = render_template('error')
    if r.status_code == 200:
        return statement(speech_text).simple_card(speech_text)
    else:
        return statement(err_speech_text).simple_card(err_speech_text)

@ask.intent('NavigateIntent', 
        mapping={'route': 'Route'})
def navigate(route):
    speech_text = render_template('navigation',route=route)
    err_speech_text = render_template('error')
    r = requests.get(SERVER_URL + "/navigate/" + route)
    if r.status_code == 200:
        return statement(speech_text).simple_card("Routing to ", speech_text)
    else:
        return statement(err_speech_text).simple_card(err_speech_text)



@ask.intent('CreateProfileIntent')
def create_profile():
    r = requests.get(SERVER_URL + "/navigate/signup")
    speech_text = "Let's get started. What is your name?"
    reprompt_speech_text = "May I please have your name?"
    err_speech_text = render_template('error')
    return question(speech_text).reprompt(reprompt_speech_text)

@ask.intent('MyNameIsIntent')
def my_name_is(firstname):
    speech_text= render_template("prompt_name",name=firstname)
    r = requests.get(SERVER_URL + "/signup/" +firstname)
    err_speech_text = render_template('error')
    if r.status_code == 200:
        return question(speech_text)
    else:
        return statement(err_speech_text).simple_card(err_speech_text)

@ask.intent('TrainingOnOffIntent',
    mapping={'status': 'Status'})
def respond_to_training(status):
    speech_text = render_template("train_on")
    if status == 'off':
        speech_text = render_template("train_off")
    r = requests.get(SERVER_URL + "/training/"+status)
    err_speech_text = render_template('error')
    if r.status_code == 200:
        return statement(speech_text).simple_card(speech_text)
    else:
        return statement(err_speech_text).simple_card(err_speech_text)

@ask.intent('WeatherIntent',
    mapping={'location':'Location'})
def show_weather(location):
    speech_text = render_template("weather",location=location)
    r = requests.get(SERVER_URL + "/weather/" + location)
    err_speech_text = render_template('error')
    if r.status_code == 200:
        return statement(speech_text).simple_card(speech_text)
    else:
        return statement(err_speech_text).simple_card(err_speech_text)

@ask.intent('FullWeatherIntent',
    mapping={'location':'Location'})
def show_weather_detail(location):
    speech_text = render_template("weather",location=location)
    if location == "":
        speech_text = render_template("weather",location="current location")
    r = requests.get(SERVER_URL + "/fullweather/" + location)
    err_speech_text = render_template('error')
    if r.status_code == 200:
        return statement(speech_text).simple_card(speech_text)
    else:
        return statement(err_speech_text).simple_card(err_speech_text)

@ask.intent('NewsPaginationIntent',
    mapping={'option':'Option'})
def  show_more_news(option):
    speech_text = render_template("news",option=option)
    err_speech_text = render_template('error')
    r = requests.get(SERVER_URL + "/feeds/" + option)
    if r.status_code == 200:
        return statement(speech_text).simple_card(speech_text)
    else:
        return statement(err_speech_text).simple_card(err_speech_text)

@ask.intent('StockLookupIntent',
    mapping={'title':'Title'})
def look_up_stock(title):
    #Make a request to look for stockname
    STOCK_API = "http://dev.markitondemand.com/Api/v2/Lookup/json?input="+title
    stock_response = requests.get(STOCK_API)
    err_speech_text = render_template("error")
    if stock_response.status_code == 200:
        if len(stock_response.json()) == 0:
            return statement(err_speech_text).simple_card(err_speech_text)
        else:
            return request_stock_from(stock_response.json()[0])
    else:
        return statement(err_speech_text).simple_card(err_speech_text)

def request_stock_from(stock_object):
    name = stock_object['Name']
    symb = stock_object['Symbol']
    exch = stock_object['Exchange']
    r = requests.get(SERVER_URL + "/stock/"+name + "/"+symb+"/"+exch)
    text_speech = render_template("stock_lookup",name=name,symb=symb,exch=exch)
    err_speech_text = render_template("error")
    if r.status_code == 200:
        return statement(text_speech).simple_card(text_speech)
    return statement(err_speech_text).simple_card(err_speech_text)


@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=PORT)

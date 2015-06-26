from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
import datetime
import os
import json
import time
import urllib2

app = Flask(__name__)

def get_weather(city):
    url = 'http://api.openweathermap.org/data/2.5/forecast/daily?q={}&cnt=10&mode=json&units=metric'.format(city)
    try:
        response = urllib2.urlopen(url).read()
    except:
        response = {}

    return response

@app.route('/')
def index():
    searchcity = request.args.get('searchcity')
    if not searchcity:
        searchcity = request.cookies.get('last_city') or 'London'

    try:
        data = json.loads(get_weather(searchcity))
        city = data['city']['name']
    except TypeError, KeyError:
        return render_template('invalid_city.html', user_input=searchcity)

    country = data['city']['country']
    forecast_list = []

    for d in data.get('list'):
        day = time.strftime('%d %B', time.localtime(d.get('dt')))
        mini = d.get('temp').get('min')
        maxi = d.get('temp').get('max')
        description = d.get('weather')[0].get('description')
        forecast_list.append((day, mini, maxi, description))

    response = make_response(render_template('index.html',
                            forecast_list=forecast_list,
                            city=city,
                            country=country))
    if request.args.get('remember'):
        response.set_cookie('last_city', '{},{}'.format(city, country),
                            expires=datetime.datetime.today() + datetime.timedelta(days=1))
    return response


if __name__ == '__main__':
    port = int(os.environ.get('port', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

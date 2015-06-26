from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
import datetime # required for cookie setting
import os
import json
import time
import urllib2

app = Flask(__name__)

def get_weather(city):
    # openweather api
    url = 'http://api.openweathermap.org/data/2.5/forecast/daily?q={}&cnt=10&mode=json&units=metric'.format(city)
    try:
        response = urllib2.urlopen(url).read()
    except:
        response = {}

    return response

# default route
@app.route('/')
def index():
    # GET request has a searchcity parameter
    searchcity = request.args.get('searchcity')
    
    # if searchcity is blank use either the last_city stored in cookie
    # else default to London
    if not searchcity:
        searchcity = request.cookies.get('last_city') or 'London'

    try:
        data = json.loads(get_weather(searchcity))
        city = data['city']['name']
    # There may be an error either because of an attempt to parse or 
    # there is no corresponding city for the input searchcity
    except TypeError, KeyError:
        return render_template('invalid_city.html', user_input=searchcity)

    country = data['city']['country']
    forecast_list = []

    # Parse the json data and format 
    for d in data.get('list'):
        day = time.strftime('%d %B', time.localtime(d.get('dt')))
        mini = d.get('temp').get('min')
        maxi = d.get('temp').get('max')
        description = d.get('weather')[0].get('description')
        forecast_list.append((day, mini, maxi, description))

    # Send back the response including the template, city, and country
    response = make_response(render_template('index.html',
                            forecast_list=forecast_list,
                            city=city,
                            country=country))
                            
    # if remember field is checked, add a cookie that expires in a day                        
    if request.args.get('remember'):
        response.set_cookie('last_city', '{},{}'.format(city, country),
                            expires=datetime.datetime.today() + datetime.timedelta(days=1))
    return response


if __name__ == '__main__':
    # get port or default to 5000
    port = int(os.environ.get('port', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

from datetime import datetime
from os import name

import folium
import pandas as pd
from flask import Flask, jsonify, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import create_engine
from wtforms import SelectField
from wtforms_sqlalchemy.fields import QuerySelectField

from datacollectionapp import *

# wiki for cities
import requests
from bs4 import BeautifulSoup
import re
lat = 30.2672
lon = -97.7431

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'SECRET_KEY'
db = SQLAlchemy(app)

#useful abbreviations as a global variable
states = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}
# Creating the SQL database from CSV file if TRUE (Unfinished)
citycsv = pd.read_csv('city_api_list.csv', index_col=False)
citycsv = citycsv.drop(citycsv[(citycsv.Working != "Yes")].index)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(2))
    name = db.Column(db.String(50))
    #cityurl = db.Column(db.String(1000))

    def __repr__(self):
        return '{}'.format(self.state)


def choice_query():
    return City.query.distinct()


class Form(FlaskForm):
    # state = QuerySelectField(query_factory=choice_query,allow_blank=True)
    state = SelectField('state', choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), (
        'MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('PR', 'Puerto Rico'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')])
    city = SelectField('city', choices=[])


@app.route('/', methods=['POST', 'GET'])
def index():
    form = Form()

    form.city.choices = [(city.id, city.name)
                         for city in City.query.filter_by(state='AL').all()]

    if request.method == 'POST':
        city = City.query.filter_by(id=form.city.data).first()
        #state = form.state.data
        #topic = City.query.filter_by(id=city.topic).first()
        # Austin : 30.2672° N, 97.7431° W
        updateCoords(city.name, form.state.data)
        m = folium.Map(location=[lat, lon], zoom_start=14)
        m.save('templates/map.html')
        # returnlist = mainprogram(city.name,form.state.data, request.form['content_topic'])

        # if returnlist is None or returnlist.size == 0:
        #
        # while True:
        #     try:
        #         returnlist = mainprogram(city.name,form.state.data, request.form['content_topic'])
        #         break
        #     except TypeError:
        #         return render_template('index.html',form=form)
        # return render_template('dataresults.html', form = form, city = city.name, state = form.state.name, topic = request.form['content_topic'], tables=[returnlist.to_html(classes='data', index = False, header = True, justify='center', render_links=True)], titles=returnlist.columns.values)
        returnlist = mainprogram(
            city.name, form.state.data, request.form['content_topic'])
        if returnlist is None or returnlist.size == 0:
            if returnlist is None:
                print("REACH HERE INVALID RETURNLIST")
            if returnlist.size == 0:
                print("REACH THE ZERO SIZE")
            return render_template('index.html', form=form)
        return render_template('dataresults.html', form=form, city=city.name, state=form.state.data, topic=request.form['content_topic'], tables=[returnlist.to_html(classes='data', index=False, header=True, justify='center', render_links=True)], titles=returnlist.columns.values, citydetails=citydetails(city.name, form.state.data), lat=citydetails(city.name, form.state.data, True))


    # tables=[returnlist.to_html(classes='data')], titles=returnlist.columns.values
    # Set form class to "input-1"
    form.state.render_kw = {'class': 'input-1'}
    form.city.render_kw = {'class': 'input-1'}
    return render_template('index.html', form=form)
    # tables=[returnlist.to_html(classes='data')], titles=returnlist.columns.values

    # return render_template('index.html', form=form)

@app.route('/updateCoords')
def updateCoords(city, state):
    global lat
    global lon
    lat, lon = citydetails(city, state, True)
    return "Updated"


@app.route('/citydetails')
def citydetails(city, state, latlon = False):
    #var curCity = "{{ city }}";
    # //if spaces in city name replace with _
    # if (curCity.includes(" ")) {
    #     curCity = curCity.replace(" ", "_");
    # }
    # var curState = "{{ state }}";
    # //console.log(curCity);
    # //console.log(curState);
    # wikistr = "https://en.wikipedia.org/wiki/" + curCity + ",_" + curState;
    # console.log(wikistr);
    # convert above code to python
    curCity = city
    cityWithSpace = curCity
    curState = state
    # if spaces in city name replace with _
    if " " in curCity:
        curCity = curCity.replace(" ", "_")
    wikistr = "https://en.wikipedia.org/wiki/" + curCity + ",_" + curState
    wikistr2 = "https://en.wikipedia.org/wiki/" + curCity
    wikistr3 = "https://en.wikipedia.org/wiki/" + curCity + ",_" + states[curState]
    print(wikistr)

    if latlon:
        # Use Beautiful Soup to scrape the wikipedia page for span class latitude and assign it to latitude
        soup = BeautifulSoup(requests.get(wikistr).text, 'html.parser')
        try:
            lat = soup.find('span', class_='latitude').text
        except:
            soup = BeautifulSoup(requests.get(wikistr3).text, 'html.parser')
            lat = soup.find('span', class_='latitude').text


        # The input is of the form 30°16′2″N, so we need to convert it to decimal degrees
        # First, split the string at the degree symbol
        latlist = []
        # latlist needs to be a list of the form ['30', '16', '2″N']
        latlist.append(lat.split('°')[0])
        latlist.append(lat.split('°')[1].split('′')[0])
        latlist.append(lat.split('°')[1].split('′')[1].split('″')[0])
        #if latlist has N or S in it, set it to 0
        if latlist[2].endswith('N') or latlist[2].endswith('S'):
            latlist[2] = 0
        try:
            if lat.split('°')[1].split('′')[1].split('″')[1] == 'S':
                latlist.append('-1')
            else:
                latlist.append('1')
        except:
            if lat.split('°')[1].split('′')[1] == 'S':
                latlist.append('-1')
            else:
                latlist.append('1')

        # Now, convert the list to a float
        latlist = [float(i) for i in latlist]
        # Finally, convert to decimal degrees
        lat = latlist[0] + latlist[1]/60 + latlist[2]/3600
        lat = lat * latlist[3]
        # cut off at 4 decimal places
        lat = round(lat, 4)
        # Repeat for longitude
        lon = soup.find('span', class_='longitude').text
        lonlist = []
        lonlist.append(lon.split('°')[0])
        lonlist.append(lon.split('°')[1].split('′')[0])
        lonlist.append(lon.split('°')[1].split('′')[1].split('″')[0])
        #if lonlist has E or W in it, set it to 0
        if lonlist[2].endswith('E') or lonlist[2].endswith('W'):
            lonlist[2] = 0
        try:
            if lon.split('°')[1].split('′')[1].split('″')[1] == 'W':
                lonlist.append('-1')
            else:
                lonlist.append('1')
        except:
            if lon.split('°')[1].split('′')[1] == 'W':
                lonlist.append('-1')
            else:
                lonlist.append('1')
        lonlist = [float(i) for i in lonlist]
        lon = lonlist[0] + lonlist[1]/60 + lonlist[2]/3600
        lon = lon * lonlist[3]
        lon = round(lon, 4)
        return lat, lon
        
    # Use Beautiful Soup to scrape the wikipedia page for the first <p> tag which starts with a <b> tag with the city name
    # and the state name in it.  This is the first paragraph of the wikipedia page and contains the city description
    # that we want to display on the page.
    try:
        soup = BeautifulSoup(requests.get(wikistr).text, 'html.parser')
        # find the first <p> tag that starts with a <b> tag
        ptag = soup.find('p', {'class': None})
        # find the first <b> tag in the <p> tag
        btag = ptag.find('b')
        # get the text of the <b> tag
        btagtext = btag.text
    except:
        # if the above fails, try the following
        print("WE ARE IN THE EXCEPTION")
        soup = BeautifulSoup(requests.get(wikistr2).text, 'html.parser')
        #iterate through the <p> tags until you find one that starts with a <b> tag
        for ptag in soup.find_all('p', {'class': None}):
            try:
                btag = ptag.find('b')
                btagtext = btag.text
                break
            except:
                continue
    # if the text of the <b> tag starts with the city name then we have the correct paragraph
    if btagtext.startswith(cityWithSpace):
        # get the text of the <p> tag
        ptagtext = ptag.text
        # remove the last character which is a period
        ptagtext = ptagtext[:-1]
        
    brackets="()[]"
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []
    for character in ptagtext:
        for i, b in enumerate(brackets):
            if character == b: # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                if count[kind] < 0: # unbalanced bracket
                    count[kind] = 0  # keep it
                else:  # found bracket to remove
                    break
        else: # character is not a [balanced] bracket
            if not any(count): # outside brackets
                saved_chars.append(character)
    ptagtext = ''.join(saved_chars)
    # remove any spaces before commas
    ptagtext = ptagtext.replace(" ,", ",")
        
    return ptagtext


        #return ptagtext
        # return the text of the <p> tag
        #return ptagtext
    print(ptagtext)

    return wikistr

@app.route('/map')
def map():
    return render_template('map.html')


@app.route('/city/<state>')
def city(state):
    cities = City.query.filter_by(state=state).all()
    cityArray = []
    for city in cities:
        cityObj = {}
        cityObj['id'] = city.id
        cityObj['name'] = city.name
        #if lowercased city name is not equal to lowercased state name
        if city.name.lower() != states[state].lower():
            #print(city.name)
            #print(state)
            cityArray.append(cityObj)

    return jsonify({'cities': cityArray})


if __name__ == "__main__":
    # db.create_all()
    '''
    city1 = City(id = 1, state = "CA", name = "Los Angeles")
    city2 = City(id = 2, state = "TX", name = "Dallas")
    city3 = City(id = 3, state = "TX", name = "Austin")
    city4 = City(id = 4, state = "WA", name = "Seattle")
    city5 = City(id = 5, state = "IL",name = "Chicago")
    '''
    db.session.commit()
    # print(citycsv)
    app.run(debug=True,host="0.0.0.0")

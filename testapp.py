from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms import SelectField 
from datetime import datetime
import pandas as pd
import folium
from datacollectionapp import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'SECRET_KEY'
db = SQLAlchemy(app)

#Creating the SQL database from CSV file if TRUE
citycsv = pd.read_csv('city_api_list.csv', index_col=False)
citycsv = citycsv.drop(citycsv[(citycsv.Working != "Yes")].index)


class City(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    state = db.Column(db.String(2))
    name = db.Column(db.String(50))
    #cityurl = db.Column(db.String(1000))

    def __repr__(self):
        return '{}'.format(self.state)

def choice_query():
    return City.query

class Form(FlaskForm):
    #state = QuerySelectField(query_factory=choice_query,allow_blank=True)
    state = SelectField('state', choices=[('CA','California'),('TX',"Texas")])
    city = SelectField('city',choices=[])

@app.route('CityData/', methods = ['POST','GET'])

def index():
    form = Form()
    form.city.choices = [(city.id, city.name) for city in City.query.filter_by(state = 'CA').all()]

    if request.method == 'POST':
        city = City.query.filter_by(id=form.city.data).first()
        #topic = City.query.filter_by(id=city.topic).first()
        m = folium.Map(location=[30.2672,-97.7431],zoom_start=14)
        m.save('templates/map.html')
        return '<h1> State: {}, City: {}</h1><iframe class="map", src="/map" width="600" height="600"></iframe>'.format(form.state.data,city.name)

    return render_template('index.html',form=form)
    
@app.route('CityData/map')
def map():
    return render_template('map.html')

@app.route('CityData/city/<state>')
def city(state):
    cities = City.query.filter_by(state=state).all()
    cityArray = []
    for city in cities:
        cityObj = {}
        cityObj['id'] = city.id
        cityObj['name'] = city.name
        cityArray.append(cityObj)

    return jsonify({'cities':cityArray})

# @app.route('/update/<int: id>')
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        content_topic2 = request.form['content_topic']
        #content_state2 = request.form['content_state']
        #content_ç = request.form['content_topic']

        #new_task = Todo(content = task_content)
        #search(content_city2, content_state2, content_topic2)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('CityData/')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks = tasks)


@app.route('CityData/delete/<int:id>')    
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try: 
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('CityData/')
    except:
        return 'There was a problem deleting that task'

@app.route('CityData/update/<int:id>',methods=['GET','POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('CityData/')
        except:
            return ' There was an issue updating your task'
    else:
        return render_template('update.html', task = task)



if __name__ == "__main__":
    #db.create_all()
    print(citycsv)
    app.run(debug = True)
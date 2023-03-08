from flask import Flask, escape, render_template
import edgedb

app = Flask(__name__)

@app.route("/", methods=['POST','GET'])
def homepage():
    button_list = {'Recommender':{'action':'/Recommender'},\
                   'DataExploration':{'action':'/'}}
    return render_template('homepage.html', button_list=button_list)

@app.route("/Recommender", methods=['POST','GET'])
def recommender_base():
    text_entries = {'Type':{'label':'Type', 'return':str()},\
                    'BodyShape':{'label':'Body Shape', 'return':str()}}
    return render_template('recommender_base.html', text_entries=text_entries)

@app.route("/query/<string:field>/<string:value>")
def query(field, value):
    return f"<b>{escape(field)}</b> : {escape(value)}"

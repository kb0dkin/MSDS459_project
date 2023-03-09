from flask import Flask, escape, render_template, request
import edgedb
import bokeh
import frontend_utils

app = Flask(__name__)

@app.route("/", methods=['POST','GET'])
def homepage():
    button_list = {'Recommender':{'action':'/Recommender'},\
                   'DataExploration':{'action':'/DataExploration'}}
    return render_template('homepage.html', button_list=button_list)

@app.route("/Recommender", methods=['POST','GET'])
def recommender_base():
    text_entries = {'Type':{'label':'Type', 'return':str()},\
                    'BodyShape':{'label':'Body Shape', 'return':str()}}
    return render_template('recommender_base.html', text_entries=text_entries)

@app.route("/DataExploration", methods=['POST','GET'])
def data_exploration():
    return "<h1>A work in progress!</h1>"

# parse the string that the person puts in using NER (for now) and
# then turn it into an edgeql request
@app.route("/NLP_request")
def nlp_request():
    req = dict(request.args)['NLP_request']
    
    query_str = frontend_utils.request_parser(req)

    return f"{query_str}"
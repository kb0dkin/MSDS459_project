from flask import Flask, escape, render_template, request
import edgedb
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
import frontend_utils
import json
import bokeh_utils

app = Flask(__name__)


# --------------------------------------------------------
@app.route("/", methods=['POST','GET'])
def homepage():

    button_list = {'Recommender':{'action':'/Recommender'},\
                   'DataExploration':{'action':'/DataExploration'}}
    return render_template('homepage.html', button_list=button_list)


# --------------------------------------------------------
@app.route("/Recommender", methods=['POST','GET'])
def recommender_base():
    text_entries = {'Type':{'label':'Type', 'return':str()},\
                    'BodyShape':{'label':'Body Shape', 'return':str()}}
    return render_template('recommender_base.html', text_entries=text_entries)


# --------------------------------------------------------
@app.route("/DataExploration", methods=['POST','GET'])
def data_exploration():
    script1, script2, script3, div1, div2, div3 = bokeh_utils.get_bokeh_items()
    # Return all the charts to the HTML template
    return render_template(
        template_name_or_list='explore_base.html',
        script=[script1, script2, script3],
        div=[div1, div2, div3],
    )


# parse the string that the person puts in using NER (for now) and
# then turn it into an edgeql request
@app.route("/KV_request")
def kv_request():

    # get data from the database
    with edgedb.create_client(dsn='MSDS_459') as client:
        req = dict(request.args)['request']
        query_str = frontend_utils.request_parser(req)
        guitars = client.query(query_str)

    # parse into something nice for jinja
    guitars_dict = frontend_utils.Guitar_results_parser(guitars)

    # render it
    return render_template('guitar_results.html', guitars=guitars_dict)



# --------------------------------------------------------
# Find guitars that have the closest descriptions, per BERT
@app.route("/NLP_request")
def nlp_request():
    # the request from the user
    req = dict(request.args)['request']

    # get a list of guitars
    guitars = frontend_utils.NLP_Guitar_Finder(req)

    # parse into something nice for jinja
    guitars_dict = frontend_utils.Guitar_results_parser(guitars)
    
    # render it
    return render_template('guitar_results.html', guitars=guitars_dict)
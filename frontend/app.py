from flask import Flask

app = Flask(__name__)

@app.route("/")
def homepage():
    return "Welcome to the party, pal"

# sending query data to be parsed and sent to the backend
@app.route("/query/<string:field>/<string:value>")
def query():
    return f"Querying {escape(field)} for {escape(value)}"



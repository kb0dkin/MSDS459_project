# MSDS459_project

This is my code for the Winter Quarter of MSDS 459. Thanks for checking it out!

The goal of the project is to build a guitar recommendation engine that gives the user a recommended guitar based on a request. It also allows the user to examine the underlying data about the guitars.

The data about the guitars comes from [Guitar Center](guitarcenter.com). We scraped the section of their website on guitars for a list of all of the guitars they offer, properties about the guitars, and reviews of the guitars. 

I then stored the data in a graph-native database built on top of PostGRES called [EdgeDB](edgedb.com). There are a few advantages of graph databases, including that it highlights the importance of connections and the simplicity of collowing those connections when compared with repeated SQL joins. 

For a frontend, I used [Flask](https://flask.palletsprojects.com/en/2.2.x/) as a *very* basic web server. The front end has three pages so far -- a landing page, a guitar recommendation page, and a data exploration page. These were all written using Jinja templates. Apologies if the setup is clunky, I'm not a web developer.

## Software requirements.
This setup requires Python with several different modules, and a copy of the EdgeDB server and client. 

### Edgedb Setup
Go [here](edgedb.com/install) to download EdgeDB. The Windows installation runs on Windows Subsystem for Linux, so just be ready for that.

Once you have the software installed, navigate to the `db\` directory, and run `edgedb project init`. Name your instance `MSDS_459` and your database `edgedb`. 
*** todo: write batch script to set up edgedb instance ***

### Python Setup
You will need Python 3.7+.

If you prefer pip, I have included a `requirements.txt` file that includes all of the necessary libraries. If you prefer conda, I have included a `environment.yml`


### Populating the database
First, make sure your EdgeDB instance is running by typing `edgedb instance list` and verify that the `MSDS_459` instance is running.

Next, navigate to the `frontend/` directory and type `flask run` and open your prefered web browser to *127.0.0.1:5000*

*~Enjoy~*

-KB

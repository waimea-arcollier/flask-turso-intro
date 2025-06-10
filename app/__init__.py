from flask          import Flask
from flask          import request
from flask          import render_template
from flask          import redirect
from libsql_client  import create_client_sync
from dotenv         import load_dotenv
import os


# Load Turso environment variables from the .env file
load_dotenv()
TURSO_URL = os.getenv("TURSO_URL")
TURSO_KEY = os.getenv("TURSO_KEY")

# Create the Flask app
app = Flask(__name__)


# Track the DB connection
client = None

#-----------------------------------------------------------
# Connect to the Turso DB and return the connection
#-----------------------------------------------------------
def connect_db():
    global client
    if client == None:
        client = create_client_sync(url=TURSO_URL, auth_token=TURSO_KEY)
    return client


#-----------------------------------------------------------
# Home Page with list of things
#-----------------------------------------------------------
@app.get("/")
def home():
    client = connect_db()
    result = client.execute("SELECT id, flavour from things")
    things = result.rows
    return render_template("pages/home.jinja", things=things)
    

#-----------------------------------------------------------
# Thing details page
#-----------------------------------------------------------
@app.get("/thing/<int:id>")
def show_thing(id):
    client = connect_db()
    sql = """
        SELECT id, flavour, rating 
        FROM things
        WHERE id=?
    """
    values= [id]
    
    result = client.execute(sql, values)
    thing = result.rows[0]
    
    return render_template("pages/thing.jinja", thing=thing)


#-----------------------------------------------------------
# New thing form page
#-----------------------------------------------------------
@app.get("/new")
def new_thing():
    return render_template("pages/thing-form.jinja")

#-----------------------------------------------------------
# Process New Thing
#-----------------------------------------------------------
@app.post("/add-thing")
def add_thing():
    #get form data
    flavour = request.form.get("flavour")
    rating = request.form.get("rating")
    
    print(flavour)
    print(rating)
    
    #connect to database
    client = connect_db()
    #add drink to db
    sql = "INSERT INTO things (flavour, rating) VALUES (?, ?)"
    values= [flavour, rating]
    client.execute(sql, values)
    
    #redirect to home
    return redirect("/")

    
#-----------------------------------------------------------
# Thing deletion
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_thing(id):
    
    client = connect_db()
    sql = "DELETE FROM things WHERE id=?"
    values= [id]
    client.execute(sql, values)
    
    return redirect("/")


#-----------------------------------------------------------
# 404 error handler
#-----------------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    return render_template("pages/404.jinja")

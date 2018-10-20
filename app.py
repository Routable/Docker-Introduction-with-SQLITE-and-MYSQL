from flaskext.mysql import MySQL
import sqlite3 as sql
from contextlib import contextmanager
from flask import Flask, request, render_template

app = Flask(__name__)

# -----------------------------------------------------------------

# The following lines are used to set the global variables used
# to configure MYSQL with Flask/Python. As MYSQL is a shared
# database, we only want to present these credentials a single
# time in order to prevent code repetition. In a production
# environment, sensitive connection details such as this should 
# be stored in a separate, secure area. 

# -----------------------------------------------------------------

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'Thanos'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Did'
app.config['MYSQL_DATABASE_DB'] = 'Nothing'
app.config['MYSQL_DATABASE_HOST'] = 'Wrong'
mysql.init_app(app)


# -----------------------------------------------------------------

# BEGIN SQLITE RELATED METHODS

# The methods below are associated with the SQLITE database. As
# each docker instance contains a single database.db file, the
# swarm nodes store their data completely separately from themselves.
# This is a clear example of the importance of data centralization, 
# and a good example of how we can work with this slave/master 
# architecture in two different scenarios.

# -----------------------------------------------------------------


# -----------------------------------------------------------------
# get_sqlite_count retrieves how many views we've received on the
# count table found in the database.db sqlite file
# -----------------------------------------------------------------
def get_sqlite_count():
  count = sqlite_lookup('SELECT COUNT(*) FROM count')
  return count

# -----------------------------------------------------------------
# insert_into_sqlite_database calls our dbAlter method that 
# executed our provided query. dbAlter is a custom made method
# to handle database entries for SQLITE.
# -----------------------------------------------------------------
def insert_into_sqlite_database():
  dbAlter('INSERT INTO count (number) VALUES (1)')


# -----------------------------------------------------------------
# connection_to_sqlite_database as the name implies handles our
# connection to the SQLITE database.db database file. We keep
# the connection open until our database commits/reads have 
# fully completed. 
# -----------------------------------------------------------------
@contextmanager
def connection_to_sqlite_database():
    try:
      connection = sql.connect('database.db')
      yield connection
      connection.close()
    except sql.Error as e:
      print("connection_to_database(): connection error: " + e)

# -----------------------------------------------------------------
# sqlite_lookup handles retrieval database queries safely.
# -----------------------------------------------------------------
def sqlite_lookup(query, *args):
    with connection_to_sqlite_database() as connection:
        connection.row_factory = sql.Row
        c = connection.cursor()
        c.execute(query, (args))
        connection.commit()
        count = c.fetchone()[0]
        return count

# -----------------------------------------------------------------
# dbAlter (safely) handles queries that mutate data.
# -----------------------------------------------------------------
def dbAlter(query, *args):
    with connection_to_sqlite_database() as connection:
        c = connection.cursor()
        c.execute(query, (args))
        connection.commit()

# -----------------------------------------------------------------

# BEGIN MYSQL RELATED METHODS

# The methods below are associated with the SQLITE database. As
# each docker instance contains a single database.db file, the
# swarm nodes store their data completely separately from themselves.
# This is a clear example of the importance of data centralization, 
# and a good example of how we can work with this slave/master 
# architecture in two different scenarios.

# -----------------------------------------------------------------


# -----------------------------------------------------------------
# A directly way to insert data into the mysql database. It's not
# taking user data, so we're just going to put in an insert. 
# -----------------------------------------------------------------

def insert_into_mysql_database():
  conn = mysql.connect()
  cur = conn.cursor()
    # Execute
  cur.execute("INSERT INTO examplecount(id) VALUES(1)")
    # Commit to DB
  conn.commit()
    #Close connection
  conn.close()

# -----------------------------------------------------------------
# A simple retrieval from our examplecount table from the middleware
# database on our MYSQL server. Keep in mind that we are counting 
# our hits by summing the rows found in examplecount. The easier
# way would be to have a single column called (hits) we could retrieve.
# However, this method allows us to capture specific user information
# such as the browser, IP, in the future.
# -----------------------------------------------------------------

def retrieve_from_mysql_database():
  conn = mysql.connect()
  cur = conn.cursor()
  cur.execute("SELECT count(*) FROM examplecount")
  rv = cur.fetchone()
  return rv[0]
  
# -----------------------------------------------------------------
# Flask routes for the index page. This class isn't about Flask, so
# google it.
# -----------------------------------------------------------------

@app.route('/')
def hello_world():

  sqlite_count = get_sqlite_count()
  mysql_count = retrieve_from_mysql_database()
  insert_into_mysql_database()
  insert_into_sqlite_database()

  return render_template('index.html', sqlite_count = sqlite_count, 
                          mysql_count = mysql_count)

if __name__ == '__main__':
   app.run(host='0.0.0.0')

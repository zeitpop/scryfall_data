import pandas as pd 
from sqlalchemy import *
from dotenv import load_dotenv

# Import database credentials
load_dotenv()
database_url = os.environ.get('DATABASE_URL')
database_username = os.environ.get('DATABASE_USERNAME')
database_password = os.environ.get('DATABASE_PASSWORD')

connection_string = ("mysql+mysqldb://" + database_username + ":" + database_password + "@" + database_url + "/scryfall")

engine = create_engine(connection_string, echo=False, future=True, pool_pre_ping=True)

# Create MetaData object
meta = MetaData()

# Construct Table objects
events = Table('events', meta, autoload_with=engine)
decks = Table('decks', meta, autoload_with=engine)
decklists = Table('decklists', meta, autoload_with=engine)
cards = Table('cards', meta, autoload_with=engine)

query = "SELECT * FROM scryfall.decks;"
df = pd.read_sql(query,mydb)

print(df.describe())
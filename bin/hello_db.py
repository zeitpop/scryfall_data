from sqlalchemy import text
from sqlalchemy import create_engine

engine = create_engine("mysql+mysqldb://root:508774Mw!@localhost/bike_stores", echo=True, future=True)


with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    print(result.all())

from sqlalchemy import create_engine
from sqlalchemy import text

def constructINSERT(table, columns, values):
    separator1 = ", "
    separator2 = ", "

    print("received input argument columns as type ", type(columns))
    print("received input argument v as type ", type(values))

    columnStatement = separator1.join(columns)
    valueStatement = separator2.join(values)

    print("created columnStatement as type ", type(columnStatement))
    print("created valueStatemenet as type ", type(valueStatement))

    insertStatement = "INSERT INTO ", table, " \n(" + columnStatement + "\n) \n VALUES (" + valueStatement + "\n);\n "

    return insertStatement

# Currently bunk func
def initDatabase(database):
    return create_engine("mysql+mysqldb://root:508774Mw!@localhost/scryfall", echo=True, future=True)


def submitSQL(engine, statement):

    with engine.connect() as conn:
        result = conn.execute(text(statement))
        return result.all()


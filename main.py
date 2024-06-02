from app import db, app
from sqlalchemy import text

with app.app_context():
    # Creating the books table in the database
    db.create_all()

    # Using SQLAlchemy to get a raw connection and execute raw SQL
    connection = db.engine.connect()
    result = connection.execute(text("SHOW TABLES"))

    for row in result:
        print(row)

    # Closing the connection
    connection.close()

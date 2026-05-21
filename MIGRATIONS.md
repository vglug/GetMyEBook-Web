Flask-Migrate (Alembic) integration using the standard Flask CLI

1. Ensure dependencies are installed:

   pip install Flask-SQLAlchemy Flask-Migrate

2. Point Flask to the application (from project root):

   export FLASK_APP=app.py

3. Set your database URL (example):

   export DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/dbname"

4. Initialize the migrations folder (Flask-Migrate will create Alembic files):

   flask db init

5. Create an autogenerate migration from current models:

   flask db migrate -m "init"

6. Apply migrations to the database:

   flask db upgrade

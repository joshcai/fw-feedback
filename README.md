# mcdermott
input system for finalist's weekend

To get started, first install a virtualenv to hold your dependencies:

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Next, create your database repository by doing the following:

```
python db_create.py
python db_migrate.py
python db_seed.py
```

You will have to run `python db_migrate.py` any time you update the models.

Finally, to run the app do:

```
python run.py
```

Navigate to http://localhost:5000/ to see the app.

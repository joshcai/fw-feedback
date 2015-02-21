# mcdermott
input system for finalist's weekend

To get the Git repository the first time do:

```
git clone https://github.com/joshcai/mcdermott.git
```

After that, install a virtualenv to hold your dependencies:

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Add a config file:

```
cp sample_config.py config.py
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

The other git commands you might need are:

```
git pull
git status
git add [file]
git add -A (to add all files)
git commit -m "[message]"
git push
```

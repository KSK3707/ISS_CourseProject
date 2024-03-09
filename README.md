[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/M9yOg1uw)

# Before Opening
## Requirments
```commandline
python >= 3.10
```
## Virtual env setup
### LINUX
```commandline
$ python -m venv ./venv
$ source venv/bin/activate
$ python -m pip install -r requirements.txt
```
### WINDOWS
```commandline
$ python -m venv ./venv
$ Set-ExecutionPolicy Unrestricted -Scope Process
$ .\venv\Scripts\Activate.ps1
$ python -m pip install -r requirements.txt
```

## Run server (make sure you're inside `venv`)
```commandline
$ cd src
$ python server.py
```

Then we can open `index.html` and go from there.

Database is stored in `src/instance/database.db`

Data Models are in `src/models.py`



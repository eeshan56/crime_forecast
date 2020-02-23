# Forensic Analysis and Forecasting using Textual Reports

## Starting the RASA NLU Server:

Production Mode:
```
rasa run --enable-api -m models/nlu-20190515-144445.tar.gz
```

Debug Mode:
```
rasa run -m models/nlu-20200212-095836.tar.gz --enable-api --cors '*' --debug
```

## Install required packages (venv is recommended) using:

```
pip install -r requirements.txt
```

If the above command doesn't work, try:
```
python run_pip_requirements.py
```

## For creating a python3 virtual environment, refer to the page:

https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-ubuntu-18-04-quickstart
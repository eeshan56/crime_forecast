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

## Install required packages using (venv is recommended):

```
pip install -r requirements.txt
```

If the above command doesn't work, try:
```
python run_pip_requirements.py
```
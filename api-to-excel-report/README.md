# API to Excel Report Generator

Pulls 7 days of hourly weather and solar data from the free Open-Meteo API,
cleans it with pandas, and creates a formatted Excel report with a summary
sheet and a chart.

## Run
pip install -r requirements.txt
python main.py

## Configure
Edit config.yaml (city, coordinates, number of days, output file name).

## Output
weather_report.xlsx with a Raw Data sheet, a Summary sheet, and a chart.

## Tests
python -m unittest test_main.py -v


## Tech
Python, requests, pandas, openpyxl, YAML

import sys
import requests
import pandas as pd
import yaml
from openpyxl import load_workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

API_URL = "https://api.open-meteo.com/v1/forecast"


def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def fetch_data(cfg):
    params = {
        "latitude": cfg["latitude"],
        "longitude": cfg["longitude"],
        "hourly": "temperature_2m,relative_humidity_2m,shortwave_radiation",
        "forecast_days": cfg["days"],
        "timezone": cfg["timezone"],
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def clean_data(raw):
    df = pd.DataFrame(raw["hourly"])
    df = df.rename(columns={
        "time": "Time",
        "temperature_2m": "Temperature (C)",
        "relative_humidity_2m": "Humidity (%)",
        "shortwave_radiation": "Solar Radiation (W/m2)",
    })
    df["Time"] = pd.to_datetime(df["Time"])
    return df.dropna()


def make_summary(df):
    df = df.copy()
    df["Date"] = df["Time"].dt.date
    summary = df.groupby("Date").agg(**{
        "Min Temp (C)": ("Temperature (C)", "min"),
        "Max Temp (C)": ("Temperature (C)", "max"),
        "Avg Temp (C)": ("Temperature (C)", "mean"),
        "Avg Humidity (%)": ("Humidity (%)", "mean"),
        "Avg Solar (W/m2)": ("Solar Radiation (W/m2)", "mean"),
    }).round(1).reset_index()
    return summary


def export_excel(df, summary, path):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Raw Data", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)

    wb = load_workbook(path)
    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1F4E78")
            cell.alignment = Alignment(horizontal="center")
        for col in ws.columns:
            longest = max(len(str(c.value)) if c.value is not None else 0 for c in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = longest + 3

    ws = wb["Summary"]
    chart = LineChart()
    chart.title = "Daily Min / Max Temperature (C)"
    chart.height, chart.width = 8, 16
    data = Reference(ws, min_col=2, max_col=3, min_row=1, max_row=ws.max_row)
    cats = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, "H2")
    wb.save(path)


def main():
    try:
        cfg = load_config()
        raw = fetch_data(cfg)
        df = clean_data(raw)
        summary = make_summary(df)
        export_excel(df, summary, cfg["output_file"])
        print(f"Report created: {cfg['output_file']} ({len(df)} rows)")
    except requests.RequestException as e:
        print(f"Could not fetch data. Check your internet connection and try again.\nDetails: {e}")
        sys.exit(1)
    except (KeyError, FileNotFoundError) as e:
        print(f"Config or data problem: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

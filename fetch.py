import argparse
import requests
import re
import pandas as pd
import json
from datetime import date

def to_float(element):
    try:
        f = float(element)
        return f
    except ValueError:
        return None

def main(args):
    city = args.city
    print(city)
    city = " ".join([w.capitalize() for w in city.split()])
    print(city)
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles={city}&rvslots=main"

    response = requests.get(url)
    content = response.content.decode("utf-8")

    exp = re.compile("===? ?(C|c)limate ?===?")
    match = exp.search(content)

    if match is not None:
        matchend = match.span()[-1]
        content = content[matchend:]

        exp = re.compile("===?")
        match = exp.search(content)
        if match is not None:
            matchend = match.span()[0]
            content = content[:matchend]

        #print(content)

    content = content.replace("\\n", "\n")
    content = content.replace("\u2212", "-")
    content = content.replace("\\u2212", "-")
    
    rows = []
    columns = ["timeframe", "type", "value"]
    timeframes = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'year']
    
    # Fetch both Celcius and Fahrenheit temperatures
    types = ["record high", "high", "mean", "low", "record low"]
    types = [t + " C" for t in types] + [t + " F" for t in types]
    
    # Add precipitation, both mm and inches
    types += ["precipitation mm", "precipitation inch", "precipitation days", "sun"]
    
    for row in content.split("\n"):
        data = []
        if "|" in row:
            for timeframe in timeframes:
                if f"{timeframe}" in row:
                    data.append(timeframe)
                    break

            print(row)

            for t in types:
                if f" {t}" in row:
                    data.append(t)
                    break
            
            numeric = row.split("=")[-1].strip()
            numeric = to_float(numeric)
            print(data)
            if numeric is not None and len(data) == 2:
                data.append(float(numeric))
                rows.append(data)

    df = pd.DataFrame(rows, columns=columns)
    df = df.drop_duplicates()
    print(df)

    city_l = city.replace(" ", "_").replace(",", "").lower()
    jsonpath = f"{args.datapath}/{city_l}.json"
    d = df.to_dict(orient="records")

    today = date.today()
    d = {
        "city": city,
        "date_fetched": {"year": today.year, "month": today.month, "day": today.day},
        "data": d
    }
    with open(jsonpath, "w") as f:
        json.dump(d, f, indent=4)

    #print(matches)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", type=str, required=True)
    parser.add_argument("--datapath", type=str, default="data")
    args = parser.parse_args()
    main(args)

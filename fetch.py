import argparse
import requests
import re
import pandas as pd

def to_float(element):
    try:
        f = float(element)
        return f
    except ValueError:
        return None

def main(args):
    city = args.city.lower().capitalize()
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
    
    rows = []
    columns = ["timeframe", "type", "value"]
    timeframes = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'year']
    types = ["record high C", "high C", "mean C", "low C", "record low C", "precipitation mm", "precipitation days", "sun"]
    
    for row in content.split("\n"):
        data = []
        if "|" in row:
            for timeframe in timeframes:
                if f"|{timeframe}" in row:
                    data.append(timeframe)
                    break

            #print(row)

            for t in types:
                if f" {t} " in row:
                    data.append(t)
                    break
            
            numeric = row.split("=")[-1].strip()
            numeric = to_float(numeric)
            if numeric is not None and len(data) == 2:
                data.append(float(numeric))
                rows.append(data)

    df = pd.DataFrame(rows, columns=columns)
    df = df.drop_duplicates()
    print(df)
    #print(matches)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", type=str, required=True)
    args = parser.parse_args()
    main(args)
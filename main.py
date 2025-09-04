import requests
import os
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
import matplotlib.pyplot as plt

FILENAME = "triple_crown_winners.json"


# ------------ horse web scraper --------------
def scrape_horses():
    """
    scrapes triple crown winners wikipedia page and returns horse name and year, ignoring one pesky tr that is a footnote
    """

    url = "https://en.wikipedia.org/wiki/Triple_Crown_of_Thoroughbred_Racing_(United_States)"

    # user agent identifier
    headers = {
        "User-Agent": "educational_horse_scraper_bot"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = bs(response.text, "html.parser")

# targets the the wikitable witth the caption Triple Crown winners
    tables = soup.find_all("table", class_="wikitable")

    target_table = None
    for table in tables:
        caption = table.find("caption")
        if caption and "Triple Crown winners" in caption.text:
            target_table = table
            break

    if not target_table:
        print("Could not find")
        return []

# remove the pesky td footnote, targeting colspan="7" as all other td have values
    for tr in target_table.find_all("tr"):
        td = tr.find("td")
        if td and td.has_attr("colspan") and td["colspan"] == "7":
            tr.decompose()

    df = pd.read_html(str(target_table))[0]
    df_simple = df[["Year", "Winner"]]

    print (df_simple.head(10))
    return df_simple.to_dict(orient="records")


# -------------json -------------
# save a copy of the data to json
def steal_horse_data(data, filename):
    """
    saves scraped horse data to json
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"data saved to {filename}")


def file_exists():
    return os.path.exists(FILENAME)


# ---------visualization---------
def plot_horses(data):
    df = pd.DataFrame(data)
    df["Year"] = df["Year"].astype(int)

    df = df.sort_values("Year")

    fig = plt.figure(figsize=(10, 8))
    fig.canvas.manager.set_window_title("US Thoroughbred Racing")

    winners = df["Winner"].unique()

    winners_to_num = {winner: i for i, winner in enumerate(winners)}
    y_nums = df["Winner"].map(winners_to_num)

    plt.scatter(df["Year"], y_nums, color="black")

    plt.yticks(list(winners_to_num.values()), list(winners_to_num.keys()))
    plt.xlabel("Year")
    plt.title("Triple Crown Winners")
    plt.grid(axis="x", linestyle="--", alpha=0.7 )

    plt.tight_layout()
    plt.show()

# -------------MAIN------------------


if __name__ == "__main__":
    try:
        horse_data = scrape_horses()
        if horse_data:
            steal_horse_data(horse_data, FILENAME)
        else:
            print("no horse data to steal")
    except Exception as e:
        print(f"Error during scraping or saving: {e}")
        horse_data = []


    if file_exists():
        print(f"{FILENAME} exists")
    else:
        print(f"{FILENAME} does not exist")

    plot_horses(horse_data)



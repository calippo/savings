"""
  Store data
"""

import os
from datetime import date, datetime
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient

plt.style.use('fivethirtyeight')

mongo_user=os.environ['MONGO_USER']
mongo_password=os.environ['MONGO_PASSWORD']
mongo_uri=os.environ['MONGO_URI']
mongo_db=os.environ['MONGO_DB']

uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_uri}/{mongo_db}"

TRIPS={
    "WIEN": (date(2018, 8, 17), date(2018, 8, 20)),
    "RUSSIA": (date(2018, 7, 7), date(2018, 7, 15))
}

def __trip(made_on):
    py_made_on = made_on.to_pydatetime().date()
    for trip, dates in TRIPS.items():
        if py_made_on >= dates[0] and py_made_on <= dates[1]:
            return trip
    return None

def __classify(row):
    trip = __trip(row["made_on"])
    if trip:
        return f"TRIP_{trip}"
    else:
        if "LUCKY MUSIC NETWORK" in row["description"]:
            return "OTHER"
        elif row["category"] == "cafes_and_restaurants" or row["category"] == "alcohol_and_bars":
            return "FOOD"
        elif row["category"] == "transportation" or row["category"] == "gas_and_fuel":
            return "TRANSPORTATION"
        else:
            return "OTHER"

def main():
    mongo = MongoClient(uri)
    db = mongo["finance"]["finance"]
    data = db.find()
    mongo.close()  
    rows = []
    for i in data:
        made_on = datetime.strptime(i["made_on"], "%Y-%m-%d")
        row = [i["amount"], made_on, i["category"], i["description"]]
        rows.append(row)
    purchases = pd.DataFrame(rows, columns=["amount", "made_on", "category", "description"])
    purchases = purchases[purchases.amount < 0]
    purchases = purchases[~purchases.description.str.startswith("ESTRATTO CONTO")]
    purchases.amount *= -1
    print(purchases[purchases.amount > 100])
    purchases["class"] = purchases.apply(lambda row: __classify(row), axis=1)
    #purchases.groupby(["made_on"])["amount"].sum().plot()
    purchases['made_on'] = pd.to_datetime(purchases['made_on']) - pd.to_timedelta(7, unit='d')
    purchases.groupby(['description', pd.Grouper(key='made_on', freq='W-MON')])['amount'].sum().reset_index().sort_values('made_on').plot()
    plt.show()
    # purchases = pd.DataFrame(rows, columns=["amount", "made_on", "category", "description"])
    # purchases = purchases[purchases.amount < 0]
    # purchases = purchases[~purchases.description.str.startswith("ESTRATTO CONTO")]
    # purchases.amount *= -1
    # purchases["class"] = purchases.apply(lambda row: __classify(row), axis=1)
    # print(purchases)
    # purchases.filter(items=["class", "amount"]).groupby(["class"]).sum().plot.pie(y="amount",
    #   autopct=lambda p: '{:.0f}'.format(p * purchases.amount.sum() / 100))
    # plt.show()

if __name__ == "__main__":
    main()

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time

SEARCH_TERMS = [
#    "CB600F",
    "G310R",
#    "FZ6-N",
#    "ER-6f",
    "CB500f",
    "XJ6",
    "ER-6N",
    "CB650F",
    "MT-03",
    "MT-07"
    ]

CITY = "hela_sverige"
BLOCKET_URL = "https://www.blocket.se"

DATA_SAVEFILE_PATH = "data.csv"
PLOT_SAVEFILE_PATH = "plots/"

TIME_MULTIPLIER = 60

COLUMNS = ["Category", "Price", "Model", "Id", "Miles", "Link"]

class Motorcycle():
    link = ""
    name = ""
    price = 0
    model = 0
    miles = 0
    id = ""
    category = ""

    def __init__(self, category, link):
        self.link = link
        self.category = category
        self.load_from_url(self.get_url())

    def get_url(self) -> str:
        return BLOCKET_URL+self.link

    def load_from_url(self, url = None):
        if url is None: return
        soup = make_soup(url)
        self.set_price(soup.find("div", {"class": "hdSuAQ"}).get_text())
        try:
            self.set_model(soup.find(string="Modellår").find_next("div").get_text().rstrip())
        except AttributeError as e:
            print(e)
            print("Problably text not found")
        self.set_id(url.split("/")[-1])
        time.sleep(np.random.beta(4,6)*TIME_MULTIPLIER)


    def get_id(self):
        return self.id

    def get_price(self):
        return self.price
    
    def get_name(self):
        return self.name
    
    def get_link(self):
        return self.link
    
    def get_model(self):
        return self.model
    
    def get_miles(self):
        return self.miles
    
    def get_category(self):
        return self.category

    def set_id(self, id):
        self.id = id

    def set_price(self, price):
        price = price.replace(" ", "").rstrip(" rk")
        self.price = int(price)
       

    def set_name(self, name):
        self.name = name

    def set_link(self, link):
        self.link = link

    def set_model(self, model):
        self.model = model

    def set_miles(self, miles):
        self.miles = miles

    def set_category(self, category):
        self.category = category

class DataManager():
    motorcycles = []
    
    def __init__(self):
        self.df = pd.DataFrame(columns=COLUMNS)
    
    def add_single_motorcycle(self, motorcycle: Motorcycle):
        self.df = pd.concat(
            [self.df, pd.DataFrame(
                [[
                motorcycle.get_category(),
                motorcycle.get_price(),
                motorcycle.get_model(),
                motorcycle.get_id(),
                motorcycle.get_miles(),
                motorcycle.get_link()
                ]], 
                columns=COLUMNS)])
    
    def add_multiple_motorcycles(self, list_of_motorcycles: list[Motorcycle]):
        lst = []
        for motorcycle in list_of_motorcycles:
            lst.append([
                motorcycle.get_category(),
                motorcycle.get_price(),
                motorcycle.get_model(),
                motorcycle.get_id(),
                motorcycle.get_miles(),
                motorcycle.get_link()
                ])
        self.df = pd.concat([self.df, pd.DataFrame(lst, columns=COLUMNS)])
        self.drop_duplicates()

    def show(self):
       print(self.df)
    
    def save(self):
        self.df.to_csv(DATA_SAVEFILE_PATH, index=False)
    
    def load(self):
        self.df = pd.read_csv(DATA_SAVEFILE_PATH)
    
    def get_df(self):
        return self.df
    
    def drop_duplicates(self):
        self.df.drop_duplicates(subset=["Id"], keep="last")
    
    def generate_plots(self):
        fig, ax = plt.subplots()
        colors = cm.rainbow(np.linspace(0, 1, len(SEARCH_TERMS)))
        for (key, grp), c in zip(self.df.groupby(["Category"]), colors):
            ax = grp.plot(ax=ax, kind="scatter", x="Model", y="Price", c=np.array([c]), label=key[0])
        plt.legend(loc='best')
        plt.savefig(PLOT_SAVEFILE_PATH + "all.png")
    
    def generate_single_plot(self, category):
        fig, ax = plt.subplots()
        ax = self.df.loc[self.df["Category"] == category].plot(ax=ax, kind="scatter", x="Model", y="Price", label=category)
        plt.legend(loc='best')
        plt.savefig(PLOT_SAVEFILE_PATH + category + ".png")


def make_soup(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")
    return soup

def get_item_links(search_term):
    soup = make_soup(BLOCKET_URL + "/annonser/" + CITY + "?q=" + search_term)
    items = [item["href"] for item in soup.findAll("a", {"class": "jVZtER"})]
    return items

def parse_page():
    for category in SEARCH_TERMS:
        items = get_item_links(category)
        lst = []
        length = len(items)
        i = 1
        for item in items:
            print(f"{i}/{length} - {category}")
            i+=1
            if category.lower().replace("-", "") not in item.replace("_", ""):
                continue

            moto = Motorcycle(category, item)
            if moto.get_price() > 10000:
                lst.append(moto)

        manager.add_multiple_motorcycles(lst)

manager = DataManager()


manager.load()
#parse_page()
#manager.drop_duplicates()
#manager.save()

for category in SEARCH_TERMS:
    manager.generate_single_plot(category)

manager.generate_plots()
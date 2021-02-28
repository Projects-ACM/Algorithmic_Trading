import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

default = "IBM"

# Given a valid company name, returns the data collected from the public Alpha Vantage API
def getRequests(symbol):
    API_URL = "https://www.alphavantage.co/query"

    data = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "30min",
        "adjusted": "false",
        "outputsize": "compact",
        "datatype": "json",
        "apikey": "E1KNEXNI75GMM1JD",
    }
    r = requests.get(API_URL, data)
    return r


# Given a compact request, returns a Pandas dataframe containing the data
def getDataframe(request):
    date = []
    colnames = list(range(0, 3))
    df = pd.DataFrame(columns=colnames)
    print("Sorting the retrieved data into a dataframe...")
    for i in tqdm(request.json()['Time Series (30min)'].keys()):
        date.append(i)
        row = pd.DataFrame.from_dict(request.json()['Time Series (30min)'][i], orient='index').reset_index().T[1:]
        df = pd.concat([df, row], ignore_index=True)
    df.columns = ["open", "high", "low", "close", "volume"]
    df['date'] = date
    df["open"] = pd.to_numeric(df["open"])

    return df


# START OF PROGRAM
root = tkinter.Tk()
root.wm_title("Plotting Stocks")

df = getDataframe(getRequests(default))

fig = Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)

fig.add_subplot(111).plot(df["date"],df["open"])
plt.gca().invert_xaxis()

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


# Runs when "<Return>" is pressed in the main entry box
def on_key_press(event):
    print("key press")
    changeCompany(entry.get())

# Switches companies if the new name is valid
def changeCompany(company):

    new_df = getDataframe(getRequests(company))
    fig.clear()
    ax = fig.add_subplot(111).plot(new_df["date"], new_df["open"])
    plt.gca().invert_xaxis()

    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

# Quit button
button = tkinter.Button(master=root, text="Quit", command=_quit)
button.pack(side=tkinter.BOTTOM)

# Company switch entry box
entry = tkinter.Entry(master=root)
entry.bind('<Return>',on_key_press)
entry.pack(side=tkinter.BOTTOM)

tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.
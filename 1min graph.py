import tkinter as tk
from tkinter import LabelFrame, Entry, Button, Label, StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mplfinance as mpf
import pandas as pd
import MetaTrader5 as mt5
import datetime

# Initialize MetaTrader5
if not mt5.initialize():
    print("Failed to initialize MetaTrader5")
    exit()

# Initialize Tkinter window
root = tk.Tk()
root.geometry("1300x600")
root.title("Live Candlestick Chart")

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=2)

info_frame = LabelFrame(root, text="Information", bg="white")
info_frame.grid(row=0, sticky="nsew")

graph_frame = LabelFrame(root, text="Graph", bg="white")
graph_frame.grid(row=1, sticky="nsew")

# Global variables
candlestick_data = pd.DataFrame()
symbol = StringVar(value="XAUUSD")

def display_input():
    user_symbol = entry.get()
    label.config(text=f"Selected symbol: {user_symbol}")
    symbol.set(user_symbol)

entry = Entry(info_frame, textvariable=symbol, width=30)
entry.pack(pady=5)

button = Button(info_frame, text="Submit", command=display_input)
button.pack(pady=5)

label = Label(info_frame, text="Enter symbol (e.g., XAUUSD, EURUSD):")
label.pack(pady=5)

def fetch_and_plot():
    global candlestick_data
    user_symbol = symbol.get()

    rates = mt5.copy_rates_from_pos(user_symbol, mt5.TIMEFRAME_M1, 0, 20)
    if rates is None or len(rates) == 0:
        print(f"No data for symbol: {user_symbol}")
        return

    data = pd.DataFrame(rates)
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data.set_index('time', inplace=True)
    data = data[['open', 'high', 'low', 'close']]

    candlestick_data = data

def create_candlestick_graph(frame):
    fig, ax = plt.subplots(figsize=(13, 4), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    return fig, ax

def update_candlestick_chart(frame_number):
    global candlestick_data, fig, ax
    fetch_and_plot()
    ax.clear()
    if not candlestick_data.empty:
        mpf.plot(candlestick_data, type='candle', ax=ax, style='charles')

fig, ax = create_candlestick_graph(graph_frame)
ani = animation.FuncAnimation(fig, update_candlestick_chart, interval=1000)

root.mainloop()

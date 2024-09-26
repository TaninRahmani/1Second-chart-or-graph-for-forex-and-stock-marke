import tkinter as tk
from tkinter import LabelFrame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
import pandas as pd
import MetaTrader5 as mt5
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import datetime
import time
from tkinter import *

# Initialize MetaTrader5
mt5.initialize()

# Initialize Tkinter window
root = tk.Tk()
root.geometry("1300x600")
root.title("Live Candlestick Chart")

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=2)

# LabelFrames for layout
info_frame = LabelFrame(root, text="Information", bg="white")
info_frame.grid(row=0, sticky="nsew")
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
graph_frame = LabelFrame(root, text="Graph", bg="white")
graph_frame.grid(row=1, sticky="nsew")


# Global variable for candlestick data and symbol
candlestick_data = pd.DataFrame()
data2graph = pd.DataFrame()
symbol = tk.StringVar(value="XAUUSD")  # Default symbol

# Function to display the input and update the global symbol
def display_input():
    user_symbol = entry.get()  # Get the text from the Entry widget
    label.config(text=f"Selected symbol: {user_symbol}")  # Update the label
    symbol.set(user_symbol)  # Update the symbol StringVar

# Create an Entry widget to enter the trading symbol
entry = Entry(info_frame, textvariable=symbol, width=30)
entry.pack(pady=5)

# Button to submit the input
button = Button(info_frame, text="Submit", command=display_input)
button.pack(pady=5)

# Label to provide instructions for symbol entry
label = Label(info_frame, text="Enter symbol (e.g., XAUUSD, EURUSD):")
label.pack(pady=5)

# Function to fetch data from MetaTrader5 and plot the candlestick chart
# Function to fetch data from MetaTrader5 and plot the candlestick chart
def fetch_and_plot():
    global candlestick_data
    global data2graph
   


    # Get the symbol entered by the user
    user_symbol = symbol.get() # Retrieve the latest value of the symbol
    
    # Fetch data from MetaTrader5 (fetching last 2 minutes of data)
    rates = mt5.copy_rates_from_pos(user_symbol, mt5.TIMEFRAME_M1, 0, 10)  # Fetch last 2 minutes
    if rates is None or len(rates) == 0:  # Check for valid data
        print(f"No data retrieved for symbol: {user_symbol}")
        return

    # Create DataFrame with the fetched data
    data = pd.DataFrame(rates)
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data.set_index('time', inplace=True)

    # Resample data for smoother plotting (optional, for real-time updating purposes)
    data_resampled = data.resample('1s').interpolate(method='linear')

    # Append new data to the existing DataFrame
    candlestick_data = data_resampled
    candlestick_data = candlestick_data._append(data_resampled.iloc[-1:])

    # Keep only the last 2 minutes (120 seconds) of data
    data2graph = candlestick_data.tail(250)


# Function to create the candlestick graph (initial setup)
def create_candlestick_graph(frame):
    # Create the candlestick chart using mplfinance
    fig, ax = plt.subplots(figsize=(13, 4), dpi=100)

    # Embed the Matplotlib figure in the Tkinter frame
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    return fig, ax

# Function to update the candlestick chart
def update_candlestick_chart(frame):
    global data2graph, fig, ax 

   
    # Fetch the latest data and append to the chart data
    fetch_and_plot()

    # Clear the previous plot
    ax.clear()

    # Redraw the candlestick chart with the updated data (showing only the last 2 minutes)
    mpf.plot(data2graph, type='candle', ax=ax, style='charles')

    return ax

# Global variable to store candlestick data


# Create the candlestick graph
fig, ax = create_candlestick_graph(graph_frame)

# Use FuncAnimation to update the chart every second (1000 ms)
ani = animation.FuncAnimation(fig, update_candlestick_chart, interval=1000)

# Start the Tkinter main loop
root.mainloop()

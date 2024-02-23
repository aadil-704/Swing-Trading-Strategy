import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go

# Fetch historical stock data
def fetch_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data

# Calculate moving averages
def calculate_moving_averages(data, short_window, long_window):
    data['Short_MA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
    return data

# Generate buy/sell signals based on moving average crossovers
def generate_signals(data):
    signals = pd.DataFrame(index=data.index)
    signals['Buy'] = np.where(data['Short_MA'] > data['Long_MA'], 1.0, 0.0)
    signals['Sell'] = np.where(data['Short_MA'] < data['Long_MA'], -1.0, 0.0)
    signals['Signal'] = signals['Buy'] + signals['Sell']
    return signals

def main():
    # Streamlit UI
    st.title("Swing Trading Strategy")
    
    # Sidebar inputs
    symbol = st.sidebar.text_input("Enter stock symbol", "WIPRO.NS")
    start_date = st.sidebar.text_input("Enter start date (YYYY-MM-DD)", "2023-01-01")
    end_date = st.sidebar.text_input("Enter end date (YYYY-MM-DD)", "2024-01-01")
    short_window = st.sidebar.slider("Short window", 1, 100, 22)
    long_window = st.sidebar.slider("Long window", 1, 200, 44)  # Adjusted the range and default value

    # Fetch data
    data = fetch_data(symbol, start_date, end_date)

    # Calculate moving averages
    data = calculate_moving_averages(data, short_window, long_window)

    # Generate signals
    signals = generate_signals(data)

    # Filter data based on start and end dates
    filtered_data = data.loc[start_date:end_date]

    # Create Plotly figure for moving averages and signals visualization
    fig = go.Figure()

    # Close price
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['Close'], mode='lines', name='Close Price', line=dict(color='blue')))

    # Short moving average
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['Short_MA'], mode='lines', name='Short Moving Average', line=dict(color='orange')))

    # Long moving average
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['Long_MA'], mode='lines', name='Long Moving Average', line=dict(color='green')))

    # Buy signals
    buy_signals = filtered_data.loc[signals['Signal'] == 1.0]
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Short_MA'], mode='markers', name='Buy Signal', marker=dict(symbol='triangle-up', size=8, color='green')))

    # Sell signals
    sell_signals = filtered_data.loc[signals['Signal'] == -1.0]
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Short_MA'], mode='markers', name='Sell Signal', marker=dict(symbol='triangle-down', size=8, color='red')))

    # Update layout for the main figure
    fig.update_layout(
        title='Moving Averages and Signals',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis=dict(tickformat='%Y-%m-%d'),
        yaxis=dict(type='linear'),
        showlegend=True
    )

    # X-Axes configuration for Plotly figure
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=5, label="5m", step="minute", stepmode="backward"),
                dict(count=4, label="4h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="todate"),
                dict(count=7, label="1w", step="day", stepmode="backward"),  # Weekly time frame
                dict(step="all")
            ])
        )
    )

    # Show Plotly figure
    st.plotly_chart(fig)

    # Display the candlestick chart with X-Axes configuration
    fig_candlestick = go.Figure()

    # Candlestick
    fig_candlestick.add_trace(go.Candlestick(x=filtered_data.index,
                                              open=filtered_data['Open'],
                                              high=filtered_data['High'],
                                              low=filtered_data['Low'],
                                              close=filtered_data['Close'], name='market data'))

    # Add 20-day SMA
    fig_candlestick.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['Short_MA'], name='20-day SMA', line=dict(color='blue')))

    # Add 200-day SMA
    fig_candlestick.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['Long_MA'], name='200-day SMA', line=dict(color='red')))

    # X-Axes configuration for candlestick chart
    fig_candlestick.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=5, label="5m", step="minute", stepmode="backward"),
                dict(count=4, label="4h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="todate"),
                dict(count=7, label="1w", step="day", stepmode="backward"),  # Weekly time frame
                dict(step="all")
            ])
        )
    )
    
    # Update layout for candlestick chart
    fig_candlestick.update_layout(
        title='Candlestick chart',
        xaxis_title='Date',
        yaxis_title='Price'
    )

    st.plotly_chart(fig_candlestick)

if __name__ == "__main__":
    main()

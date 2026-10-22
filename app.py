import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Market Dashboard", layout="wide")
st.title("📈 Real-Time Stock Market Dashboard")

# Sidebar
st.sidebar.header("Settings")
tickers_input = st.sidebar.text_input(
    "Stock symbols (comma separated)", "AAPL, MSFT, GOOGL, TCS.NS"
)
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
interval = st.sidebar.selectbox("Interval", ["1d", "1wk"], index=0)

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

@st.cache_data(ttl=60)
def load_data(ticker, period, interval):
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    df = df.reset_index()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    # RSI (14)
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

for ticker in tickers:
    st.subheader(ticker)
    df = load_data(ticker, period, interval)

    if df.empty:
        st.warning(f"{ticker} ka data nahi mila. Symbol check karo.")
        continue

    last = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2] if len(df) > 1 else last
    change = last - prev
    pct = (change / prev) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Last Price", f"{last:.2f}", f"{change:.2f} ({pct:.2f}%)")
    c2.metric("High", f"{df['High'].max():.2f}")
    c3.metric("Low", f"{df['Low'].min():.2f}")
    c4.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.1f}")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Price"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA20"], name="SMA 20"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA50"], name="SMA 50"))
    fig.update_layout(height=450, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, width="stretch")

st.caption("Data source: Yahoo Finance (yfinance). Auto-refresh cache: 60 sec.")
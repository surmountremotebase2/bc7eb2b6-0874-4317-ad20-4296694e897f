from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    
    def __init__(self):
        # High-growth sectors typically include technology, biotech, and renewable energy.
        self.high_growth_tickers = ["AAPL", "MSFT", "TSLA", "NVDA", "BIIB", "CRSP", "ENPH"]
    
    @property
    def interval(self):
        # Using daily data for trend monitoring and adapting strategies.
        return "1day"
    
    @property
    def assets(self):
        return self.high_growth_tickers
    
    def run(self, data):
        allocation = {}
        
        for ticker in self.high_growth_tickers:
            try:
                # Capture trends with EMA
                short_ema = EMA(ticker, data["ohlcv"], length=12)
                long_ema = EMA(ticker, data["ohlcv"], length=26)
                # Identify overbought/oversold conditions with RSI
                rsi = RSI(ticker, data["ohlcv"], length=14)
                # Confirm trend direction and momentum with MACD
                macd = MACD(ticker, data["ohlcv"], fast=12, slow=26)["MACD"][-1]
                signal = MACD(ticker, data["ohlcv"], fast=12, slow=26)["signal"][-1]
                
                # Strategy Logic
                if short_ema[-1] > long_ema[-1] and rsi[-1] > 50 and macd > signal:
                    # Position in growth if EMA, RSI, and MACD align positively
                    allocation[ticker] = 1.0 / len(self.high_growth_tickers)
                elif short_ema[-1] < long_ema[-1] or rsi[-1] < 40:
                    # Avoid or minimize position if trend is negative or asset is oversold
                    allocation[ticker] = 0
                else:
                    # Hold existing positions if conditions are neutral
                    allocation[ticker] = allocation.get(ticker, 1.0 / len(self.high_growth_tickers))
            except Exception as e:
                log(f"Error processing {ticker}: {str(e)}")
                # In case of errors, avoid altering allocation for this iteration
                allocation[ticker] = allocation.get(ticker, 0)
        
        return TargetAllocation(allocation)
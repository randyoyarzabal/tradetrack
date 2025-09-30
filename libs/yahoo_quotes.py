"""
Yahoo Finance API integration for the Stock Portfolio Tracker.
Replaces TD Ameritrade API with free Yahoo Finance data.
"""

import yfinance as yf
import time
from typing import Dict, List, Optional, Any
from .config_loader import get_config_loader


class YahooQuotes:
    """Handles Yahoo Finance API integration for stock and crypto quotes."""
    
    def __init__(self):
        """Initialize the Yahoo Finance client."""
        self.config_loader = get_config_loader()
        self.api_config = self.config_loader.get_api_config()['yahoo']
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamps: Dict[str, float] = {}
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data for a symbol is still valid."""
        if symbol not in self.cache_timestamps:
            return False
        
        cache_duration = self.api_config['cache_duration']
        return time.time() - self.cache_timestamps[symbol] < cache_duration
    
    def _get_ticker_data(self, symbol: str) -> Optional[yf.Ticker]:
        """
        Get ticker data for a symbol with caching.
        
        Args:
            symbol: Stock or crypto symbol
            
        Returns:
            yfinance Ticker object or None if failed
        """
        try:
            return yf.Ticker(symbol)
        except Exception as e:
            print(f"WARNING: Failed to create ticker for {symbol}: {e}")
            return None
    
    def _get_quote_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get quote data for a symbol with caching and retries.
        
        Args:
            symbol: Stock or crypto symbol
            
        Returns:
            Dictionary containing quote data or None if failed
        """
        # Check cache first
        if symbol in self.cache and self._is_cache_valid(symbol):
            return self.cache[symbol]
        
        ticker = self._get_ticker_data(symbol)
        if not ticker:
            return None
        
        retries = self.api_config['retries']
        timeout = self.api_config['timeout']
        
        for attempt in range(retries + 1):
            try:
                # Get current price and basic info
                info = ticker.info
                history = ticker.history(period="2d")
                
                if history.empty:
                    print(f"WARNING: No price data available for {symbol}")
                    return None
                
                # Extract relevant data
                current_price = history['Close'].iloc[-1]
                previous_close = history['Close'].iloc[-2] if len(history) > 1 else current_price
                
                quote_data = {
                    'symbol': symbol,
                    'current_price': float(current_price),
                    'previous_close': float(previous_close),
                    'open_price': float(history['Open'].iloc[-1]),
                    'day_high': float(history['High'].iloc[-1]),
                    'day_low': float(history['Low'].iloc[-1]),
                    'volume': int(history['Volume'].iloc[-1]),
                    'description': info.get('longName', symbol),
                    'currency': info.get('currency', 'USD'),
                    'exchange': info.get('exchange', 'Unknown'),
                    'market_cap': info.get('marketCap'),
                    'pe_ratio': info.get('trailingPE'),
                    'dividend_yield': info.get('dividendYield'),
                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                    'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                    'timestamp': time.time()
                }
                
                # Cache the data
                self.cache[symbol] = quote_data
                self.cache_timestamps[symbol] = time.time()
                
                return quote_data
                
            except Exception as e:
                if attempt < retries:
                    print(f"WARNING: Attempt {attempt + 1} failed for {symbol}: {e}")
                    time.sleep(1)  # Wait before retry
                else:
                    print(f"ERROR: Failed to get quote for {symbol} after {retries + 1} attempts: {e}")
                    return None
        
        return None
    
    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get quotes for multiple symbols.
        
        Args:
            symbols: List of stock/crypto symbols
            
        Returns:
            Dictionary mapping symbols to quote data
        """
        quotes = {}
        
        for symbol in symbols:
            quote_data = self._get_quote_data(symbol)
            if quote_data:
                quotes[symbol] = quote_data
            else:
                print(f"WARNING: Could not get quote for {symbol}")
        
        return quotes
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get quote for a single symbol.
        
        Args:
            symbol: Stock or crypto symbol
            
        Returns:
            Quote data dictionary or None if failed
        """
        return self._get_quote_data(symbol)
    
    def is_crypto(self, symbol: str) -> bool:
        """
        Check if a symbol is a cryptocurrency.
        
        Args:
            symbol: Symbol to check
            
        Returns:
            True if symbol is crypto, False otherwise
        """
        crypto_symbols = self.config_loader.get_crypto_symbols()
        return symbol.upper() in [s.upper() for s in crypto_symbols]
    
    def get_market_movers(self, index: str = "SPY", direction: str = "up") -> List[Dict[str, Any]]:
        """
        Get market movers for an index.
        
        Args:
            index: Index symbol (e.g., "SPY", "QQQ", "DIA")
            direction: "up" or "down"
            
        Returns:
            List of mover data
        """
        try:
            ticker = yf.Ticker(index)
            # This is a simplified implementation
            # In practice, you might want to use a different approach
            # as yfinance doesn't have a direct movers API
            return []
        except Exception as e:
            print(f"WARNING: Could not get movers for {index}: {e}")
            return []
    
    def clear_cache(self):
        """Clear the quote cache."""
        self.cache.clear()
        self.cache_timestamps.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cached_symbols': len(self.cache),
            'cache_hit_rate': len([s for s in self.cache_timestamps if self._is_cache_valid(s)]) / max(len(self.cache_timestamps), 1),
            'oldest_cache': min(self.cache_timestamps.values()) if self.cache_timestamps else None,
            'newest_cache': max(self.cache_timestamps.values()) if self.cache_timestamps else None
        }


# Global Yahoo quotes instance
_yahoo_quotes: Optional[YahooQuotes] = None


def get_yahoo_quotes() -> YahooQuotes:
    """Get the global Yahoo quotes instance."""
    global _yahoo_quotes
    if _yahoo_quotes is None:
        _yahoo_quotes = YahooQuotes()
    return _yahoo_quotes


def get_quotes(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """Get quotes for multiple symbols using the global instance."""
    return get_yahoo_quotes().get_quotes(symbols)


def get_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """Get quote for a single symbol using the global instance."""
    return get_yahoo_quotes().get_quote(symbol)

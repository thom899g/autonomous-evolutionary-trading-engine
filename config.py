"""
Configuration management for the Evolutionary Trading Engine.
Centralizes all configurable parameters with environment variable support.
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
from enum import Enum

# Environment variable defaults
os.environ.setdefault('FIREBASE_CREDENTIALS_PATH', './firebase-credentials.json')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('MAX_EVOLUTION_GENERATIONS', '100')
os.environ.setdefault('POPULATION_SIZE', '50')

class Market(Enum):
    """Supported markets for trading"""
    SPOT = "spot"
    FUTURES = "futures"
    MARGIN = "margin"

class Exchange(Enum):
    """Supported exchanges via CCXT"""
    BINANCE = "binance"
    COINBASE = "coinbase"
    KRAKEN = "kraken"

@dataclass
class EvolutionConfig:
    """Evolutionary algorithm configuration"""
    population_size: int = int(os.getenv('POPULATION_SIZE', 50))
    mutation_rate: float = 0.15
    crossover_rate: float = 0.65
    elitism_count: int = 2
    max_generations: int = int(os.getenv('MAX_EVOLUTION_GENERATIONS', 100))
    fitness_threshold: float = 0.85
    diversity_penalty: float = 0.3
    
    def validate(self) -> None:
        """Validate configuration parameters"""
        if not 0 <= self.mutation_rate <= 1:
            raise ValueError(f"mutation_rate must be between 0 and 1, got {self.mutation_rate}")
        if not 0 <= self.crossover_rate <= 1:
            raise ValueError(f"crossover_rate must be between 0 and 1, got {self.crossover_rate}")
        if self.elitism_count >= self.population_size:
            raise ValueError(f"elitism_count ({self.elitism_count}) must be less than population_size ({self.population_size})")

@dataclass
class TradingConfig:
    """Trading engine configuration"""
    exchange: Exchange = Exchange.BINANCE
    market: Market = Market.SPOT
    base_currency: str = "USDT"
    initial_capital: float = 10000.0
    max_position_size: float = 0.1  # 10% of capital
    stop_loss_pct: float = 0.02  # 2% stop loss
    take_profit_pct: float = 0.05  # 5% take profit
    max_open_positions: int = 5
    risk_free_rate: float = 0.02  # For Sharpe ratio calculation
    
    def validate(self) -> None:
        """Validate trading configuration"""
        if self.initial_capital <= 0:
            raise ValueError(f"initial_capital must be positive, got {self.initial_capital}")
        if not 0 < self.max_position_size <= 1:
            raise ValueError(f"max_position_size must be between 0 and 1, got {self.max_position_size}")

@dataclass
class DataConfig:
    """Data fetching configuration"""
    timeframe: str = "1h"
    lookback_periods: int = 200
    symbols: List[str] = None
    data_source: str = "ccxt"  # Alternatives: "local_csv", "firestore_cache"
    
    def __post_init__(self):
        """Initialize default symbols if not provided"""
        if self.symbols is None:
            self.symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT"]
    
    def validate(self) -> None:
        """Validate data configuration"""
        valid_timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
        if self.timeframe not in valid_timeframes:
            raise ValueError(f"timeframe must be one of {valid_timeframes}, got {self.timeframe}")
        if self.lookback_periods < 50:
            raise ValueError(f"lookback_periods must be at least 50, got {self.lookback_periods}")

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.evolution = EvolutionConfig()
        self.trading = TradingConfig()
        self.data = DataConfig()
        self.firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Validate all configurations
        self._validate()
    
    def _validate(self) -> None:
        """Validate all configuration sections"""
        self.evolution.validate()
        self.trading.validate()
        self.data.validate()
        
        # Check Firebase credentials exist
        if self.firebase_credentials_path and not os.path.exists(self.firebase_credentials_path):
            logging.warning(f"Firebase credentials not found at {self.firebase_credentials_path}. Firebase features will be disabled.")
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables"""
        return cls()
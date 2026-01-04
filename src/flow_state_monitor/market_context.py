"""
Market context analysis for relative strength comparison.

This module compares a stock's price performance against major market benchmarks
(SPY and QQQ) to provide context on whether the stock is outperforming or
underperforming the broader market.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class RelativeStrength:
    """Relative strength comparison data."""
    symbol: str
    stock_return: float
    spy_return: float
    qqq_return: Optional[float]
    spy_relative: float  # stock return - spy return
    qqq_relative: Optional[float]  # stock return - qqq return
    outperforming_spy: bool
    outperforming_qqq: Optional[bool]
    description: str


class MarketContextAnalyzer:
    """
    Analyze relative strength by comparing stock performance to benchmarks.

    Compares against:
    - SPY: S&P 500 (broad market, 500 large-cap US stocks)
    - QQQ: Nasdaq-100 (tech-heavy, 100 largest non-financial Nasdaq stocks)
    """

    DEFAULT_BENCHMARKS = ['SPY', 'QQQ']

    def __init__(self):
        """Initialize market context analyzer."""
        self.benchmarks = self.DEFAULT_BENCHMARKS

    def calculate_return(self, prices: list) -> Optional[float]:
        """
        Calculate total return from price list.

        Args:
            prices: List of closing prices (oldest to newest)

        Returns:
            Percentage return, or None if insufficient data
        """
        if not prices or len(prices) < 2:
            logger.debug(f"Insufficient price data: {len(prices) if prices else 0} points")
            return None

        # Filter out None values
        valid_prices = [p for p in prices if p is not None]
        if len(valid_prices) < 2:
            logger.debug(f"Insufficient valid prices: {len(valid_prices)} after filtering")
            return None

        start_price = valid_prices[0]
        end_price = valid_prices[-1]

        if start_price <= 0:
            logger.debug(f"Invalid start price: {start_price}")
            return None

        return_pct = ((end_price - start_price) / start_price) * 100
        logger.debug(f"Calculated return: {return_pct:.2f}% (from {start_price:.2f} to {end_price:.2f})")
        return return_pct

    def analyze_relative_strength(
        self,
        symbol: str,
        stock_prices: list,
        benchmark_prices: Dict[str, Optional[list]]
    ) -> RelativeStrength:
        """
        Analyze stock's relative strength vs benchmarks.

        Args:
            symbol: Stock symbol being analyzed
            stock_prices: List of stock closing prices
            benchmark_prices: Dict mapping benchmark symbols to their price lists

        Returns:
            RelativeStrength object with comparison results
        """
        # Calculate stock return
        stock_return = self.calculate_return(stock_prices)
        if stock_return is None:
            logger.warning(f"Could not calculate return for {symbol}")
            stock_return = 0.0

        # Calculate SPY return
        spy_prices = benchmark_prices.get('SPY')
        spy_return = self.calculate_return(spy_prices) if spy_prices else None
        if spy_return is None:
            logger.warning("Could not calculate SPY return")
            spy_return = 0.0

        # Calculate QQQ return
        qqq_prices = benchmark_prices.get('QQQ')
        qqq_return = self.calculate_return(qqq_prices) if qqq_prices else None

        # Calculate relative performance
        spy_relative = stock_return - spy_return
        qqq_relative = (stock_return - qqq_return) if qqq_return is not None else None

        outperforming_spy = spy_relative > 0
        outperforming_qqq = (qqq_relative > 0) if qqq_relative is not None else None

        # Generate description
        description = self._generate_description(
            symbol, stock_return, spy_return, qqq_return,
            outperforming_spy, outperforming_qqq
        )

        return RelativeStrength(
            symbol=symbol,
            stock_return=stock_return,
            spy_return=spy_return,
            qqq_return=qqq_return,
            spy_relative=spy_relative,
            qqq_relative=qqq_relative,
            outperforming_spy=outperforming_spy,
            outperforming_qqq=outperforming_qqq,
            description=description
        )

    def _generate_description(
        self,
        symbol: str,
        stock_return: float,
        spy_return: float,
        qqq_return: Optional[float],
        outperforming_spy: bool,
        outperforming_qqq: Optional[bool]
    ) -> str:
        """Generate human-readable description of relative strength."""
        lines = []

        # Stock performance
        lines.append(f"{symbol}: {stock_return:+.2f}%")

        # SPY comparison
        spy_diff = stock_return - spy_return
        spy_status = "outperforming" if outperforming_spy else "underperforming"
        lines.append(f"vs SPY ({spy_return:+.2f}%): {spy_status} by {spy_diff:+.2f}%")

        # QQQ comparison (if available)
        if qqq_return is not None and outperforming_qqq is not None:
            qqq_diff = stock_return - qqq_return
            qqq_status = "outperforming" if outperforming_qqq else "underperforming"
            lines.append(f"vs QQQ ({qqq_return:+.2f}%): {qqq_status} by {qqq_diff:+.2f}%")

        return " | ".join(lines)

    def get_benchmark_prices(self, fetcher, days: int = 25) -> Dict[str, Optional[list]]:
        """
        Fetch price data for benchmarks.

        Args:
            fetcher: Data fetcher instance with fetch_daily_bars() method
            days: Number of days of historical data to fetch

        Returns:
            Dict mapping benchmark symbols to their closing price lists
        """
        benchmark_prices = {}

        for benchmark in self.benchmarks:
            try:
                data = fetcher.fetch_daily_bars(benchmark, days=days)
                # Try both 'prices' and 'closes' keys for compatibility with different fetchers
                prices = data.get('prices', data.get('closes', []))
                benchmark_prices[benchmark] = prices
                logger.info(f"Fetched {benchmark} prices ({len(prices)} bars)")
            except Exception as e:
                logger.warning(f"Failed to fetch {benchmark} data: {e}")
                benchmark_prices[benchmark] = None

        return benchmark_prices


def format_relative_strength(rs: RelativeStrength, flow_state: str) -> str:
    """
    Format relative strength into a user-friendly message with warnings.

    Args:
        rs: RelativeStrength object
        flow_state: Current flow state ('ON', 'OFF', 'WEAKENING', etc.)

    Returns:
        Formatted string with relative strength analysis and warnings
    """
    lines = []
    lines.append("\n" + "="*60)
    lines.append("RELATIVE STRENGTH ANALYSIS")
    lines.append("="*60)
    lines.append(rs.description)

    # Add warnings for conflicting signals
    if flow_state == 'ON' and not rs.outperforming_spy:
        lines.append("\n⚠️  WARNING: Flow is ON but stock is underperforming SPY")
        lines.append("    This may indicate a weak or false signal.")

    if flow_state == 'ON' and rs.outperforming_qqq is False:
        lines.append("\n⚠️  WARNING: Flow is ON but stock is underperforming QQQ")
        lines.append("    This may indicate a weak or false signal.")

    if flow_state == 'OFF' and rs.outperforming_spy:
        lines.append("\n💡 NOTE: Flow is OFF but stock is outperforming SPY")
        lines.append("    Stock may have momentum independent of short interest.")

    lines.append("="*60)

    return "\n".join(lines)


def check_narrative_boundary(rs: RelativeStrength, flow_state: str, borrow_rate: float) -> str:
    """
    Check if we're at the boundary between money flow and narrative domains.

    Args:
        rs: RelativeStrength object
        flow_state: Current flow state ('ON', 'OFF', 'WEAKENING', etc.)
        borrow_rate: Current borrow rate percentage

    Returns:
        Hint message if at boundary, empty string otherwise
    """
    # Only show hint for Flow OFF with low borrow rate and significant movement
    if flow_state != 'OFF' or borrow_rate >= 5.0:
        return ""

    # Check for significant price movement or relative performance divergence
    significant_move = abs(rs.stock_return) > 5.0
    significant_divergence = abs(rs.spy_relative) > 3.0 or (rs.qqq_relative and abs(rs.qqq_relative) > 3.0)

    if significant_move or significant_divergence:
        return (
            "\n💭 HINT: Significant price movement without flow pressure detected.\n"
            "    Consider narrative analysis for non-mechanical drivers.\n"
            "    See docs/money_flow_vs_narrative.md for more info."
        )

    return ""

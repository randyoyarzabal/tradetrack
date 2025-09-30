"""
Lot Analysis Library for Portfolio Management.
Handles individual lot tracking, aging, and portfolio analytics.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class LotPerformance:
    """Performance metrics for a single lot."""
    symbol: str
    lot_index: int
    purchase_date: datetime
    shares: float
    cost_basis: float
    current_price: Optional[float]
    days_held: int
    years_held: float
    total_cost: float
    current_value: Optional[float]
    unrealized_gain_loss: Optional[float]
    unrealized_gain_loss_pct: Optional[float]
    annualized_return: Optional[float]


class LotAnalyzer:
    """
    Analyzes individual lots and provides portfolio analytics.
    Handles lot aging, performance tracking, and optimization suggestions.
    """

    def __init__(self):
        """Initialize the lot analyzer."""
        self.long_term_threshold_days = 365  # 1 year in days

    def analyze_lot_performance(self, symbol: str, lot: Dict[str, Any],
                                lot_index: int, current_price: Optional[float] = None) -> LotPerformance:
        """
        Analyze performance metrics for a single lot.

        Args:
            symbol: Stock symbol
            lot: Lot data dictionary
            lot_index: Index of the lot
            current_price: Current market price (optional)

        Returns:
            LotPerformance: Performance analysis for the lot
        """
        # Parse purchase date
        purchase_date = datetime.strptime(lot['date'], '%Y-%m-%d')

        # Calculate holding period
        days_held = (datetime.now() - purchase_date).days
        years_held = days_held / 365.25

        # Calculate cost basis
        shares = lot['shares']
        cost_basis = lot['cost_basis']
        total_cost = shares * cost_basis

        # Calculate current value and gains if price available
        current_value = None
        unrealized_gain_loss = None
        unrealized_gain_loss_pct = None
        annualized_return = None

        if current_price is not None:
            current_value = shares * current_price
            unrealized_gain_loss = current_value - total_cost
            unrealized_gain_loss_pct = (
                unrealized_gain_loss / total_cost * 100) if total_cost > 0 else 0

            # Calculate annualized return
            if years_held > 0:
                annualized_return = (
                    (current_value / total_cost) ** (1 / years_held) - 1) * 100

        return LotPerformance(
            symbol=symbol,
            lot_index=lot_index,
            purchase_date=purchase_date,
            shares=shares,
            cost_basis=cost_basis,
            current_price=current_price,
            days_held=days_held,
            years_held=years_held,
            total_cost=total_cost,
            current_value=current_value,
            unrealized_gain_loss=unrealized_gain_loss,
            unrealized_gain_loss_pct=unrealized_gain_loss_pct,
            annualized_return=annualized_return
        )

    def analyze_portfolio_lots(self, portfolio_data: Dict[str, Any],
                               current_prices: Optional[Dict[str, float]] = None) -> List[LotPerformance]:
        """
        Analyze performance for all lots in a portfolio.

        Args:
            portfolio_data: Portfolio data dictionary
            current_prices: Dictionary of current prices by symbol

        Returns:
            List[LotPerformance]: Performance analysis for all lots
        """
        performance_list = []

        for symbol, stock_data in portfolio_data.get('stocks', {}).items():
            lots = stock_data.get('lots', [])
            current_price = current_prices.get(
                symbol) if current_prices else None

            for i, lot in enumerate(lots):
                performance = self.analyze_lot_performance(
                    symbol, lot, i, current_price)
                performance_list.append(performance)

        return performance_list

    def get_lots_by_age(self, performance_list: List[LotPerformance],
                        min_days: int = 0, max_days: Optional[int] = None) -> List[LotPerformance]:
        """
        Get lots within a specific age range.

        Args:
            performance_list: List of lot performance data
            min_days: Minimum days held
            max_days: Maximum days held (None for no limit)

        Returns:
            List[LotPerformance]: Filtered lots
        """
        filtered = []
        for lot in performance_list:
            if lot.days_held >= min_days:
                if max_days is None or lot.days_held <= max_days:
                    filtered.append(lot)
        return filtered

    def get_oldest_lots(self, performance_list: List[LotPerformance],
                        count: int = 5) -> List[LotPerformance]:
        """Get the oldest lots in the portfolio."""
        sorted_lots = sorted(
            performance_list, key=lambda x: x.days_held, reverse=True)
        return sorted_lots[:count]

    def get_newest_lots(self, performance_list: List[LotPerformance],
                        count: int = 5) -> List[LotPerformance]:
        """Get the newest lots in the portfolio."""
        sorted_lots = sorted(performance_list, key=lambda x: x.days_held)
        return sorted_lots[:count]

    def get_best_performing_lots(self, performance_list: List[LotPerformance],
                                 count: int = 5) -> List[LotPerformance]:
        """Get the best performing lots by percentage gain."""
        lots_with_gains = [lot for lot in performance_list
                           if lot.unrealized_gain_loss_pct is not None]
        sorted_lots = sorted(
            lots_with_gains, key=lambda x: x.unrealized_gain_loss_pct, reverse=True)
        return sorted_lots[:count]

    def get_worst_performing_lots(self, performance_list: List[LotPerformance],
                                  count: int = 5) -> List[LotPerformance]:
        """Get the worst performing lots by percentage loss."""
        lots_with_gains = [lot for lot in performance_list
                           if lot.unrealized_gain_loss_pct is not None]
        sorted_lots = sorted(
            lots_with_gains, key=lambda x: x.unrealized_gain_loss_pct)
        return sorted_lots[:count]

    def calculate_portfolio_metrics(self, performance_list: List[LotPerformance]) -> Dict[str, Any]:
        """
        Calculate portfolio-level metrics.

        Args:
            performance_list: List of lot performance data

        Returns:
            Dict: Portfolio metrics
        """
        if not performance_list:
            return {}

        # Basic counts
        total_lots = len(performance_list)
        lots_with_prices = [
            lot for lot in performance_list if lot.current_price is not None]

        # Cost basis metrics
        total_cost = sum(lot.total_cost for lot in performance_list)
        avg_cost_per_lot = total_cost / total_lots if total_lots > 0 else 0

        # Performance metrics (only for lots with current prices)
        if lots_with_prices:
            total_current_value = sum(
                lot.current_value for lot in lots_with_prices)
            total_unrealized_gains = sum(
                lot.unrealized_gain_loss for lot in lots_with_prices)
            total_gains_pct = (total_unrealized_gains /
                               total_cost * 100) if total_cost > 0 else 0

            # Calculate weighted average return
            gains_pcts = [lot.unrealized_gain_loss_pct for lot in lots_with_prices
                          if lot.unrealized_gain_loss_pct is not None]
            avg_gains_pct = statistics.mean(gains_pcts) if gains_pcts else 0

            # Calculate weighted average annualized return
            annualized_returns = [lot.annualized_return for lot in lots_with_prices
                                  if lot.annualized_return is not None]
            avg_annualized_return = statistics.mean(
                annualized_returns) if annualized_returns else 0
        else:
            total_current_value = None
            total_unrealized_gains = None
            total_gains_pct = None
            avg_gains_pct = None
            avg_annualized_return = None

        # Age metrics
        days_held = [lot.days_held for lot in performance_list]
        avg_days_held = statistics.mean(days_held) if days_held else 0
        oldest_lot_days = max(days_held) if days_held else 0
        newest_lot_days = min(days_held) if days_held else 0

        # Long-term vs short-term breakdown
        long_term_lots = [
            lot for lot in performance_list if lot.days_held >= self.long_term_threshold_days]
        short_term_lots = [
            lot for lot in performance_list if lot.days_held < self.long_term_threshold_days]

        return {
            'total_lots': total_lots,
            'lots_with_prices': len(lots_with_prices),
            'total_cost': total_cost,
            'avg_cost_per_lot': avg_cost_per_lot,
            'total_current_value': total_current_value,
            'total_unrealized_gains': total_unrealized_gains,
            'total_gains_pct': total_gains_pct,
            'avg_gains_pct': avg_gains_pct,
            'avg_annualized_return': avg_annualized_return,
            'avg_days_held': avg_days_held,
            'oldest_lot_days': oldest_lot_days,
            'newest_lot_days': newest_lot_days,
            'long_term_lots': len(long_term_lots),
            'short_term_lots': len(short_term_lots),
            'long_term_pct': (len(long_term_lots) / total_lots * 100) if total_lots > 0 else 0
        }

    def suggest_lot_consolidation(self, performance_list: List[LotPerformance]) -> List[Dict[str, Any]]:
        """
        Suggest lot consolidation opportunities.

        Args:
            performance_list: List of lot performance data

        Returns:
            List[Dict]: Consolidation suggestions
        """
        suggestions = []

        # Group lots by symbol
        symbol_groups = {}
        for lot in performance_list:
            if lot.symbol not in symbol_groups:
                symbol_groups[lot.symbol] = []
            symbol_groups[lot.symbol].append(lot)

        # Analyze each symbol for consolidation opportunities
        for symbol, lots in symbol_groups.items():
            if len(lots) > 1:
                # Check if lots have similar cost basis (within 5%)
                cost_bases = [lot.cost_basis for lot in lots]
                avg_cost_basis = statistics.mean(cost_bases)

                similar_cost_lots = []
                for lot in lots:
                    cost_diff_pct = abs(
                        lot.cost_basis - avg_cost_basis) / avg_cost_basis * 100
                    if cost_diff_pct <= 5:  # Within 5%
                        similar_cost_lots.append(lot)

                if len(similar_cost_lots) > 1:
                    total_shares = sum(lot.shares for lot in similar_cost_lots)
                    weighted_avg_cost = sum(
                        lot.total_cost for lot in similar_cost_lots) / total_shares

                    suggestions.append({
                        'symbol': symbol,
                        'lots_count': len(similar_cost_lots),
                        'total_shares': total_shares,
                        'weighted_avg_cost': weighted_avg_cost,
                        'reason': f'Multiple lots with similar cost basis (within 5%)',
                        'lots': similar_cost_lots
                    })

        return suggestions

    def get_lot_aging_timeline(self, performance_list: List[LotPerformance]) -> Dict[str, List[LotPerformance]]:
        """
        Get lots organized by aging timeline.

        Args:
            performance_list: List of lot performance data

        Returns:
            Dict: Lots organized by age categories
        """
        timeline = {
            'new_0_30_days': [],
            'recent_31_90_days': [],
            'medium_91_365_days': [],
            'long_term_1_2_years': [],
            'very_long_term_2_plus_years': []
        }

        for lot in performance_list:
            days = lot.days_held
            if days <= 30:
                timeline['new_0_30_days'].append(lot)
            elif days <= 90:
                timeline['recent_31_90_days'].append(lot)
            elif days < 365:
                timeline['medium_91_365_days'].append(lot)
            elif days < 730:  # 2 years
                timeline['long_term_1_2_years'].append(lot)
            else:
                timeline['very_long_term_2_plus_years'].append(lot)

        return timeline

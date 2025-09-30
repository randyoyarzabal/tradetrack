"""
Tax Analysis Library for Portfolio Management.
Handles lot aging, capital gains calculations, and tax optimization.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LotTaxInfo:
    """Tax information for a single lot."""
    symbol: str
    lot_index: int
    purchase_date: datetime
    shares: float
    cost_basis: float
    current_price: Optional[float]
    days_held: int
    years_held: float
    is_long_term: bool
    total_cost: float
    current_value: Optional[float]
    unrealized_gain_loss: Optional[float]
    unrealized_gain_loss_pct: Optional[float]
    tax_treatment: str


class TaxAnalyzer:
    """
    Analyzes tax implications of portfolio holdings.
    Focuses on lot aging and capital gains calculations.
    """

    def __init__(self):
        """Initialize the tax analyzer."""
        self.long_term_threshold_days = 365  # 1 year in days
        self.long_term_threshold_years = 1.0  # 1 year in years

    def analyze_lot_tax_info(self, symbol: str, lot: Dict[str, Any],
                             lot_index: int, current_price: Optional[float] = None) -> LotTaxInfo:
        """
        Analyze tax information for a single lot.

        Args:
            symbol: Stock symbol
            lot: Lot data dictionary
            lot_index: Index of the lot
            current_price: Current market price (optional)

        Returns:
            LotTaxInfo: Tax analysis for the lot
        """
        # Parse purchase date
        purchase_date = datetime.strptime(lot['date'], '%Y-%m-%d')

        # Calculate holding period
        days_held = (datetime.now() - purchase_date).days
        years_held = days_held / 365.25

        # Determine if long-term
        is_long_term = years_held >= self.long_term_threshold_years

        # Calculate cost basis
        shares = lot['shares']
        cost_basis = lot['cost_basis']
        total_cost = shares * cost_basis

        # Calculate current value and gains if price available
        current_value = None
        unrealized_gain_loss = None
        unrealized_gain_loss_pct = None

        if current_price is not None:
            current_value = shares * current_price
            unrealized_gain_loss = current_value - total_cost
            unrealized_gain_loss_pct = (
                unrealized_gain_loss / total_cost * 100) if total_cost > 0 else 0

        # Determine tax treatment
        if is_long_term:
            tax_treatment = "Long-term capital gains (no tax if held 1+ years)"
        else:
            tax_treatment = "Short-term capital gains (ordinary income tax rates)"

        return LotTaxInfo(
            symbol=symbol,
            lot_index=lot_index,
            purchase_date=purchase_date,
            shares=shares,
            cost_basis=cost_basis,
            current_price=current_price,
            days_held=days_held,
            years_held=years_held,
            is_long_term=is_long_term,
            total_cost=total_cost,
            current_value=current_value,
            unrealized_gain_loss=unrealized_gain_loss,
            unrealized_gain_loss_pct=unrealized_gain_loss_pct,
            tax_treatment=tax_treatment
        )

    def analyze_portfolio_tax_info(self, portfolio_data: Dict[str, Any],
                                   current_prices: Optional[Dict[str, float]] = None) -> List[LotTaxInfo]:
        """
        Analyze tax information for all lots in a portfolio.

        Args:
            portfolio_data: Portfolio data dictionary
            current_prices: Dictionary of current prices by symbol

        Returns:
            List[LotTaxInfo]: Tax analysis for all lots
        """
        tax_info_list = []

        for symbol, stock_data in portfolio_data.get('stocks', {}).items():
            lots = stock_data.get('lots', [])
            current_price = current_prices.get(
                symbol) if current_prices else None

            for i, lot in enumerate(lots):
                tax_info = self.analyze_lot_tax_info(
                    symbol, lot, i, current_price)
                tax_info_list.append(tax_info)

        return tax_info_list

    def get_short_term_lots(self, tax_info_list: List[LotTaxInfo]) -> List[LotTaxInfo]:
        """Get all short-term lots (held less than 1 year)."""
        return [lot for lot in tax_info_list if not lot.is_long_term]

    def get_long_term_lots(self, tax_info_list: List[LotTaxInfo]) -> List[LotTaxInfo]:
        """Get all long-term lots (held 1+ years)."""
        return [lot for lot in tax_info_list if lot.is_long_term]

    def get_lots_approaching_long_term(self, tax_info_list: List[LotTaxInfo],
                                       days_threshold: int = 30) -> List[LotTaxInfo]:
        """
        Get lots that are approaching long-term status.

        Args:
            tax_info_list: List of tax info for lots
            days_threshold: Days within long-term threshold to consider "approaching"

        Returns:
            List[LotTaxInfo]: Lots approaching long-term status
        """
        approaching = []
        for lot in tax_info_list:
            if not lot.is_long_term:
                days_until_long_term = self.long_term_threshold_days - lot.days_held
                if 0 < days_until_long_term <= days_threshold:
                    approaching.append(lot)
        return approaching

    def calculate_tax_summary(self, tax_info_list: List[LotTaxInfo]) -> Dict[str, Any]:
        """
        Calculate tax summary for all lots.

        Args:
            tax_info_list: List of tax info for lots

        Returns:
            Dict: Tax summary statistics
        """
        short_term_lots = self.get_short_term_lots(tax_info_list)
        long_term_lots = self.get_long_term_lots(tax_info_list)

        # Calculate totals
        short_term_cost = sum(lot.total_cost for lot in short_term_lots)
        long_term_cost = sum(lot.total_cost for lot in long_term_lots)
        total_cost = short_term_cost + long_term_cost

        # Calculate unrealized gains/losses (only for lots with current prices)
        short_term_gains = sum(lot.unrealized_gain_loss for lot in short_term_lots
                               if lot.unrealized_gain_loss is not None)
        long_term_gains = sum(lot.unrealized_gain_loss for lot in long_term_lots
                              if lot.unrealized_gain_loss is not None)
        total_gains = short_term_gains + long_term_gains

        return {
            'total_lots': len(tax_info_list),
            'short_term_lots': len(short_term_lots),
            'long_term_lots': len(long_term_lots),
            'short_term_cost': short_term_cost,
            'long_term_cost': long_term_cost,
            'total_cost': total_cost,
            'short_term_gains': short_term_gains,
            'long_term_gains': long_term_gains,
            'total_gains': total_gains,
            'short_term_gains_pct': (short_term_gains / short_term_cost * 100) if short_term_cost > 0 else 0,
            'long_term_gains_pct': (long_term_gains / long_term_cost * 100) if long_term_cost > 0 else 0,
            'total_gains_pct': (total_gains / total_cost * 100) if total_cost > 0 else 0
        }

    def suggest_tax_optimization(self, tax_info_list: List[LotTaxInfo]) -> Dict[str, Any]:
        """
        Suggest tax optimization strategies.

        Args:
            tax_info_list: List of tax info for lots

        Returns:
            Dict: Tax optimization suggestions
        """
        suggestions = {
            'tax_loss_harvesting': [],
            'hold_for_long_term': [],
            'consider_selling_short_term': [],
            'general_advice': []
        }

        # Find lots with losses for tax-loss harvesting
        for lot in tax_info_list:
            if lot.unrealized_gain_loss is not None and lot.unrealized_gain_loss < 0:
                if lot.is_long_term:
                    suggestions['tax_loss_harvesting'].append({
                        'symbol': lot.symbol,
                        'lot_index': lot.lot_index,
                        'loss': lot.unrealized_gain_loss,
                        'reason': 'Long-term loss - good for tax-loss harvesting'
                    })
                else:
                    suggestions['tax_loss_harvesting'].append({
                        'symbol': lot.symbol,
                        'lot_index': lot.lot_index,
                        'loss': lot.unrealized_gain_loss,
                        'reason': 'Short-term loss - can offset short-term gains'
                    })

        # Find lots approaching long-term status
        approaching_long_term = self.get_lots_approaching_long_term(
            tax_info_list)
        for lot in approaching_long_term:
            days_until_long_term = self.long_term_threshold_days - lot.days_held
            suggestions['hold_for_long_term'].append({
                'symbol': lot.symbol,
                'lot_index': lot.lot_index,
                'days_until_long_term': days_until_long_term,
                'reason': f'Only {days_until_long_term} days until long-term status'
            })

        # Find short-term lots with significant gains
        for lot in tax_info_list:
            if (not lot.is_long_term and
                lot.unrealized_gain_loss is not None and
                lot.unrealized_gain_loss > 0 and
                    lot.unrealized_gain_loss_pct > 20):  # 20%+ gain
                suggestions['consider_selling_short_term'].append({
                    'symbol': lot.symbol,
                    'lot_index': lot.lot_index,
                    'gain': lot.unrealized_gain_loss,
                    'gain_pct': lot.unrealized_gain_loss_pct,
                    'reason': 'Significant short-term gain - consider selling before 1 year'
                })

        # General advice
        if not suggestions['tax_loss_harvesting']:
            suggestions['general_advice'].append(
                "No tax-loss harvesting opportunities found")

        if not suggestions['hold_for_long_term']:
            suggestions['general_advice'].append(
                "No lots approaching long-term status")

        return suggestions

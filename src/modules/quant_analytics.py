"""
Module: quant_analytics.py
Deskripsi: Engine komputasi performa trading kuantitatif tingkat lanjut.
Menghitung Expected Value (EV), Calmar Ratio, Sharpe & Sortino Ratio,
System Quality Number (SQN), Maximum Drawdown, Profit Factor, Kelly Criterion,
dan time-series agregasi untuk visualisasi Web GUI.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from src.utils.helper import logger, convert_timestamp_to_wib_str
from src.modules.mongo_manager import MongoManager


class QuantAnalyticsEngine:
    """
    Engine untuk memproses data histori trade dari MongoDB
    dan menghasilkan statistik performa kuantitatif komprehensif.
    """

    def __init__(self, mongo_manager: Optional[MongoManager] = None):
        self.mongo = mongo_manager or MongoManager()

    def fetch_raw_trades(
        self,
        days: int = 0,
        symbol: Optional[str] = None,
        strategy: Optional[str] = None,
        side: Optional[str] = None,
        limit: int = 5000,
        collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Mengambil raw trades dari MongoDB berdasarkan filter.
        
        Args:
            days: Rentang hari ke belakang (0 = semua waktu)
            symbol: Filter simbol (opsional)
            strategy: Filter strategi (opsional)
            side: Filter side BUY/SELL (opsional)
            limit: Maksimum data yang diambil
            collection_name: Target MongoDB collection (opsional)
        """
        if collection_name:
            self.mongo.switch_collection(collection_name)

        filter_query = {}
        
        if days > 0:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            filter_query['timestamp'] = {'$gte': cutoff_date}
            
        if symbol and symbol.upper() != 'ALL':
            filter_query['symbol'] = symbol.upper()
            
        if strategy and strategy.upper() != 'ALL':
            filter_query['strategy_tag'] = strategy.upper()
            
        if side and side.upper() != 'ALL':
            filter_query['side'] = side.upper()
            
        try:
            trades = self.mongo.get_trades(
                filter_query=filter_query,
                sort_by="timestamp",
                ascending=True,  # Urutkan kronologis dari terlama ke terbaru untuk time series
                limit=limit
            )
            return trades
        except Exception as e:
            logger.error(f"❌ QuantAnalyticsEngine: Gagal fetch trades dari MongoDB: {e}")
            return []

    def calculate_metrics(self, raw_trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Menghitung seluruh metrik statistik kuantitatif dari list transaksi.
        
        Returns:
            dict: Berisi 'summary', 'breakdown', dan 'charts_data'.
        """
        if not raw_trades:
            return self._get_empty_analytics_response()

        df = pd.DataFrame(raw_trades)
        
        # Standarisasi kolom dan tipe data numerik
        if 'pnl_usdt' not in df.columns:
            df['pnl_usdt'] = 0.0
        df['pnl_usdt'] = pd.to_numeric(df['pnl_usdt'], errors='coerce').fillna(0.0)
        
        if 'fee' not in df.columns:
            df['fee'] = 0.0
        df['fee'] = pd.to_numeric(df['fee'], errors='coerce').fillna(0.0)
        
        if 'size_usdt' not in df.columns:
            df['size_usdt'] = 0.0
        df['size_usdt'] = pd.to_numeric(df['size_usdt'], errors='coerce').fillna(0.0)
        
        if 'roi_percent' not in df.columns:
            df['roi_percent'] = 0.0
        df['roi_percent'] = pd.to_numeric(df['roi_percent'], errors='coerce').fillna(0.0)
        
        if 'result' not in df.columns:
            df['result'] = 'UNKNOWN'
        
        # Filter trade yang benar-benar terekskusi vs non-filled (CANCELLED/TIMEOUT)
        executed_mask = ~df['result'].isin(['CANCELLED', 'TIMEOUT', 'EXPIRED'])
        df_exec = df[executed_mask].copy()

        total_recorded = len(df)
        total_executed = len(df_exec)
        
        if total_executed == 0:
            resp = self._get_empty_analytics_response()
            resp['summary']['total_recorded_trades'] = total_recorded
            resp['summary']['cancelled_count'] = total_recorded
            return resp

        # 1. Klasifikasi Win / Loss / Breakeven
        win_mask = df_exec['pnl_usdt'] > 0
        loss_mask = df_exec['pnl_usdt'] < 0
        be_mask = df_exec['pnl_usdt'] == 0

        win_count = int(win_mask.sum())
        loss_count = int(loss_mask.sum())
        be_count = int(be_mask.sum())
        cancelled_count = total_recorded - total_executed

        win_rate_pct = round((win_count / total_executed * 100), 2) if total_executed > 0 else 0.0
        loss_rate_pct = round((loss_count / total_executed * 100), 2) if total_executed > 0 else 0.0

        # 2. PnL & Keuntungan Kotor / Rugi Kotor
        gross_profit = float(df_exec[win_mask]['pnl_usdt'].sum())
        gross_loss = float(abs(df_exec[loss_mask]['pnl_usdt'].sum()))
        total_pnl = float(df_exec['pnl_usdt'].sum())
        total_fees = float(df_exec['fee'].sum())
        net_pnl = float(total_pnl - total_fees)

        # 3. Average Win, Average Loss, & Payoff Ratio
        avg_win = round(gross_profit / win_count, 4) if win_count > 0 else 0.0
        avg_loss = round(gross_loss / loss_count, 4) if loss_count > 0 else 0.0
        payoff_ratio = round(avg_win / avg_loss, 2) if avg_loss > 0 else (99.0 if avg_win > 0 else 0.0)

        # 4. Profit Factor (PF)
        if gross_loss > 0:
            profit_factor = round(gross_profit / gross_loss, 2)
        elif gross_profit > 0:
            profit_factor = 99.0
        else:
            profit_factor = 0.0

        # 5. Expected Value (EV / Statistical Expectancy)
        # Formula: (P_win * Avg_Win) - (P_loss * Avg_Loss)
        p_win = win_count / total_executed
        p_loss = loss_count / total_executed
        expected_value_usdt = round((p_win * avg_win) - (p_loss * avg_loss), 4)

        # EV dalam persentase ROI
        win_rois = df_exec[win_mask]['roi_percent']
        loss_rois = df_exec[loss_mask]['roi_percent'].abs()
        avg_win_roi = float(win_rois.mean()) if len(win_rois) > 0 else 0.0
        avg_loss_roi = float(loss_rois.mean()) if len(loss_rois) > 0 else 0.0
        expected_value_roi = round((p_win * avg_win_roi) - (p_loss * avg_loss_roi), 2)

        # 6. Cumulative Equity Curve, High-Water Mark, & Drawdown
        df_exec['cum_pnl'] = df_exec['pnl_usdt'].cumsum()
        df_exec['peak'] = df_exec['cum_pnl'].cummax()
        df_exec['drawdown_usdt'] = df_exec['peak'] - df_exec['cum_pnl']
        
        max_dd_usdt = float(df_exec['drawdown_usdt'].max()) if len(df_exec) > 0 else 0.0
        
        # Hitung Max Drawdown % (terhadap simulasi modal)
        avg_margin = float(df_exec['size_usdt'].mean()) if float(df_exec['size_usdt'].mean()) > 0 else 100.0
        estimated_capital = max(avg_margin * 5, float(df_exec['peak'].max()) + avg_margin)
        
        df_exec['equity_sim'] = estimated_capital + df_exec['cum_pnl']
        df_exec['peak_sim'] = df_exec['equity_sim'].cummax()
        df_exec['drawdown_pct'] = ((df_exec['peak_sim'] - df_exec['equity_sim']) / df_exec['peak_sim']) * 100.0
        max_dd_pct = round(float(df_exec['drawdown_pct'].max()), 2)

        # 7. Calmar Ratio
        # Formula: Net PnL / Max Drawdown (USDT)
        if max_dd_usdt > 0:
            calmar_ratio = round(net_pnl / max_dd_usdt, 2)
        elif net_pnl > 0:
            calmar_ratio = 99.0
        else:
            calmar_ratio = 0.0

        # 8. Sharpe Ratio & Sortino Ratio
        pnl_series = df_exec['pnl_usdt'].values
        mean_pnl = float(np.mean(pnl_series))
        std_pnl = float(np.std(pnl_series))

        # Sharpe Ratio (Per-trade Sharpe)
        if std_pnl > 0:
            sharpe_ratio = round(mean_pnl / std_pnl, 2)
        else:
            sharpe_ratio = 0.0

        # Sortino Ratio (Hanya menghukum downside/loss volatility)
        downside_returns = pnl_series[pnl_series < 0]
        if len(downside_returns) > 0:
            downside_std = float(np.std(downside_returns))
            sortino_ratio = round(mean_pnl / downside_std, 2) if downside_std > 0 else 0.0
        else:
            sortino_ratio = 99.0 if mean_pnl > 0 else 0.0

        # 9. System Quality Number (SQN - Van Tharp)
        # Formula: sqrt(N) * (Mean PnL / StdDev PnL)
        if total_executed > 1 and std_pnl > 0:
            sqn = round(math.sqrt(total_executed) * (mean_pnl / std_pnl), 2)
        else:
            sqn = 0.0

        sqn_grade = self._get_sqn_grade(sqn)

        # 10. Kelly Criterion (% Alokasi Modal Matematis Optimal)
        # Formula: K% = W - [(1 - W) / R]
        if payoff_ratio > 0:
            kelly_pct = round((p_win - ((1.0 - p_win) / payoff_ratio)) * 100, 2)
        else:
            kelly_pct = 0.0
        half_kelly_pct = round(max(0.0, kelly_pct / 2.0), 2)

        # 11. Ekstrak Trade Terbesar
        largest_win = float(df_exec['pnl_usdt'].max()) if len(df_exec) > 0 else 0.0
        largest_loss = float(df_exec['pnl_usdt'].min()) if len(df_exec) > 0 else 0.0

        # 12. Breakdown Data (Per Koin, Per Strategi, Per Side, Per Exit Type)
        breakdown_symbol = self._calc_breakdown(df_exec, 'symbol')
        breakdown_strategy = self._calc_breakdown(df_exec, 'strategy_tag')
        breakdown_side = self._calc_breakdown(df_exec, 'side')
        breakdown_exit = self._calc_breakdown(df_exec, 'exit_type')

        # 13. Data Time Series untuk Chart.js
        equity_curve_data = []
        drawdown_curve_data = []

        for idx, row in df_exec.iterrows():
            ts = str(row.get('timestamp', ''))
            ts_label = convert_timestamp_to_wib_str(ts, fmt='%d/%m %H:%M') if ts else ts
            
            equity_curve_data.append({
                "timestamp": ts,
                "label": ts_label,
                "pnl": round(float(row.get('pnl_usdt', 0)), 2),
                "cumulative_pnl": round(float(row.get('cum_pnl', 0)), 2),
                "symbol": str(row.get('symbol', ''))
            })
            
            drawdown_curve_data.append({
                "timestamp": ts,
                "label": ts_label,
                "drawdown_usdt": round(float(row.get('drawdown_usdt', 0)), 2),
                "drawdown_pct": round(float(row.get('drawdown_pct', 0)), 2)
            })

        return {
            "status": "success",
            "summary": {
                "total_recorded_trades": total_recorded,
                "total_executed_trades": total_executed,
                "win_count": win_count,
                "loss_count": loss_count,
                "breakeven_count": be_count,
                "cancelled_count": cancelled_count,
                "win_rate_percent": win_rate_pct,
                "loss_rate_percent": loss_rate_pct,
                "total_pnl_usdt": round(total_pnl, 2),
                "total_fees_usdt": round(total_fees, 2),
                "net_pnl_usdt": round(net_pnl, 2),
                "gross_profit_usdt": round(gross_profit, 2),
                "gross_loss_usdt": round(gross_loss, 2),
                "avg_win_usdt": round(avg_win, 2),
                "avg_loss_usdt": round(avg_loss, 2),
                "payoff_ratio": payoff_ratio,
                "profit_factor": profit_factor,
                "expected_value_usdt": expected_value_usdt,
                "expected_value_roi_percent": expected_value_roi,
                "max_drawdown_usdt": round(max_dd_usdt, 2),
                "max_drawdown_percent": max_dd_pct,
                "calmar_ratio": calmar_ratio,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "sqn": sqn,
                "sqn_grade": sqn_grade,
                "kelly_percent": kelly_pct,
                "half_kelly_percent": half_kelly_pct,
                "largest_win_usdt": round(largest_win, 2),
                "largest_loss_usdt": round(largest_loss, 2)
            },
            "breakdown": {
                "by_symbol": breakdown_symbol,
                "by_strategy": breakdown_strategy,
                "by_side": breakdown_side,
                "by_exit_type": breakdown_exit
            },
            "charts": {
                "equity_curve": equity_curve_data,
                "drawdown_curve": drawdown_curve_data,
                "distribution": {
                    "win": win_count,
                    "loss": loss_count,
                    "breakeven": be_count,
                    "cancelled": cancelled_count
                }
            }
        }

    def _calc_breakdown(self, df: pd.DataFrame, group_col: str) -> List[Dict[str, Any]]:
        """Helper untuk menghitung agregasi performa per grup (symbol, strategy, side, exit_type)."""
        if group_col not in df.columns or len(df) == 0:
            return []
        
        results = []
        for name, group in df.groupby(group_col):
            count = len(group)
            wins = int((group['pnl_usdt'] > 0).sum())
            losses = int((group['pnl_usdt'] < 0).sum())
            pnl_sum = float(group['pnl_usdt'].sum())
            wr = round((wins / count * 100), 1) if count > 0 else 0.0
            
            results.append({
                "category": str(name),
                "total_trades": count,
                "win_trades": wins,
                "loss_trades": losses,
                "win_rate_percent": wr,
                "net_pnl_usdt": round(pnl_sum, 2)
            })
            
        results.sort(key=lambda x: x['net_pnl_usdt'], reverse=True)
        return results

    @staticmethod
    def _get_sqn_grade(sqn: float) -> str:
        """Kategorisasi System Quality Number berdasarkan standar Van Tharp."""
        if sqn < 1.6:
            return "Poor (Hard to Trade)"
        elif sqn < 2.0:
            return "Average"
        elif sqn < 3.0:
            return "Good"
        elif sqn < 5.0:
            return "Excellent"
        else:
            return "Superb (Holy Grail)"

    @staticmethod
    def _get_empty_analytics_response() -> Dict[str, Any]:
        """Format respon default jika belum ada histori trade."""
        return {
            "status": "success",
            "summary": {
                "total_recorded_trades": 0,
                "total_executed_trades": 0,
                "win_count": 0,
                "loss_count": 0,
                "breakeven_count": 0,
                "cancelled_count": 0,
                "win_rate_percent": 0.0,
                "loss_rate_percent": 0.0,
                "total_pnl_usdt": 0.0,
                "total_fees_usdt": 0.0,
                "net_pnl_usdt": 0.0,
                "gross_profit_usdt": 0.0,
                "gross_loss_usdt": 0.0,
                "avg_win_usdt": 0.0,
                "avg_loss_usdt": 0.0,
                "payoff_ratio": 0.0,
                "profit_factor": 0.0,
                "expected_value_usdt": 0.0,
                "expected_value_roi_percent": 0.0,
                "max_drawdown_usdt": 0.0,
                "max_drawdown_percent": 0.0,
                "calmar_ratio": 0.0,
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "sqn": 0.0,
                "sqn_grade": "No Data",
                "kelly_percent": 0.0,
                "half_kelly_percent": 0.0,
                "largest_win_usdt": 0.0,
                "largest_loss_usdt": 0.0
            },
            "breakdown": {
                "by_symbol": [],
                "by_strategy": [],
                "by_side": [],
                "by_exit_type": []
            },
            "charts": {
                "equity_curve": [],
                "drawdown_curve": [],
                "distribution": {"win": 0, "loss": 0, "breakeven": 0, "cancelled": 0}
            }
        }

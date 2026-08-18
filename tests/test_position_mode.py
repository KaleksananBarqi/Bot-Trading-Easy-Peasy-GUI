import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch

# Add project root and src to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

# Mock Env
os.environ["MONGO_URI"] = "mongodb://dummy:27017/test"

import config
from src.modules.executor import OrderExecutor

async def test_ensure_position_mode():
    print("🧪 Starting Position Mode Sync Tests...")

    # Case 1: Direct success
    mock_exchange = AsyncMock()
    mock_exchange.set_position_mode = AsyncMock(return_value={"code": 200, "msg": "success"})
    executor = OrderExecutor(mock_exchange)

    res = await executor.ensure_position_mode(hedged=False)
    assert res is True, "Case 1 failed: Expected True on success"
    mock_exchange.set_position_mode.assert_called_once_with(False)
    print("✅ Case 1 Passed: Direct set_position_mode success.")

    # Case 2: -4059 No need to change position side
    mock_exchange.set_position_mode = AsyncMock(side_effect=Exception('binance {"code":-4059,"msg":"No need to change position side."}'))
    res = await executor.ensure_position_mode(hedged=False)
    assert res is True, "Case 2 failed: Expected True when already in target position mode (-4059)"
    print("✅ Case 2 Passed: Handled -4059 (No need to change) safely.")

    # Case 3: -4068 Cannot change position side with open positions
    mock_exchange.set_position_mode = AsyncMock(side_effect=Exception('binance {"code":-4068,"msg":"Position side cannot be changed if there are open orders or positions."}'))
    with patch('src.modules.executor_impl.sync.kirim_tele', new_callable=AsyncMock) as mock_tele:
        res = await executor.ensure_position_mode(hedged=False)
        assert res is False, "Case 3 failed: Expected False when blocked by open positions (-4068)"
        mock_tele.assert_called_once()
    print("✅ Case 3 Passed: Handled -4068 with warning and telegram alert.")

    # Case 4: Test Entry Error -4061 Handling in execute_entry
    mock_exchange.fetch_ticker = AsyncMock(return_value={'last': 50000.0})
    mock_exchange.price_to_precision = MagicMock(side_effect=lambda s, p: str(p)) if not hasattr(mock_exchange, 'price_to_precision') else mock_exchange.price_to_precision
    mock_exchange.amount_to_precision = MagicMock(side_effect=lambda s, a: str(a)) if not hasattr(mock_exchange, 'amount_to_precision') else mock_exchange.amount_to_precision
    mock_exchange.create_order = AsyncMock(side_effect=Exception('binance {"code":-4061,"msg":"Order\'s position side does not match user\'s setting."}'))
    
    with patch('src.modules.executor_impl.orders.kirim_tele', new_callable=AsyncMock) as mock_tele:
        await executor.execute_entry(
            symbol="BTC/USDT",
            side="buy",
            order_type="MARKET",
            price=50000,
            amount_usdt=10,
            leverage=10,
            strategy_tag="TEST"
        )
        mock_tele.assert_called_once()
        alert_msg = mock_tele.call_args[0][0]
        assert "Position Mode Mismatch" in alert_msg, "Alert message must mention Position Mode Mismatch"
    print("✅ Case 4 Passed: Handled execute_entry -4061 error gracefully with informative alert.")

    print("\n🎉 All Position Mode tests passed successfully!")

if __name__ == "__main__":
    from unittest.mock import MagicMock
    asyncio.run(test_ensure_position_mode())

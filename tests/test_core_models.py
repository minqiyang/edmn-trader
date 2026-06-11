from decimal import Decimal

import pytest

from edmn_trader.core.models import ExecutionMode, OrderIntent


def test_execution_mode_has_no_enabled_live_mode() -> None:
    assert "LIVE" not in ExecutionMode.__members__
    assert ExecutionMode.LIVE_DISABLED.value == "live_disabled"


def test_live_disabled_cannot_be_used_for_order_intent() -> None:
    with pytest.raises(ValueError, match="not an executable order mode"):
        OrderIntent(
            instrument_id="DEMO",
            side="buy",
            price=Decimal("0.4200"),
            quantity=Decimal("1"),
            execution_mode=ExecutionMode.LIVE_DISABLED,
        )

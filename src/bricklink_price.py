"""Shared helpers for BrickLink price guide access."""

from typing import Dict


def fetch_minifig_price(api, minifig_id: str) -> Dict:
    """Fetch price guide data for a minifigure and return a safe result."""
    try:
        return api.get_price_guide('MINIFIG', minifig_id)
    except Exception:
        return {}

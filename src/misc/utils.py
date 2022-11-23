def normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip()
    if len(symbol) > 4 or len(symbol) < 1:
        raise ValueError(f"Symbol '{symbol}' must be between 1 and 4 letters long.")
    return symbol.upper()

def currency(val: float) -> str:
    return f"${val:,.2f}"
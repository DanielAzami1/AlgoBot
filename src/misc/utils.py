def normalize_symbol(symbol: str):
    if not isinstance(symbol, str):
        raise TypeError(f"Symbol '{symbol}' must be of type str.")
    symbol = symbol.strip()
    if len(symbol) > 4 or len(symbol) < 1:
        raise ValueError(f"Symbol '{symbol}' must be between 1 and 4 letters long.")
    return symbol.upper()

def currency(val: float):
    return f"${val:.2f}"
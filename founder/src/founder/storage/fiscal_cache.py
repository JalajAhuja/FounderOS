"""Fiscal cache and ticker metadata."""


class FiscalCache:

    def __init__(self):
        self._cache = {}

    def set_fiscal_year_end(self, ticker: str, month: int) -> None:

        self._cache[ticker] = {"fiscal_year_end_month": month}

    def get_fiscal_year_end(self, ticker: str) -> int | None:

        if ticker not in self._cache:
            return None

        return self._cache[ticker].get("fiscal_year_end_month")


_default_cache = FiscalCache()


def get_fiscal_cache() -> FiscalCache:

    return _default_cache

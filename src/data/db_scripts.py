import sqlite3
from contextlib import closing
from loguru import logger
import sys
import os
from typing import Optional, List, Tuple, Any

sys.path.append("..")
"""Local imports"""
import config
from models.asset import Stock
from models.company import Company
from misc.utils import normalize_symbol
from misc.enums import TableType


class SQLiteWrapper:
    """
    Wrapper for all transactions within the sqlite3 db(/src/data/tables/sqlite.db).
    Implementing __enter__ and __exit__ allows this object to be used with a context manager, simplifying
    the handling of db connections.
    """
    def __init__(self, test: Optional[bool] = False):
        if test:
            db_path = config.BASE_DB_PATH_DUMMY
        else:
            db_path = config.BASE_DB_PATH
        self.db_path = os.path.join(os.getcwd(), db_path)

    def __enter__(self):
        self.con = sqlite3.connect(self.db_path)
        logger.debug(f"Connection established to {self.db_path}.")
        return self

    def __exit__(self, *args, **kwargs):
        if any(args):
            logger.error(f"Exceptions raised - cancelling transaction:\n {args}")
            self.con.rollback()
        else:
            self.con.commit()
        self.con.close()
        logger.debug(f"Connection closed with {self.db_path}.")

    def create_table(self, table_type: TableType, **kwargs: Optional[str]):
        """
        Table names for TableType: ticker and TableType: portfolio will be the name of the stock or portfolio
        (respectively) themselves, so we can pass those names in as kwargs.
        """
        cur = self.con.cursor()
        if table_type is TableType.company:
            cur.execute(
                """
                CREATE TABLE company (
                    symbol PRIMARY KEY,
                    company_name,
                    sector,
                    industry, 
                    business_summary, 
                    country, 
                    employee_count, 
                    market_cap, 
                    float_shares, 
                    is_esg_populated
                )
                """
            )
        elif table_type is TableType.ticker:
            table_name = kwargs["symbol"]
            cur.execute(
                """
                CREATE TABLE ? (
                    date PRIMARY KEY,
                    open,
                    high,
                    low,
                    close,
                    volume,
                    dividends,
                    splits
                )
                """, (table_name,)
            )
        elif table_type is TableType.holding:
            cur.execute(
                """
                CREATE TABLE holding (
                    symbol PRIMARY KEY,
                    qty_owned,
                    date_purchased
                )
                """
            )
        elif table_type is TableType.transaction:
            cur.execute(
                """
                CREATE TABLE transaction (
                    date PRIMARY KEY,
                    symbol,
                    direction,
                    price,
                    qty
                )
                """
            )
        elif table_type is TableType.portfolio:
            table_name = kwargs["portfolio_name"]
            cur.execute(
                """
                CREATE TABLE ? (
                    date PRIMARY KEY,
                    value,
                    unique_holdings
                )
                """, (table_name,)
            )
        logger.success(f"Created table for table type {table_type}")

    def __repr__(self):
        return f"SQLiteWrapper<test: Optional[bool] = False>"

    def __str__(self):
        return f"SQLiteWrapper - db_path: {self.db_path}"



# def _company_insert_rows(*args: Company, db_path: str = config.BASE_DB_PATH) -> None:
#     path = os.path.join(os.getcwd(), db_path)
#     with closing(
#         sqlite3.connect(path)
#     ) as con:
#         with con:
#             cur = con.cursor()
#             for company in args:
#                 company_data = tuple(vars(company).values())
#                 try:
#                     cur.execute(
#                         """
#                         INSERT INTO company
#                         VALUES 
#                         (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                         """, company_data
#                     )
#                     logger.success(f"Inserted the following into company:\n{company_data}\n")
#                 except sqlite3.IntegrityError:
#                     logger.warning(f"Attempted to insert duplicate company {company.company_name} ({company.symbol}) into 'company'.\n")
                


# def _company_select_rows(*args: Optional[str], all: bool = False, db_path: str = config.BASE_DB_PATH) -> Optional[List[Tuple[Any]]]:
#     path = os.path.join(os.getcwd(), db_path)
#     res = None
#     if args:
#         args = map(normalize_symbol, args)
#     with closing(
#         sqlite3.connect(path)
#     ) as con:
#         with con:
#             cur = con.cursor()
#             if all:
#                 cur.execute(
#                     """
#                     SELECT *
#                     FROM COMPANY
#                     """
#                 )
#                 res = cur.fetchall()
#             else:
#                 res = []
#                 for symbol in args:
#                     cur.execute(
#                         """
#                         SELECT * 
#                         FROM COMPANY
#                         WHERE symbol=?
#                         """, (symbol,)
#                     )
#                     data = cur.fetchone()
#                     if not data:
#                         logger.warning(f"No record found for {symbol}.\n")
#                     else:
#                         res.append(data)
#     return res

if __name__ == "__main__":

    with SQLiteWrapper(test=True) as db:
        db.create_table(TableType.company)

    # import yfinance as yf
    # msft = yf.Ticker("MSFT")
    # info = msft.info
    # msft_company = Company(
    #     company_name = info['shortName'], symbol = info['symbol'], sector = info['sector'],
    #     industry = info['industry'], business_summary = info['longBusinessSummary'], country = info['country'],
    #     employee_count = info['fullTimeEmployees'], market_cap = info['marketCap'], float_shares = info['floatShares'],
    #     is_esg_populated = info['isEsgPopulated']
    # )

    # aapl = yf.Ticker("aapl")
    # info = aapl.info
    # aapl_company = Company(
    #     company_name = info['shortName'], symbol = info['symbol'], sector = info['sector'],
    #     industry = info['industry'], business_summary = info['longBusinessSummary'], country = info['country'],
    #     employee_count = info['fullTimeEmployees'], market_cap = info['marketCap'], float_shares = info['floatShares'],
    #     is_esg_populated = info['isEsgPopulated']
    # )

    # meta = yf.Ticker("meta")
    # info = meta.info
    # meta_company = Company(
    #     company_name = info['shortName'], symbol = info['symbol'], sector = info['sector'],
    #     industry = info['industry'], business_summary = info['longBusinessSummary'], country = info['country'],
    #     employee_count = info['fullTimeEmployees'], market_cap = info['marketCap'], float_shares = info['floatShares'],
    #     is_esg_populated = info['isEsgPopulated']
    # )

    #_company_insert_rows(msft_company, aapl_company, meta_company)

    # res = _company_select_rows(all=True)
    # msft_data = res[0]

    # msft_company = Company(*msft_data)
    # print(msft_company)

    # print(msft_company.company_name)
    # print(msft_company.symbol)

    # res = _company_select_rows("aapl")
    
    # aapl_company = Company(*res[0])

    # print(aapl_company)
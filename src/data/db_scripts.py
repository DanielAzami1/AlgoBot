import sqlite3
from contextlib import closing
from loguru import logger
import sys
import os

sys.path.append("..")
"""Local imports"""
import config
from models.asset import Stock
from models.company import Company
from misc.utils import normalize_symbol


def _company_create_table(db_path: str = config._COMPANY_BASE_DB_PATH):
    path = os.path.join(os.getcwd(), db_path)
    if os.path.exists(path):
        logger.warning(f"\n'company' table ({path}) already exists.")
        return None
    with closing(
        sqlite3.connect(path)
    ) as con:  # context-manager for opening connection to db
        with con:  # context-manager for transaction
            cur = con.cursor()
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
    logger.success(f"Created company table in {db_path}")


def _company_insert_rows(*args: Company, db_path: str = config._COMPANY_BASE_DB_PATH):
    path = os.path.join(os.getcwd(), db_path)
    with closing(
        sqlite3.connect(path)
    ) as con:
        with con:
            cur = con.cursor()
            for company in args:
                company_data = tuple(vars(company).values())
                try:
                    cur.execute(
                        """
                        INSERT INTO company
                        VALUES 
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, company_data
                    )
                    logger.success(f"Inserted the following into company:\n{company_data}\n")
                except sqlite3.IntegrityError:
                    logger.warning(f"Attempted to insert duplicate company {company.company_name} ({company.symbol}) into 'company'.\n")
                


def _company_select_rows(*args: str, all: bool = False, db_path: str = config._COMPANY_BASE_DB_PATH):
    path = os.path.join(os.getcwd(), db_path)
    if args:
        args = map(normalize_symbol, args)
    with closing(
        sqlite3.connect(path)
    ) as con:
        with con:
            cur = con.cursor()
            if all:
                cur.execute(
                    """
                    SELECT *
                    FROM COMPANY
                    """
                )
                res = cur.fetchall()
            else:
                res = []
                for symbol in args:
                    cur.execute(
                        """
                        SELECT * 
                        FROM COMPANY
                        WHERE symbol=?
                        """, (symbol,)
                    )
                    data = cur.fetchone()
                    if not data:
                        logger.warning(f"No record found for {symbol}.\n")
                    else:
                        res.append(data)
    return res

if __name__ == "__main__":

    _company_create_table()

    import yfinance as yf
    msft = yf.Ticker("MSFT")
    info = msft.info
    msft_company = Company(
        company_name = info['shortName'], symbol = info['symbol'], sector = info['sector'],
        industry = info['industry'], business_summary = info['longBusinessSummary'], country = info['country'],
        employee_count = info['fullTimeEmployees'], market_cap = info['marketCap'], float_shares = info['floatShares'],
        is_esg_populated = info['isEsgPopulated']
    )

    aapl = yf.Ticker("aapl")
    info = aapl.info
    aapl_company = Company(
        company_name = info['shortName'], symbol = info['symbol'], sector = info['sector'],
        industry = info['industry'], business_summary = info['longBusinessSummary'], country = info['country'],
        employee_count = info['fullTimeEmployees'], market_cap = info['marketCap'], float_shares = info['floatShares'],
        is_esg_populated = info['isEsgPopulated']
    )

    meta = yf.Ticker("meta")
    info = meta.info
    meta_company = Company(
        company_name = info['shortName'], symbol = info['symbol'], sector = info['sector'],
        industry = info['industry'], business_summary = info['longBusinessSummary'], country = info['country'],
        employee_count = info['fullTimeEmployees'], market_cap = info['marketCap'], float_shares = info['floatShares'],
        is_esg_populated = info['isEsgPopulated']
    )

    #_company_insert_rows(msft_company, aapl_company, meta_company)

    res = _company_select_rows(all=True)
    msft_data = res[0]

    msft_company = Company(*msft_data)
    print(msft_company)

    print(msft_company.company_name)
    print(msft_company.symbol)

    res = _company_select_rows("aapl", "meta ", "gm")
    
    aapl_company, meta_company = Company(*res[0]), Company(*res[1])

    print(aapl_company)
    print(meta_company)
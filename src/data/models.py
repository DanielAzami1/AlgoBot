from peewee import *
from loguru import logger
from typing import List, Type, Optional
from functools import partial
from datetime import datetime
import os
import pathlib
from src.misc.utils import load_cfg, timed, use_threadpool_exec, normalize_symbol, currency
from src.classes.company import Company
from src.classes.holding import Holding
from src.classes.transaction import Transaction
from src.data.download_remote_data import download_index_constituents, download_ticker_data


module_path = pathlib.Path(__file__).parent.resolve()
cfg = load_cfg(prepend_path=os.path.join(module_path, '..'))
db_path = os.path.join(module_path, cfg["BASE_DB_PATH_DUMMY"])
db = SqliteDatabase(db_path)


class CompanyModel(Model):
    symbol = CharField(primary_key=True)
    company_name = CharField()
    sector = CharField()
    industry = CharField()
    business_summary = TextField()
    country = CharField()
    employee_count = DoubleField(null=True)
    market_cap = DoubleField(null=True)
    float_shares = DoubleField(null=True)
    is_esg_populated = BooleanField(null=True)

    class Meta:
        database = db


class HoldingModel(Model):
    symbol = CharField(primary_key=True)
    qty_owned = IntegerField()
    date_purchased = DateField()
    portfolio = CharField()

    class Meta:
        database = db


class TransactionModel(Model):
    date = DateTimeField(primary_key=True)
    symbol = CharField()
    direction = CharField()
    order_type = CharField()
    price = FloatField()
    qty = IntegerField()
    portfolio = CharField()

    class Meta:
        database = db


class PortfolioModel(Model):
    date = DateTimeField(primary_key=True)
    portfolio = CharField()
    value = DoubleField()

    class Meta:
        database = db


def create_table(*models: Type[Model]):
    """
    Create database tables
    :param models: (positional) CompanyModel, HoldingModel, TransactionModel, PortfolioModel - tables to be created.
    :return: None
    """
    db.connect()
    db.create_tables(models)
    logger.success(f"Tables ready for {models}")
    db.close()


@timed
def insert_into_company_table(*companies: Company):
    """
    :param companies: (positional) Company objects to be inserted into the Company table.
    :return: None
    """
    db.connect()
    with db.atomic():
        for company in companies:
            model = CompanyModel.create(**vars(company))
            model.save()
            logger.success(f"Inserted into Company: {company.company_name} ({company.symbol})")
    logger.debug(f"Inserted {len(companies)} companies into company table.")
    db.close()


@timed
def insert_into_holdings_table(*holdings: Holding, portfolio: str):
    """
    :param portfolio: (kwarg) associated portfolio.
    :param holdings: (positional) Holding objects to be inserted into the Holding table.
    :return: None
    """
    db.connect()
    with db.atomic():
        for holding in holdings:
            model = CompanyModel.create(**vars(holding), portfolio=portfolio)
            model.save()
            logger.success(f"Inserted into Holding: {holding}")
    db.close()


@timed
def insert_into_transactions_table(*transactions: Transaction, portfolio: str):
    """
    :param portfolio: (kwarg) associated portfolio.
    :param transactions: (positional) Transaction objects to be inserted into the Transaction table.
    :return: None
    """
    db.connect()
    with db.atomic():
        for transaction in transactions:
            model = TransactionModel.create(**vars(transaction), portfolio=portfolio)
            model.save()
            logger.success(f"Inserted into Transaction: "
                           f"{transaction.symbol}: {transaction.order_type} {transaction.direction}")
    db.close()


@timed
def insert_into_portfolio_table(portfolio: str, value: float, timestamp: datetime = datetime.now()):
    """
    :param value: (kwarg) current market value of portfolio in $.
    :param portfolio: (kwarg) name of portfolio.
    :param timestamp: (kwarg) timestamp of when value was entered into the db.
    :return: None
    """
    db.connect()
    model = PortfolioModel.create(date=timestamp, portfolio=portfolio, value=value)
    model.save()
    logger.success(f"Inserted into Portfolio a new value for {portfolio} - {currency(value)} <{timestamp}>")
    db.close()


@timed
def fetch_from_company_table(*symbols: str, every: bool = False) -> List[Company]:
    """
    :param symbols: (positional) symbols to retrieve company metadata for.
    :param every: (kwarg) set to True for all companies in the table.
    :return: a list of Company objects returned from query.
    """
    db.connect()
    companies = []
    symbols = map(normalize_symbol, symbols)
    if every:
        companies.append(CompanyModel.select().get())
    else:
        for symbol in symbols:
            company = CompanyModel.get(CompanyModel.symbol == symbol)
            companies.append(company)

    db.close()
    return [Company(**company.__data__) for company in companies]


@timed
def fetch_from_holdings_table(*symbols: str, portfolio: str, every: bool = False) -> List[Holding]:
    """
    :param symbols: (positional) symbols to retrieve associated Holding objects.
    :param portfolio: (kwarg) portfolio name associated with the desired holdings.
    :param every: (kwarg) set to True for all holdings associated with given portfolio.
    :return: a list of Holding objects returned from query.
    """
    db.connect()
    holdings = []
    if every:
        holdings.append(HoldingModel.select().get(HoldingModel.portfolio == portfolio))
    else:
        for symbol in symbols:
            holding = HoldingModel.get(HoldingModel.symbol == symbol and HoldingModel.portfolio == portfolio)
            holdings.append(holding)
    db.close()
    return [Holding(**holding.__data__) for holding in holdings]


@timed
def fetch_from_transactions_table(*symbols: str, portfolio: str, every: bool = False) -> List[Transaction]:
    """
    :param symbols: (positional) symbols to retrieve associated Holding objects.
    :param portfolio: (kwarg) portfolio name associated with the desired holdings.
    :param every: (kwarg) set to True for all holdings associated with given portfolio.
    :return: a list of Holding objects returned from query.
    """
    db.connect()
    transactions = []
    if every:
        transactions.append(TransactionModel.select().get(TransactionModel.portfolio == portfolio))
    else:
        for symbol in symbols:
            transaction = TransactionModel.get(
                TransactionModel.symbol == symbol and TransactionModel.portfolio == portfolio
            )
            transactions.append(transaction)
    db.close()
    return [Transaction(**transaction.__data__) for transaction in transactions]


@timed
def fetch_from_portfolio_table(portfolio: str, timestamp: Optional[datetime] = None) -> List:
    """
    :param portfolio: (kwarg) name of portfolio to retrieve history for.
    :param timestamp: optional argument to retrieve portfolio value on a given date/time.
    :return: List of portfolio values enumerated by date.
    """
    db.connect()
    value_history = []
    if not timestamp:
        value_history.append(PortfolioModel.select().get(PortfolioModel.portfolio == portfolio))
    else:
        value_history.append(PortfolioModel.select().get(
            PortfolioModel.portfolio == portfolio and PortfolioModel.date == timestamp)
        )
    return value_history


def get_unique_sectors_and_industries():
    """
    :return: Dict containing two lists, one for all unique company sectors, and one for unique industries.
    """
    db.connect()
    unique_sectors = []
    models_sector = CompanyModel.select(CompanyModel.sector).distinct()
    for model in models_sector:
        unique_sectors.append(model.sector)
    unique_industries = []
    models_industry = CompanyModel.select(CompanyModel.industry).distinct()
    for model in models_industry:
        unique_industries.append(model.industry)
    db.close()
    return {
        "unique_sectors": unique_sectors,
        "unique_industries": unique_industries
    }


if __name__ == "__main__":
    """This file can be run directly to set up company table with company metadata"""
    create_table(CompanyModel, TransactionModel, HoldingModel, PortfolioModel)

    def populate_company_table_with_defaults():
        """Populate the Company table / model with company data (pulled from snp500 constituents list)."""
        snp_constituents = download_index_constituents()
        map_download = partial(download_ticker_data, include_metadata=True)
        all_stock_data = use_threadpool_exec(func=map_download, iterable=snp_constituents)
        all_stock_data = list(filter(None, all_stock_data))  # Filter out any downloads that returned nothing
        comps = []
        for stock in all_stock_data:
            try:
                metadata = stock['metadata']
                kwargs = {
                    "symbol": metadata['symbol'],
                    "company_name": metadata['longName'],
                    "sector": metadata['sector'],
                    "industry": metadata['industry'],
                    "business_summary": metadata['longBusinessSummary'],
                    "country": metadata["country"],
                    "employee_count": metadata["fullTimeEmployees"],
                    "market_cap": metadata["marketCap"],
                    "float_shares": metadata["floatShares"],
                    "is_esg_populated": metadata["isEsgPopulated"]
                }
                comp: Company = Company(**kwargs)
                comps.append(comp)
            except KeyError as e:
                logger.warning(e)
                continue
        insert_into_company_table(*comps)

    # aapl = fetch_from_company_table("aapl")
    # aapl = aapl[0]
    # print(aapl)

    # print(fetch_from_company_table(every=True))

    uniques = get_unique_sectors_and_industries()
    sectors = uniques['unique_sectors']
    industries = uniques['unique_industries']
    for m in sectors:
        print(m.sector)
    for i, m in enumerate(industries):
        print(m.industry)
        print(i)


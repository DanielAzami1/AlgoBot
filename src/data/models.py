from peewee import *
from loguru import logger
from typing import List, Type
from functools import partial
from src.misc.utils import load_cfg, timed, use_threadpool_exec, normalize_symbol
from src.classes.company import Company
from src.classes.holding import Holding
from src.classes.transaction import Transaction
from src.data.download_remote_data import download_index_constituents, download_ticker_data


cfg = load_cfg()
db_path = cfg["BASE_DB_PATH_DUMMY"]

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

    class Meta:
        database = db


class TransactionModel(Model):
    date = DateTimeField(primary_key=True)
    symbol = CharField()
    direction = CharField()
    order_type = CharField()
    price = FloatField()
    qty = IntegerField()

    class Meta:
        database = db


def create_table(*models: Type[Model]):
    """Pass in any of models.Company, models.Holding, Models.Transaction."""
    db.connect()
    db.create_tables(models)
    logger.success(f"Tables ready for {models}")
    db.close()


@timed
def insert_into_company_table(*companies: Company):
    """Pass in Company objects to be saved to Company table (model)."""
    db.connect()
    with db.atomic():
        for company in companies:
            model = CompanyModel.create(**vars(company))
            model.save()
            logger.success(f"Inserted into Company: {company.company_name} ({company.symbol})")
    logger.debug(f"Inserted {len(companies)} companies into company table.")
    db.close()


@timed
def insert_into_holdings_table(*holdings: Holding):
    """Pass in Holding objects to be saved to Holding table (model)."""
    db.connect()
    with db.atomic():
        for holding in holdings:
            model = CompanyModel.create(**vars(holding))
            model.save()
            logger.success(f"Inserted into Holding: {holding}")
    db.close()


@timed
def insert_into_transactions_table(*transactions: Transaction):
    """Pass in Transaction objects to be saved to Transaction table (model)."""
    db.connect()
    with db.atomic():
        for transaction in transactions:
            model = TransactionModel.create(**vars(transaction))
            model.save()
            logger.success(f"Inserted into Transaction: "
                           f"{transaction.symbol}: {transaction.order_type} {transaction.direction}")
    db.close()


@timed
def fetch_from_company_table(*symbols: str, every: bool = False) -> List[Company]:
    """Pass in every=True for all companies in the Company table."""
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
def fetch_from_holdings_table(*symbols: str, every: bool = False) -> List[Holding]:
    """Pass in every=True for all holdings in the Holding table."""
    db.connect()
    holdings = []
    if every:
        holdings.append(HoldingModel.select().get())
    else:
        for symbol in symbols:
            holding = HoldingModel.get(HoldingModel.symbol == symbol)
            holdings.append(holding)
    db.close()
    return [Holding(**holding.__data__) for holding in holdings]


@timed
def fetch_from_transactions_table(*symbols: str, every: bool = False) -> List[Transaction]:
    """Pass in every=True for all transactions in the Transactions table."""
    db.connect()
    transactions = []
    if every:
        transactions.append(TransactionModel.select().get())
    else:
        for symbol in symbols:
            transaction = TransactionModel.get(TransactionModel.symbol == symbol)
            transactions.append(transaction)
    db.close()
    return [Transaction(**transaction.__data__) for transaction in transactions]


if __name__ == "__main__":
    """This file can be run directly to set up basic table data"""
    create_table(CompanyModel, TransactionModel, HoldingModel)

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

    aapl = fetch_from_company_table("gm")
    aapl = aapl[0]
    print(aapl)



from typing import Dict

CREATE_TABLE: Dict = {
    "company":
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
}
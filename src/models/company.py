class Company:
    def __init__(self, company_name: str):
        self.company_name = company_name
    
    def add_sector_industry(self, sector: str, industry: str):
        self.sector = [sector, industry]
    
    def add_business_summary(self, summary: str):
        self.business_summary = summary

    def add_employee_count(self, employee_count: int):
        self.employee_count = employee_count
    
    def add_country(self, country: str):
        self.country = country
    
    def add_esg(self, is_esg_populated: bool):
        self.is_esg_populated = is_esg_populated
    
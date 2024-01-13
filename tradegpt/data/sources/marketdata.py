# tradegpt/data/sources/marketdata.py
import os
import requests
import json
import dataclasses
from arrow import Arrow
from datetime import datetime
from dotenv import load_dotenv

from data.sources.datasource import DataSource
from data.models import Contract, Datum

load_dotenv()

TOKEN = os.getenv('MARKET_DATA_API_TOKEN')

class MarketDataAPI(DataSource):
    def __init__(self) -> None:
        self.base_url = "https://api.marketdata.app/v1/options/chain/"

    def fetch_data(self, start: Arrow, end: Arrow, symbol: str):
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Token {TOKEN}'
        }
        response = requests.get(f"{self.base_url}{symbol}/", headers=headers)
        if response.status_code == 200:
            return self._parse_chain(response.json())
        else:
            return []

    @staticmethod
    def _parse_chain(response):
        contracts = []

        for (option_symbol, strike, delta, theta, gamma, vega, rho, iv, volume, open_interest, 
             bid, ask, dte, contract_type, itm) in zip(
                 response["optionSymbol"], response["strike"], response["delta"], response["theta"], 
                 response["gamma"], response["vega"], response["rho"], response["iv"], 
                 response["volume"], response["openInterest"], response["bid"], response["ask"], 
                 response["dte"], response["side"], response["inTheMoney"]):

            contract = Contract(
                desc=option_symbol,
                strike=strike,
                delta=delta,
                theta=theta,
                gamma=gamma,
                vega=vega,
                rho=rho,
                volatility=iv,
                volume=volume,
                openInterest=open_interest,
                bid=bid,
                ask=ask,
                daysToExp=dte,
                contractType=contract_type,
                itm=itm
            )

            value = json.dumps(dataclasses.asdict(contract))
            contracts.append(Datum(
                name='OPTION',
                date=datetime.now(),  # Replace with appropriate date field if needed
                value=value,
                symbol=contract.desc.split('_')[0]
            ))

        return contracts

# Additional classes and methods (Contract, Datum, etc.) need to be defined as per your project's structure.

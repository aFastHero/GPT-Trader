# tradegpt/data/sources/interactivebrokers.py #
import dataclasses
import os
import arrow
from dotenv import load_dotenv
from arrow import Arrow
from ib_insync import IB, Option, util
import json

from data.sources.datasource import DataSource
from data.models import Contract, Datum

load_dotenv()

IB_HOST = os.getenv('IB_HOST')
IB_PORT = os.getenv('IB_PORT')
IB_CLIENT_ID = os.getenv('IB_CLIENT_ID')

class InteractiveBrokers(DataSource):
    def __init__(self, max_dte=36) -> None:
        self.max_dte = max_dte
        self.client = IB()
        self.client.connect(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID)

    def fetch_data(self, start: Arrow, end: Arrow, symbol: str):
        now = arrow.now(tz="America/New_York")
        chains = self.client.reqSecDefOptParams(underlyingSymbol=symbol, futFopExchange='', underlyingSecType='STK', underlyingConId=0)
        chain = next(c for c in chains if c.tradingClass == symbol and c.exchange == 'SMART')

        contracts = []

        for exp in sorted(chain.expirations)[:self.max_dte]:
            for strike in chain.strikes:
                for right in ['P', 'C']:
                    contract = Option(symbol, exp, strike, right, 'SMART')
                    contracts.append(contract)

        results = InteractiveBrokers._parse_chain(self.client, contracts)
        return results
    
    @staticmethod
    def _parse_chain(client, contracts):
        data = []

        for contract in contracts:
            option = client.reqContractDetails(contract)[0].contract
            ticker = client.reqMktData(option, '', False, False)
            util.waitUntil(lambda: ticker.bid and ticker.ask and ticker.modelGreeks)

            contract = Contract(
                desc=option.localSymbol,
                strike=option.strike,
                delta=ticker.modelGreeks.delta,
                theta=ticker.modelGreeks.theta,
                gamma=ticker.modelGreeks.gamma,
                vega=ticker.modelGreeks.vega,
                rho=ticker.modelGreeks.rho,
                bid=ticker.bid,
                ask=ticker.ask,
                volume=ticker.volume,
                openInterest=ticker.openInterest,
                volatility=ticker.modelGreeks.impliedVol,
                daysToExp=(arrow.get(option.lastTradeDateOrContractMonth, 'YYYYMMDD') - arrow.now()).days,
                contractType=option.right,
                itm=option.strike < ticker.last if option.right == 'C' else option.strike > ticker.last)

            value = json.dumps(dataclasses.asdict(contract))
            data.append(Datum(
                name='OPTION',
                date=arrow.now(tz='America/New_York'),
                value=value,
                symbol=contract.desc.split('_')[0]
            ))

        return data

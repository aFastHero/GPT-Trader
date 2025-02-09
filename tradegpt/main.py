import arrow
import sys
from dotenv import load_dotenv

from data.context import DataContext, InsightContext
from data.insights.price_action import PriceAction
from data.insights.current_price import CurrentPrice
from data.insights.linelevels import LineLevels
from data.insights.macd import MACD
from data.insights.fiblevels import FibonacciLevels
from data.insights.momentum import Momentum
from data.insights.news import News
from data.sources.yahoo import YahooSource
from data.sources.marketdata import MarketDataAPI
from data.sources.tdameritrade import TDAmeritrade
from data.insights.options import Options
from data.insights.vix import VIX
from utils import ask_gpt, save_response
from prompt import MARKET_SYSTEM, MARKET_USER, OPTIONS_SYSTEM, OPTIONS_USER, DAY_TRADING_SYSTEM, DAY_TRADING_USER, CMT_SYSTEM, CMT_USER

load_dotenv()

def main(prompt_only=False):
    # use the last argument as the symbol if one is provided
    if len(sys.argv) > 1:
        symbols = [sys.argv[-1].upper()]
    else:
        symbols = ['NVDA']

    sources = [
        YahooSource(),
        # MarketDataAPI(), # - requires marketdata.app account
        # TDAmeritrade(), # - requires TDAmeritrade account
    ]

    insights = [
        # Options(), # - requires TDAmeritrade or marketdata.app account
        Momentum(most_recent=True),
        News(),
        LineLevels(3, 45),
        FibonacciLevels(),
        MACD(),
        CurrentPrice(),
        PriceAction(day_lookback=120),
        VIX()
    ]

    for symbol in symbols:
        print(f'Getting insights for {symbol}...')
        datum = DataContext(sources, cache=False)
        insights_context = InsightContext(datum, [symbol], insights)

        results = insights_context.get_insights(arrow.now().shift(days=-1))

        insight_prompts = "\n".join([r.to_prompt() for r in results])
        prompt = CMT_USER.replace('$C', insight_prompts)

        with open('prompt.txt', 'w', encoding='utf-8') as f:
            f.write(prompt)

        if not prompt_only:
            response = ask_gpt(CMT_SYSTEM, prompt, model='gpt-4-1106-preview')
            save_response(response, symbol)

if __name__ == "__main__":
    main()

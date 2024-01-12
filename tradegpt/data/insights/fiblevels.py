import arrow
import pandas as pd
from typing import List
from data.insights.insight import Insight
from data.models import InsightResult

class FibonacciLevels(Insight):
    def __init__(self) -> None:
        super().__init__("Fibonacci Levels", 0)  # Adjust the lookback period as needed

    def generate(self, datum: pd.DataFrame) -> List[InsightResult]:
        results = []

        # Assuming 'datum' contains 'HIGH' and 'LOW' price data
        high = datum[datum['name'] == 'HIGH']['value'].max()
        low = datum[datum['name'] == 'LOW']['value'].min()

        # Fibonacci Levels
        diff = high - low
        levels = [low + diff * factor for factor in [0, 0.236, 0.382, 0.5, 0.618, 1]]
        # Fibonacci Extensions (using common extension levels)
        extensions = [high + diff * factor for factor in [1.382, 1.5, 1.618]]

        # Adding insights
        for level in levels:
            results.append(
                InsightResult(
                    "Fibonacci Level",
                    level,
                    arrow.get(datum['date'].iloc[-1]),  # using the last date in the data
                    datum['symbol'].iloc[0]  # assuming all rows have the same symbol
                )
            )

        for extension in extensions:
            results.append(
                InsightResult(
                    "Fibonacci Extension",
                    extension,
                    arrow.get(datum['date'].iloc[-1]),
                    datum['symbol'].iloc[0]
                )
            )

        return results
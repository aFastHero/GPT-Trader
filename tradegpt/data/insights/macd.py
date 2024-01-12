import arrow
import pandas as pd
from typing import List
from data.insights.insight import Insight
from data.models import InsightResult

class MACD(Insight):
    def __init__(self) -> None:
        super().__init__("MACD", 26)  # The lookback period is set to 26, the longer EMA period

    def generate(self, datum: pd.DataFrame) -> List[InsightResult]:
        results = []

        # Assuming 'datum' contains a 'CLOSE' price column
        df = datum[datum['name'] == 'CLOSE'].copy()
        
        # Calculate the MACD and Signal line
        df['EMA_12'] = df['value'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['value'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        for _, row in df.iterrows():
            results.extend([
                InsightResult(
                    "MACD",
                    row['MACD'],
                    arrow.get(row['date']),
                    row['symbol']
                ),
                InsightResult(
                    "Signal Line",
                    row['Signal_Line'],
                    arrow.get(row['date']),
                    row['symbol']
                )
            ])

        return results
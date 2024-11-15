import pandas as pd
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from collections import OrderedDict
from app import main

def optimise(pivot_df, portfolio_value):

        pivot_df.index = pd.to_datetime(pivot_df.index)
        pivot_df = pivot_df.sort_index()

        mu = mean_historical_return(pivot_df)
        S = CovarianceShrinkage(pivot_df).ledoit_wolf()

        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe(risk_free_rate=0)

        cleaned_weights = ef.clean_weights()

        response = {}

        for k, v in cleaned_weights.items():
              if v != 0:
                    response[k] = v

        metrics_tuple = ef.portfolio_performance(verbose=True)

        metrics = {"Expected return": f"{round(metrics_tuple[0] * 100, 2)}%", "Semivariance": f"{round(metrics_tuple[1] * 100, 2)}%" , "Sortino ratio": metrics_tuple[2]}

        value = {}

        for ticker, weight in response.items():
            value[ticker] = "$" + '{:.2f}'.format(portfolio_value * weight)

        return { "weights" : response, "metrics" : metrics, "value": value }

if __name__ == "__main__":
    main(optimise)
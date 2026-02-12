import numpy as np

class MonteCarloSimulator:
    def __init__(
        self,
        years: int,
        start_balance: float,
        monthly_contribution: float,
        expected_return_annual: float,
        volatility_annual: float,
        inflation_annual: float,
        simulations: int = 1000,
        seed: int = 42
    ):
        self.years = years
        self.start_balance = start_balance
        self.monthly_contribution = monthly_contribution
        self.expected_return_annual = expected_return_annual
        self.volatility_annual = volatility_annual
        self.inflation_annual = inflation_annual
        self.simulations = simulations
        self.seed = seed

    def run(self):
        np.random.seed(self.seed)

        months = self.years * 12

        # Convert annual return + volatility to monthly
        mean_monthly_return = self.expected_return_annual / 12
        monthly_volatility = self.volatility_annual / np.sqrt(12)

        # Generate random monthly returns
        random_returns = np.random.normal(
            mean_monthly_return,
            monthly_volatility,
            (self.simulations, months)
        )

        # Initialise balance array
        balances = np.zeros((self.simulations, months + 1))
        balances[:, 0] = self.start_balance

        # Simulate
        for t in range(1, months + 1):
            balances[:, t] = (
                balances[:, t - 1] * (1 + random_returns[:, t - 1])
                + self.monthly_contribution
            )

        # Adjust for inflation
        monthly_inflation = (1 + self.inflation_annual) ** (1/12) - 1
        inflation_factor = (1 + monthly_inflation) ** np.arange(months + 1)

        balances_real = balances / inflation_factor

        return balances_real

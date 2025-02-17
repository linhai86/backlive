from ..domain.models import Candle, OrderSide


class MovingAverageCrossoverStrategy:
    def __init__(self, short_window: int, long_window: int):
        self.short_window = short_window
        self.long_window = long_window
        self.prices: list[float] = []

    def generate_signal(self, candle: Candle) -> OrderSide | None:
        self.prices.append(candle.close)
        if len(self.prices) < self.long_window:
            return None
        short_avg = sum(self.prices[-self.short_window :]) / self.short_window
        long_avg = sum(self.prices[-self.long_window :]) / self.long_window
        if short_avg > long_avg:
            return OrderSide.BUY
        elif short_avg < long_avg:
            return OrderSide.SELL
        return None

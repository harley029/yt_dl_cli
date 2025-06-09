""" Tests global settings  """
import warnings

warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="coroutine '.*' was never awaited"
)

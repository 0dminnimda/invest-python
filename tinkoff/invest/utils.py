import ast
import dataclasses
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Generator, Tuple

import dateutil.parser  # noqa:  I900 'dateutil' not listed as a requirement

from .schemas import CandleInterval, Quotation, SubscriptionInterval

__all__ = ("get_intervals",)

DAYS_IN_YEAR = 365


MAX_INTERVALS = {
    CandleInterval.CANDLE_INTERVAL_1_MIN: timedelta(days=1),
    CandleInterval.CANDLE_INTERVAL_5_MIN: timedelta(days=1),
    CandleInterval.CANDLE_INTERVAL_15_MIN: timedelta(days=1),
    CandleInterval.CANDLE_INTERVAL_HOUR: timedelta(weeks=1),
    CandleInterval.CANDLE_INTERVAL_DAY: timedelta(days=DAYS_IN_YEAR),
}


def get_intervals(
    interval: CandleInterval, from_: datetime, to: datetime
) -> Generator[Tuple[datetime, datetime], None, None]:
    max_interval = MAX_INTERVALS[interval]
    local_from = from_
    interval_timedelta = candle_interval_to_timedelta(interval)
    while local_from + interval_timedelta <= to:
        yield local_from, min(local_from + max_interval, to)
        local_from += max_interval


def quotation_to_decimal(quotation: Quotation) -> Decimal:
    fractional = quotation.nano / Decimal("10e8")
    return Decimal(quotation.units) + fractional


def decimal_to_quotation(decimal: Decimal) -> Quotation:
    fractional = decimal % 1
    return Quotation(units=int(decimal // 1), nano=int(fractional * Decimal("10e8")))


# fmt: off
_CANDLE_INTERVAL_TO_SUBSCRIPTION_INTERVAL_MAPPING = {
    CandleInterval.CANDLE_INTERVAL_1_MIN:
        SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    CandleInterval.CANDLE_INTERVAL_5_MIN:
        SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES,
    CandleInterval.CANDLE_INTERVAL_UNSPECIFIED:
        SubscriptionInterval.SUBSCRIPTION_INTERVAL_UNSPECIFIED,
}
# fmt: on


def candle_interval_to_subscription_interval(
    candle_interval: CandleInterval,
) -> SubscriptionInterval:
    return _CANDLE_INTERVAL_TO_SUBSCRIPTION_INTERVAL_MAPPING.get(
        candle_interval, SubscriptionInterval.SUBSCRIPTION_INTERVAL_UNSPECIFIED
    )


def now() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)


_CANDLE_INTERVAL_TO_TIMEDELTA_MAPPING = {
    CandleInterval.CANDLE_INTERVAL_1_MIN: timedelta(minutes=1),
    CandleInterval.CANDLE_INTERVAL_5_MIN: timedelta(minutes=5),
    CandleInterval.CANDLE_INTERVAL_15_MIN: timedelta(minutes=15),
    CandleInterval.CANDLE_INTERVAL_HOUR: timedelta(hours=1),
    CandleInterval.CANDLE_INTERVAL_DAY: timedelta(days=1),
    CandleInterval.CANDLE_INTERVAL_UNSPECIFIED: timedelta(minutes=1),
}


def candle_interval_to_timedelta(candle_interval: CandleInterval) -> timedelta:
    if delta := _CANDLE_INTERVAL_TO_TIMEDELTA_MAPPING.get(candle_interval):
        return delta
    raise ValueError(f"Cannot convert {candle_interval} to timedelta")


_DATETIME_MIN = datetime.min.replace(tzinfo=timezone.utc)


def ceil_datetime(datetime_: datetime, delta: timedelta):
    return datetime_ + (_DATETIME_MIN - datetime_) % delta


def floor_datetime(datetime_: datetime, delta: timedelta):
    return datetime_ - (datetime_ - _DATETIME_MIN) % delta


def dataclass_from_dict(klass, d):
    if issubclass(int, klass):
        return int(d)
    if issubclass(bool, klass):
        return bool(d)
    if issubclass(klass, datetime):
        return dateutil.parser.parse(d).replace(tzinfo=timezone.utc)
    if issubclass(klass, Quotation):
        d = ast.literal_eval(d)
    fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
    return klass(**{f: dataclass_from_dict(fieldtypes[f], d[f]) for f in d})


def datetime_range_floor(
    date_range: Tuple[datetime, datetime]
) -> Tuple[datetime, datetime]:
    start, end = date_range
    return start.replace(second=0, microsecond=0), end.replace(second=0, microsecond=0)

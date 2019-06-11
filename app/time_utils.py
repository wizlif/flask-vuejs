from datetime import datetime, timedelta

import datedelta


def format_time_to_mysql(date: datetime):
    return date.strftime('%Y-%m-%d %H:%M:%S')


def n_days_ago(days):
    return (datetime.now() - timedelta(days=days)).replace(
        hour=0, minute=0, second=0, microsecond=0)


def future(days=None, months=None, years=None):
    if days is not None:
        return datetime.now() + datedelta.datedelta(days=days)
    elif months is not None:
        return datetime.now() + datedelta.datedelta(months=months)
    elif years is not None:
        return datetime.now() + datedelta.datedelta(years=years)
    else:
        return datetime.now()

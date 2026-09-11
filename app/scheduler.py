import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from . import config, fetcher, keepalive

_scheduler = None


def start():
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(
        fetcher.run_fetch_cycle,
        trigger="interval",
        minutes=config.FETCH_INTERVAL_MINUTES,
        id="fetch_cycle",
        next_run_time=datetime.datetime.now(),
    )
    _scheduler.add_job(
        keepalive.ping,
        trigger="interval",
        hours=config.SUPABASE_KEEPALIVE_INTERVAL_HOURS,
        id="supabase_keepalive",
        next_run_time=datetime.datetime.now(),
    )
    _scheduler.start()
    return _scheduler

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.services.notification import send_low_stock_alert, send_weekly_report

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    hour, minute = settings.notification_time.split(":")
    scheduler.add_job(
        send_low_stock_alert,
        CronTrigger(hour=int(hour), minute=int(minute)),
        id="daily_low_stock_alert",
        replace_existing=True,
    )
    scheduler.add_job(
        send_weekly_report,
        CronTrigger(day_of_week=settings.weekly_report_day, hour=int(hour), minute=int(minute)),
        id="weekly_consumption_report",
        replace_existing=True,
    )
    scheduler.start()

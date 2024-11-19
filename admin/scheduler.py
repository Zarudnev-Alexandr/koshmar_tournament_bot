from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from start.saver import check_giveaways

scheduler = AsyncIOScheduler()


def schedule_start_giveaway(giveaway, bot):
    run_time = datetime.now() + timedelta(hours=giveaway.end_value)
    # run_time = datetime.now() + timedelta(seconds=15)
    print('hi from schedule_start_giveaway', flush=True)
    try:
        scheduler.add_job(
            check_giveaways,
            trigger=DateTrigger(run_date=run_time),
            args=(bot, giveaway.id)
        )
        if not scheduler.running:
            scheduler.start()
    except Exception as e:
        print(f"Ошибка при добавлении задачи: {e}", flush=True)
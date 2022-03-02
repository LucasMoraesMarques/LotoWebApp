import os
from celery import shared_task
from django.core import management


# We can have either registered task
@shared_task(name='get_draws_daily')
def get_draws_daily():
    management.call_command("get_draws", "--last")
    management.call_command("update_combinations")
    send_daily_results.delay()


@shared_task(name="send_daily_results_by_email")
def send_daily_results():
    try:
        management.call_command("generate_daily_results")
    except Exception as exc:
        print(exc)
    else:
        management.call_command("send_daily_results")


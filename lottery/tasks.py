import os

from celery import shared_task
from django.core import management


# We can have either registered task
@shared_task(name='get_draws_daily')
def get_draws_daily():
    management.call_command("get_draws", "--last")
    update_lottery_combinations_daily.delay()
    send_daily_results.delay()


@shared_task(name="update_lottery_combinations_daily")
def update_lottery_combinations_daily():
    management.call_command("update_combinations")



@shared_task
def send_daily_results():
    os.system("python /home/lucas/PycharmProjects/ProjetosLoteria/send_daily_result_heroku/verifica.py")

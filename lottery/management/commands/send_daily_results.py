from django.core.management import CommandError, BaseCommand
from django.utils import timezone
from lottery.services.email_sending import custom_send_email
from django.contrib.auth import get_user_model
from lottery.models import Result, Lottery


class Command(BaseCommand):
    help = "Send all generated reports files by email for each registered user"

    def handle(self, *args, **options):
        results = Result.objects.all()
        results = results.select_related("collection__user")
        users = get_user_model().objects.all()
        lotteries = Lottery.objects.all()
        email_info = {}
        for user in users:
            user_results = results.filter(collection__user=user)
            email_info[f"{user.username}"] = []
            for lottery in lotteries:
                files = []
                lottery_results = user_results.filter(lottery=lottery)
                if results:
                    for result in lottery_results:
                        files.append(result.report_file)
                    email_info[f"{user.username}"].append({
                        "SUBJECT": "TESTE",
                        "BODY": "TESTE",
                        "FROM": "lucasmoraes@gmail.com",
                        "TO": [user.email],
                        "TEMPLATE": "emails/template1.html",
                        "FILES": files})
        print(email_info)
        custom_send_email(email_info)

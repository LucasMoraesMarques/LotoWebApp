from django.core.management import CommandError, BaseCommand
from django.contrib.auth import get_user_model
from lottery.models import Lottery
from lottery.services import results
from django.utils import timezone


class Command(BaseCommand):
    help = "Generate the report files for each user after draw registration"

    def handle(self, *args, **options):
        users = get_user_model().objects.all()
        lotteries = Lottery.objects.all()
        date_now = timezone.datetime.now()
        for lottery in lotteries:
            last_draw = lottery.draws.last()
            print(lottery)
            if last_draw.date != date_now.date():
                for user in users:
                    print(user.username)
                    collections = user.collections.filter(is_reported=True, lottery=lottery)
                    print(collections)
                    for collection in collections:
                        actives_games_sets = collection.gamesets.filter(isActive=True)
                        print(actives_games_sets)
                        if actives_games_sets:
                            scores_by_games_set = results.check_scores_in_draw(last_draw, actives_games_sets)
                            print(scores_by_games_set)
                            prizes_balance = results.check_prizes_in_draw(last_draw, scores_by_games_set)
                            print(prizes_balance)
                            file_url, result_obj = results.create_text_report_file(last_draw, scores_by_games_set,
                                                                                   collection,
                                                                                   prizes_balance)
                            print(file_url)


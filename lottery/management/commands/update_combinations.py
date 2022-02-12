from django.core.management.base import BaseCommand
from lottery.models import Draw, Combinations, Lottery, Combinations
from django.db.models import F


class Command(BaseCommand):
    help = "Update the n-uplas combinations repetitions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--last",
            action="store_true",
            help="Update based only on the last draw saved"
        )

    def handle(self, *args, **options):
        lotteries = Lottery.objects.all()
        for loto in lotteries:
            draws = Draw.objects.filter(lottery=loto, number__gt=loto.last_draw_number)
            if draws:
                self.stdout.write(self.style.SUCCESS("\nThere are %d new draw for %s" % (len(draws), loto.name)))
                if not options['last']:
                    self.update_combinations(loto, draws)
                else:
                    last_draw = draws.last()
                    self.update_combinations(loto, [last_draw])
            else:
                self.stdout.write(self.style.ERROR("There are no new draws for %s" % loto.name))

    @staticmethod
    def update_combinations(lottery, draws):
        combinations = Combinations.objects.filter(lottery=lottery)
        for draw in draws:
            print(f"\nDraw {draw.number} - {draw.lottery.name} - {draw.result}")
            filtered_combs = combinations.filter(numbers__contained_by=draw.result)
            print(f"\nUpdating {len(filtered_combs)} combinations that are contained by the draw")
            filtered_combs.update(repetitions=F("repetitions") + 1)
            filtered_combs.save()

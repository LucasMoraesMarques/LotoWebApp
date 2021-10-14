from django import forms
from lottery.models import Lottery

LOTTERY_CHOICES = [
    ("lotofacil", "Lotofácil"),
    ("diadesorte", "Dia de Sorte"),
    ("megasena", "Mega Sena"),
]


class GameGeneratorForm(forms.Form):
    def __init__(self, loto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(loto)
        loto = Lottery.objects.get(id=loto)
        choicesNPlayed = [(str(i), i) for i in loto.possiblesChoicesRange]
        choicesNFixed = [(str(i), i) for i in range(1, loto.numbersRangeLimit + 1)]
        choicesNRemoved = [(str(i), i) for i in range(1, loto.numbersRangeLimit + 1)]
        self.fields["nPlayed"] = forms.ChoiceField(
            widget=forms.RadioSelect, choices=choicesNPlayed
        )
        self.fields["nFixed"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple, choices=choicesNFixed
        )
        self.fields["nRemoved"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple, choices=choicesNRemoved
        )

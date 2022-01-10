from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from datetime import datetime
import requests
from lottery.models import Draw, Lottery

LOTTERY_CHOICES = {"lotofacil": 1, "diadesorte": 2, "megasena": 3}


class Command(BaseCommand):
    help = "Get all draws for each lottery and save the new ones"

    def add_arguments(self, parser):
        parser.add_argument(
            '--last',
            action='store_true',
            help="Get just the last draw"
        )

    def handle(self, *args, **options):
        lotteries = Lottery.objects.all()
        for loto in lotteries:
            if not options['last']:
                draws = self.get_draws(loto)
                data = self.parse_response(draws, loto)
                self.check_has_draw(loto, data)
            else:
                draw = self.get_last(loto)
                self.save_last_draw(draw, loto)



    @staticmethod
    def get_draws(loto):
        try:
            resp = requests.get(loto.urlHistoricResultAPI)
            if resp.status_code != 200:
                raise requests.exceptions.RequestException
        except requests.exceptions.RequestException:
            raise CommandError("Error in requisition! '%s'" % resp.status_code)
        else:
            df = pd.read_html(resp.text, decimal=',', thousands='.')[0]
            return df

    @staticmethod
    def get_last(loto):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux i686; G518Rco3Yp0uLV40Lcc9hAzC1BOROTJADjicLjOmlr4=) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}
            response = requests.get(loto.urlDailyResultAPI, headers=headers)
        except Exception:
            raise CommandError("Error in requisition! '%s'" % response.status_code)
        else:
            if response.status_code == 200:
                data = response.json()
                return data

    def save_last_draw(self, draw, loto):
        faixas = draw["listaRateioPremio"]
        faixas = faixas[::-1]
        if not Draw.objects.filter(number=draw["numero"], lottery__name=loto.name).exists():
            if loto.name == "megasena":
                metadata = ([{f'Faixa {i - 3}':
                    {
                        "numeroDeGanhadores": faixas[index]["numeroDeGanhadores"],
                        "valorPremio": faixas[index]["valorPremio"],
                        "descricaoFaixa": f"{i} acertos"
                    }
                    for index, i in enumerate(loto.possiblesPointsToEarn)
                }])
                self.stdout.write(self.style.SUCCESS('Salvando Concurso "%s" - "%s"  da "%s"' % (
                    draw["numero"], draw["dataApuracao"], loto.name.capitalize())))
                rateio = [{}]
                for index, i in enumerate(loto.possiblesPointsToEarn):
                    rateio[0][f"Rateio {i} acertos"] = faixas[index]["valorPremio"]

            elif loto.name == 'diadesorte':
                faixas.pop(0)
                metadata = ([{f'Faixa {i - 3}':
                    {
                        "numeroDeGanhadores": faixas[index]["numeroDeGanhadores"],
                        "valorPremio": faixas[index]["valorPremio"],
                        "descricaoFaixa": f"{i} acertos"
                    }
                    for index, i in enumerate(loto.possiblesPointsToEarn)
                }])
                self.stdout.write(self.style.SUCCESS('Salvando Concurso "%s" - "%s"  da "%s"' % (
                    draw["numero"], draw["dataApuracao"], loto.name.capitalize())))
                rateio = [{}]
                for index, i in enumerate(loto.possiblesPointsToEarn):
                    rateio[0][f"Rateio {i} acertos"] = faixas[index]["valorPremio"]

            elif loto.name == "lotofacil":
                metadata = ([{f'Faixa {i - 10}':
                    {
                        "numeroDeGanhadores": faixas[index]["numeroDeGanhadores"],
                        "valorPremio": faixas[index]["valorPremio"],
                        "descricaoFaixa": f"{i} acertos"
                    }
                    for index, i in enumerate(loto.possiblesPointsToEarn)
                }])
                self.stdout.write(self.style.SUCCESS('Salvando Concurso "%s" - "%s"  da "%s"' % (
                    draw["numero"], draw["dataApuracao"], loto.name.capitalize())))
                rateio = [{}]
                for index, i in enumerate(loto.possiblesPointsToEarn):
                    rateio[0][f"Rateio {i} acertos"] = faixas[index]["valorPremio"]
            print(faixas)
            draw = Draw.objects.create(
                number=draw["numero"],
                date=datetime.strptime(draw["dataApuracao"], "%d/%m/%Y"),
                result=[int(i) for i in draw["listaDezenas"]],
                prizesInfoByRange=rateio,
                earnedValue=draw["valorArrecadado"],
                nextDrawEstimatedPrize=draw["valorEstimadoProximoConcurso"],
                nextDrawAccumulatedPrize=draw['valorAcumuladoProximoConcurso'],
                hasAccumulated=True if faixas[-1]["numeroDeGanhadores"] == 0 else False,
                lottery=loto,
                maxPrize=rateio[0][f'Rateio {loto.possiblesPointsToEarn[-1]} acertos'],
                metadata=metadata,
                extraResultField=draw["nomeTimeCoracaoMesSorte"].strip() if loto.name == 'diadesorte' else 0
            )
            draw.save()
        else:
            self.stdout.write(self.style.SUCCESS('Concurso "%s" - "%s"  da "%s" já está salvo no banco de dados' % (
                draw["numero"], draw["dataApuracao"], loto.name.capitalize())))

    @staticmethod
    def parse_response(df, loto):
        if loto.name == 'megasena':
            columns = ['Concurso', 'Local', 'Data do Sorteio', 'Bola 1', 'Bola 2', 'Bola 3', 'Bola 4',
                       'Bola 5', 'Bola 6', 'Ganhadores 6 acertos', 'Ganhadores 5 acertos', 'Ganhadores 4 acertos',
                       'Rateio 6 acertos', 'Rateio 5 acertos', 'Rateio 4 acertos', 'Cidade', 'Valor Arrecadado',
                       'Estimativa para o próximo concurso', 'Valor Acumulado Próximo Concurso', 'Acumulado',
                       'Sorteio Especial', 'Observação']
            df.columns = columns
            df = df.drop('Observação', axis=1)

        elif loto.name == "diadesorte":
            columns = ['Concurso', 'Local', 'Data do Sorteio', 'Bola 1', 'Bola 2', 'Bola 3', 'Bola 4',
                       'Bola 5', 'Bola 6', 'Bola 7', 'Mês da Sorte', 'Ganhadores 7 acertos', 'Ganhadores 6 acertos',
                       'Ganhadores 5 acertos', 'Ganhadores 4 acertos', 'Ganhadores Mês de Sorte', 'Rateio 7 acertos',
                       'Rateio 6 acertos', 'Rateio 5 acertos', 'Rateio 4 acertos', 'Rateio Mês de Sorte', 'Cidade',
                       'Valor Arrecadado', 'Estimativa para o próximo concurso',
                       'Valor Acumulado Próximo Concurso', 'Acumulado', 'Sorteio Especial', 'Observação']
            df.columns = columns
            df = df.drop('Observação', axis=1)
        elif loto.name == "lotofacil":
            columns = ['Concurso', 'Data do Sorteio', 'Bola 1', 'Bola 2', 'Bola 3', 'Bola 4', 'Bola 5', 'Bola 6',
                       'Bola 7', 'Bola 8', 'Bola 9', 'Bola 10', 'Bola 11', 'Bola 12', 'Bola 13', 'Bola 14',
                       'Bola 15', 'Valor Arrecadado', 'Ganhadores 15 acertos', 'Cidade', 'Ganhadores 14 acertos',
                       'Ganhadores 13 acertos', 'Ganhadores 12 acertos', 'Ganhadores 11 acertos', 'Rateio 15 acertos',
                       'Rateio 14 acertos', 'Rateio 13 acertos', 'Rateio 12 acertos', 'Rateio 11 acertos', 'Acumulado',
                       'Estimativa para o próximo concurso', 'Sorteio Especial']
            df.columns = columns
        df = df.dropna(how='any', thresh=3)
        df['Concurso'] = df['Concurso'].astype("int64")
        df.set_index('Concurso', inplace=True)
        df.sort_index(ascending=False, inplace=True)
        return df

    def check_has_draw(self, loto, df):
        if loto.name == 'megasena':
            for index, row in df.iterrows():
                if not loto.draws.all().filter(number=index).exists():
                    metadata = ([{f'Faixa {i - 3}':
                        {
                            "numeroDeGanhadores": row[f"Ganhadores {i} acertos"],
                            "valorPremio": row[f"Rateio {i} acertos"],
                            "descricaoFaixa": f"{i} acertos"
                        }
                        for i in loto.possiblesPointsToEarn
                    }])
                    self.stdout.write(self.style.SUCCESS('Salvando Concurso "%s" - "%s"  da "%s"' % (
                    index, row['Data do Sorteio'], loto.name.capitalize())))
                    rateio = [row['Rateio 6 acertos':'Rateio 4 acertos'].to_dict()]

                    Draw.objects.create(
                        number=index,
                        date=datetime.strptime(row['Data do Sorteio'], "%d/%m/%Y"),
                        result=row['Bola 1': 'Bola 6'].to_list(),
                        prizesInfoByRange=rateio,
                        earnedValue=row['Valor Arrecadado'],
                        nextDrawEstimatedPrize=row['Estimativa para o próximo concurso'],
                        nextDrawAccumulatedPrize=row['Valor Acumulado Próximo Concurso'],
                        hasAccumulated=True if row[f"Ganhadores 6 acertos"] == 0 else False,
                        lottery=loto,
                        maxPrize=row['Rateio 6 acertos'],
                        metadata=metadata,
                    )
                else:
                    break
        elif loto.name == "diadesorte":
            for index, row in df.iterrows():
                if not loto.draws.all().filter(number=index).exists():
                    metadata = ([{f'Faixa {i - 3}':
                        {
                            "numeroDeGanhadores": row[f"Ganhadores {i} acertos"],
                            "valorPremio": row[f"Rateio {i} acertos"],
                            "descricaoFaixa": f"{i} acertos"
                        }
                        for i in loto.possiblesPointsToEarn
                    }])
                    self.stdout.write(self.style.SUCCESS('Salvando Concurso "%s" - "%s"  da "%s"' % (
                    index, row['Data do Sorteio'], loto.name.capitalize())))
                    rateio = [row['Rateio 7 acertos':'Rateio 4 acertos'].to_dict()]

                    Draw.objects.create(
                        number=index,
                        date=datetime.strptime(row['Data do Sorteio'], "%d/%m/%Y"),
                        result=row['Bola 1': 'Bola 7'].to_list(),
                        prizesInfoByRange=rateio,
                        earnedValue=row['Valor Arrecadado'],
                        nextDrawEstimatedPrize=row['Estimativa para o próximo concurso'],
                        nextDrawAccumulatedPrize=row['Valor Acumulado Próximo Concurso'],
                        hasAccumulated=True if row[f"Ganhadores 7 acertos"] == 0 else False,
                        lottery=loto,
                        metadata=metadata,
                        maxPrize=row['Rateio 7 acertos'],
                        extraResultField=row["Mês da Sorte"]
                    )
                else:
                    break

        elif loto.name == "lotofacil":
            for index, row in df.iterrows():
                if not loto.draws.all().filter(number=index).exists():
                    metadata = ([{f'Faixa {i - 10}':
                        {
                            "numeroDeGanhadores": row[f"Ganhadores {i} acertos"],
                            "valorPremio": row[f"Rateio {i} acertos"],
                            "descricaoFaixa": f"{i} acertos"
                        }
                        for i in loto.possiblesPointsToEarn
                    }])
                    self.stdout.write(self.style.SUCCESS('Salvando Concurso "%s" - "%s"  da "%s"' % (
                        index, row['Data do Sorteio'], loto.name.capitalize())))
                    rateio = [row['Rateio 15 acertos':'Rateio 11 acertos'].to_dict()]

                    Draw.objects.create(
                        number=index,
                        date=datetime.strptime(row['Data do Sorteio'], "%d/%m/%Y"),
                        result=row['Bola 1': 'Bola 15'].to_list(),
                        prizesInfoByRange=rateio,
                        earnedValue=row['Valor Arrecadado'],
                        nextDrawEstimatedPrize=row['Estimativa para o próximo concurso'],
                        nextDrawAccumulatedPrize=row['Acumulado'],
                        hasAccumulated=True if row[f"Ganhadores 15 acertos"] == 0 else False,
                        lottery=loto,
                        maxPrize=row['Rateio 15 acertos'],
                        metadata=metadata)
                else:
                    break

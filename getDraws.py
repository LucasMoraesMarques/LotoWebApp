import os
import re

import django
import pandas as pd
from datetime import datetime
import requests
import lxml
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LotoWebApp.settings")
django.setup()
from lottery.models import Draw, Lottery

LOTTERY_CHOICES = {"lotofacil": 1, "diadesorte": 2, "megasena": 3}

def getDraws(loto):
    while True:
        try:
            resp = requests.get(loto.urlHistoricResultAPI)
            if resp.status_code != 200:
                raise requests.exceptions.RequestException
        except requests.exceptions.RequestException:
            continue
        else:
            dt = pd.read_html(resp.text, decimal=',', thousands='.')[0]
            if loto.name == 'megasena':
                columns = ['Concurso', 'Local', 'Data do Sorteio', 'Bola 1', 'Bola 2', 'Bola 3', 'Bola 4',
                           'Bola 5', 'Bola 6', 'Ganhadores 6 acertos', 'Ganhadores 5 acertos', 'Ganhadores 4 acertos',
                           'Rateio 6 acertos', 'Rateio 5 acertos', 'Rateio 4 acertos', 'Cidade', 'Valor Arrecadado',
                           'Estimativa para o próximo concurso', 'Valor Acumulado Próximo Concurso', 'Acumulado',
                           'Sorteio Especial', 'Observação']
                dt.columns = columns
                dt = dt.drop('Observação', axis=1)

            elif loto.name == "diadesorte":
                columns = ['Concurso', 'Local', 'Data do Sorteio', 'Bola 1', 'Bola 2', 'Bola 3', 'Bola 4',
                           'Bola 5', 'Bola 6', 'Bola 7', 'Mês da Sorte', 'Ganhadores 7 acertos', 'Ganhadores 6 acertos',
                           'Ganhadores 5 acertos', 'Ganhadores 4 acertos', 'Ganhadores Mês de Sorte', 'Rateio 7 acertos',
                           'Rateio 6 acertos', 'Rateio 5 acertos', 'Rateio 4 acertos', 'Rateio Mês de Sorte', 'Cidade',
                           'Valor Arrecadado', 'Estimativa para o próximo concurso',
                           'Valor Acumulado Próximo Concurso', 'Acumulado', 'Sorteio Especial', 'Observação']
                dt.columns = columns
                dt = dt.drop('Observação', axis=1)
            elif loto.name == "lotofacil":
                columns = ['Concurso', 'Data do Sorteio', 'Bola 1', 'Bola 2', 'Bola 3', 'Bola 4', 'Bola 5', 'Bola 6',
                           'Bola 7', 'Bola 8', 'Bola 9', 'Bola 10', 'Bola 11', 'Bola 12', 'Bola 13', 'Bola 14',
                           'Bola 15', 'Valor Arrecadado', 'Ganhadores 15 acertos', 'Cidade', 'Ganhadores 14 acertos',
                           'Ganhadores 13 acertos', 'Ganhadores 12 acertos', 'Ganhadores 11 acertos', 'Rateio 15 acertos',
                           'Rateio 14 acertos', 'Rateio 13 acertos', 'Rateio 12 acertos', 'Rateio 11 acertos', 'Acumulado',
                           'Estimativa para o próximo concurso', 'Sorteio Especial']
                dt.columns = columns
            dt = dt.dropna(how='any', thresh=3)
            dt['Concurso'] = dt['Concurso'].astype("int64")
            dt.set_index('Concurso', inplace=True)
            dt.sort_index(ascending=False, inplace=True)
            return dt


def checkHasDraw(loto, dt):

    if loto.name == 'megasena':
        for index, row in dt.iterrows():
            if not loto.draws.all().filter(number=index).exists():
                metadata = ([{f'Faixa {i - 3}':
                    {
                        "numeroDeGanhadores": row[f"Ganhadores {i} acertos"],
                        "valorPremio": row[f"Rateio {i} acertos"],
                        "descricaoFaixa": f"{i} acertos"
                    }
                    for i in loto.possiblesPointsToEarn
                }])
                print(f"Salvando Concurso {index} - {row['Data do Sorteio']} da {loto.name.capitalize()}")
                rateio = [row['Rateio 6 acertos':'Rateio 4 acertos'].to_dict()]

                draw = Draw.objects.create(
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
                draw.save()
            else:
                break
    elif loto.name == "diadesorte":
        for index, row in dt.iterrows():
            if not loto.draws.all().filter(number=index).exists():
                metadata = ([{f'Faixa {i-3}':
                            {
                                "numeroDeGanhadores": row[f"Ganhadores {i} acertos"],
                                "valorPremio": row[f"Rateio {i} acertos"],
                                "descricaoFaixa": f"{i} acertos"
                            }
                        for i in loto.possiblesPointsToEarn
                }])
                print(f"Salvando Concurso {index} - {row['Data do Sorteio']} da {loto.name.capitalize()}")
                rateio = [row['Rateio 7 acertos':'Rateio 4 acertos'].to_dict()]

                draw = Draw.objects.create(
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
                    extraResultField = row["Mês da Sorte"]
                )
                draw.save()
            else:
                break

    elif loto.name == "lotofacil":
        for index, row in dt.iterrows():
            if not loto.draws.all().filter(number=index).exists():
                metadata = ([{f'Faixa {i-10}':
                            {
                                "numeroDeGanhadores": row[f"Ganhadores {i} acertos"],
                                "valorPremio": row[f"Rateio {i} acertos"],
                                "descricaoFaixa": f"{i} acertos"
                            }
                        for i in loto.possiblesPointsToEarn
                }])
                print(f"Salvando Concurso {index} - {row['Data do Sorteio']} da {loto.name.capitalize()}")
                rateio = [row['Rateio 15 acertos':'Rateio 11 acertos'].to_dict()]

                draw = Draw.objects.create(
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
                draw.save()
            else:
                break

if __name__ == "__main__":
    for loto in Lottery.objects.all():
        draws = getDraws(loto)
        print(draws.head())
        checkHasDraw(loto, dt=draws)

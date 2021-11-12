import os
import re

import django
import pandas as pd
from datetime import datetime
import json
import requests
import lxml
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LotoWebApp.settings")
django.setup()
from lottery.models import Draw, Lottery

LOTTERY_CHOICES = {"lotofacil": 1, "diadesorte": 2, "megasena": 3}



def mapDrawFields(loto, dt):
    accumulated = {
        'SIM': True,
        'NÃO': False,
    }
    print(loto.name)
    if loto.name == 'megasena':
        for index, row in dt.iterrows():
            metadata = ([{f'Faixa {i - 3}':
                {
                    "numeroDeGanhadores": row[f"Ganhadores {i} acertos"],
                    "valorPremio": row[f"Rateio {i} acertos"],
                    "descricaoFaixa": f"{i} acertos"
                }
                for i in loto.possiblesPointsToEarn
            }])
            print(metadata)
            rateio = [row['Rateio 6 acertos':'Rateio 4 acertos'].to_dict()]

            print(rateio)
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



    elif loto.name == "diadesorte":
        for index, row in dt.iterrows():
            metadata = ([{f'Faixa {i-3}':
                        {
                            "numeroDeGanhadores": row[f"Ganhadores {i} acertos"],
                            "valorPremio": row[f"Rateio {i} acertos"],
                            "descricaoFaixa": f"{i} acertos"
                        }
                    for i in loto.possiblesPointsToEarn
            }])
            print(metadata)
            rateio = [row['Rateio 7 acertos':'Rateio 4 acertos'].to_dict()]

            print(rateio)
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


    elif loto.name == "lotofacil":
        for index, row in dt.iterrows():
            metadata = ([{f'Faixa {i-10}':
                        {
                            "numeroDeGanhadores": row[f"Ganhadores {i} acertos"],
                            "valorPremio": row[f"Rateio {i} acertos"],
                            "descricaoFaixa": f"{i} acertos"
                        }
                    for i in loto.possiblesPointsToEarn
            }])
            print(metadata)
            rateio = [row['Rateio 15 acertos':'Rateio 11 acertos'].to_dict()]

            print(rateio)
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


if __name__ == "__main__":
    #draws = pd.read_excel("drawsLotofacil.xlsx", index_col=0, header=0).sort_index(ascending=True)
    draws = pd.read_excel("drawsMegasena.xlsx", index_col=0, header=0).sort_index(ascending=True)
    #draws = pd.read_excel("drawsDiadesorte.xlsx", index_col=0, header=0).sort_index(ascending=True)
    print(draws.head())
    lotoId = 3
    loto = Lottery.objects.get(id=lotoId)
    """try:
        resp = requests.get(loto.urlHistoricResultAPI)
        if resp.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException:
        pass
    else:
        dt = pd.read_html(resp.text, decimal=',', thousands='.')[0]"""
    #print(dt.iloc[:5,:].to_string())
    mapDrawFields(loto, dt=draws)

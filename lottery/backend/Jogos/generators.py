import numpy as np
import pandas as pd
from lottery.models import Lottery, Game
import random


def simple(lototype, nPlayed, nJogos, removedNumbers, fixedNumbers):
    """ Gerador simples. Sem filtros específicos

    :param nPlayed: Quantidade de números escolhidos por jogo
    :param nJogos: Número de jogos a ser criado
    :param removedNumbers: Números removidos
    :param fixedNumbers: Números fixados
    :return: None. Cria n jogos pedidos pelo user
    """
    loto = Lottery.objects.get(name=lototype)
    nFixed = len(fixedNumbers)
    nPossibles = range(1, loto.numbersRangeLimit+1)
    print(loto.possiblesChoicesRange)
    jogos = [0]
    numbersAllowed = np.array(np.setdiff1d(np.array(nPossibles), removedNumbers))
    numbersAllowed = np.setdiff1d(numbersAllowed, fixedNumbers)

    cont = 0
    while cont < nJogos:
        numbersAllowedCopy = list(numbersAllowed)
        random.shuffle(numbersAllowedCopy)
        np.random.RandomState(cont)
        jogo = np.zeros(nPlayed - nFixed)
        for i in range(0, jogo.size):
            number = np.random.choice(numbersAllowedCopy, 1)
            jogo[i] = number
            numbersAllowedCopy.remove(number)

        jogo = np.union1d(jogo, fixedNumbers).astype("int8")
        jogo = list(jogo)
        if jogo in jogos:
            continue
        else:
            jogos.append(jogo)
            cont += 1

    jogos.pop(0)
    jogos = pd.DataFrame(jogos)
    return jogos


def smart(lototype, nJogos, removedNumbers, fixedNumbers, kwargs):
    """ Gerador inteligente que realiza queries na database de combinações possíveis

    :param nPlayed: Quantidade de números escolhidos por jogo
    :param removedNumbers: Números removidos
    :param fixedNumbers: Números fixados
    :param kwargs: Filtros específicos para a query
    :return: None. Cria n jogos pedidos pelo user dentro dos possíveis
    """
    games = calc_combs(lototype, removedNumbers, fixedNumbers, kwargs)
    games = pd.DataFrame(games.values())
    index = list(games.index)
    random.shuffle(index)
    games = games.iloc[index, :]
    games = games[:nJogos]
    return games


def calc_combs(lototype, numbersRemoved, numbersFixed, kwargs):
    """ Calcula todas as combinações com os filtro dados através da database de todos os jogos

    :param lototype: Loteria escolhida
    :param numbersRemoved: Números removidos
    :param numbersFixed: Números fixados
    :param kwargs: Filtros inteligentes
    :return: Todas as combinações válidas
    """
    loto = Lottery.objects.get(name=lototype)
    games = Game.objects.filter(lottery=loto)
    if numbersRemoved:
        games = games.exclude(arrayNumbers__contains=numbersRemoved)
    if numbersFixed:
        games = games.filter(arrayNumbers__contains=numbersFixed)
    print(games.count())
    print(kwargs)
    for k, v in kwargs.items():
        if k == "nPrimes":
            games = games.filter(n_primes=v)
        elif k == "maxSeq":
            games = games.filter(max_seq__lte=v)
        elif k == "minSeq":
            games = games.filter(min_seq__gte=v)
        elif k == "maxGap":
            games = games.filter(max_gap__lte=v)
        elif k == "isOdd":
            games = games.filter(is_odd=v)
    return games


"""

class Jogos(object):

    def __init__(self, loto_type, name="default"):
        " Classe Jogos

        :param loto_type: Tipo de Loteria
        :param name: Nome do conjunto de jogos
        "
        self.loteria = loto_type
        self.jogos = pd.DataFrame()
        self.nPlayed = self.loteria.metadata["nRange"][0]
        self.jogoname = name + ".xlsx"
        self.metadata = dict()

    def __str__(self):
        return "Classe Jogos:\n" \
               "-> Cria, salva, carrega e confere conjuntos de jogos\n" \
               "-> Atributos:\n" \
               "    -> Tipo de Loteria\n" \
               "    -> Conjunto de Jogos\n" \
               "    -> Nome dos Jogos\n" \
               "    -> Metadados do conjunto de Jogos\n" \
               "-> Possui 2 geradores de jogos:\n" \
               "    -> Gerador Simples: \n" \
               "        - Cria combinações sem filtros inteligentes, com números fixos e excluídos facultativos\n" \
               "        - Funciona bem para números de jogos factíveis\n" \
               "    -> Gerador Complexo:\n" \
               "        - Cria combinações inteligentes levando em conta filtros pré-determinados\n" \
               "        - Usa a database contendo todas as combinações possíveis\n"

    def readJogos(self, name):
        " Lê os jogos armazenados com o nome dado

        :param name: Nome do conjunto de jogos a ser lido
        :return: None
        "
        self.jogos = pd.read_excel(
            os.path.join(os.getcwd(), f"user_data\\user_games\\{self.loteria.nome}\\games\\{name}"),
            header=0,
            index_col=0)
        self.jogoname = name
        self.jogos.astype('int8')
        self.nPlayed = self.jogos.shape[1]

    def writeJogos(self):
        " Salva os jogos em um arquivo excel

        :return: None
        "
        self.jogos.index = [f"Jogo {i}" for i in range(1, self.jogos.shape[0]+1)]
        self.jogos.columns = [f"bola {i}" for i in range(1, self.nPlayed + 1)]
        self.jogos.to_excel(
            os.path.join(os.getcwd(), f"user_data\\user_games\\{self.loteria.nome}\\games\\{self.jogoname}"))

    def delete(self):
        " Deleta o arquivo de um determinado set de jogos

        :return: None
        "
        os.remove(os.path.join(os.getcwd(), f"user_data\\user_games\\{self.loteria.nome}\\games\\{self.jogoname}"),)

    def getExternalJogos(self, manual=False, clipboarb=False, nPlayed=0, nJogos=0, jogoname='', path='', filename=''):
        "Lê jogos externos entrados pelo user

        :param manual: Especifica se a entrada será por digitação
        :param clipboarb: Especifica se a entrada será por Área de Transferência
        :param nPlayed: Número de marcações por jogo
        :param nJogos: Número de jogos a serem lidos
        :param jogoname: Nome do conjunto de jogos lido
        :param path: Se manual e clipboard são falsos, especifica o caminho do arquivo a ser lido
        :param filename: Nome do arquivo a ser lido no path dado
        :return: None
        "

        self.jogoname = jogoname + ".xlsx"

        if manual:
            jogos = funcs.getExternalJogo(nJogos, nPlayed, nrange=self.loteria.metadata["nPossiveis"])
            self.jogos = pd.DataFrame.from_dict(jogos, orient="index")
            self.nPlayed = nPlayed
            self.writeJogos()

        elif path != '':
            try:
                path += f"/{filename}"
                ext = filename.split(".")[-1]
                if ext in ['txt', 'text', 'csv']:
                    jogos = pd.read_csv(path, header=None, index_col=None, sep=r"\s+|[,]", engine='python')
                elif ext in ["xlsx", 'xls']:
                    jogos = pd.read_excel(path, header=None, index_col=None)
                else:
                    raise FileNotFoundError
                if jogos.shape[1] not in self.loteria.metadata['nRange']:
                    raise ValueError

            except (FileExistsError, FileNotFoundError):
                print(st.textLine("Não foi possível encontrar o arquivo. Tente novamente com um endereço absoluto para "
                                  "o diretório do arquivo.\n", 'vermelho'))
                filename = input(st.textLine("Digite o nome do arquivo com extensão:", 'amarelo'))
                self.getExternalJogos(path=input(st.textLine("Endereço do diretório:", 'amarelo')),
                                      jogoname=self.jogoname, filename=filename)

            except ValueError:
                print(st.textLine("Os jogos carregados não seguem os números de marcações permitidas pelo tipo de "
                                  "loteria.\n", 'vermelho'))
                return
            else:
                self.jogos = jogos
                self.nPlayed = jogos.shape[1]
                self.writeJogos()

        elif clipboarb:
            try:
                jogos = pd.read_clipboard(sep=r"[,]|\s+", header=None)
                if jogos.shape[1] not in self.loteria.metadata['nRange']:
                    raise ValueError
            except pd.errors.EmptyDataError:
                print(st.textLine("Não há nada para ser lido no clipboard", 'vermelho'))
            except ValueError:
                print(st.textLine("Não há jogos com o padrão esperado na Área de Transferência. "
                                  "Leia o menu ajuda.", 'vermelho'))
            else:
                self.jogos = jogos
                self.nPlayed = self.jogos.shape[1]
                self.writeJogos()

    def checkResults(self, sorteio):
        " Confere os resultados para dado conjunto de jogos

        :param sorteio: Instância da classe Sorteio
        :return: None. Exporta para arquivo.
        "
        filePath = os.path.join(os.getcwd(), f"user_data\\user_games\\{self.loteria.nome}"
                                           f"\\results\\res_{self.loteria.nome}_{sorteio.metadata['numero']}_"
                                             f"{self.jogoname.replace('.xlsx', '')}.txt")

        with open(filePath, "w+") as f:
            f.write(f"Resultado referente ao concurso nº {sorteio.metadata['numero']} "
                f"da {sorteio.metadata['tipoJogo']} "
                f"realizado no dia {sorteio.metadata['dataApuracao']}\n")

        if self.loteria.nome == 'diadesorte':
            res = [int(i) for i in sorteio.resultado[0:7]]
        else:
            res = sorteio.resultado
            res = [int(i) for i in res]

        print(st.textLine(f'Os resultados do jogo {self.jogoname.replace(".xlsx", "")} são:', 'azul'))

        with open(filePath, "a") as f:
            if type(self.jogos) == dict:
                # Pandas retorna um dict para excel com mais de 1 planilha
                for k, v in self.jogos.items():
                    f.write(f"\n{k:=^20}\n")
                    for key, value in funcs.checkScores(v, res).items():
                        f.write(f"{key}: {value} acertos\n")
                        print(st.textLine(f"{key}: ", 'azul') + st.textLine(f"{value} acertos", 'verde'))

            elif type(self.jogos) == pd.core.frame.DataFrame:
                f.write(f"\n{self.jogoname.replace('.xlsx', ''):=^20}\n")
                for k, v in self.jogos.iterrows():
                    scores = funcs.checkScores(v, res)
                    f.write(f"{k}: {scores} acertos\n")
                    print(st.textLine(f"{k}: ", 'azul') + st.textLine(f"{scores} acertos", 'verde'))

        print(st.textLine(f"\nOs resultados podem ser exportados através do arquivo txt no seguinte diretório:",'azul'))
        print(st.textLine(f"\nuser_data\\user_games\\{self.loteria.nome}"
                          f"\\results\\res_{self.loteria.nome}_{sorteio.metadata['numero']}_"
                          f"{self.jogoname.replace('.xlsx', '')}.txt", 'amarelo'))

   
    def applyFiltersOnJogos(self):
        " Gera metadados dos filtros sobre o conjunto de jogos

        :return: None. Atribui dados ao atributo metadata
        "
        nPos = self.nPlayed
        self.metadata["Jogos Filtrados"] = pd.DataFrame()
        dt = self.metadata["Jogos Filtrados"]
        dt["isOdd"] = self.jogos.iloc[:, : nPos].apply(funcs.isOdd, axis=1)
        dt["maxSeq"] = self.jogos.iloc[:, : nPos].apply(lambda x: funcs.sequences(x), axis=1).\
            apply(lambda x: max(x))
        dt["minSeq"] = self.jogos.iloc[:, : nPos].apply(lambda x: funcs.sequences(x), axis=1).\
            apply(lambda x: min(x))
        dt["maxGap"] = self.jogos.iloc[:, : nPos].apply(funcs.gap, axis=1).apply(lambda x: max(x))
        dt["nPrime"] = self.jogos.iloc[:, : nPos].apply(funcs.nPrimeNumbers, axis=1)

    def showDatabaseMetadata(self):
        " Imprime metadados sobre a database do set de jogos carregado

        :return: None
        "
        if self.jogos.shape[0] > 200:
            print(st.textLine("Os primeiros 200 jogos são:", 'azul'))
            print(self.jogos.iloc[:200, :].to_string())
        else:
            print(st.textLine("Os jogos carregados são:", 'azul'))
            print(self.jogos.to_string())

        print(st.textLine("\nO ranking dos números é:", 'amarelo'))
        print(st.textLine(self.numberRankingAll().to_string()))
        print(st.textLine("\nAs informações dos filtros são:\n"))

        for col in ['isOdd', 'maxGap', 'maxSeq', 'minSeq', 'nPrime']:
            if col != 'isOdd':
                print(funcs.transFilterNames(col))
                print(st.textLine("Número Repetições", 'amarelo'))
            else:
                print(funcs.transFilterNames(col))
                print(st.textLine("Ímpar Repetições", 'amarelo'))
            print(st.textLine(self.metadata["Jogos Filtrados"][col].value_counts().to_string()))

    def filterDatabase(self, filters):
        " Realiza queries na database de jogos com os filtros dados

        :param filters: Dicionário com os filtros entrados pelo user
        :return: None
        "
        dt = self.jogos.copy()
        for filter, value in filters.items():
            funcs.transFilterNames(filter)
            if 'min' in filter:
                dt = dt.loc[self.metadata["Jogos Filtrados"][filter] >= value]
            elif 'max' in filter:
                dt = dt.loc[self.metadata["Jogos Filtrados"][filter] <= value]
            elif filter in ['isOdd', 'nPrime']:
                dt = dt.loc[self.metadata["Jogos Filtrados"][filter] == value]

        if dt.shape[0] != 0:
            print(st.textLine(f"A database resultante da aplicação dos filtros é:", 'amarelo'))
            print(st.textLine(dt.to_string()))
            print(st.textLine(f"\nA database filtrada possui {dt.shape[0]} jogos, sendo que a database original"
                              f" tinha {self.jogos.shape[0]}, o que resulta numa redução de "
                              f"{round(100*(1-round(dt.shape[0]/self.jogos.shape[0], 2)), 2)} %", 'amarelo'))
        else:
            print(st.textLine(f"Não há jogos com essas combinações de filtros", 'vermelho'))

    def numberRankingAll(self):
        "Rankeia os números mais sorteados na database de jogos

        :return: Ranking dos números
        "
        print(self.jogos)
        rank = dict()
        for i in self.loteria.metadata["nPossiveis"]:
            v = np.where(self.jogos == i, True, False).sum()
            rank[f'{i}'] = v
        rankSeries = pd.Series(rank)
        rankSeries.sort_values(ascending=False, inplace=True)
        rankSeries.name = "Ranking Geral"
        self.metadata["Ranking"] = rankSeries
        return self.metadata["Ranking"]
"""


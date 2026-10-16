"""Regras e modelos da Batalha Naval.

Este módulo não exibe menus nem lê input. Ele concentra as regras para que
elas possam ser testadas sem depender do terminal.
"""

import random


class Navio:
    """Representa um navio e as casas que ele ocupa e recebeu tiros."""

    def __init__(self, tamanho, nome):
        if type(tamanho) is not int or tamanho < 1:
            raise ValueError("O tamanho do navio deve ser um inteiro positivo.")
        self.tamanho = tamanho
        self.nome = nome
        self.posicoes = []
        self.acertos = {}

    def esta_afundado(self):
        return len(self.acertos) == self.tamanho


class Tabuleiro:
    """Armazena navios, tiros e regras de posicionamento do tabuleiro."""

    def __init__(self, tamanho=5):
        if type(tamanho) is not int or not 1 <= tamanho <= 26:
            raise ValueError("O tabuleiro deve ter entre 1 e 26 casas por lado.")
        self.tamanho = tamanho
        self.grade = [[None for _ in range(tamanho)] for _ in range(tamanho)]
        self.navios = []
        self.tiros = {}

    def validar_coordenada(self, linha, coluna):
        if type(linha) is not int or type(coluna) is not int:
            raise ValueError("Linha e coluna devem ser números inteiros.")
        if not (0 <= linha < self.tamanho and 0 <= coluna < self.tamanho):
            raise ValueError("Coordenada fora do tabuleiro.")

    def posicionar_navio(self, navio, linha, coluna, orientacao):
        if navio.posicoes:
            raise ValueError("Este navio já foi posicionado.")
        if orientacao not in ("H", "V"):
            raise ValueError("Use H para horizontal ou V para vertical.")

        posicoes = []
        for deslocamento in range(navio.tamanho):
            nova_linha = linha + (deslocamento if orientacao == "V" else 0)
            nova_coluna = coluna + (deslocamento if orientacao == "H" else 0)
            self.validar_coordenada(nova_linha, nova_coluna)
            if self.grade[nova_linha][nova_coluna] is not None:
                raise ValueError("Um navio não pode sobrepor outro.")
            posicoes.append((nova_linha, nova_coluna))

        for nova_linha, nova_coluna in posicoes:
            self.grade[nova_linha][nova_coluna] = navio
        navio.posicoes = posicoes
        self.navios.append(navio)

    def receber_tiro(self, linha, coluna):
        self.validar_coordenada(linha, coluna)
        coordenada = (linha, coluna)
        if coordenada in self.tiros:
            raise ValueError("Esta coordenada já recebeu tiro.")

        alvo = self.grade[linha][coluna]
        self.tiros[coordenada] = alvo
        if alvo is not None:
            alvo.acertos[coordenada] = True
        return alvo

    def quantidade_navios_afundados(self):
        return sum(navio.esta_afundado() for navio in self.navios)


class Jogador:
    """Jogador humano ou base para o jogador controlado pelo computador."""

    def __init__(self, nome):
        self.nome = nome
        self.tabuleiro = Tabuleiro()
        self.tiros = {}

    def atacar(self, adversario, linha, coluna):
        if adversario is self:
            raise ValueError("Um jogador não pode atacar o próprio tabuleiro.")
        resultado = adversario.tabuleiro.receber_tiro(linha, coluna)
        self.tiros[(linha, coluna)] = resultado
        return resultado

    def verificar_derrota(self):
        return bool(self.tabuleiro.navios) and all(
            navio.esta_afundado() for navio in self.tabuleiro.navios
        )


class Computador(Jogador):
    """Computador que escolhe tiros aleatórios ou persegue um acerto."""

    def __init__(self, dificuldade):
        super().__init__("Computador")
        self.dificuldade = dificuldade
        self.alvos_pendentes = []

    def escolher_tiro(self):
        disponiveis = [
            (linha, coluna)
            for linha in range(self.tabuleiro.tamanho)
            for coluna in range(self.tabuleiro.tamanho)
            if (linha, coluna) not in self.tiros
        ]
        if self.dificuldade == "fácil" or not self.alvos_pendentes:
            return random.choice(disponiveis)

        while self.alvos_pendentes:
            alvo = self.alvos_pendentes.pop(0)
            if alvo in disponiveis:
                return alvo
        return random.choice(disponiveis)

    def registrar_resultado(self, linha, coluna, resultado):
        if resultado is None or self.dificuldade == "fácil":
            return
        if resultado.esta_afundado():
            self.alvos_pendentes.clear()
            return

        # Depois de acertar, adiciona as casas vizinhas como próximos alvos.
        for vizinho in (
            (linha - 1, coluna),
            (linha + 1, coluna),
            (linha, coluna - 1),
            (linha, coluna + 1),
        ):
            if (
                0 <= vizinho[0] < self.tabuleiro.tamanho
                and 0 <= vizinho[1] < self.tabuleiro.tamanho
                and vizinho not in self.tiros
                and vizinho not in self.alvos_pendentes
            ):
                self.alvos_pendentes.append(vizinho)


def ler_coordenada(texto, tamanho=5):
    """Converte 'A1' em índices internos (0, 0)."""
    texto = texto.strip().upper()
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:tamanho]
    if len(texto) < 2 or texto[0] not in letras or not texto[1:].isdigit():
        raise ValueError("Use uma coordenada como A1 ou E5.")
    linha = int(texto[1:]) - 1
    coluna = letras.index(texto[0])
    if not 0 <= linha < tamanho:
        raise ValueError("Coordenada fora do tabuleiro.")
    return linha, coluna


def frota_padrao():
    """Retorna os navios usados em cada partida."""
    return [(3, "Cruzador"), (2, "Destroyer"), (1, "Submarino")]


def posicionar_frota_automaticamente(jogador):
    """Posiciona a frota embaralhando todas as tentativas possíveis."""
    for tamanho, nome in frota_padrao():
        candidatos = [
            (linha, coluna, orientacao)
            for linha in range(jogador.tabuleiro.tamanho)
            for coluna in range(jogador.tabuleiro.tamanho)
            for orientacao in ("H", "V")
        ]
        random.shuffle(candidatos)
        for linha, coluna, orientacao in candidatos:
            try:
                jogador.tabuleiro.posicionar_navio(
                    Navio(tamanho, nome), linha, coluna, orientacao
                )
                break
            except ValueError:
                continue
        else:
            raise RuntimeError("Não foi possível posicionar a frota.")

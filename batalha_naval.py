"""Ponto de entrada da Batalha Naval.

Execute este arquivo para abrir o menu do jogo. As classes principais são
reexportadas para manter compatibilidade com testes e comandos antigos.
"""

from interface import menu
from jogo import (
    Computador,
    Jogador,
    Navio,
    Tabuleiro,
    frota_padrao,
    ler_coordenada,
    posicionar_frota_automaticamente,
)

__all__ = [
    "Computador",
    "Jogador",
    "Navio",
    "Tabuleiro",
    "frota_padrao",
    "ler_coordenada",
    "posicionar_frota_automaticamente",
]


if __name__ == "__main__":
    menu()

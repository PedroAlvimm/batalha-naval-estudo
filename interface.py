"""Interface de terminal da Batalha Naval."""

import json
import sys
from datetime import datetime
from pathlib import Path

from jogo import (
    Computador,
    Jogador,
    Navio,
    Tabuleiro,
    frota_padrao,
    ler_coordenada,
    posicionar_frota_automaticamente,
)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


RESET = "\033[0m"
AZUL = "\033[94m"
CIANO = "\033[96m"
VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
NEGRITO = "\033[1m"
HISTORICO = Path(__file__).with_name("historico.json")


def colorir(texto, cor):
    return f"{cor}{texto}{RESET}"


def limpar_tela():
    print("\033[2J\033[H", end="")


def pausar(mensagem="Pressione ENTER para continuar..."):
    input(f"\n{mensagem}")


def exibir_tabuleiro(tabuleiro, revelar_navios=False):
    """Monta a grade para a tela sem misturar apresentação com as regras."""
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:tabuleiro.tamanho]
    linhas = [f"    {' '.join(letras)}"]
    for linha in range(tabuleiro.tamanho):
        valores = []
        for coluna in range(tabuleiro.tamanho):
            coordenada = (linha, coluna)
            navio = tabuleiro.grade[linha][coluna]
            if coordenada in tabuleiro.tiros:
                simbolo = colorir("X", VERMELHO) if navio else colorir("O", AZUL)
            elif revelar_navios and navio:
                simbolo = colorir("N", VERDE)
            else:
                simbolo = colorir("~", CIANO)
            valores.append(simbolo)
        linhas.append(f"{linha + 1:>2}  {' '.join(valores)}")
    return "\n".join(linhas)


def posicionar_frota_manual(jogador):
    """Pede ao jogador a casa inicial e a orientação de cada navio."""
    print("\nPosicione sua frota. Digite 'auto' para posicionar automaticamente.")
    for tamanho, nome in frota_padrao():
        while True:
            limpar_tela()
            print(colorir(f"Posicionando {nome} (tamanho {tamanho})", NEGRITO + CIANO))
            print(exibir_tabuleiro(jogador.tabuleiro, revelar_navios=True))
            texto = input("\nCoordenada inicial (ex.: A1): ").strip()
            if texto.lower() == "auto":
                jogador.tabuleiro = Tabuleiro()
                posicionar_frota_automaticamente(jogador)
                return
            try:
                linha, coluna = ler_coordenada(texto)
                orientacao = input("Orientação (H = horizontal, V = vertical): ").strip().upper()
                jogador.tabuleiro.posicionar_navio(
                    Navio(tamanho, nome), linha, coluna, orientacao
                )
                break
            except ValueError as erro:
                print(colorir(f"\nAtenção: {erro}", AMARELO))
                pausar()


def mostrar_status(humano, computador, rodada):
    print(colorir("═" * 61, CIANO))
    print(colorir("                 BATALHA NAVAL", NEGRITO + CIANO))
    print(colorir(f"                         RODADA {rodada}", CIANO))
    print(colorir("═" * 61, CIANO))
    print(f"{colorir(humano.nome, NEGRITO)}                  {colorir('COMPUTADOR', NEGRITO)}")
    print(exibir_tabuleiro(humano.tabuleiro, revelar_navios=True))
    print()
    print(exibir_tabuleiro(computador.tabuleiro))
    print()
    print(
        f"Seus navios afundados: {humano.tabuleiro.quantidade_navios_afundados()}/3"
        f"    Inimigos afundados: {computador.tabuleiro.quantidade_navios_afundados()}/3"
    )
    print(colorir("─" * 61, CIANO))
    print(f"{colorir('N', VERDE)} navio  {colorir('X', VERMELHO)} acerto  "
          f"{colorir('O', AZUL)} água  {colorir('~', CIANO)} desconhecido")
    print(colorir("─" * 61, CIANO))


def mensagem_tiro(jogador, resultado):
    if resultado is None:
        return colorir(f"{jogador} acertou a água.", AZUL)
    if resultado.esta_afundado():
        return colorir(f"{jogador} afundou o {resultado.nome}!", VERMELHO)
    return colorir(f"{jogador} acertou o {resultado.nome}!", AMARELO)


def mostrar_regras():
    limpar_tela()
    print(colorir("REGRAS", NEGRITO + CIANO))
    print("\n1. Posicione um Cruzador, um Destroyer e um Submarino.")
    print("2. Ataque informando coordenadas como A1, B3 ou E5.")
    print("3. X representa acerto, O representa água e ~ é desconhecido.")
    print("4. O primeiro jogador a afundar toda a frota vence.")
    print("5. Use 'sair' durante a partida para voltar ao menu.")
    pausar()


def carregar_historico():
    if not HISTORICO.exists():
        return []
    try:
        return json.loads(HISTORICO.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def salvar_resultado(nome, resultado, rodadas, dificuldade):
    historico = carregar_historico()
    historico.append({
        "jogador": nome,
        "resultado": resultado,
        "rodadas": rodadas,
        "dificuldade": dificuldade,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })
    HISTORICO.write_text(
        json.dumps(historico[-20:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def mostrar_historico():
    limpar_tela()
    historico = carregar_historico()
    print(colorir("HISTÓRICO DE PARTIDAS", NEGRITO + CIANO))
    if not historico:
        print("\nNenhuma partida registrada.")
    else:
        for partida in reversed(historico):
            print(
                f"\n{partida['data']} | {partida['jogador']} | "
                f"{partida['resultado']} | {partida['rodadas']} rodadas | "
                f"{partida['dificuldade']}"
            )
    pausar()


def escolher_dificuldade():
    opcoes = {"1": "fácil", "2": "médio", "3": "difícil"}
    while True:
        escolha = input("\nDificuldade: 1-Fácil  2-Médio  3-Difícil: ").strip()
        if escolha in opcoes:
            return opcoes[escolha]
        print(colorir("Escolha 1, 2 ou 3.", AMARELO))


def jogar():
    limpar_tela()
    print(colorir("BATALHA NAVAL", NEGRITO + CIANO))
    nome = input("\nComo devemos chamar você? ").strip() or "Jogador"
    dificuldade = escolher_dificuldade()
    humano = Jogador(nome)
    computador = Computador(dificuldade)
    posicionar_frota_manual(humano)
    posicionar_frota_automaticamente(computador)
    pausar("Frota pronta! Pressione ENTER para começar...")
    rodada = 1

    while True:
        limpar_tela()
        mostrar_status(humano, computador, rodada)
        texto = input(f"\n{nome}, escolha um alvo (A1-E5) ou 'sair': ").strip()
        if texto.lower() == "sair":
            salvar_resultado(nome, "Desistência", rodada, dificuldade)
            print(colorir("\nPartida encerrada.", AMARELO))
            return
        try:
            linha, coluna = ler_coordenada(texto)
            resultado = humano.atacar(computador, linha, coluna)
        except ValueError as erro:
            print(colorir(f"\nAtenção: {erro}", AMARELO))
            pausar()
            continue

        print(f"\n{mensagem_tiro('Você', resultado)}")
        if computador.verificar_derrota():
            salvar_resultado(nome, "Vitória", rodada, dificuldade)
            print(colorir("\nPARABÉNS! Você venceu!", VERDE + NEGRITO))
            pausar()
            return

        linha, coluna = computador.escolher_tiro()
        resultado = computador.atacar(humano, linha, coluna)
        computador.registrar_resultado(linha, coluna, resultado)
        print(f"Computador escolheu {chr(65 + coluna)}{linha + 1}.")
        print(mensagem_tiro("O computador", resultado))
        if humano.verificar_derrota():
            salvar_resultado(nome, "Derrota", rodada, dificuldade)
            print(colorir("\nO computador venceu.", VERMELHO + NEGRITO))
            pausar()
            return
        rodada += 1
        pausar()


def menu():
    while True:
        limpar_tela()
        print(colorir("╔══════════════════════════════════════╗", CIANO))
        print(colorir("║          BATALHA NAVAL               ║", NEGRITO + CIANO))
        print(colorir("╠══════════════════════════════════════╣", CIANO))
        print("║  1 - Jogar                           ║")
        print("║  2 - Ver regras                      ║")
        print("║  3 - Ver histórico                   ║")
        print("║  4 - Sair                            ║")
        print(colorir("╚══════════════════════════════════════╝", CIANO))
        escolha = input("\nEscolha uma opção: ").strip()
        if escolha == "1":
            jogar()
        elif escolha == "2":
            mostrar_regras()
        elif escolha == "3":
            mostrar_historico()
        elif escolha == "4":
            print("\nAté a próxima!")
            return
        else:
            print(colorir("\nOpção inválida.", AMARELO))
            pausar()

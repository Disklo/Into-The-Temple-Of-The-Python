import curses
from bsp import BSP
from random import randint, choice
from screen_utils import draw_layout

# Define as dimensões da dungeon e densidade de salas
LARGURA_DUNGEON = 280
ALTURA_DUNGEON = 64
DENSIDADE_SALAS = 0.75

# Classe para representar um NPC inimigo genérico
class NPC:
    def __init__(self, y, x, velocidade=2, raio_deteccao=8, simbolo="N"):
        self.y = y
        self.x = x
        self.velocidade = velocidade
        self.raio_deteccao = raio_deteccao
        self.contador_movimento = 0
        self.simbolo = simbolo

    # Verifica se o jogador está perto o suficiente para o NPC reagir
    def perto_do_jogador(self, pos_jogador):
        jogador_y, jogador_x = pos_jogador
        return abs(self.y - jogador_y) + abs(self.x - jogador_x) <= self.raio_deteccao

    # Decide o próximo movimento do NPC com base na posição do jogador
    def proximo_movimento(self, dungeon, pos_jogador):
        movimentos_possiveis = []
        if self.perto_do_jogador(pos_jogador):
            jogador_y, jogador_x = pos_jogador
            if self.y > jogador_y:
                movimentos_possiveis.append((self.y - 1, self.x))
            if self.y < jogador_y:
                movimentos_possiveis.append((self.y + 1, self.x))
            if self.x > jogador_x:
                movimentos_possiveis.append((self.y, self.x - 1))
            if self.x < jogador_x:
                movimentos_possiveis.append((self.y, self.x + 1))
        else:
            movimentos_possiveis = [(self.y + dy, self.x + dx) for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]]

        movimentos_validos = [(y, x) for y, x in movimentos_possiveis
                            if 0 <= y < ALTURA_DUNGEON and 0 <= x < LARGURA_DUNGEON and dungeon[y][x] == "."]
        return choice(movimentos_validos) if movimentos_validos else (self.y, self.x)

    # Atualiza a posição do NPC baseado em sua velocidade
    def mover(self, dungeon, pos_jogador):
        self.contador_movimento += 1
        if self.contador_movimento >= self.velocidade:
            self.y, self.x = self.proximo_movimento(dungeon, pos_jogador)
            self.contador_movimento = 0

# Subclasses para NPCs rápidos e lentos
class NPC_Rapido(NPC):
    def __init__(self, y, x):
        super().__init__(y, x, velocidade=1, raio_deteccao=12, simbolo="F")

class NPC_Lento(NPC):
    def __init__(self, y, x):
        super().__init__(y, x, velocidade=3, raio_deteccao=8, simbolo="S")

# Classes para representar o jogador e subclasses de classes jogáveis
class Jogador:
    def __init__(self, nome, vida, usa_arma_distancia, usa_escudo):
        self.nome = nome
        self.vida = vida
        self.usa_arma_distancia = usa_arma_distancia
        self.usa_escudo = usa_escudo

class Cavaleiro(Jogador):
    def __init__(self, nome):
        super().__init__(nome, vida=100, usa_arma_distancia=False, usa_escudo=True)

class Patrulheiro(Jogador):
    def __init__(self, nome):
        super().__init__(nome, vida=80, usa_arma_distancia=True, usa_escudo=False)

# Funções auxiliares para localizar posições vazias para personagens e objetos
def posicao_vazia_aleatoria(dungeon):
    posicoes = [(linha, col) for linha in range(ALTURA_DUNGEON)
                for col in range(LARGURA_DUNGEON) if dungeon[linha][col] == "."]
    return choice(posicoes)

def posicao_inimigo_longe_jogador(dungeon, pos_jogador):
    y_jogador, x_jogador = pos_jogador
    posicoes = [(linha, col) for linha in range(ALTURA_DUNGEON) for col in range(LARGURA_DUNGEON)
                if dungeon[linha][col] == "." and abs(linha - y_jogador) > 10 and abs(col - x_jogador) > 10]
    return choice(posicoes) if posicoes else posicao_vazia_aleatoria(dungeon)

def posicao_item_longe_jogador(dungeon, pos_jogador):
    y_jogador, x_jogador = pos_jogador
    posicoes = [(linha, col) for linha in range(ALTURA_DUNGEON) for col in range(LARGURA_DUNGEON)
                if dungeon[linha][col] == "." and abs(linha - y_jogador) > 20 and abs(col - x_jogador) > 20]
    return choice(posicoes) if posicoes else posicao_vazia_aleatoria(dungeon)

# Tela para o jogador escolher a classe
def escolher_classe(stdscr):
    stdscr.clear()
    stdscr.addstr(5, 10, "Escolha sua classe:", curses.A_BOLD)
    stdscr.addstr(7, 12, "1 - Cavaleiro (Tanque, usa escudos)")
    stdscr.addstr(8, 12, "2 - Patrulheiro (Ágil, usa armas de longa distância)")
    stdscr.refresh()

    while True:
        tecla = stdscr.getch()
        if tecla == ord('1'):
            return "Cavaleiro"
        elif tecla == ord('2'):
            return "Patrulheiro"

# Tela para o jogador digitar seu nome
def obter_nome_jogador(stdscr):
    stdscr.clear()
    stdscr.addstr(5, 10, "Digite seu nome: ")
    stdscr.refresh()
    curses.echo()
    nome = stdscr.getstr(6, 12, 20).decode("utf-8")
    curses.noecho()
    return nome

# Tela de menu inicial
def tela_menu(stdscr):
    stdscr.clear()
    altura, largura = stdscr.getmaxyx()
    titulo = "Into The Temple Of The Python"
    instrucao = "Pressione S para começar o jogo"
    stdscr.addstr(altura // 2 - 1, (largura - len(titulo)) // 2, titulo, curses.A_BOLD)
    stdscr.addstr(altura // 2 + 1, (largura - len(instrucao)) // 2, instrucao)
    stdscr.refresh()

    while True:
        tecla = stdscr.getch()
        if tecla == ord('s') or tecla == ord('S'):
            return

# Loop principal do jogo
def loop_jogo(stdscr):
    tela_menu(stdscr)
    classe = escolher_classe(stdscr)
    nome = obter_nome_jogador(stdscr)

    if classe == "Cavaleiro":
        jogador = Cavaleiro(nome)
    else:
        jogador = Patrulheiro(nome)

    dungeon = BSP(LARGURA_DUNGEON, ALTURA_DUNGEON, DENSIDADE_SALAS)
    jogador_y, jogador_x = posicao_vazia_aleatoria(dungeon)

    # Criação dos NPCs espalhados pelo mapa
    npcs = [choice([NPC, NPC_Rapido, NPC_Lento])(*posicao_inimigo_longe_jogador(dungeon, (jogador_y, jogador_x))) for _ in range(12)]

    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.nodelay(True)

    conteudo2 = "Texto de rodapé teste"
    conteudo3 = "Painel lateral teste"

    em_combate = False
    inimigo_combate = None

    while True:
        stdscr.clear()

        for npc in npcs:
            if npc.y == jogador_y and npc.x == jogador_x:
                em_combate = True
                inimigo_combate = npc
                break
        else:
            em_combate = False
            inimigo_combate = None

        # Atualiza visualização de combate ou exploração
        if em_combate:
            visual_dungeon = [[" " for _ in range(LARGURA_DUNGEON)] for _ in range(ALTURA_DUNGEON)]
            visual_dungeon[jogador_y][jogador_x] = inimigo_combate.simbolo
            conteudo2 = "Pressione F para fugir"
        else:
            visual_dungeon = [list(linha) for linha in dungeon]
            for npc in npcs:
                visual_dungeon[npc.y][npc.x] = npc.simbolo
            visual_dungeon[jogador_y][jogador_x] = "@"
            conteudo2 = "Texto de rodapé teste"

        dungeon_str = ["".join(linha) for linha in visual_dungeon]
        draw_layout(stdscr, dungeon_str, (jogador_y, jogador_x), conteudo2, conteudo3, jogador)

        tecla = stdscr.getch()
        if tecla == ord('q'):
            break

        if em_combate and tecla == ord('f'):
            inimigo_combate.y, inimigo_combate.x = posicao_inimigo_longe_jogador(dungeon, (jogador_y, jogador_x))
            em_combate = False
            continue

        if em_combate:
            continue

        movimento_y, movimento_x = 0, 0
        if tecla == curses.KEY_UP:
            movimento_y = -1
        elif tecla == curses.KEY_DOWN:
            movimento_y = 1
        elif tecla == curses.KEY_LEFT:
            movimento_x = -1
        elif tecla == curses.KEY_RIGHT:
            movimento_x = 1

        if movimento_y == 0 and movimento_x == 0:
            continue

        novo_y = jogador_y + movimento_y
        novo_x = jogador_x + movimento_x
        if 0 <= novo_y < ALTURA_DUNGEON and 0 <= novo_x < LARGURA_DUNGEON and dungeon[novo_y][novo_x] == ".":
            jogador_y, jogador_x = novo_y, novo_x

        for npc in npcs:
            npc.mover(dungeon, (jogador_y, jogador_x))

# Inicia o jogo com a função wrapper do curses
curses.wrapper(loop_jogo)

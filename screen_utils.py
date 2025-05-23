import curses
import textwrap
import math

# Função principal responsável por desenhar toda a interface do jogo no terminal
def desenhar_layout(tela, dungeon, pos_jogador, texto_secao2, texto_secao3, jogador):
    # Inicializa as cores apenas uma vez
    if not hasattr(desenhar_layout, 'cores_inicializadas'):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        desenhar_layout.cores_inicializadas = True

    # Monta informações do jogador para mostrar na lateral direita
    info_jogador = f"Nome: {jogador.nome}\nClasse: {jogador.__class__.__name__}\nVida: {jogador.vida}\n"
    info_jogador += "Arma: Arco" if jogador.usa_arma_distancia else "Arma: Espada & Escudo"
    texto_secao3 = info_jogador

    jogador_y, jogador_x = pos_jogador

    # Mapa de visibilidade e memória visual da dungeon
    if not hasattr(desenhar_layout, 'mapa_visibilidade'):
        desenhar_layout.mapa_visibilidade = [[False for _ in range(len(dungeon[0]))] for _ in range(len(dungeon))]
    if not hasattr(desenhar_layout, 'mapa_ultima_visao'):
        desenhar_layout.mapa_ultima_visao = [[None for _ in range(len(dungeon[0]))] for _ in range(len(dungeon))]

    tela.clear()

    # Tamanho da janela visível da dungeon
    largura_visao = 70
    altura_visao = 16

    # Calcula o canto superior esquerdo da visão do jogador
    topo = max(0, min(jogador_y - altura_visao // 2, len(dungeon) - altura_visao))
    esquerda = max(0, min(jogador_x - largura_visao // 2, len(dungeon[0]) - largura_visao))

    # Define as divisões da tela (meio vertical e horizontal)
    altura, largura = tela.getmaxyx()
    divisor_vertical = (largura // 2) + 25
    divisor_horizontal = (altura // 2) + 6

    # Função auxiliar para exibir texto quebrado (formatado)
    def exibir_texto_formatado(inicio_y, inicio_x, largura_max, altura_max, texto):
        linhas_quebradas = textwrap.wrap(texto, largura_max)
        for i, linha in enumerate(linhas_quebradas[:altura_max]):
            tela.addstr(inicio_y + i, inicio_x, linha)

    # Determina se uma posição é visível ao jogador (usando linha de visão)
    def visivel(y, x):
        distancia = math.sqrt((y - jogador_y) ** 2 + (x - jogador_x) ** 2)
        if distancia > 12:
            return False
        linha = linha_bresenham(jogador_y, jogador_x, y, x)
        for (ly, lx) in linha:
            if dungeon[ly][lx] == '#':
                return (ly == y and lx == x)
        return True

    # Algoritmo de Bresenham para traçar linhas entre dois pontos
    def linha_bresenham(y0, x0, y1, x1):
        linha = []
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        erro = dx + dy
        while True:
            linha.append((y0, x0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * erro
            if e2 >= dy:
                erro += dy
                x0 += sx
            if e2 <= dx:
                erro += dx
                y0 += sy
        return linha

    # Atualiza os mapas de visibilidade e visão anterior
    for y in range(len(dungeon)):
        for x in range(len(dungeon[0])):
            if visivel(y, x):
                desenhar_layout.mapa_visibilidade[y][x] = True
                desenhar_layout.mapa_ultima_visao[y][x] = dungeon[y][x]

    # Desenha a visão da dungeon com base na posição do jogador
    for y in range(altura_visao):
        for x in range(largura_visao):
            tile_y = topo + y
            tile_x = esquerda + x
            if 0 <= tile_y < len(dungeon) and 0 <= tile_x < len(dungeon[0]):
                if desenhar_layout.mapa_visibilidade[tile_y][tile_x]:
                    if visivel(tile_y, tile_x):
                        tile = dungeon[tile_y][tile_x]
                        if tile in ["N", "F", "S"]:
                            tela.addch(y + 1, x + 1, tile)
                        elif tile_y == jogador_y and tile_x == jogador_x:
                            tela.addch(y + 1, x + 1, "@")
                        else:
                            tela.addch(y + 1, x + 1, tile)
                    else:
                        tile = desenhar_layout.mapa_ultima_visao[tile_y][tile_x]
                        if tile == '#':
                            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                ny, nx = tile_y + dy, tile_x + dx
                                if 0 <= ny < len(dungeon) and 0 <= nx < len(dungeon[0]):
                                    if dungeon[ny][nx] in ['.', '@', 'N', 'F', 'S'] and desenhar_layout.mapa_visibilidade[ny][nx]:
                                        tela.addch(y + 1, x + 1, '#', curses.color_pair(1))
                                        break
                        else:
                            tela.addch(y + 1, x + 1, tile, curses.color_pair(1))
                else:
                    tela.addch(y + 1, x + 1, ' ')

    # Exibe os textos das seções laterais e de rodapé
    exibir_texto_formatado(divisor_horizontal + 1, 1, divisor_vertical - 2, altura - divisor_horizontal - 2, texto_secao2)
    exibir_texto_formatado(1, divisor_vertical + 2, largura - divisor_vertical - 4, altura - 2, texto_secao3)

    # Desenha as divisões visuais na interface
    for y in range(altura):
        tela.addch(y, divisor_vertical, '|')
    for x in range(divisor_vertical):
        tela.addch(divisor_horizontal, x, '-')

    # Atualiza a tela com todas as alterações
    tela.refresh()

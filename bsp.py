import random

# Função que gera a dungeon utilizando o algoritmo de divisão binária (BSP - Binary Space Partitioning)
def BSP(LARGURA_DUNGEON, ALTURA_DUNGEON, DENSIDADE_SALAS):
    # Classe que representa uma sala retangular
    class Sala:
        def __init__(self, x, y, largura, altura):
            self.x = x
            self.y = y
            self.largura = largura
            self.altura = altura

        # Retorna o centro da sala
        def centro(self):
            return (self.x + self.largura // 2, self.y + self.altura // 2)

        # Verifica se esta sala intersecta outra
        def intersecta(self, outra):
            return not (
                self.x + self.largura < outra.x or
                self.x > outra.x + outra.largura or
                self.y + self.altura < outra.y or
                self.y > outra.y + outra.altura
            )

    # Classe que representa um "nó folha" da divisão BSP
    class Folha:
        TAMANHO_MINIMO = 6  # Tamanho mínimo que uma folha pode ter antes de parar de dividir

        def __init__(self, x, y, largura, altura):
            self.x = x
            self.y = y
            self.largura = largura
            self.altura = altura
            self.filho_esquerdo = None
            self.filho_direito = None
            self.sala = None

        # Divide a folha em duas folhas-filhas
        def dividir(self):
            if self.filho_esquerdo or self.filho_direito:
                return False  # Já foi dividida

            dividir_horizontal = random.choice([True, False])

            # Decide automaticamente a melhor direção de divisão com base no aspecto
            if self.largura > self.altura and self.largura / self.altura >= 1.25:
                dividir_horizontal = False
            elif self.altura > self.largura and self.altura / self.largura >= 1.25:
                dividir_horizontal = True

            maximo_divisao = (self.altura if dividir_horizontal else self.largura) - Folha.TAMANHO_MINIMO
            if maximo_divisao <= Folha.TAMANHO_MINIMO:
                return False  # Muito pequena para dividir

            ponto_divisao = random.randint(Folha.TAMANHO_MINIMO, maximo_divisao)

            if dividir_horizontal:
                self.filho_esquerdo = Folha(self.x, self.y, self.largura, ponto_divisao)
                self.filho_direito = Folha(self.x, self.y + ponto_divisao, self.largura, self.altura - ponto_divisao)
            else:
                self.filho_esquerdo = Folha(self.x, self.y, ponto_divisao, self.altura)
                self.filho_direito = Folha(self.x + ponto_divisao, self.y, self.largura - ponto_divisao, self.altura)

            return True

        # Cria salas dentro das folhas (ou conecta salas se for uma folha interna)
        def criar_salas(self):
            if self.filho_esquerdo or self.filho_direito:
                if self.filho_esquerdo:
                    self.filho_esquerdo.criar_salas()
                if self.filho_direito:
                    self.filho_direito.criar_salas()

                sala1 = self.filho_esquerdo.obter_sala_mais_proxima() if self.filho_esquerdo else None
                sala2 = self.filho_direito.obter_sala_mais_proxima() if self.filho_direito else None

                self.criar_corredor(sala1, sala2)
            else:
                if random.random() < DENSIDADE_SALAS:
                    largura_sala = random.randint(3, self.largura - 2)
                    altura_sala = random.randint(3, self.altura - 2)
                    x_sala = random.randint(self.x + 1, self.x + self.largura - largura_sala - 1)
                    y_sala = random.randint(self.y + 1, self.y + self.altura - altura_sala - 1)
                    self.sala = Sala(x_sala, y_sala, largura_sala, altura_sala)

        # Cria um corredor entre duas salas
        def criar_corredor(self, sala1, sala2):
            if not sala1 or not sala2:
                return

            x1, y1 = sala1.centro()
            x2, y2 = sala2.centro()

            # Escolhe aleatoriamente entre corredor em L começando horizontal ou vertical
            if random.choice([True, False]):
                self.criar_corredor_horizontal(x1, x2, y1)
                self.criar_corredor_vertical(y1, y2, x2)
            else:
                self.criar_corredor_vertical(y1, y2, x1)
                self.criar_corredor_horizontal(x1, x2, y2)

        # Função auxiliar para obter a sala mais próxima em uma subárvore
        def obter_sala_mais_proxima(self):
            if self.sala:
                return self.sala
            salas = []
            if self.filho_esquerdo:
                sala_esq = self.filho_esquerdo.obter_sala_mais_proxima()
                if sala_esq:
                    salas.append(sala_esq)
            if self.filho_direito:
                sala_dir = self.filho_direito.obter_sala_mais_proxima()
                if sala_dir:
                    salas.append(sala_dir)
            return min(salas, key=lambda s: (s.x + s.y)) if salas else None

        # Cria um corredor horizontal
        def criar_corredor_horizontal(self, x1, x2, y):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                dungeon[y][x] = '.'

        # Cria um corredor vertical
        def criar_corredor_vertical(self, y1, y2, x):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                dungeon[y][x] = '.'

        # Retorna a sala da folha (ou tenta buscar em filhos)
        def obter_sala(self):
            if self.sala:
                return self.sala
            elif self.filho_esquerdo:
                return self.filho_esquerdo.obter_sala()
            elif self.filho_direito:
                return self.filho_direito.obter_sala()
            return None

    # Inicializa a dungeon com paredes
    dungeon = [['#' for _ in range(LARGURA_DUNGEON)] for _ in range(ALTURA_DUNGEON)]

    raiz = Folha(0, 0, LARGURA_DUNGEON, ALTURA_DUNGEON)
    folhas = [raiz]

    # Realiza divisões sucessivas até não ser mais possível
    divisao_ativa = True
    while divisao_ativa:
        divisao_ativa = False
        for folha in folhas[:]:
            if not folha.filho_esquerdo and not folha.filho_direito:
                if folha.dividir():
                    folhas.append(folha.filho_esquerdo)
                    folhas.append(folha.filho_direito)
                    divisao_ativa = True

    # Cria salas dentro das folhas e conecta-as
    raiz.criar_salas()

    # Marca as salas no mapa (trocando paredes '#' por chão '.')
    for folha in folhas:
        if folha.sala:
            for y in range(folha.sala.y, folha.sala.y + folha.sala.altura):
                for x in range(folha.sala.x, folha.sala.x + folha.sala.largura):
                    dungeon[y][x] = '.'

    return dungeon

import pygame
import random
import sys

# --- Inicialização do Pygame ---
pygame.init()

# --- Configurações da Tela ---
LARGURA, ALTURA = 1200, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Duelo no Velho Oeste")

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (211, 47, 47)
VERDE = (76, 175, 80)
AZUL_DEFESA = (33, 150, 243)
CINZA = (120, 120, 120)

# --- Fontes ---
fonte_padrao = pygame.font.Font(None, 36)
fonte_maior = pygame.font.Font(None, 74)
fonte_menor = pygame.font.Font(None, 28)

# --- Carregamento de Imagens ---
try:
    jogador_img_original = pygame.image.load("jogador.png").convert_alpha()
    ia_img_original = pygame.image.load("ia.png").convert_alpha()
    fundo_img_original = pygame.image.load("fundo.png").convert()
except pygame.error as e:
    print(f"Erro ao carregar imagem: {e}")
    print("\nPor favor, verifique se os arquivos de imagem ('jogador.png', 'ia.png', 'fundo.png')")
    print("estão na mesma pasta que o seu script Python.")
    pygame.quit()
    sys.exit()

# Redimensiona as imagens para um tamanho padrão
TAMANHO_PERSONAGEM = (120, 200)
jogador_img = pygame.transform.scale(jogador_img_original, TAMANHO_PERSONAGEM)
ia_img = pygame.transform.scale(ia_img_original, TAMANHO_PERSONAGEM)
fundo_img = pygame.transform.scale(fundo_img_original, (LARGURA, ALTURA))

# (NOVO) Cria a superfície para a barra da UI
altura_barra_ui = 160
fundo_ui_surface = pygame.Surface((LARGURA, altura_barra_ui), pygame.SRCALPHA)
fundo_ui_surface.fill((0, 0, 0, 128)) # Preto com 50% de transparência


# --- Classe do Jogador (e da IA) ---
class Pistoleiro:
    def __init__(self, x_center, y_bottom, image, nome):
        self.nome = nome
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x_center
        self.rect.bottom = y_bottom
        
        self.vidas = 3
        self.max_vidas = 3
        self.municao = 0
        self.max_municao = 4
        self.esta_defendendo = False
        self.acao_do_turno = ""

    def desenhar(self):
        tela.blit(self.image, self.rect)
        
        largura_bloco_vida = 30
        espacamento_vida = 5
        x_inicial_vida = self.rect.centerx - ((largura_bloco_vida * self.max_vidas + espacamento_vida * (self.max_vidas - 1)) / 2)
        
        for i in range(self.max_vidas):
            cor_vida = VERDE if i < self.vidas else CINZA
            bloco_rect = pygame.Rect(x_inicial_vida + i * (largura_bloco_vida + espacamento_vida), self.rect.y - 30, largura_bloco_vida, 20)
            pygame.draw.rect(tela, cor_vida, bloco_rect)
            pygame.draw.rect(tela, PRETO, bloco_rect, 2)

        texto_municao = fonte_padrao.render(f"Balas: {self.municao}", True, PRETO)
        pos_x_texto = self.rect.centerx - texto_municao.get_width() // 2
        tela.blit(texto_municao, (pos_x_texto, self.rect.y - 65))

        if self.esta_defendendo:
            raio_defesa = self.rect.width // 2 + 10
            pygame.draw.circle(tela, AZUL_DEFESA, self.rect.center, raio_defesa, 5)

    def tomar_dano(self):
        if self.vidas > 0:
            self.vidas -= 1

    def recarregar(self):
        self.municao = min(self.municao + 1, self.max_municao)
        self.acao_do_turno = "Recarregou"

    def atirar(self, oponente, balas):
        if self.municao < balas:
            print("Tentou atirar sem balas suficientes!")
            self.acao_do_turno = "Falhou"
            return

        self.municao -= balas
        
        if oponente.esta_defendendo:
            print(f"{oponente.nome} se defendeu do ataque!")
            self.acao_do_turno = f"Atirou {balas}x (Defendido)"
            oponente.esta_defendendo = False
            return

        for _ in range(balas):
            oponente.tomar_dano()
        
        self.acao_do_turno = f"Atirou {balas}x"

    def defender(self):
        self.esta_defendendo = True
        self.acao_do_turno = "Defendeu"

# --- Elementos da UI (Botões) ---
botao_atirar = pygame.Rect(LARGURA // 4 - 75, ALTURA - 80, 150, 50)
botao_defender = pygame.Rect(LARGURA // 2 - 75, ALTURA - 80, 150, 50)
botao_recarregar = pygame.Rect(LARGURA * 3 // 4 - 75, ALTURA - 80, 150, 50)
campo_balas = pygame.Rect(botao_atirar.centerx - 50, botao_atirar.y - 60, 100, 50)

botao_menos = pygame.Rect(campo_balas.left - 45, campo_balas.y, 40, 50)
botao_mais = pygame.Rect(campo_balas.right + 5, campo_balas.y, 40, 50)

# --- Instâncias dos Personagens ---
LINHA_DO_CHAO = ALTURA - 80 
jogador = Pistoleiro(200, LINHA_DO_CHAO, jogador_img, "Jogador")
ia = Pistoleiro(LARGURA - 200, LINHA_DO_CHAO, ia_img, "O Renegado")

# --- Variáveis de Controle de Jogo ---
rodando = True
turno_do_jogador = True
estado_jogo = "JOGANDO"
balas_para_atirar = 0
relogio = pygame.time.Clock()
mensagem_turno = ""

# --- Funções de Desenho ---
def desenhar_cenario():
    tela.blit(fundo_img, (0, 0))

def desenhar_ui():
    # (MODIFICADO) Desenha a barra de fundo da UI primeiro
    tela.blit(fundo_ui_surface, (0, ALTURA - altura_barra_ui))
    
    # Desenha os botões de ação por cima da barra
    pygame.draw.rect(tela, VERMELHO, botao_atirar)
    pygame.draw.rect(tela, AZUL_DEFESA, botao_defender)
    pygame.draw.rect(tela, VERDE, botao_recarregar)

    texto_atirar = fonte_padrao.render("Atirar", True, BRANCO)
    tela.blit(texto_atirar, (botao_atirar.x + 40, botao_atirar.y + 10))
    texto_defender = fonte_padrao.render("Defender", True, BRANCO)
    tela.blit(texto_defender, (botao_defender.x + 25, botao_defender.y + 10))
    texto_recarregar = fonte_padrao.render("Recarregar", True, BRANCO)
    tela.blit(texto_recarregar, (botao_recarregar.x + 10, botao_recarregar.y + 10))

    # Desenha o seletor de balas
    pygame.draw.rect(tela, BRANCO, campo_balas)
    pygame.draw.rect(tela, PRETO, campo_balas, 2)
    texto_balas = fonte_padrao.render(str(balas_para_atirar), True, PRETO)
    tela.blit(texto_balas, (campo_balas.centerx - texto_balas.get_width() // 2, campo_balas.centery - texto_balas.get_height() // 2))
    
    # Label do seletor (agora branco para contrastar com a barra preta)
    texto_label_balas = fonte_menor.render("Balas a usar:", True, BRANCO)
    tela.blit(texto_label_balas, (campo_balas.centerx - texto_label_balas.get_width() // 2, campo_balas.y - 25))
    
    pygame.draw.rect(tela, CINZA, botao_menos)
    pygame.draw.rect(tela, CINZA, botao_mais)
    texto_menos = fonte_maior.render("-", True, PRETO)
    tela.blit(texto_menos, (botao_menos.centerx - texto_menos.get_width() // 2, botao_menos.centery - texto_menos.get_height() // 2 - 5))
    texto_mais = fonte_maior.render("+", True, PRETO)
    tela.blit(texto_mais, (botao_mais.centerx - texto_mais.get_width() // 2, botao_mais.centery - texto_mais.get_height() // 2 - 5))

    # Mensagem de ação do turno
    texto_acao = fonte_padrao.render(mensagem_turno, True, PRETO)
    tela.blit(texto_acao, (LARGURA // 2 - texto_acao.get_width() // 2, 20))


# --- Loop Principal do Jogo ---
while rodando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        
        if turno_do_jogador and estado_jogo == "JOGANDO":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if botao_atirar.collidepoint(event.pos):
                    if jogador.municao >= balas_para_atirar and balas_para_atirar > 0:
                        jogador.atirar(ia, balas_para_atirar)
                        turno_do_jogador = False
                elif botao_defender.collidepoint(event.pos):
                    jogador.defender()
                    turno_do_jogador = False
                elif botao_recarregar.collidepoint(event.pos):
                    jogador.recarregar()
                    turno_do_jogador = False
                elif botao_mais.collidepoint(event.pos):
                    if jogador.municao > 0:
                        balas_para_atirar = min(jogador.municao, balas_para_atirar + 1)
                elif botao_menos.collidepoint(event.pos):
                    balas_para_atirar = max(1, balas_para_atirar - 1)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if jogador.municao > 0:
                        balas_para_atirar = min(jogador.municao, balas_para_atirar + 1)
                if event.key == pygame.K_DOWN:
                    balas_para_atirar = max(1, balas_para_atirar - 1)

    if not turno_do_jogador and estado_jogo == "JOGANDO":
        pygame.time.wait(1000)
        
        if ia.municao == 0:
            ia.recarregar()
        elif jogador.vidas <= ia.municao:
            ia.atirar(jogador, jogador.vidas)
        elif jogador.vidas == 1 and ia.municao > 0:
            ia.atirar(jogador, 1)
        elif ia.municao < ia.max_municao and random.random() < 0.5:
            ia.recarregar()
        else:
            if random.random() < 0.8 and ia.municao > 0:
                ia.atirar(jogador, 1)
            else:
                ia.defender()
        
        turno_do_jogador = True
        
        if jogador.municao > 0:
            balas_para_atirar = 1
        else:
            balas_para_atirar = 0

    # --- Renderização ---
    desenhar_cenario()
    jogador.desenhar()
    ia.desenhar()

    mensagem_turno = f"Turno do {jogador.nome if turno_do_jogador else ia.nome}"
    if estado_jogo == "JOGANDO":
        if jogador.vidas <= 0:
            estado_jogo = "FIM_DE_JOGO"
            vencedor = ia
        elif ia.vidas <= 0:
            estado_jogo = "FIM_DE_JOGO"
            vencedor = jogador
            
        if turno_do_jogador:
            desenhar_ui()
    else:
        texto_fim = fonte_maior.render(f"O Vencedor é {vencedor.nome}!", True, PRETO)
        tela.blit(texto_fim, (LARGURA // 2 - texto_fim.get_width() // 2, ALTURA // 2 - 50))

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
sys.exit()

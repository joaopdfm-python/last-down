import pygame
import sys
import os
import random 
import math 

largura = 930
altura = 320
fps = 60

preto = (0, 0, 0)
branco = (255, 255, 255)
vermelho = (255, 0, 0)
azul = (0, 0, 255)
cor_fundo = (0, 91, 91)
laranja = (255, 165, 0)
vermelho_titulo = (231, 52, 38)
amarelo_botao = (238, 238, 0)

linha_chegada = 866 
tempo_jogo = 60

DEBUG = False

stamina_max = 100
perde_colisao = 10
perde_minuto = 25
td_intervalo = 120

dificuldades = {
    "Fácil": (1, 1.05),   
    "Médio": (2, 1.10),   
    "Difícil": (3, 1.50)  
}

dash_dist = 50     
dash_frames = 10       
dash_offset = 2
dash_cd = 1000    
dash_stamina = 1.5

limites_def = [
    (425, 467),
    (507, 549),
    (589, 629),
    (667, 709),
    (751, 822)
]

pygame.init()
pygame.mixer.init()
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Last Down")
clock = pygame.time.Clock()

def carregar_fonte_pixel(tam):
    return pygame.font.Font(
        os.path.join("assets", "PressStart2P.ttf"),
        tam
    )

fonte_tempo = carregar_fonte_pixel(18)
fonte_placar = carregar_fonte_pixel(13)
fonte_resultado = carregar_fonte_pixel(36)

musica_menu = os.path.join("assets", "menu.mp3")
musica_jogo = os.path.join("assets", "jogo.mp3")
som_jogador = os.path.join("assets", "jogador.mp3")
som_apito = os.path.join("assets", "apito.mp3")
som_touchdown = os.path.join("assets", "touchdown.mp3")
som_tackle = os.path.join("assets", "tackle.mp3")

musica_atual = None

def carregar_som(caminho, volume=1.0):
    try:
        if caminho and os.path.exists(caminho):
            som = pygame.mixer.Sound(caminho)
            som.set_volume(volume)
            return som
    except:
        pass
    return None

efeito_jogador = carregar_som(som_jogador, 1.0)
efeito_apito = carregar_som(som_apito, 0.1)
efeito_touchdown = carregar_som(som_touchdown, 1.0)
efeito_tackle = carregar_som(som_tackle, 1.0)

def tocar_musica(arquivo):
    global musica_atual
    if arquivo and os.path.exists(arquivo) and musica_atual != arquivo:
        try:
            pygame.mixer.music.load(arquivo)
            pygame.mixer.music.set_volume(1)  
            pygame.mixer.music.play(-1)
            musica_atual = arquivo
        except:
            print(f"Erro ao carregar música: {arquivo}")

def parar_musica():
    global musica_atual
    pygame.mixer.music.stop()
    musica_atual = None

def pausar_musica():
    pygame.mixer.music.pause()

def retomar_musica():
    pygame.mixer.music.unpause()

try:
    campo_sheet = pygame.image.load(os.path.join("assets", "campo.png")).convert()
    campo_img = campo_sheet.subsurface(pygame.Rect(0, 257, 930, 240))
except:
    print("Erro ao carregar campo.png")
    campo_img = pygame.Surface((930, 240))
    campo_img.fill(cor_fundo)

campo_y = altura - 240
lim_esq = 343
limite_campo = pygame.Rect(lim_esq, campo_y, largura - lim_esq, 240)

tam = 35
vel_base = 2
vel_def = 1 

try:
    jogador_sheet = pygame.image.load(os.path.join("assets", "jogador_Transparent.png")).convert_alpha()

    parado_frames = [
    jogador_sheet.subsurface(pygame.Rect(7, 358, tam, tam)),
    jogador_sheet.subsurface(pygame.Rect(205, 358, tam, tam))
    ]

    dir_frames = [
        jogador_sheet.subsurface(pygame.Rect(8, 46, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(48, 47, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(88, 47, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(127, 46, tam, tam))
    ]
    
    esq_frames = [
        jogador_sheet.subsurface(pygame.Rect(980, 45, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(942, 46, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(902, 46, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(864, 45, tam, tam))
    ]
    
    cima_frames = [
        jogador_sheet.subsurface(pygame.Rect(2, 279, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(34, 278, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(66, 280, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(98, 280, tam, tam))
    ]
    
    baixo_frames = [
        jogador_sheet.subsurface(pygame.Rect(3, 8, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(36, 6, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(66, 8, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(100, 8, tam, tam))
    ]
    
    diag_dir_cima_frames = [
        jogador_sheet.subsurface(pygame.Rect(2, 207, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(33, 207, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(64, 207, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(97, 207, tam, tam))
    ]
    
    diag_dir_baixo_frames = [
        jogador_sheet.subsurface(pygame.Rect(367, 636, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(408, 637, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(447, 637, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(8, 678, tam, tam))
    ]
    
    diag_esq_cima_frames = [
        jogador_sheet.subsurface(pygame.Rect(989, 207, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(957, 207, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(924, 207, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(893, 206, tam, tam))
    ]

    diag_esq_baixo_frames = [
        jogador_sheet.subsurface(pygame.Rect(622, 637, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(582, 636, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(543, 637, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(982, 676, tam, tam))
    ]
    jogador_dash_cima_frames = [
        jogador_sheet.subsurface(pygame.Rect(146, 713, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(178, 720, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(107, 675, tam, tam))
    ]
    jogador_dash_baixo_frames = [
        jogador_sheet.subsurface(pygame.Rect(83, 716, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(114, 716, tam, tam))
    ]
    jogador_dash_esq_frames = [
        jogador_sheet.subsurface(pygame.Rect(732, 681, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(693, 686, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(653, 680, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(612, 687, tam, tam))
    ]
    jogador_dash_dir_frames = [
        jogador_sheet.subsurface(pygame.Rect(256, 682, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(298, 684, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(336, 682, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(376, 685, tam, tam))
    ]
    jogador_dash_diag_esq_cima_frames = [
        jogador_sheet.subsurface(pygame.Rect(982, 755, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(943, 755, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(902, 762, tam, tam))
    ]
    jogador_dash_diag_dir_cima_frames = [
        jogador_sheet.subsurface(pygame.Rect(8, 754, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(47, 754, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(88, 759, tam, tam))
    ]
    jogador_dash_diag_esq_baixo_frames = [
        jogador_sheet.subsurface(pygame.Rect(981, 718, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(943, 718, tam, tam))
    ]
    jogador_dash_diag_dir_baixo_frames = [
        jogador_sheet.subsurface(pygame.Rect(8, 718, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(46, 717, tam, tam))
    ]
    jogador_td_frames = [
        jogador_sheet.subsurface(pygame.Rect(399, 1037, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(438, 1036, tam, tam)),
        jogador_sheet.subsurface(pygame.Rect(258, 599, tam, tam))
    ]
    jogador_tackle_frames = [
    jogador_sheet.subsurface(pygame.Rect(448, 1747, tam, tam)),
    jogador_sheet.subsurface(pygame.Rect(298, 1797, tam, tam)),
    jogador_sheet.subsurface(pygame.Rect(257, 1875, tam, tam))
]
    
    jogador_sprites = {
        'direita': dir_frames,
        'esquerda': esq_frames,
        'cima': cima_frames,
        'baixo': baixo_frames,
        'diag_dir_cima': diag_dir_cima_frames,
        'diag_dir_baixo': diag_dir_baixo_frames,
        'diag_esq_cima': diag_esq_cima_frames,
        'diag_esq_baixo': diag_esq_baixo_frames,
        'parado': parado_frames
    }
    
    inimigo_sheet = pygame.image.load(os.path.join("assets", "inimigos_transprnt.png")).convert_alpha()

    inimigo_sprites = {
    'direita': [
        inimigo_sheet.subsurface(pygame.Rect(8, 46, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(48, 47, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(88, 47, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(127, 46, 35, 35))
    ],
    'esquerda': [
        inimigo_sheet.subsurface(pygame.Rect(980, 45, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(942, 46, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(902, 46, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(864, 45, 35, 35))
    ],
    'cima': [
        inimigo_sheet.subsurface(pygame.Rect(2, 279, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(34, 278, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(66, 280, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(98, 280, 35, 35))
    ],
    'baixo': [
        inimigo_sheet.subsurface(pygame.Rect(3, 8, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(36, 6, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(66, 8, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(100, 8, 35, 35))
    ],
    'diag_dir_cima': [
        inimigo_sheet.subsurface(pygame.Rect(2, 207, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(33, 207, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(64, 207, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(97, 207, 35, 35))
    ],
    'diag_dir_baixo': [
        inimigo_sheet.subsurface(pygame.Rect(367, 636, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(408, 637, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(447, 637, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(8, 678, 35, 35))
    ],
    'diag_esq_cima': [
        inimigo_sheet.subsurface(pygame.Rect(989, 207, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(957, 207, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(924, 207, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(893, 206, 35, 35))
    ],
    'diag_esq_baixo': [
        inimigo_sheet.subsurface(pygame.Rect(622, 637, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(582, 636, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(543, 637, 35, 35)),
        inimigo_sheet.subsurface(pygame.Rect(982, 676, 35, 35))
    ]
}
    defensor_tackle_frames = [
    inimigo_sheet.subsurface(pygame.Rect(982, 1789, tam, tam)),
    inimigo_sheet.subsurface(pygame.Rect(703, 1749, tam, tam)),
    inimigo_sheet.subsurface(pygame.Rect(662, 1748, tam, tam)),
    inimigo_sheet.subsurface(pygame.Rect(622, 1748, tam, tam)),
    inimigo_sheet.subsurface(pygame.Rect(582, 1749, tam, tam)),
    inimigo_sheet.subsurface(pygame.Rect(542, 1748, tam, tam)),
]
    
except:
    surf1 = pygame.Surface((tam, tam))
    surf1.fill(azul)
    surf2 = pygame.Surface((tam, tam))
    surf2.fill((100, 100, 255))  

    jogador_sprites = {
        'direita': [surf1, surf2],
        'esquerda': [surf1, surf2],
        'cima': [surf1, surf2],
        'baixo': [surf1, surf2],
        'diag_dir_cima': [surf1, surf2],
        'diag_dir_baixo': [surf1, surf2],
        'diag_esq_cima': [surf1, surf2],
        'diag_esq_baixo': [surf1, surf2],
        'parado': [surf1, surf2]
    }
    
    inimigo_img = pygame.Surface((tam, tam))
    inimigo_img.fill(vermelho)

def carregar_highscore():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def salvar_highscore(score):
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(score))
    except:
        print("Erro ao salvar highscore")

def mostra_tempo(t):
    m = int(t // 60)
    s = int(t % 60)
    m_str = str(m).zfill(2)
    s_str = str(s).zfill(2)
    return m_str + ":" + s_str

def desenha_tempo(surf, tempo):
    txt = mostra_tempo(tempo)
    img = fonte_tempo.render(txt, True, vermelho)
    surf.blit(img, (largura // 2 - img.get_width() // 2, 10))

def desenha_resultado(surf, texto):
    img = fonte_resultado.render(texto, True, vermelho)
    r = img.get_rect(center=(largura // 2, altura // 2 - 85))
    surf.blit(img, r)

def desenha_stamina(surf, stam, x, y, w, h):
    pygame.draw.rect(surf, branco, (x, y, w, h), 1)
    
    w_atual = int((stam / stamina_max) * w)
    
    if w_atual > 0:
        pygame.draw.rect(surf, azul, (x + 1, y + 1, w_atual - 2, h - 2))
    
    txt = str(int(stam))
    img = fonte_tempo.render(txt, True, branco)
    surf.blit(img, (x + w + 5, y))
    
def desenha_vidas(surf, v):
    txt = f"Vidas: {v}"
    img = fonte_tempo.render(txt, True, branco) 
    surf.blit(img, (10, 10))

def desenha_pontos(surf, pts):
    txt = f"Pontos: {pts}"
    img = fonte_placar.render(txt, True, amarelo_botao)
    surf.blit(img, (10, 45))

def desenha_highscore(surf, hs):
    txt = f"Highscore: {hs}"
    img = fonte_placar.render(txt, True, vermelho)
    surf.blit(img, (largura - 190, 45))

def texto_menu(surf, texto, tam, cor, x, y):
    f = carregar_fonte_pixel(tam)
    img = f.render(texto, True, cor)
    r = img.get_rect(center=(x, y))
    surf.blit(img, r)
    return r 

def seleciona_defensores(num, grupo, mult_vel):
    for d in grupo:
        d.tipo = 'aleatorio'
        d.alvo = pygame.Vector2(d.x_inicio, d.y_inicio) 
    
    if num > 0 and len(grupo) >= num:
        escolhidos = random.sample(list(grupo), num)
        
        for d in escolhidos:
            d.tipo = 'persegue'
            d.vel = vel_def * mult_vel
            
    return grupo


class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frame_index = 0
        self.ultimo_troca = 0
        self.anim_mov = 150

        self.anim_dash = 175
        self.ultimo_troca_dash = 0

        self.idle_timer = 0
        self.idle_interval = 0.5
        self.idle_delay = 0
        self.idle_delay_timer = 0

        self.td_usado = False
        self.fazendo_td = False
        self.td_frame = 0 
        self.td_ultimo_troca = 0
        #self.td_passo = 0

        self.direcao_atual = 'direita'
        self.image = jogador_sprites[self.direcao_atual][self.frame_index]
        self.rect = pygame.Rect(x, y, tam, tam)

        self.jogador_dash_sprites = {
            'direita': jogador_dash_dir_frames,
            'esquerda': jogador_dash_esq_frames,
            'cima': jogador_dash_cima_frames,
            'baixo': jogador_dash_baixo_frames,
            'diag_dir_cima': jogador_dash_diag_dir_cima_frames,
            'diag_dir_baixo': jogador_dash_diag_dir_baixo_frames,
            'diag_esq_cima': jogador_dash_diag_esq_cima_frames,
            'diag_esq_baixo': jogador_dash_diag_esq_baixo_frames
        }

        self.hitbox = self.rect.inflate(-12, -12)

        self.stam = stamina_max
        self.vel = vel_base

        self.dashing = False
        self.dash_frame = 0
        self.dash_target = pygame.Vector2(x, y) 
        self.dash_start = pygame.Vector2(x, y)  
        self.dash_dir = 1  
        self.ultimo_dash = 0
        
        self.em_movimento = False
        #self.pos_anterior = pygame.Vector2(x, y)

        self.em_tackle = False
        self.tackle_frame = 0
        self.tackle_timer = 0
        self.tackle_interval = 0.12

    def animar_idle(self, dt):
        self.idle_timer += dt

        if self.idle_timer >= self.idle_interval:
            self.idle_timer = 0
            self.frame_index = (self.frame_index + 1) % len(jogador_sprites['parado'])
            self.image = jogador_sprites['parado'][self.frame_index]

    def iniciar_tackle(self):
        self.em_tackle = True
        self.tackle_frame = 0
        self.tackle_timer = 0

    def animar_tackle(self, dt):
        if not self.em_tackle:
            return False
        
        self.tackle_timer += dt

        if self.tackle_timer >= self.tackle_interval:
            self.tackle_timer = 0
            self.tackle_frame += 1

            if self.tackle_frame < len(jogador_tackle_frames):
                self.image = jogador_tackle_frames[self.tackle_frame]

        if self.tackle_frame >= len(jogador_tackle_frames) - 1:
            self.em_tackle = False
            return True
        
        self.hitbox.center = self.rect.center

        return False

    def get_vel(self):
        perdida = stamina_max - self.stam
        red = (perdida // 5) * 0.1
        v = self.vel - red
        return max(1, round(v))

    def determinar_direcao(self, dx, dy):
        if dx > 0 and dy < 0:  
            return 'diag_dir_cima'
        elif dx > 0 and dy > 0:  
            return 'diag_dir_baixo'
        elif dx < 0 and dy < 0:  
            return 'diag_esq_cima'
        elif dx < 0 and dy > 0: 
            return 'diag_esq_baixo'
        elif dx > 0:  
            return 'direita'
        elif dx < 0:  
            return 'esquerda'
        elif dy < 0: 
            return 'cima'
        elif dy > 0:  
            return 'baixo'
        return self.direcao_atual  

    def iniciar_dash(self, keys):
        if self.dashing:
            return
            
        agora = pygame.time.get_ticks()

        if agora - self.ultimo_dash < dash_cd:
            return
        
        if self.stam < dash_stamina:
            return

        dx = 0
        dy = 0
        
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        
        if keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1

        if dx == 0 and dy == 0:
            return

        self.dash_dir = 1 
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            self.dash_dir = -1

        self.direcao_atual = self.determinar_direcao(dx, dy)
        
        direcao = pygame.Vector2(dx, dy)
        
        if direcao.length() > 0:
            direcao = direcao.normalize()
            
            self.dash_start.x = self.rect.x
            self.dash_start.y = self.rect.y
            
            tx = self.rect.x + direcao.x * dash_dist
            ty = self.rect.y + direcao.y * dash_dist
            
            tx = pygame.math.clamp(tx, limite_campo.left, limite_campo.right - tam)
            ty = pygame.math.clamp(ty, limite_campo.top, limite_campo.bottom - tam)

            self.dash_target.x = tx
            self.dash_target.y = ty
            
            self.dashing = True
            self.dash_frame = 0

            self.frame_index = 0
            self.ultimo_troca_dash = pygame.time.get_ticks()
            
            self.stam -= dash_stamina
            self.ultimo_dash = agora

    def fazer_dash(self):
        if not self.dashing:
            return

        self.dash_frame += 1

        if self.dash_frame >= dash_frames:
            self.rect.x = int(self.dash_target.x)
            self.rect.y = int(self.dash_target.y)
            self.dashing = False
            return

        t = self.dash_frame / dash_frames
        
        nx = self.dash_start.x + t * (self.dash_target.x - self.dash_start.x)
        ny = self.dash_start.y + t * (self.dash_target.y - self.dash_start.y)

        curva = math.sin(t * math.pi)
        vetor = self.dash_target - self.dash_start
        perp = pygame.Vector2(vetor.y, -vetor.x)
        
        if perp.length() > 0:
            perp = perp.normalize()
            offset = curva * dash_offset * self.dash_dir
            nx += perp.x * offset
            ny += perp.y * offset

        self.rect.x = int(nx)
        self.rect.y = int(ny)
        self.rect.clamp_ip(limite_campo)
        
    def fazer_touchdown(self):
        if self.td_usado or self.fazendo_td:
            return False
        
        corpo = self.rect.x + (tam // 3)

        if corpo < linha_chegada:
            return "perdeu"  

        self.fazendo_td = True
        self.td_frame = 0 
        self.td_ultimo_troca = pygame.time.get_ticks() 
        self.image = jogador_td_frames[0] 
        self.td_usado = True
        return "ok"

    def animar_dash(self):
        if not self.dashing:
            return

        agora = pygame.time.get_ticks()
        
        direcao = self.direcao_atual if self.direcao_atual != 'parado' else 'direita'
        frames = self.jogador_dash_sprites.get(direcao, jogador_dash_dir_frames)
        num_frames = len(frames)
        
        if num_frames == 0:
            self.image = jogador_sprites[direcao][0]
            return

        if agora - self.ultimo_troca_dash >= self.anim_dash:
            self.ultimo_troca_dash = agora
            self.frame_index = (self.frame_index + 1) % num_frames 
            
        self.image = frames[self.frame_index]
    
    def animar_td(self):
        if not self.fazendo_td:
            return False
        
        agora = pygame.time.get_ticks()

        if agora - self.td_ultimo_troca >= td_intervalo:
            self.td_ultimo_troca = agora
            self.td_frame += 1

            if self.td_frame < len(jogador_td_frames):
                self.image = jogador_td_frames[self.td_frame]
            else:
                self.fazendo_td = False
                self.td_frame = 0
                return True 

        return False

    def atualizar_animacao(self):
        agora = pygame.time.get_ticks()

        if agora - self.ultimo_troca >= self.anim_mov:
            self.ultimo_troca = agora
            frames = jogador_sprites[self.direcao_atual]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]

    def update(self, keys, dt):
        
        if self.em_tackle:
            return
    
        pos_inicial = pygame.Vector2(self.rect.x, self.rect.y)
        
        if self.fazendo_td:
            self.animar_td()
            return
            
        if keys[pygame.K_SPACE]:
            self.iniciar_dash(keys)

        if self.dashing:
            self.fazer_dash()
            self.animar_dash()
            #self.atualizar_animacao()
        else:
            v = self.get_vel()
            
            dx = 0
            dy = 0
            
            if keys[pygame.K_LEFT]:
                self.rect.x -= v
                dx = -1
            if keys[pygame.K_RIGHT]:
                self.rect.x += v
                dx = 1
            if keys[pygame.K_UP]:
                self.rect.y -= v
                dy = -1
            if keys[pygame.K_DOWN]:
                self.rect.y += v
                dy = 1

            self.rect.clamp_ip(limite_campo)

            if dx != 0 or dy != 0:
                nova_direcao = self.determinar_direcao(dx, dy)
                if nova_direcao != self.direcao_atual:
                    self.direcao_atual = nova_direcao
                    self.frame_index = 0 

        pos_final = pygame.Vector2(self.rect.x, self.rect.y)

        #if not self.dashing:
        if pos_inicial.distance_to(pos_final) > 0.5:
                self.em_movimento = True
                self.idle_delay_timer = 0
                self.atualizar_animacao()
        else:
                self.em_movimento = False
                self.idle_delay_timer += dt

                if self.idle_delay_timer >= self.idle_delay:
                        if self.direcao_atual != 'parado':
                                self.direcao_atual = 'parado'
                                self.frame_index = 0
                        self.animar_idle(dt)
                else:
                        self.atualizar_animacao()
                        
        self.hitbox.center = self.rect.center

    def draw(self, surf, scroll):
        pos = self.rect.move(-scroll, 0)
        surf.blit(self.image, pos)
        
        if self.fazendo_td:
            cor = laranja
        elif self.dashing:
            cor = vermelho
        else:
            cor = azul

        if DEBUG:
            pygame.draw.rect(surf, cor, pos, 1)
            pygame.draw.rect(surf, (0, 255, 0), self.hitbox.move(-scroll, 0), 1)

class Defensor(pygame.sprite.Sprite):
    def __init__(self, x, y, lims, tipo='aleatorio'):
        super().__init__()
        self.anim_timer = 0
        self.anim_interval = 0.15

        self.frame_index = 0
        self.ultimo_troca = 0
        self.direcao_atual = 'baixo'
        self.image = inimigo_sprites[self.direcao_atual][0]
        self.rect = pygame.Rect(x, y, tam, tam)

        self.hitbox = self.rect.inflate(-10, -10)
        
        self.tipo = tipo 
        self.perseguindo = False 
        self.ultrapassado = False
        
        self.x_inicio = x 
        self.y_inicio = y
        self.vel = vel_def
        self.alvo = pygame.Vector2(self.x_inicio, self.y_inicio) 
        
        self.min_x = lims[0]
        self.max_x = lims[1]
        
        self.min_y = limite_campo.top
        self.max_y = limite_campo.bottom - tam

        self.em_tackle = False
        self.tackle_frame = 0
        self.tackle_timer = 0
        self.tackle_interval = 0.2

    def iniciar_tackle(self):
        self.em_tackle = True
        self.tackle_frame = 0
        self.tackle_timer = 0

    def animar_tackle(self, dt):
        if not self.em_tackle:
            return False

        self.tackle_timer += dt

        if self.tackle_frame < len(defensor_tackle_frames) - 1:
            if self.tackle_timer >= self.tackle_interval:
                self.tackle_timer = 0
                self.tackle_frame += 1
                self.image = defensor_tackle_frames[self.tackle_frame]
        else:
            self.em_tackle = False
            return True

        self.hitbox.center = self.rect.center

        return False

    def determinar_direcao(self, dx, dy):
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        margem = 10  

        if abs_dx > margem and abs_dy > margem:
            if dx > 0 and dy < 0:
                return 'diag_dir_cima'
            elif dx > 0 and dy > 0:
                return 'diag_dir_baixo'
            elif dx < 0 and dy < 0:
                return 'diag_esq_cima'
            elif dx < 0 and dy > 0:
                return 'diag_esq_baixo'

        if abs_dx >= abs_dy:
            return 'direita' if dx > 0 else 'esquerda'
        else:
            return 'baixo' if dy > 0 else 'cima'

    def animar(self, dt):
        self.anim_timer += dt

        if self.anim_timer >= self.anim_interval:
            self.anim_timer = 0
            frames = inimigo_sprites[self.direcao_atual]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            
    def get_area(self):
        x1 = self.min_x - 5
        y1 = self.min_y - 15
        w = self.max_x - self.min_x + tam + 10
        h = self.max_y - self.min_y + tam + 30
        
        return pygame.Rect(x1, y1, w, h).clamp(limite_campo)

    def mover_aleatorio(self, dt):
        pos = pygame.Vector2(self.rect.x, self.rect.y)
        
        if pos.distance_to(self.alvo) < 5:
            nx = random.randint(self.min_x, self.max_x)
            ny = random.randint(self.min_y, self.max_y)
            
            self.alvo.x = nx
            self.alvo.y = ny

            self.alvo.x = pygame.math.clamp(self.alvo.x, limite_campo.left, limite_campo.right - tam)
            self.alvo.y = pygame.math.clamp(self.alvo.y, limite_campo.top, limite_campo.bottom - tam)

        dir = self.alvo - pos
        
        if dir.length() > 0:
            dir = dir.normalize() * self.vel
            
            self.rect.x += dir.x
            self.rect.y += dir.y

        self.rect.x = pygame.math.clamp(self.rect.x, self.min_x, self.max_x)
        self.rect.y = pygame.math.clamp(self.rect.y, self.min_y, self.max_y)
        dx = self.alvo.x - self.rect.x
        dy = self.alvo.y - self.rect.y
        self.direcao_atual = self.determinar_direcao(dx, dy)
        self.animar(dt)
        self.rect.clamp_ip(limite_campo)

    def perseguir(self, alvo, dt):
        if alvo.centerx > self.rect.centerx:
            self.rect.x += self.vel
        elif alvo.centerx < self.rect.centerx:
            self.rect.x -= self.vel
            
        if alvo.centery > self.rect.centery:
            self.rect.y += self.vel
        elif alvo.centery < self.rect.centery:
            self.rect.y -= self.vel
            
        self.rect.x = pygame.math.clamp(self.rect.x, self.min_x, self.max_x)
        self.rect.y = pygame.math.clamp(self.rect.y, self.min_y, self.max_y)
        dx = alvo.centerx - self.rect.centerx
        dy = alvo.centery - self.rect.centery
        self.direcao_atual = self.determinar_direcao(dx, dy)
        self.animar(dt)
        self.rect.clamp_ip(limite_campo)

    def update(self, dt, jogador=None):
        if self.em_tackle:
            self.animar_tackle(dt)
            return
    
        if jogador:
            self.perseguindo = True
            self.perseguir(jogador, dt)
        else:
            self.perseguindo = False
            self.mover_aleatorio(dt)

        self.hitbox.center = self.rect.center

    def draw(self, surf, scroll):
        pos = self.rect.move(-scroll, 0)
        surf.blit(self.image, pos)
        
        if DEBUG:
            if self.tipo == 'persegue':
                cor = vermelho if self.perseguindo else branco
                pygame.draw.rect(surf, cor, pos, 1)
            else:
                pygame.draw.rect(surf, branco, pos, 1)

            pygame.draw.rect(surf, (0, 255, 0), self.hitbox.move(-scroll, 0), 1)


def menu_dificuldade():
    rodando = True

    while rodando:
        tela.fill(cor_fundo)
        
        texto_menu(tela, "Escolha a dificuldade", 40, branco, largura // 2, altura // 4)
        
        y = altura // 2 - 30
        opts = list(dificuldades.keys())
        botoes = {}
        
        for i, opt in enumerate(opts):
            r = texto_menu(tela, opt, 30, branco, largura // 2, y + i * 50)
            botoes[opt] = r

        voltar = texto_menu(tela, "Voltar", 30, branco, largura // 2, altura - 20)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                mp = e.pos
                
                for opt, r in botoes.items():
                    if r.collidepoint(mp):
                        num_perseg, mult_vel = dificuldades[opt]
                        parar_musica()
                        while True:
                            tocar_musica(musica_jogo)
                            resultado = main(num_perseg, mult_vel)
                            if resultado != "reiniciar":
                                break
                            parar_musica()
                        tocar_musica(musica_menu)
                        return 
                
                if voltar.collidepoint(mp):
                    return 

        pygame.display.flip()
        clock.tick(fps)

def menu_instrucoes():
    rodando = True

    while rodando:
        tela.fill(cor_fundo)
        
        texto_menu(tela, "Instruções", 50, branco, largura // 2, 50)
        
        f = pygame.font.SysFont('Consolas', 22, bold=False)
        
        t1 = "Você move nas setas, pula na barra de espaço e faz o"
        img1 = f.render(t1, True, branco)
        tela.blit(img1, (largura // 2 - img1.get_width() // 2, 120))
        
        t2 = "touchdown com o clique esquerdo do mouse. Cuidado para"
        img2 = f.render(t2, True, branco)
        tela.blit(img2, (largura // 2 - img2.get_width() // 2, 150))
        
        t3 = "não clicar antes de chegar na linha vermelha. P pausa o jogo."
        img3 = f.render(t3, True, branco)
        tela.blit(img3, (largura // 2 - img3.get_width() // 2, 180))

        voltar = texto_menu(tela, "Voltar", 30, branco, largura // 2, altura - 40)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                mp = e.pos
                
                if voltar.collidepoint(mp):
                    return

        pygame.display.flip()
        clock.tick(fps)

def menu_pausa():
    pausar_musica()
    
    pausado = True
    
    while pausado:
        tela.fill(cor_fundo)
        
        texto_menu(tela, "PAUSA", 60, branco, largura // 2, altura // 3)
        
        continuar = texto_menu(tela, "Voltar ao jogo", 35, branco, largura // 2, altura // 2)
        menu = texto_menu(tela, "Voltar ao menu", 35, branco, largura // 2, altura // 2 + 60)
        sair = texto_menu(tela, "Sair do jogo", 35, branco, largura // 2, altura // 2 + 120)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    retomar_musica()
                    return "continuar"
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                mp = e.pos
                
                if continuar.collidepoint(mp):
                    retomar_musica()
                    return "continuar"
                
                if menu.collidepoint(mp):
                    parar_musica()
                    return "menu"
                
                if sair.collidepoint(mp):
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()
        clock.tick(fps)

def tela_final(ganhou, pontos_finais, highscore_atual):
    parar_musica()
    
    rodando = True
    
    while rodando:
        tela.fill(cor_fundo)
        
        if ganhou:
            desenha_resultado(tela, "Ganhou!")
        else:
            desenha_resultado(tela, "Perdeu!")
        
        f = pygame.font.SysFont('Consolas', 30, bold=True)
        txt_pontos = f"Pontos: {pontos_finais}"
        img_pontos = f.render(txt_pontos, True, amarelo_botao)
        tela.blit(img_pontos, (largura // 2 - img_pontos.get_width() // 2, altura // 2 - 35))
        
        txt_high = f"Highscore: {highscore_atual}"
        img_high = f.render(txt_high, True, vermelho)
        tela.blit(img_high, (largura // 2 - img_high.get_width() // 2, altura // 2))
        
        reiniciar = texto_menu(tela, "Reiniciar", 30, branco, largura // 2, altura // 2 + 60)
        menu = texto_menu(tela, "Voltar ao menu", 30, branco, largura // 2, altura // 2 + 100)
        sair = texto_menu(tela, "Sair do jogo", 30, branco, largura // 2, altura // 2 + 140)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                mp = e.pos
                
                if reiniciar.collidepoint(mp):
                    return "reiniciar"
                
                if menu.collidepoint(mp):
                    return "menu"
                
                if sair.collidepoint(mp):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(fps)

def menu_principal():
    global DEBUG
    rodando = True
    tocar_musica(musica_menu)

    while rodando:
        tela.fill(cor_fundo)
        
        texto_menu(tela, "Futebol Americano", 50, vermelho_titulo, largura // 2, altura // 6)
        
        jogar = texto_menu(tela, "Jogar", 40, branco, largura // 2, altura // 2 - 40)
        instruc = texto_menu(tela, "Instruções", 40, branco, largura // 2, altura // 2 + 30)
        sair = texto_menu(tela, "Sair", 40, branco, largura // 2, altura // 2 + 100)
        cor_debug = azul if DEBUG else vermelho
        debug_btn = texto_menu(
            tela,
            "DEBUG",
            22,
            cor_debug,
            70,              
            altura - 30      
        )
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                mp = e.pos
                
                if jogar.collidepoint(mp):
                    menu_dificuldade()
                
                if instruc.collidepoint(mp):
                    menu_instrucoes()
                
                if sair.collidepoint(mp):
                    pygame.quit()
                    sys.exit()

                if debug_btn.collidepoint(mp):
                    DEBUG = not DEBUG

        pygame.display.flip()
        clock.tick(fps)


def main(num_perseg, mult_vel): 
    rodando = True
    
    if efeito_apito:
        efeito_apito.play()
    
    py = campo_y + (240 // 2) - (tam // 2)
    px = limites_def[0][0] - 50 

    player = Jogador(px, py)

    max_v = 3
    vidas = max_v 
    pontos = 0
    highscore = carregar_highscore()
    
    touchdown_tocado = False 

    defs = pygame.sprite.Group()
    
    for i in range(len(limites_def)):
        lim = limites_def[i]
        sx = lim[0] 
        d = Defensor(sx, py, lim, tipo='aleatorio') 
        defs.add(d)
        
    defs = seleciona_defensores(num_perseg, defs, mult_vel)

    cam = 0
    ancora = 550
    tackle_ativo = False

    status = "jogando"
    t_inicio = pygame.time.get_ticks()
    t_mostra = tempo_jogo
    min_ant = 0
    
    tempo_touchdown = 0 # ou pygame.time.get_ticks(), posi talvez esteja redundntante
    aguardando_fim = False

    canal_passos = None 
    if efeito_jogador:
        canal_passos = pygame.mixer.find_channel()
        if canal_passos:
            canal_passos.play(efeito_jogador, -1)
            canal_passos.pause()

    while rodando:
        dt = clock.tick(fps) / 1000
        
        t_pass = (pygame.time.get_ticks() - t_inicio) / 1000

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if e.type == pygame.KEYDOWN and status == "jogando":
                if e.key == pygame.K_p:
                    acao = menu_pausa()
                    if acao == "menu":
                        parar_musica()
                        tocar_musica(musica_menu)
                        return "menu"
                    elif acao == "continuar":
                        t_inicio = pygame.time.get_ticks() - int(t_pass * 1000)
            
            if e.type == pygame.MOUSEBUTTONDOWN and status == "jogando":
                if e.button == 1:  
                    res = player.fazer_touchdown()
                    if res == "perdeu":
                        status = "perdeu"
                        if canal_passos:
                            canal_passos.stop()
                    elif res == "ok" and not touchdown_tocado:
                       
                        if efeito_touchdown:
                            efeito_touchdown.play()
                        touchdown_tocado = True
                        tempo_touchdown = pygame.time.get_ticks()
                        aguardando_fim = True 

        keys = pygame.key.get_pressed()
        
        if status == "jogando":
            t_rest = tempo_jogo - t_pass
            t_mostra = max(0, t_rest)

            min_atual = int(t_pass // 60)

            if min_atual > min_ant:
                player.stam -= perde_minuto
                min_ant = min_atual
                
            player.stam = max(0, player.stam)
            
            if player.em_movimento and canal_passos:
                canal_passos.unpause()
            elif not player.em_movimento and canal_passos:
                canal_passos.pause()

            for d in defs:
                if d.tipo == 'persegue':
                    area = d.get_area()
                    
                    if player.rect.colliderect(area):
                        d.update(dt, player.rect) 
                    else:
                        d.update(dt) 
                else:
                    d.update(dt)
                
                if not d.ultrapassado and player.rect.x > d.rect.x + tam:
                    d.ultrapassado = True
                    pontos += 10

            if not tackle_ativo:
                colidiu = None
                for d in defs:
                    if player.hitbox.colliderect(d.hitbox):
                        colidiu = d
                        break

                if colidiu and not player.dashing and not player.em_tackle:
                    tackle_ativo = True
                    defensor_em_tackle = colidiu

                    player.iniciar_tackle()
                    colidiu.iniciar_tackle()

                    if canal_passos:
                        canal_passos.pause() 

                    if efeito_tackle:
                        efeito_tackle.play()
                else:
                    player.update(keys, dt)

            elif tackle_ativo:
                player.animar_tackle(dt)
                defensor_em_tackle.animar_tackle(dt)

                player.hitbox.center = player.rect.center
                defensor_em_tackle.hitbox.center = defensor_em_tackle.rect.center

                if not player.em_tackle and not defensor_em_tackle.em_tackle:
                    tackle_ativo = False
                    defensor_em_tackle = None

                    player.direcao_atual = 'parado'
                    player.frame_index = 0
                    player.image = jogador_sprites['parado'][0]
                    player.em_movimento = False

                    player.stam -= perde_colisao
                    vidas -= 1

                    if vidas <= 0:
                        status = "perdeu"
                        if canal_passos:
                            canal_passos.stop()
                    else:
                        player.rect.x = px
                        player.rect.y = py
                        player.hitbox.center = player.rect.center
                        cam = player.rect.x - ancora

                        if canal_passos:
                            canal_passos.stop()
                            canal_passos.play(efeito_jogador, -1)
                            canal_passos.pause()

            if player.stam <= 0 or t_rest <= 0:
                status = "perdeu"
                
                if canal_passos:
                    canal_passos.stop()

            corpo = player.rect.x + (tam // 3)
            if corpo >= linha_chegada and player.td_usado:
                
                if aguardando_fim:
                    tempo_passado = pygame.time.get_ticks() - tempo_touchdown
                    if tempo_passado >= 800:  
                        status = "ganhou"
                       
                        if canal_passos: 
                            canal_passos.stop()
                else:
                    status = "ganhou"
                    if canal_passos: 
                        canal_passos.stop()
                
            cam = player.rect.x - ancora

        if status == "ganhou":
            bonus = 0
            tempo_usado = int(t_pass)
            
            if tempo_usado < 12:
                bonus = 50
            elif tempo_usado < 24:
                bonus = 40
            elif tempo_usado < 36:
                bonus = 30
            elif tempo_usado < 48:
                bonus = 20
            
            pontos += bonus
            
            if pontos > highscore:
                highscore = pontos
                salvar_highscore(highscore)
            
            resultado = tela_final(True, pontos, highscore)
            return resultado
        
        if status == "perdeu":
            pontos = 0
            resultado = tela_final(False, pontos, highscore)
            return resultado

        tela.fill(cor_fundo)
        tela.blit(campo_img, (0 - cam, campo_y))
        
        player.draw(tela, cam)

        for d in defs:
            d.draw(tela, cam)

        desenha_tempo(tela, t_mostra)
        desenha_stamina(tela, player.stam, largura - 180, 10, 120, 20)
        desenha_vidas(tela, vidas)
        desenha_pontos(tela, pontos)
        desenha_highscore(tela, highscore)

        txt_pausa = fonte_tempo.render("p = Pausa", True, branco)
        tela.blit(txt_pausa,(largura // 2 - txt_pausa.get_width() // 2, 35))
        
        if aguardando_fim and status == "jogando":
            desenha_resultado(tela, "Ganhou!")
            
        pygame.display.flip()
        
    return "menu"

menu_principal()

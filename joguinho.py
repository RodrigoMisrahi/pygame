import pygame
import random
import ranking
import json

def carregar_rankings():
    try:
        with open('rankings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def salvar_rankings(rankings):
    with open('rankings.json', 'w') as f:
        json.dump(rankings, f)

def adicionar_pontuacao(nome, pontuacao):
    rankings = carregar_rankings()
    rankings.append({'nome': nome, 'pontuacao': pontuacao})
    # Ordena do maior para o menor e mantém apenas os top 10
    rankings.sort(key=lambda x: x['pontuacao'], reverse=True)
    rankings = rankings[:10]
    salvar_rankings(rankings)
# Inicializa o Pygame
pygame.init()

pygame.mixer.init()

# Música de fundo
pygame.mixer.music.load('assets/sons/fundo.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Toca em loop

# Música de colisão
som_colisao = pygame.mixer.Sound('assets/sons/colisao.mp3')
som_colisao.set_volume(0.7)


# Constantes
tela_largura = 500
tela_altura = 720
branco = (255, 255, 255)
preto = (0, 0, 0)
azulescuro = (10, 10, 80)
cinza = (200, 200, 200)
vermelho = (200, 0, 0)

# Tela
window = pygame.display.set_mode((tela_largura, tela_altura))
pygame.display.set_caption('Joguinho')

# Fontes
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)
input_font = pygame.font.SysFont(None, 40)

# Botões
play_button = pygame.Rect(150, 250, 200, 60)
rankings_button = pygame.Rect(150, 350, 200, 60)
back_button = pygame.Rect(20, 20, 100, 40)

# Estados
INICIO = 'inicio'
JOGO = 'jogo'
RANKINGS = 'rankings'
FIM_JOGO = 'fim_jogo'
estado = INICIO

# Variáveis jogador
player_largura = 70
player_altura = 120
player_x = tela_largura // 2 - player_largura // 2
player_y = tela_altura - player_altura - 30
player_velocidade = 7
image_player = pygame.image.load('assets/imagens/user.png').convert()
image_player = pygame.transform.scale(image_player, (70, 120))

# Carros inimigos
enemy_largura = 70
enemy_altura = 120
image_enemy = pygame.image.load('assets/imagens/policia.png').convert()
image_enemy = pygame.transform.scale(image_enemy, (70, 120))

# Imagens adicionais
estrela_img = pygame.image.load('assets/imagens/estrela.png').convert_alpha()
estrela_img = pygame.transform.scale(estrela_img, (30, 30))

poder_images = {
    'escudo': pygame.transform.scale(pygame.image.load('assets/imagens/escudo.png').convert_alpha(), (50, 80)),
    'vida_extra': pygame.transform.scale(pygame.image.load('assets/imagens/vida.png').convert_alpha(), (50, 80)),
    'carros_devagar': pygame.transform.scale(pygame.image.load('assets/imagens/lento.png').convert_alpha(), (50, 80)),
    'menos_carros': pygame.transform.scale(pygame.image.load('assets/imagens/menos.png').convert_alpha(), (50, 80)),
}

coracao_img = pygame.image.load('assets/imagens/coracao.png').convert_alpha()
coracao_img = pygame.transform.scale(coracao_img, (30, 30))

# Fundo
telafundo = pygame.image.load('assets/imagens/WhatsApp Image 2025-05-15 at 16.57.15.jpeg').convert()
telafundo = pygame.transform.scale(telafundo, (tela_largura, tela_altura))

# Inicializa variáveis
def reset_jogo():
    global player_x, enemy_list, poder_list, start_ticks, score, vidas, invulneravel
    global escudo_ativo, carros_devagar_ativo, menos_carros_ativo
    global tempo_ultimo_spawn, tempo_ultimo_poder
    player_x = tela_largura // 2 - player_largura // 2
    enemy_list = []
    poder_list = []
    start_ticks = pygame.time.get_ticks()
    score = 0
    vidas = 2
    invulneravel = False
    escudo_ativo = False
    carros_devagar_ativo = False
    menos_carros_ativo = False
    tempo_ultimo_spawn = 0
    tempo_ultimo_poder = 0

reset_jogo()

# Controle de inimigos e poderes
max_inimigos = 7
intervalo_spawn = 600

# Invulnerabilidade
tempo_invulneravel = 2000
tempo_invulneravel_inicio = 0

# Temporizadores de poderes
escudo_tempo = 5000
escudo_inicio = 0
carros_devagar_tempo = 10000
carros_devagar_inicio = 0
menos_carros_tempo = 10000
menos_carros_inicio = 0

# Clock
clock = pygame.time.Clock()

# Tela de fim
digitar_nome = ''
input_ativo = True

# Loop principal
game = True
while game:
    clock.tick(60)
    tempo_atual = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if estado == INICIO:
                if play_button.collidepoint(event.pos):
                    reset_jogo()
                    estado = JOGO
                elif rankings_button.collidepoint(event.pos):
                    estado = RANKINGS
            elif estado == RANKINGS and back_button.collidepoint(event.pos):
                estado = INICIO
            elif estado == FIM_JOGO and back_button.collidepoint(event.pos):
                estado = INICIO

        elif estado == FIM_JOGO and event.type == pygame.KEYDOWN and input_ativo:
            if event.key == pygame.K_RETURN:
                print(f"Nome: {digitar_nome}, Pontuação: {score}")  # Aqui você pode salvar os dados em arquivo
                estado = INICIO
                digitar_nome = ''
            elif event.key == pygame.K_BACKSPACE:
                digitar_nome = digitar_nome[:-1]
            elif len(digitar_nome) < 10:
                digitar_nome += event.unicode

    keys = pygame.key.get_pressed()
    if estado == JOGO:
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_velocidade
        if keys[pygame.K_RIGHT] and player_x < tela_largura - player_largura:
            player_x += player_velocidade

        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 25
        score = seconds_passed

        qtd_inimigos = min(1 + (score // 500), max_inimigos)
        vel_max = 5 + (score // 500)

        vel_min = 3
        if carros_devagar_ativo:
            vel_min = 1
            vel_max = max(vel_max // 2, 2)

        if menos_carros_ativo:
            qtd_inimigos = max(qtd_inimigos - 2, 1)

        if len(enemy_list) < qtd_inimigos and tempo_atual - tempo_ultimo_spawn > intervalo_spawn:
            tentativas = 0
            while tentativas < 20:
                x_pos = random.randint(0, tela_largura - enemy_largura)
                novo_rect = pygame.Rect(x_pos, -enemy_altura, enemy_largura, enemy_altura)
                if not any(novo_rect.colliderect(e['rect']) for e in enemy_list):
                    vel = random.randint(vel_min, vel_max)
                    enemy_list.append({'rect': novo_rect, 'velocidade': vel})
                    tempo_ultimo_spawn = tempo_atual
                    break
                tentativas += 1

        if score > 0 and score % 1250 == 0 and tempo_atual - tempo_ultimo_poder > 2000:
            tipo = random.choice(list(poder_images.keys()))
            tentativas = 0
            while tentativas < 20:
                x_pos = random.randint(0, tela_largura - enemy_largura)
                novo_rect = pygame.Rect(x_pos, -enemy_altura, enemy_largura, enemy_altura)
                if not any(novo_rect.colliderect(e['rect']) for e in enemy_list):
                    poder_list.append({'rect': novo_rect, 'tipo': tipo, 'velocidade': 3})
                    tempo_ultimo_poder = tempo_atual
                    break
                tentativas += 1

        for enemy in enemy_list:
            enemy['rect'].y += enemy['velocidade']
        for poder in poder_list:
            poder['rect'].y += poder['velocidade']

        player_rect = pygame.Rect(player_x, player_y, player_largura, player_altura)
        if not invulneravel:
            for enemy in enemy_list:
                if player_rect.colliderect(enemy['rect']):
                    if escudo_ativo:
                        escudo_ativo = False
                    else:
                        vidas -= 1
                        invulneravel = True
                        tempo_invulneravel_inicio = tempo_atual
                    enemy_list.remove(enemy)
                    break

        for poder in poder_list:
            if player_rect.colliderect(poder['rect']):
                tipo = poder['tipo']
                if tipo == 'escudo':
                    escudo_ativo = True
                    escudo_inicio = tempo_atual
                elif tipo == 'vida_extra' and vidas < 5:
                    vidas += 1
                elif tipo == 'carros_devagar':
                    carros_devagar_ativo = True
                    carros_devagar_inicio = tempo_atual
                elif tipo == 'menos_carros':
                    menos_carros_ativo = True
                    menos_carros_inicio = tempo_atual
                poder_list.remove(poder)
                break

        enemy_list = [e for e in enemy_list if e['rect'].y < tela_altura]
        poder_list = [p for p in poder_list if p['rect'].y < tela_altura]

        if invulneravel and tempo_atual - tempo_invulneravel_inicio > tempo_invulneravel:
            invulneravel = False

        if escudo_ativo and tempo_atual - escudo_inicio > escudo_tempo:
            escudo_ativo = False
        if carros_devagar_ativo and tempo_atual - carros_devagar_inicio > carros_devagar_tempo:
            carros_devagar_ativo = False
        if menos_carros_ativo and tempo_atual - menos_carros_inicio > menos_carros_tempo:
            menos_carros_ativo = False

        if vidas <= 0:
            estado = FIM_JOGO

    # Renderiza telas
    if estado == INICIO:
        window.blit(telafundo, (0, 0))
        window.blit(font.render('INSPER', True, branco), (180, 120))
        window.blit(font.render('SMASH', True, branco), (180, 160))
        pygame.draw.rect(window, cinza, play_button)
        pygame.draw.rect(window, cinza, rankings_button)
        window.blit(font.render("Jogar", True, preto), (play_button.x + 50, play_button.y + 10))
        window.blit(font.render("Rankings", True, preto), (rankings_button.x + 30, rankings_button.y + 10))

    elif estado == JOGO:
        window.fill(preto)
        for x in [tela_largura // 3, 2 * tela_largura // 3]:
            for y in range(0, tela_altura, 40):
                pygame.draw.line(window, branco, (x, y), (x, y + 20), 5)

        if not (invulneravel and (tempo_atual // 200) % 2 == 0):
            window.blit(image_player, (player_x, player_y))
        if escudo_ativo:
            pygame.draw.rect(window, (0, 150, 255), (player_x - 5, player_y - 5, player_largura + 10, player_altura + 10), 3)

        for enemy in enemy_list:
            window.blit(image_enemy, (enemy['rect'].x, enemy['rect'].y))
        for poder in poder_list:
            window.blit(poder_images[poder['tipo']], (poder['rect'].x, poder['rect'].y))

        for i in range(vidas):
            window.blit(coracao_img, (10 + i * 35, 10))

        window.blit(small_font.render(f'Pontuação: {score}', True, branco), (tela_largura - 200, 10))

        estrelas = min(score // 1000, 5)
        for i in range(estrelas):
            window.blit(estrela_img, (tela_largura - (i + 1) * 35, 40))

    elif estado == RANKINGS:
        window.fill(azulescuro)
        window.blit(font.render("Rankings (em breve)", True, branco), (100, tela_altura // 2))
        pygame.draw.rect(window, cinza, back_button)
        window.blit(small_font.render("Voltar", True, preto), (back_button.x + 10, back_button.y + 5))

    elif estado == FIM_JOGO:
        window.fill(preto)
        fim_text = font.render("Fim de jogo!", True, vermelho)
        score_text = small_font.render(f'Pontuação final: {score}', True, branco)
        input_text = small_font.render("Digite seu nome:", True, branco)
        nome_surface = input_font.render(digitar_nome, True, branco)

        window.blit(fim_text, fim_text.get_rect(center=(tela_largura // 2, 150)))
        window.blit(score_text, score_text.get_rect(center=(tela_largura // 2, 200)))
        window.blit(input_text, input_text.get_rect(center=(tela_largura // 2, 260)))
        pygame.draw.rect(window, branco, (tela_largura // 2 - 100, 300, 200, 40), 2)
        window.blit(nome_surface, (tela_largura // 2 - 95, 305))
        pygame.draw.rect(window, cinza, back_button)
        window.blit(small_font.render("Voltar", True, preto), (back_button.x + 10, back_button.y + 5))

    pygame.display.update()

pygame.quit()

#quando colidir fazer animação de explosão
#som de colisão
#arrumar a hitbox

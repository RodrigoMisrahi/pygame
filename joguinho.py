import pygame
import random

# Inicialização
pygame.init()

# Constantes
largura = 500
altura = 720
branco = (255, 255, 255)
preto = (0, 0, 0)
azulescuro = (10, 10, 80)
cinza = (200, 200, 200)
vermelho = (200, 0, 0)

# Tela
window = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Joguinho')

# Fontes
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

# Botões
play_button = pygame.Rect(150, 250, 200, 60)
rankings_button = pygame.Rect(150, 350, 200, 60)
back_button = pygame.Rect(20, 20, 100, 40)

# Estados
inicio = 'inicio'
jogo = 'jogo'
rankings = 'rankings'
estado = inicio

# Carrinho do jogador
player_largura = 70
player_altura = 120
player_x = largura // 2 - player_largura // 2
player_y = altura - player_altura - 30
player_velocidade = 7
image_player = pygame.image.load('assets/imagens/user.png').convert()
image_player = pygame.transform.scale(image_player, (70, 120))

# Carros inimigos
enemy_largura = 70
enemy_altura = 120
image_enemy = pygame.image.load('assets/imagens/policia.png').convert()
image_enemy = pygame.transform.scale(image_enemy, (70, 120))

# Estrela
estrela_img = pygame.image.load('assets/imagens/estrela.png').convert_alpha()
estrela_img = pygame.transform.scale(estrela_img, (30, 30))

# Poderes
poder_images = {
    'escudo': pygame.transform.scale(pygame.image.load('assets/imagens/escudo.png').convert_alpha(), (50, 80)),
    'vida_extra': pygame.transform.scale(pygame.image.load('assets/imagens/vida.png').convert_alpha(), (50, 80)),
    'carros_devagar': pygame.transform.scale(pygame.image.load('assets/imagens/lento.png').convert_alpha(), (50, 80)),
    'menos_carros': pygame.transform.scale(pygame.image.load('assets/imagens/menos.png').convert_alpha(), (50, 80)),
}

# Corações para vidas
coracao_img = pygame.image.load('assets/imagens/coracao.png').convert_alpha()
coracao_img = pygame.transform.scale(coracao_img, (30, 30))

# Fundo da tela inicial
telafundo = pygame.image.load('assets/imagens/WhatsApp Image 2025-05-15 at 16.57.15.jpeg').convert()
telafundo = pygame.transform.scale(telafundo, (largura, altura))

# Lista de inimigos (cada inimigo é um dicionário com rect e velocidade)
enemy_list = []
poder_list = []

max_inimigos = 7
tempo_ultimo_spawn = 0
intervalo_spawn = 600  # ms entre spawns (mínimo)
tempo_ultimo_poder = 0

# Pontuação e vidas
start_ticks = 0
score = 0
vidas = 2
max_vidas = 5

# Invulnerabilidade
invulneravel = False
tempo_invulneravel = 2000  # 2 segundos
tempo_invulneravel_inicio = 0

# Poderes ativos
escudo_ativo = False
escudo_tempo = 5000
escudo_inicio = 0
carros_devagar_ativo = False
carros_devagar_tempo = 10000
carros_devagar_inicio = 0
menos_carros_ativo = False
menos_carros_tempo = 10000
menos_carros_inicio = 0

# Clock
clock = pygame.time.Clock()

# Loop principal
game = True
while game:
    clock.tick(60)
    tempo_atual = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if estado == inicio:
                if play_button.collidepoint(event.pos):
                    estado = jogo
                    # Reset do jogo
                    player_x = largura // 2 - player_largura // 2
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
                elif rankings_button.collidepoint(event.pos):
                    estado = rankings
            elif estado == rankings:
                if back_button.collidepoint(event.pos):
                    estado = inicio

    keys = pygame.key.get_pressed()
    if estado == jogo:
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_velocidade
        if keys[pygame.K_RIGHT] and player_x < largura - player_largura:
            player_x += player_velocidade

        # Atualiza pontuação
        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 25
        score = seconds_passed

        # Dificuldade progressiva
        qtd_inimigos_desejada = min(1 + (score // 500), max_inimigos)
        velocidade_maxima = 5 + (score // 500)

        # Aplica efeito carros mais devagar
        velocidade_min = 3
        if carros_devagar_ativo:
            velocidade_min = 1
            velocidade_maxima = max(velocidade_maxima // 2, 2)

        # Aplica efeito menos carros
        if menos_carros_ativo:
            qtd_inimigos_desejada = max(qtd_inimigos_desejada - 2, 1)

        # Spawn de inimigos se houver espaço
        if len(enemy_list) < qtd_inimigos_desejada and tempo_atual - tempo_ultimo_spawn > intervalo_spawn:
            tentativas = 0
            while tentativas < 20:
                x_pos = random.randint(0, largura - enemy_largura)
                novo_rect = pygame.Rect(x_pos, -enemy_altura, enemy_largura, enemy_altura)
                sobrepoe = any(novo_rect.colliderect(e['rect']) for e in enemy_list)
                if not sobrepoe:
                    velocidade_enemy = random.randint(velocidade_min, velocidade_maxima)
                    enemy_list.append({
                        'rect': novo_rect,
                        'velocidade': velocidade_enemy
                    })
                    tempo_ultimo_spawn = tempo_atual
                    break
                tentativas += 1

        # Spawn de poder a cada 1250 pontos
        if score > 0 and score % 1250 == 0 and tempo_atual - tempo_ultimo_poder > 2000:
            tipo_poder = random.choice(list(poder_images.keys()))
            tentativas = 0
            while tentativas < 20:
                x_pos = random.randint(0, largura - enemy_largura)
                novo_rect = pygame.Rect(x_pos, -enemy_altura, enemy_largura, enemy_altura)
                sobrepoe = any(novo_rect.colliderect(e['rect']) for e in enemy_list) or any(novo_rect.colliderect(p['rect']) for p in poder_list)
                if not sobrepoe:
                    poder_list.append({
                        'rect': novo_rect,
                        'tipo': tipo_poder,
                        'velocidade': 3
                    })
                    tempo_ultimo_poder = tempo_atual
                    break
                tentativas += 1

        # Atualiza posição inimigos
        for enemy in enemy_list:
            enemy['rect'].y += enemy['velocidade']

        # Atualiza posição poderes
        for poder in poder_list:
            poder['rect'].y += poder['velocidade']

        # Colisão inimigos
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

        # Colisão poderes
        for poder in poder_list:
            if player_rect.colliderect(poder['rect']):
                tipo = poder['tipo']
                if tipo == 'escudo':
                    escudo_ativo = True
                    escudo_inicio = tempo_atual
                elif tipo == 'vida_extra':
                    if vidas < max_vidas:
                        vidas += 1
                elif tipo == 'carros_devagar':
                    carros_devagar_ativo = True
                    carros_devagar_inicio = tempo_atual
                elif tipo == 'menos_carros':
                    menos_carros_ativo = True
                    menos_carros_inicio = tempo_atual
                poder_list.remove(poder)
                break

        # Remove inimigos e poderes fora da tela
        enemy_list = [e for e in enemy_list if e['rect'].y < altura]
        poder_list = [p for p in poder_list if p['rect'].y < altura]

        # Controla tempo invulnerabilidade
        if invulneravel and tempo_atual - tempo_invulneravel_inicio > tempo_invulneravel:
            invulneravel = False

        # Controla tempo poderes
        if escudo_ativo and tempo_atual - escudo_inicio > escudo_tempo:
            escudo_ativo = False
        if carros_devagar_ativo and tempo_atual - carros_devagar_inicio > carros_devagar_tempo:
            carros_devagar_ativo = False
        if menos_carros_ativo and tempo_atual - menos_carros_inicio > menos_carros_tempo:
            menos_carros_ativo = False

        # Fim de jogo
        if vidas <= 0:
            estado = inicio

    # Desenho telas
    if estado == inicio:
        window.blit(telafundo, (0, 0))

        title_text = font.render('INSPER', True, branco)
        window.blit(title_text, title_text.get_rect(center=(largura // 2, 120)))
        title2_text = font.render('SMASH', True, branco)
        window.blit(title2_text, title2_text.get_rect(center=(largura // 2, 160)))

        pygame.draw.rect(window, cinza, play_button)
        pygame.draw.rect(window, cinza, rankings_button)

        play_text = font.render("Jogar", True, preto)
        rankings_text = font.render("Rankings", True, preto)
        window.blit(play_text, (play_button.x + 50, play_button.y + 10))
        window.blit(rankings_text, (rankings_button.x + 30, rankings_button.y + 10))

    elif estado == jogo:
        window.fill(preto)

        # Faixas tracejadas
        linha_largura = largura // 3
        traco_altura = 20
        traco_espaco = 20
        for x in [linha_largura, linha_largura * 2]:
            y = 0
            while y < altura:
                pygame.draw.line(window, branco, (x, y), (x, y + traco_altura), 5)
                y += traco_altura + traco_espaco

        # Jogador (invulnerável pisca)
        if invulneravel and (tempo_atual // 200) % 2 == 0:
            # pisca invisível
            pass
        else:
            pygame.draw.rect(window, (0, 200, 0), (player_x, player_y, player_largura, player_altura))
            window.blit(image_player, (player_x, player_y))

        # Escudo visual (um contorno azul ao redor do jogador)
        if escudo_ativo:
            pygame.draw.rect(window, (0, 150, 255), (player_x - 5, player_y - 5, player_largura + 10, player_altura + 10), 3)

        # Inimigos
        for enemy in enemy_list:
            window.blit(image_enemy, (enemy['rect'].x, enemy['rect'].y))

        # Poderes
        for poder in poder_list:
            img = poder_images[poder['tipo']]
            window.blit(img, (poder['rect'].x, poder['rect'].y))

        # Vidas com corações
        for i in range(vidas):
            window.blit(coracao_img, (10 + i * 35, 10))

        # Pontuação
        score_text = small_font.render(f'Pontuação: {score}', True, branco)
        window.blit(score_text, (largura - 200, 10))

        # Estrelas
        estrelas = min(score // 1000, 5)
        for i in range(estrelas):
            x = largura - (i + 1) * 35
            window.blit(estrela_img, (x, 40))
        
    elif estado == rankings:
        window.fill(azulescuro)
        rankings_text = font.render("Rankings (em breve)", True, branco)
        window.blit(rankings_text, rankings_text.get_rect(center=(largura // 2, altura // 2)))
        pygame.draw.rect(window, cinza, back_button)
        back_text = small_font.render("Voltar", True, preto)
        window.blit(back_text, (back_button.x + 10, back_button.y + 5))

    pygame.display.update()

pygame.quit()

#quando colidir fazer animação de explosão
#som de fundo e de colisão
#sistema de ranking
#tela de fim de jogo com pontuação
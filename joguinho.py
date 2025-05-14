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
player_largura = 50
player_altura = 80
player_x = largura // 2 - player_largura // 2
player_y = altura - player_altura - 30
player_velocidade = 7
image_player = pygame.image.load('assets/imagens/user.png').convert()
image_player = pygame.transform.scale(image_player, (70, 120))

# Carros inimigos
enemy_largura = 50
enemy_altura = 80
image_enemy = pygame.image.load('assets/imagens/policia.png').convert()
image_enemy = pygame.transform.scale(image_enemy, (70, 120))

# Estrela
estrela_img = pygame.image.load('assets/imagens/estrela.png').convert_alpha()
estrela_img = pygame.transform.scale(estrela_img, (30, 30))

# Lista de inimigos (cada inimigo é um dicionário com rect e velocidade)
enemy_list = []
max_inimigos = 7
tempo_ultimo_spawn = 0
intervalo_spawn = 600  # ms entre spawns (mínimo)

# Pontuação
start_ticks = 0
score = 0

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
                    start_ticks = pygame.time.get_ticks()
                    score = 0
                    tempo_ultimo_spawn = 0
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

        # Spawn de inimigos se houver espaço
        if len(enemy_list) < qtd_inimigos_desejada and tempo_atual - tempo_ultimo_spawn > intervalo_spawn:
            # Geração segura de posição sem sobreposição
            tentativas = 0
            while tentativas < 20:
                x_pos = random.randint(0, largura - enemy_largura)
                novo_rect = pygame.Rect(x_pos, -enemy_altura, enemy_largura, enemy_altura)

                sobrepoe = any(novo_rect.colliderect(e['rect']) for e in enemy_list)
                if not sobrepoe:
                    enemy_list.append({
                        'rect': novo_rect,
                        'velocidade': random.randint(3, velocidade_maxima)
                    })
                    tempo_ultimo_spawn = tempo_atual
                    break
                tentativas += 1

        # Atualiza posição dos inimigos
        for enemy in enemy_list:
            enemy['rect'].y += enemy['velocidade']

        # Colisão
        player_rect = pygame.Rect(player_x, player_y, player_largura, player_altura)
        for enemy in enemy_list:
            if player_rect.colliderect(enemy['rect']):
                estado = inicio

        # Remove inimigos fora da tela
        enemy_list = [enemy for enemy in enemy_list if enemy['rect'].y < altura]

    # Desenho das telas
    if estado == inicio:
        window.fill(preto)

        image_explosao = pygame.image.load('assets/imagens/explosao.png').convert()
        image_explosao = pygame.transform.scale(image_explosao, (125, 166))
        window.blit(image_explosao, (270, 20))

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

        # Jogador
        pygame.draw.rect(window, (0, 200, 0), (player_x, player_y, player_largura, player_altura))
        window.blit(image_player, (player_x, player_y))

        # Inimigos
        for enemy in enemy_list:
            window.blit(image_enemy, (enemy['rect'].x, enemy['rect'].y))

        # Pontuação
        score_text = small_font.render(f"Pontos: {score}", True, branco)
        window.blit(score_text, (20, 20))

        # Estrelas no canto superior direito
        estrelas = min(score // 1000, 5)
        for i in range(estrelas):
            x = largura - (i + 1) * 35
            window.blit(estrela_img, (x, 20))

    elif estado == rankings:
        window.fill(azulescuro)
        pygame.draw.rect(window, cinza, back_button)
        back_text = small_font.render("Voltar", True, branco)
        window.blit(back_text, (back_button.x + 10, back_button.y + 5))

    pygame.display.update()

pygame.quit()

#poderes: escudo, vida extra, carros mais devagares, menos carros na tela, 
#quando colidir fazer animação de explosão
#colocar fundos na tela inicial e na de rankings
#cpa fazer uma paisagem na tela de jogo
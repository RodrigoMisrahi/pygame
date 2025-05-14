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

# Tela principal
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
enemy_list = []
image_enemy = pygame.image.load('assets/imagens/policia.png').convert()
image_enemy = pygame.transform.scale(image_enemy, (70, 120))
enemy_velocidade = 3
spawn_interval = 1500  # milissegundos
min_spawn_interval = 400
max_enemy_speed = 12

# Estrelas
estrela_img = pygame.image.load('assets/imagens/estrela.png').convert_alpha()
estrela_img = pygame.transform.scale(estrela_img, (40, 40))

# Temporizador de spawn
spawn_timer = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_timer, spawn_interval)

# Pontuação
start_ticks = 0
score = 0

# Clock
clock = pygame.time.Clock()

# Loop principal
game = True
while game:
    clock.tick(60)

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
                    enemy_velocidade = 3
                    spawn_interval = 1500
                    pygame.time.set_timer(spawn_timer, spawn_interval)
                elif rankings_button.collidepoint(event.pos):
                    estado = rankings
            elif estado == rankings:
                if back_button.collidepoint(event.pos):
                    estado = inicio
        elif estado == jogo and event.type == spawn_timer:
            x_pos = random.randint(0, largura - enemy_largura)
            enemy_list.append(pygame.Rect(x_pos, -enemy_altura, enemy_largura, enemy_altura))

    keys = pygame.key.get_pressed()
    if estado == jogo:
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_velocidade
        if keys[pygame.K_RIGHT] and player_x < largura - player_largura:
            player_x += player_velocidade

        # Atualiza inimigos
        for enemy in enemy_list:
            enemy.y += enemy_velocidade

        # Colisão
        player_rect = pygame.Rect(player_x, player_y, player_largura, player_altura)
        for enemy in enemy_list:
            if player_rect.colliderect(enemy):
                estado = inicio

        # Remove carros fora da tela
        enemy_list = [enemy for enemy in enemy_list if enemy.y < altura]

        # Atualiza pontuação
        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 25
        score = seconds_passed

        # Aumenta velocidade e reduz intervalo com base na pontuação
        nova_velocidade = 3 + (score // 500)
        if nova_velocidade != enemy_velocidade and nova_velocidade <= max_enemy_speed:
            enemy_velocidade = nova_velocidade

        novo_intervalo = 1500 - (score // 250) * 100
        novo_intervalo = max(min_spawn_interval, novo_intervalo)
        if novo_intervalo != spawn_interval:
            spawn_interval = novo_intervalo
            pygame.time.set_timer(spawn_timer, spawn_interval)

    # Desenho das telas
    if estado == inicio:
        window.fill(preto)

        image_explosao = pygame.image.load('assets/imagens/explosao.png').convert()
        image_explosao = pygame.transform.scale(image_explosao, (125, 166))
        window.blit(image_explosao, (270, 20))

        title_text = font.render('INSPER', True, branco)
        title_rect = title_text.get_rect(center=(largura // 2, 150))
        window.blit(title_text, title_rect)

        title_text = font.render('SMASH', True, branco)
        title_rect = title_text.get_rect(center=(largura // 2, 120))
        window.blit(title_text, title_rect)

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

        # Carrinho do jogador
        window.blit(image_player, (player_x, player_y))

        # Inimigos
        for enemy in enemy_list:
            window.blit(image_enemy, (enemy.x, enemy.y))

        # Pontuação
        score_text = small_font.render(f"Pontos: {score}", True, branco)
        window.blit(score_text, (20, 20))

        # Estrelas no canto superior direito
        num_estrelas = min(score // 1000, 5)
        for i in range(num_estrelas):
            window.blit(estrela_img, (largura - 50 - i * 45, 20))

    elif estado == rankings:
        window.fill(azulescuro)
        pygame.draw.rect(window, cinza, back_button)
        back_text = small_font.render("Voltar", True, branco)
        window.blit(back_text, (back_button.x + 10, back_button.y + 5))

    pygame.display.update()

pygame.quit()

#poderes: escudo, vida extra, carros mais devagares, menos carros na tela, 
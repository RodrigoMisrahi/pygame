import pygame
import random

# Inicialização
pygame.init()

# Constantes
WIDTH = 500
HEIGHT = 720
branco = (255, 255, 255)
preto = (0, 0, 0)
azulescuro = (10, 10, 80)
cinza = (200, 200, 200)
vermelho = (200, 0, 0)

# Tela principal
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Joguinho')

# Fonte
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
player_width = 50
player_height = 80
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 30
player_speed = 7

# Carros inimigos
enemy_width = 50
enemy_height = 80
enemy_speed = 5
enemy_list = []

spawn_timer = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_timer, 1500)  # Novo inimigo a cada 1.5s

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
                    player_x = WIDTH // 2 - player_width // 2
                    enemy_list = []
                elif rankings_button.collidepoint(event.pos):
                    estado = rankings
            elif estado == rankings:
                if back_button.collidepoint(event.pos):
                    estado = inicio
        elif estado == jogo and event.type == spawn_timer:
            x_pos = random.randint(0, WIDTH - enemy_width)
            enemy_list.append(pygame.Rect(x_pos, -enemy_height, enemy_width, enemy_height))

    keys = pygame.key.get_pressed()
    if estado == jogo:
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed

        

        # Remove inimigos que saíram da tela
        enemy_list = [enemy for enemy in enemy_list if enemy.y < HEIGHT]

    # Desenhos
    if estado == inicio:
        window.fill(preto)

        title_text = font.render('Joguinho', True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(WIDTH // 2, 150))
        window.blit(title_text, title_rect)

        pygame.draw.rect(window, cinza, play_button)
        pygame.draw.rect(window, cinza, rankings_button)

        play_text = font.render("Jogar", True, preto)
        rankings_text = font.render("Rankings", True, preto)

        window.blit(play_text, (play_button.x + 50, play_button.y + 10))
        window.blit(rankings_text, (rankings_button.x + 30, rankings_button.y + 10))

    elif estado == jogo:
        window.fill(preto)

        # Desenha jogador
        pygame.draw.rect(window, (0, 200, 0), (player_x, player_y, player_width, player_height))

        # Desenha inimigos
        for enemy in enemy_list:
            pygame.draw.rect(window, vermelho, enemy)

    elif estado == rankings:
        window.fill(azulescuro)
        pygame.draw.rect(window, cinza, back_button)
        back_text = small_font.render("Voltar", True, branco)
        window.blit(back_text, (back_button.x + 10, back_button.y + 5))

    pygame.display.update()

pygame.quit()

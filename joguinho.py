import pygame

# Inicialização
pygame.init()

# Constantes
WIDTH, HEIGHT = 500, 720
branco = (255, 255, 255)
preto = (0, 0, 0)
azulescuro = (10, 10, 80)
cinza = (200, 200, 200)
DARK_cinza = (100, 100, 100)

# Tela principal
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Joguinho')

# Fonte
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

# Botões (posição e tamanho)
play_button = pygame.Rect(150, 250, 200, 60)
rankings_button = pygame.Rect(150, 350, 200, 60)
back_button = pygame.Rect(20, 20, 100, 40)

# Estados do jogo
inicio = 'inicio'
jogo = 'jogo'
rankings = 'rankings'
estado = inicio

# Loop principal
game = True
while game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if estado == inicio:
                if play_button.collidepoint(event.pos):
                    estado = jogo
                elif rankings_button.collidepoint(event.pos):
                    estado = rankings
            elif estado == rankings:
                if back_button.collidepoint(event.pos):
                    estado = inicio

    # Atualização da tela
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

    elif estado == rankings:
        window.fill(azulescuro)

        # Botão Voltar
        pygame.draw.rect(window, DARK_cinza, back_button)
        back_text = small_font.render("Voltar", True, branco)
        window.blit(back_text, (back_button.x + 10, back_button.y + 5))

    pygame.display.update()

pygame.quit()
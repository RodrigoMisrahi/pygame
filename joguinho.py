import pygame
import random
import ranking

# Inicialização e carregamento
def init_pygame():
    """Inicializa o Pygame e seus módulos de áudio."""
    pygame.init()
    pygame.mixer.init()


def load_assets():
    """Carrega imagens, sons e configurações iniciais."""
    # Música de fundo
    pygame.mixer.music.load('assets/sons/fundo.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    # Música de colisão
    som = pygame.mixer.Sound('assets/sons/colisao.mp3')
    som.set_volume(0.7)

    # Imagens do jogador e inimigos
    player_img = pygame.image.load('assets/imagens/user.png').convert()
    player_img = pygame.transform.scale(player_img, (player_largura, player_altura))
    enemy_img = pygame.image.load('assets/imagens/policia.png').convert()
    enemy_img = pygame.transform.scale(enemy_img, (enemy_largura, enemy_altura))

    # Ícones de poderes e vidas
    estrela = pygame.image.load('assets/imagens/estrela.png').convert_alpha()
    estrela = pygame.transform.scale(estrela, (30, 30))

    poder_imgs = {
        'escudo': pygame.transform.scale(pygame.image.load('assets/imagens/escudo.png').convert_alpha(), (50, 80)),
        'vida_extra': pygame.transform.scale(pygame.image.load('assets/imagens/vida.png').convert_alpha(), (50, 80)),
        'carros_devagar': pygame.transform.scale(pygame.image.load('assets/imagens/lento.png').convert_alpha(), (50, 80)),
        'menos_carros': pygame.transform.scale(pygame.image.load('assets/imagens/menos.png').convert_alpha(), (50, 80)),
    }

    coracao = pygame.image.load('assets/imagens/coracao.png').convert_alpha()
    coracao = pygame.transform.scale(coracao, (30, 30))

    # Fundo da tela inicial
    fundo = pygame.image.load('assets/imagens/WhatsApp Image 2025-05-15 at 16.57.15.jpeg').convert()
    fundo = pygame.transform.scale(fundo, (tela_largura, tela_altura))

    return som, player_img, enemy_img, estrela, poder_imgs, coracao, fundo


# FSM e reset do jogo
INICIO, JOGO, RANKINGS, FIM_JOGO = 'inicio', 'jogo', 'rankings', 'fim_jogo'
estado = INICIO


def reset_jogo():
    """Reseta variáveis do jogo para o estado inicial."""
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


# Spawn de inimigos e poderes
def spawn_enemy(tempo_atual):
    """Adiciona um novo inimigo se condições de tempo e quantidade forem atendidas."""
    global tempo_ultimo_spawn
    qtd = min(1 + (score // 500), max_inimigos)
    if menos_carros_ativo:
        qtd = max(qtd - 2, 1)

    vel_min = 3
    vel_max = 5 + (score // 500)
    if carros_devagar_ativo:
        vel_min = 1
        vel_max = max(vel_max // 2, 2)

    if len(enemy_list) < qtd and tempo_atual - tempo_ultimo_spawn > intervalo_spawn:
        for _ in range(20):
            x_pos = random.randint(0, tela_largura - enemy_largura)
            rect = pygame.Rect(x_pos, -enemy_altura, enemy_largura, enemy_altura)
            if not any(rect.colliderect(e['rect']) for e in enemy_list):
                enemy_list.append({'rect': rect, 'velocidade': random.randint(vel_min, vel_max)})
                tempo_ultimo_spawn = tempo_atual
                break


def spawn_poder(tempo_atual):
    """Adiciona um novo poder aleatório a cada 1250 pontos."""
    global tempo_ultimo_poder
    if score > 0 and score % 1250 == 0 and tempo_atual - tempo_ultimo_poder > 2000:
        tipo = random.choice(list(poder_images.keys()))
        for _ in range(20):
            x_pos = random.randint(0, tela_largura - enemy_largura)
            rect = pygame.Rect(x_pos, -enemy_altura, enemy_largura, enemy_altura)
            if not any(rect.colliderect(e['rect']) for e in enemy_list):
                poder_list.append({'rect': rect, 'tipo': tipo, 'velocidade': 3})
                tempo_ultimo_poder = tempo_atual
                break


# Colisões e timers
def handle_collisions(tempo_atual):
    """Detecta colisões com inimigos e poderes e aplica efeitos."""
    global vidas, invulneravel, tempo_invulneravel_inicio
    global escudo_ativo, escudo_inicio
    global carros_devagar_ativo, carros_devagar_inicio
    global menos_carros_ativo, menos_carros_inicio

    player_rect = pygame.Rect(player_x, player_y, player_largura, player_altura)

    # Colisão com inimigos
    if not invulneravel:
        for e in enemy_list:
            if player_rect.colliderect(e['rect']):
                if escudo_ativo:
                    escudo_ativo = False
                else:
                    vidas -= 1
                    invulneravel = True
                    tempo_invulneravel_inicio = tempo_atual
                enemy_list.remove(e)
                break

    # Colisão com poderes
    for p in poder_list:
        if player_rect.colliderect(p['rect']):
            if p['tipo'] == 'escudo':
                scudo_ativo = True; escudo_inicio = tempo_atual
            elif p['tipo'] == 'vida_extra' and vidas < 5:
                vidas += 1
            elif p['tipo'] == 'carros_devagar':
                carros_devagar_ativo = True; carros_devagar_inicio = tempo_atual
            elif p['tipo'] == 'menos_carros':
                menos_carros_ativo = True; menos_carros_inicio = tempo_atual
            poder_list.remove(p)
            break


# Atualização de estado
def update_game(tempo_atual):
    """Atualiza posições, timers e pontuação."""
    global score, invulneravel

    # Atualiza score pelo tempo decorrido
    score = (pygame.time.get_ticks() - start_ticks) // 25

    # Move inimigos e poderes
    for e in enemy_list:
        e['rect'].y += e['velocidade']
    for p in poder_list:
        p['rect'].y += p['velocidade']

    # Filtra objetos fora da tela
    enemy_list[:] = [e for e in enemy_list if e['rect'].y < tela_altura]
    poder_list[:] = [p for p in poder_list if p['rect'].y < tela_altura]

    # Reseta invulnerabilidade e efeitos
    if invulneravel and tempo_atual - tempo_invulneravel_inicio > tempo_invulneravel:
        invulneravel = False
    if escudo_ativo and tempo_atual - escudo_inicio > escudo_tempo:
        escudo_ativo = False
    if carros_devagar_ativo and tempo_atual - carros_devagar_inicio > carros_devagar_tempo:
        carros_devagar_ativo = False
    if menos_carros_ativo and tempo_atual - menos_carros_inicio > menos_carros_tempo:
        menos_carros_ativo = False


# Renderização das telas
def render_inicio():
    """Desenha a tela inicial com botões de Jogar e Rankings."""
    window.blit(telafundo, (0, 0))
    window.blit(font.render('INSPER', True, branco), (180, 160))
    window.blit(font.render('SMASH', True, branco), (180, 120))
    pygame.draw.rect(window, cinza, play_button)
    pygame.draw.rect(window, cinza, rankings_button)
    window.blit(font.render('Jogar', True, preto), (play_button.x+50, play_button.y+10))
    window.blit(font.render('Rankings', True, preto), (rankings_button.x+30, rankings_button.y+10))


def render_jogo():
    """Desenha o jogo em andamento: pista, jogador, inimigos, poderes e HUD."""
    window.fill(preto)
    # Traços da pista
    for x in [tela_largura//3, 2*tela_largura//3]:
        for y in range(0, tela_altura, 40):
            pygame.draw.line(window, branco, (x, y), (x, y+20), 5)

    # Jogador
    if not (invulneravel and ((pygame.time.get_ticks()//200) % 2) == 0):
        window.blit(image_player, (player_x, player_y))
    if escudo_ativo:
        pygame.draw.rect(window, (0,150,255), (player_x-5, player_y-5, player_largura+10, player_altura+10), 3)

    # Inimigos e poderes
    for e in enemy_list:
        window.blit(image_enemy, (e['rect'].x, e['rect'].y))
    for p in poder_list:
        window.blit(poder_images[p['tipo']], (p['rect'].x, p['rect'].y))

    # Vidas e pontuação
    for i in range(vidas): window.blit(coracao_img, (10 + i*35, 10))
    window.blit(small_font.render(f'Pontuação: {score}', True, branco), (tela_largura-200,10))

    # Estrelas bônus
    for i in range(min(score//1000,5)):
        window.blit(estrela_img, (tela_largura-(i+1)*35,40))


def render_rankings():
    """Desenha a tela de Rankings com top 10."""
    window.fill(preto)
    window.blit(font.render('Top 10 Rankings', True, branco), (150, 50))
    lst = ranking.carregar_rankings()
    y = 120
    for idx, e in enumerate(lst):
        text = f"{idx+1}. {e['nome']}: {e['pontuacao']}"
        window.blit(small_font.render(text, True, branco), (100, y)); y += 40
    pygame.draw.rect(window, cinza, back_button)
    window.blit(small_font.render('Voltar', True, preto), (back_button.x+10, back_button.y+5))


def render_fim_jogo():
    """Desenha a tela de fim de jogo com input de nome e top5."""
    window.fill(preto)
    window.blit(font.render('Fim de jogo!', True, vermelho), (tela_largura//2-100,150))
    window.blit(small_font.render(f'Pontuação final: {score}', True, branco), (tela_largura//2-120,200))
    window.blit(small_font.render('Digite seu nome:', True, branco), (tela_largura//2-120,260))
    pygame.draw.rect(window, branco, (tela_largura//2-100,300,200,40), 2)
    window.blit(input_font.render(digitar_nome, True, branco), (tela_largura//2-95,305))
    pygame.draw.rect(window, cinza, back_button)
    window.blit(small_font.render('Voltar', True, preto), (back_button.x+10, back_button.y+5))
    # Top 5
    lst = ranking.carregar_rankings()[:5]
    y = 400
    for idx, e in enumerate(lst):
        txt = f"{idx+1}. {e['nome']}: {e['pontuacao']}"
        window.blit(small_font.render(txt, True, branco), (100, y)); y += 35


# Função principal
def main():
    init_pygame()
    global som_colisao, image_player, image_enemy, estrela_img, poder_images, coracao_img, telafundo
    som_colisao, image_player, image_enemy, estrela_img, poder_images, coracao_img, telafundo = load_assets()
    reset_jogo()

    # Loop principal
    clock = pygame.time.Clock()
    game = True
    global estado, digitar_nome, input_ativo
    digitar_nome = ''
    input_ativo = True

    while game:
        clock.tick(60)
        tempo_atual = pygame.time.get_ticks()

        # Tratamento de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            elif event.type == pygame.MOUSEBUTTONUP:
                handle_mouse(event.pos)
            elif estado == FIM_JOGO and event.type == pygame.KEYDOWN and input_ativo:
                handle_name_input(event)

        # Input de teclado no jogo
        if estado == JOGO:
            handle_keyboard()
            spawn_enemy(tempo_atual)
            spawn_poder(tempo_atual)
            handle_collisions(tempo_atual)
            update_game(tempo_atual)
            if vidas <= 0:
                estado = FIM_JOGO

        # Renderização de acordo com o estado
        if estado == INICIO:
            render_inicio()
        elif estado == JOGO:
            render_jogo()
        elif estado == RANKINGS:
            render_rankings()
        elif estado == FIM_JOGO:
            render_fim_jogo()

        pygame.display.update()

    pygame.quit()

# Funções auxiliares para input
def handle_mouse(pos):
    """Gerencia cliques de mouse conforme o estado atual."""
    global estado
    if estado == INICIO:
        if play_button.collidepoint(pos):
            reset_jogo(); estado = JOGO
        elif rankings_button.collidepoint(pos):
            estado = RANKINGS
    elif estado in (RANKINGS, FIM_JOGO):
        if back_button.collidepoint(pos):
            estado = INICIO


def handle_keyboard():
    # Gerencia setas esquerda/direita durante o jogo
    keys = pygame.key.get_pressed()
    global player_x
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_velocidade
    if keys[pygame.K_RIGHT] and player_x < tela_largura-player_largura:
        player_x += player_velocidade


def handle_name_input(event):
    # Lê caracteres para o nome no fim de jogo e salva ranking
    global digitar_nome, estado
    if event.key == pygame.K_RETURN and digitar_nome.strip():
        ranking.adicionar_pontuacao(digitar_nome.strip(), score)
        estado = INICIO; digitar_nome = ''
    elif event.key == pygame.K_BACKSPACE:
        digitar_nome = digitar_nome[:-1]
    elif len(digitar_nome) < 10:
        digitar_nome += event.unicode


if __name__ == '__main__':
    # Constantes globais usadas em todo código
    tela_largura, tela_altura = 500, 720
    branco, preto, azulescuro = (255,255,255), (0,0,0), (10,10,80)
    cinza, vermelho = (200,200,200), (200,0,0)
    player_largura, player_altura = 70, 120
    player_y = tela_altura - player_altura - 30
    player_velocidade = 7
    enemy_largura, enemy_altura = 70, 120
    intervalo_spawn = 600; max_inimigos = 7
    tempo_invulneravel = 2000
    escudo_tempo, carros_devagar_tempo, menos_carros_tempo = 5000, 10000, 10000

    # Botões e fontes
    play_button = pygame.Rect(150,250,200,60)
    rankings_button = pygame.Rect(150,350,200,60)
    back_button = pygame.Rect(20,20,100,40)
    font = pygame.font.SysFont(None,48)
    small_font = pygame.font.SysFont(None,36)
    input_font = pygame.font.SysFont(None,40)

    window = pygame.display.set_mode((tela_largura,tela_altura))
    pygame.display.set_caption('Smash Insper')

    main()

#quando colidir fazer animação de explosão
#som de colisão
#arrumar a hitbox
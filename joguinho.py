import pygame
import random
import ranking
from pygame import mask

# Configurações iniciais
def init_pygame():
    """Inicializa o pygame, mixer e configura a tela e fontes"""
    pygame.init()
    pygame.mixer.init()

    # Música de fundo
    pygame.mixer.music.load('assets/sons/fundo.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    # Som de colisão
    som = pygame.mixer.Sound('assets/sons/colisao.mp3')
    som.set_volume(0.7)

    # Tela
    tela = pygame.display.set_mode((500, 720))
    pygame.display.set_caption('Smash Insper')

    # Fontes
    fonts = {
        'large': pygame.font.SysFont(None, 48),
        'medium': pygame.font.SysFont(None, 36),
        'input': pygame.font.SysFont(None, 40)
    }
    return tela, fonts, som

# Carregamento de imagens
def load_assets():
    """Carrega e retorna todas as imagens do jogo"""
    assets = {}
    
    # Player com máscara
    player_img = pygame.image.load('assets/imagens/user.png').convert_alpha()
    assets['player'] = pygame.transform.scale(player_img, (70, 120))
    assets['player_mask'] = mask.from_surface(assets['player'])
    
    # Inimigo com máscara
    enemy_img = pygame.image.load('assets/imagens/policia.png').convert_alpha()
    assets['enemy'] = pygame.transform.scale(enemy_img, (70, 120))
    assets['enemy_mask'] = mask.from_surface(assets['enemy'])
    
    # Demais assets
    assets['estrela'] = pygame.transform.scale(
        pygame.image.load('assets/imagens/estrela.png').convert_alpha(), (30, 30)
    )
    assets['poder'] = {k: pygame.transform.scale(
        pygame.image.load(f'assets/imagens/{filename}.png').convert_alpha(), (50, 80)
    ) for k, filename in {
        'escudo': 'escudo',
        'vida_extra': 'vida',
        'carros_devagar': 'lento',
        'menos_carros': 'menos'
    }.items()}
    assets['coracao'] = pygame.transform.scale(
        pygame.image.load('assets/imagens/coracao.png').convert_alpha(), (30, 30)
    )
    assets['fundo_inicio'] = pygame.transform.scale(
        pygame.image.load('assets/imagens/WhatsApp Image 2025-05-15 at 16.57.15.jpeg').convert(), (500, 720)
    )
    return assets

# Estado e variáveis do jogo
def reset_jogo(state, assets):
    """Reseta variáveis de jogo para novo início ou reinício"""
    state.update({
        'player_x': 500 // 2 - 70 // 2,
        'enemy_list': [],
        'poder_list': [],
        'start_ticks': pygame.time.get_ticks(),
        'score': 0,
        'vidas': 2,
        'invulneravel': False,
        'escudo_ativo': False,
        'carros_devagar_ativo': False,
        'menos_carros_ativo': False,
        'tempo_ultimo_spawn': 0,
        'tempo_ultimo_poder': 0,
        'tempo_invulneravel_inicio': 0,
        'escudo_inicio': 0,
        'carros_devagar_inicio': 0,
        'menos_carros_inicio': 0
    })

def criar_state():
    """Cria dicionário inicial de estado"""
    return {
        'estado': 'inicio',
        'digitar_nome': '',
        'input_ativo': True
    }

# Spawns de inimigos e poderes
def tentar_spawn(lista, max_tentativas, largura, altura, y_vel, existing):
    """Função genérica para tentar spawn em posição não colidida"""
    for _ in range(max_tentativas):
        x = random.randint(0, 500 - largura)
        rect = pygame.Rect(x, -altura, largura, altura)
        if not any(rect.colliderect(e['rect']) for e in existing):
            return rect
    return None

def spawn_inimigos(state):
    """Gerencia spawn de inimigos baseado em score e timers"""
    now = pygame.time.get_ticks()
    score = state['score']
    qtd = min(1 + (score // 500), 7)
    vel_max = 5 + (score // 500)
    vel_min = 3
    if state['carros_devagar_ativo']:
        vel_min, vel_max = 1, max(vel_max // 2, 2)
    if state['menos_carros_ativo']:
        qtd = max(qtd - 2, 1)

    if len(state['enemy_list']) < qtd and now - state['tempo_ultimo_spawn'] > 600:
        rect = tentar_spawn(state['enemy_list'], 20, 70, 120, 0, state['enemy_list'])
        if rect:
            state['enemy_list'].append({'rect': rect, 'velocidade': random.randint(vel_min, vel_max)})
            state['tempo_ultimo_spawn'] = now

def spawn_poderes(state):
    """Gerencia spawn de poderes a cada múltiplo de 1250 pontos"""
    now = pygame.time.get_ticks()
    if state['score'] > 0 and state['score'] % 750 == 0 and now - state['tempo_ultimo_poder'] > 2000:
        tipo = random.choice(list(assets['poder'].keys()))
        rect = tentar_spawn(state['poder_list'], 20, 70, 120, 0, state['enemy_list'])
        if rect:
            state['poder_list'].append({'rect': rect, 'tipo': tipo, 'velocidade': 3})
            state['tempo_ultimo_poder'] = now

# Botões
play_button = pygame.Rect(150, 250, 200, 60)
rankings_button = pygame.Rect(150, 350, 200, 60)
howto_button = pygame.Rect(150, 450, 200, 60)  # Novo botão
back_button = pygame.Rect(20, 20, 100, 40)

# Tratamento de eventos
def handle_events(state, assets, fonts):
    """Captura e processa eventos de teclado e mouse para todas as telas"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        # Clique de mouse
        if event.type == pygame.MOUSEBUTTONUP:
            x, y = event.pos
            # Botões da tela inicial
            if state['estado'] == 'inicio':
                if play_button.collidepoint((x, y)):
                    reset_jogo(state, assets)
                    state['estado'] = 'jogo'
                elif rankings_button.collidepoint((x, y)):
                    state['estado'] = 'rankings'
                elif howto_button.collidepoint((x, y)):  # Novo caso
                    state['estado'] = 'como_jogar'
            
            # Botões de voltar
            elif state['estado'] in ['rankings', 'fim_jogo', 'como_jogar']:
                if back_button.collidepoint((x, y)):
                    state['estado'] = 'inicio'
        
        # Digitação no fim de jogo
        if state['estado'] == 'fim_jogo' and event.type == pygame.KEYDOWN and state['input_ativo']:
            if event.key == pygame.K_RETURN and state['digitar_nome'].strip():
                ranking.adicionar_pontuacao(state['digitar_nome'].strip(), state['score'])
                state['estado'] = 'inicio'
                state['digitar_nome'] = ''
            elif event.key == pygame.K_BACKSPACE:
                state['digitar_nome'] = state['digitar_nome'][:-1]
            elif len(state['digitar_nome']) < 10:
                state['digitar_nome'] += event.unicode
    return True

# Lógica de atualização
def update_game(state, assets):
    """Move inimigos, poderes, trata colisões e gerencia timers de status"""
    now = pygame.time.get_ticks()

    # Movimenta inimigos e poderes
    for e in state['enemy_list']:
        e['rect'].y += e['velocidade']
    for p in state['poder_list']:
        p['rect'].y += p['velocidade']

    # Atualiza score e configurações de spawn
    state['score'] = (now - state['start_ticks']) // 25
    spawn_inimigos(state)
    spawn_poderes(state)

    player_rect = pygame.Rect(state['player_x'], 720 - 120 - 30, 70, 120)
    player_mask = assets['player_mask']

    # Colisões com inimigos 
    if not state['invulneravel']:
        for e in state['enemy_list']:
            enemy_rect = e['rect']
            enemy_mask = assets['enemy_mask']
            
            # Calcula offset entre as máscaras
            offset_x = enemy_rect.x - player_rect.x
            offset_y = enemy_rect.y - player_rect.y
            
            # Verifica colisão pixel-perfect
            if player_mask.overlap(enemy_mask, (offset_x, offset_y)):
                if state['escudo_ativo']:
                    state['escudo_ativo'] = False
                else:
                    state['vidas'] -= 1
                    state['invulneravel'] = True
                    state['tempo_invulneravel_inicio'] = now
                state['enemy_list'].remove(e)
                break

    # Coleta de poderes
    for p in state['poder_list']:
        if player_rect.colliderect(p['rect']):
            tipo = p['tipo']
            # Aplica efeito do poder
            if tipo == 'escudo':
                state['escudo_ativo'] = True
                state['escudo_inicio'] = now
            elif tipo == 'vida_extra' and state['vidas'] < 5:
                state['vidas'] += 1
            elif tipo == 'carros_devagar':
                state['carros_devagar_ativo'] = True
                state['carros_devagar_inicio'] = now
            elif tipo == 'menos_carros':
                state['menos_carros_ativo'] = True
                state['menos_carros_inicio'] = now
            state['poder_list'].remove(p)
            break

    # Remove objetos fora da tela
    state['enemy_list'] = [e for e in state['enemy_list'] if e['rect'].y < 720]
    state['poder_list'] = [p for p in state['poder_list'] if p['rect'].y < 720]

    # Reseta invulnerabilidade
    if state['invulneravel'] and now - state['tempo_invulneravel_inicio'] > 2000:
        state['invulneravel'] = False

    # Expiração de poderes
    if state['escudo_ativo'] and now - state['escudo_inicio'] > 5000:
        state['escudo_ativo'] = False
    if state['carros_devagar_ativo'] and now - state['carros_devagar_inicio'] > 10000:
        state['carros_devagar_ativo'] = False
    if state['menos_carros_ativo'] and now - state['menos_carros_inicio'] > 10000:
        state['menos_carros_ativo'] = False

    # Transição para fim de jogo
    if state['vidas'] <= 0:
        state['estado'] = 'fim_jogo'

# Funções de renderização
def render_inicio(window, assets, fonts):
    """Desenha a tela inicial com botões"""
    window.blit(assets['fundo_inicio'], (0, 0))
    
    # Título do jogo
    titulo1 = fonts['large'].render('SMASH', True, (255, 255, 255))
    titulo2 = fonts['large'].render('INSPER', True, (255, 255, 255))
    window.blit(titulo1, (180, 120))
    window.blit(titulo2, (180, 160))
    
    # Botões imagem
    pygame.draw.rect(window, (200, 200, 200), play_button)
    pygame.draw.rect(window, (200, 200, 200), rankings_button)
    pygame.draw.rect(window, (200, 200, 200), howto_button)  # Novo botão
    
    # Texto dos botões
    texto_jogar = fonts['large'].render('Jogar', True, (0, 0, 0))
    texto_rankings = fonts['large'].render('Rankings', True, (0, 0, 0))
    texto_howto = fonts['large'].render('Instruções', True, (0, 0, 0))
    window.blit(texto_jogar, (play_button.x + 50, play_button.y + 10))
    window.blit(texto_rankings, (rankings_button.x + 30, rankings_button.y + 10))
    window.blit(texto_howto, (howto_button.x + 20, howto_button.y + 10))

def render_jogo(window, assets, fonts, state):
    """Desenha a tela de jogo incluindo jogador, inimigos e HUD"""
    window.fill((0, 0, 0))
    
    # Desenha pistas
    for x in [500 // 3, 2 * 500 // 3]:
        for y in range(0, 720, 40):
            pygame.draw.line(window, (255, 255, 255), (x, y), (x, y + 20), 5)
    
    # Jogador
    if not (state['invulneravel'] and (pygame.time.get_ticks() // 200) % 2 == 0):
        window.blit(assets['player'], (state['player_x'], 720 - 120 - 30))
    
    # Escudo visual
    if state['escudo_ativo']:
        pygame.draw.rect(window, (0, 150, 255), 
                       (state['player_x'] - 5, 720 - 120 - 35, 80, 130), 3)
    
    # Inimigos
    for e in state['enemy_list']:
        window.blit(assets['enemy'], (e['rect'].x, e['rect'].y))
    
    # Poderes
    for p in state['poder_list']:
        window.blit(assets['poder'][p['tipo']], (p['rect'].x, p['rect'].y))
    
    # HUD - Vidas
    for i in range(state['vidas']):
        window.blit(assets['coracao'], (10 + i * 35, 10))
    
    # Pontuação
    texto_score = fonts['medium'].render(f"Pontuação: {state['score']}", True, (255, 255, 255))
    window.blit(texto_score, (500 - 200, 10))
    
    # Estrelas de progresso
    estrelas = min(state['score'] // 1000, 5)
    for i in range(estrelas):
        window.blit(assets['estrela'], (500 - (i + 1) * 35, 40))

def render_rankings(window, fonts):
    """Desenha a tela de rankings com top 10"""
    window.blit(assets['fundo_inicio'], (0, 0))
    
    # Título
    titulo = fonts['large'].render('Top 10 Rankings', True, (255, 255, 255))
    window.blit(titulo, (150, 50))
    
    # Carrega dados
    dados = ranking.carregar_rankings()
    y = 120
    for i, entry in enumerate(dados):
        texto = f"{i+1}. {entry['nome']}: {entry['pontuacao']}"
        window.blit(fonts['medium'].render(texto, True, (255, 255, 255)), (100, y))
        y += 40
    
    # Botão voltar
    pygame.draw.rect(window, (200, 200, 200), back_button)
    window.blit(fonts['medium'].render('Voltar', True, (0, 0, 0)), (back_button.x + 10, back_button.y + 5))

def render_howto(window, assets, fonts):
    """Desenha a tela de instruções do jogo"""
    # Fundo igual ao inicial
    window.blit(assets['fundo_inicio'], (0, 0))
    
    # Overlay semi-transparente
    overlay = pygame.Surface((500, 720), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))  # Preto com 200/255 de opacidade
    window.blit(overlay, (0, 0))
    
    # Título
    titulo = fonts['large'].render('Como Jogar', True, (255, 255, 255))
    window.blit(titulo, (160, 50))
    
    # Textos explicativos
    textos = [
        'Objetivo:',
        'O jogo consiste em uma fuga policial',
        'Desvie dos carros da policia usando',
        'as setas direita/esquerda.',
        'Colete poderes para ajudar na fuga!',
        '',
        'Poderes:',
        'Coração - Vida extra',
        'Escudo - Bloqueia uma colisão',
        'Menos - Reduz quantidade de carros',
        'Caracol - Diminui velocidade inimiga'
    ]
    
    y = 120
    for linha in textos:
        if ':' in linha:
            cor = (255, 255, 0) if linha.endswith(':') else (255, 255, 255)
            texto = fonts['medium'].render(linha, True, cor)
        else:
            texto = fonts['medium'].render(linha, True, (255, 255, 255))
        window.blit(texto, (50, y))
        y += 40 if ':' in linha else 30
    
    # Botão voltar
    pygame.draw.rect(window, (200, 200, 200), back_button)
    window.blit(fonts['medium'].render('Voltar', True, (0, 0, 0)), (back_button.x + 10, back_button.y + 5))

def render_fim_jogo(window, assets, fonts, state):
    """Desenha a tela de fim de jogo e input de nome"""
    window.fill((0, 0, 0))
    
    # Mensagens principais
    window.blit(fonts['large'].render('Fim de jogo!', True, (200, 0, 0)), (130, 90))
    window.blit(fonts['medium'].render(f"Pontuação final: {state['score']}", True, (255, 255, 255)), (130, 140))
    
    # Input de nome
    window.blit(fonts['medium'].render('Digite seu nome:', True, (255, 255, 255)), (130, 200))
    pygame.draw.rect(window, (255, 255, 255), (90, 240, 300, 40), 2)
    window.blit(fonts['input'].render(state['digitar_nome'], True, (255, 255, 255)), (155, 245))
    
    # Rankings
    dados = ranking.carregar_rankings()
    y = 310
    for i, entry in enumerate(dados):
        texto = f"{i+1}. {entry['nome']}: {entry['pontuacao']}"
        window.blit(fonts['medium'].render(texto, True, (255, 255, 255)), (100, y))
        y += 40
    
    # Botão voltar
    pygame.draw.rect(window, (200, 200, 200), back_button)
    window.blit(fonts['medium'].render('Voltar', True, (0, 0, 0)), (back_button.x + 10, back_button.y + 5))

# Função principal
def main():
    # Inicialização geral
    window, fonts, som_colisao = init_pygame()
    global assets
    assets = load_assets()
    state = criar_state()
    clock = pygame.time.Clock()
    running = True

    # Loop principal
    while running:
        clock.tick(60)

        # Tratamento de eventos
        running = handle_events(state, assets, fonts)

        # Movimentação do jogador
        keys = pygame.key.get_pressed()
        if state['estado'] == 'jogo':
            if keys[pygame.K_LEFT] and state['player_x'] > 0:
                state['player_x'] -= 7
            if keys[pygame.K_RIGHT] and state['player_x'] < 500-70:
                state['player_x'] += 7

            # Atualiza lógica do jogo
            update_game(state, assets)

        # Renderização de cada tela
        if state['estado'] == 'inicio':
            render_inicio(window, assets, fonts)
        elif state['estado'] == 'jogo':
            render_jogo(window, assets, fonts, state)
        elif state['estado'] == 'rankings':
            render_rankings(window, fonts)
        elif state['estado'] == 'como_jogar':  # Nova tela
            render_howto(window, assets, fonts)
        elif state['estado'] == 'fim_jogo':
            render_fim_jogo(window, assets, fonts, state)

        pygame.display.update()

    pygame.quit()
    
if __name__ == '__main__':
    main()
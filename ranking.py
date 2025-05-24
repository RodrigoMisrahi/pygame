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

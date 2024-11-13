import json
from config import QUEST_DATA_FILE
from party_manager import get_party_info, is_in_party

active_quest = None  # Armazena a quest atualmente postada no grupo
ready_players = set()  # Armazena jogadores que estão prontos para a missão


# Carrega todas as quests do arquivo JSON
def load_quests():
    with open(QUEST_DATA_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data["quests"]


# Exibe a lista de quests disponíveis (com id e nome)
def get_quests_list():
    quests = load_quests()
    quest_list = "📜 Missões Disponíveis:\n"
    for quest in quests:
        quest_list += f"- {quest['id']}: {quest['name']}\n"
    return quest_list


# Retorna a quest com base no id
def get_quest_by_id(quest_id):
    quests = load_quests()
    for quest in quests:
        if quest["id"] == quest_id:
            return quest
    return None


# Marca a missão como ativa no grupo
def post_quest(quest_id, player_name):
    global active_quest, ready_players
    if active_quest:
        return "⚠️ Já existe uma missão ativa! Por favor, recuse a missão atual antes de propor outra."

    quest = get_quest_by_id(quest_id)
    if not quest:
        return "❌ ID de missão inválido."

    active_quest = quest
    ready_players.clear()  # Limpa a lista de jogadores prontos

    # Formata e exibe a missão para o grupo
    quest_info = (
        f"🗣️ {player_name} propôs uma nova missão!\n"
        f"📜 Missão: {quest['name']}\n"
        f"🧙 Pedido por: {quest['requested_by']['name']} - {quest['requested_by']['profession']}\n"
        f"💬 Descrição: {quest['description']}\n\n"
        f"Use /pronto para aceitar a missão ou /recusar para recusá-la."
    )
    return quest_info


# Marca o jogador como "pronto" para a missão
def player_ready(player_id, party_size):
    global ready_players
    if not active_quest:
        return "⚠️ Não há uma missão ativa no momento."

    ready_players.add(player_id)
    if len(ready_players) == party_size:
        return f"🎉 Todos os jogadores estão prontos! A missão '{active_quest['name']}' começará agora!"
    else:
        return f"📢 Jogador pronto! ({len(ready_players)}/{party_size} prontos para a missão)"


# Marca o jogador como "recusou" a missão
def player_decline():
    global active_quest, ready_players
    if not active_quest:
        return "⚠️ Não há uma missão ativa no momento."

    # Reseta o estado da missão para permitir que outra seja proposta
    active_quest = None
    ready_players.clear()
    return "🚫 Missão recusada. Vocês podem propor uma nova missão."

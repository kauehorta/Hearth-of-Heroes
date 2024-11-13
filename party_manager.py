from character_manager import Character
from config import MAX_PARTY_SIZE

parties = {}  # Stores active parties by chat_id


def create_party(chat_id, creator_id):
    if chat_id in parties:
        return None  # Party already exists
    parties[chat_id] = {
        "members": [creator_id],
        "creator": creator_id
    }
    return parties[chat_id]


def join_party(chat_id, user_id):
    party = parties.get(chat_id)
    if party and len(party["members"]) < MAX_PARTY_SIZE:
        if user_id not in party["members"]:
            party["members"].append(user_id)
            return True
    return False


def leave_party(chat_id, user_id):
    """Allows a user to leave the party."""
    party = parties.get(chat_id)
    if party and user_id in party["members"]:
        party["members"].remove(user_id)
        if len(party["members"]) == 0:
            del parties[chat_id]  # Delete party if empty
        return True
    return False


def is_in_party(chat_id, user_id):
    party = parties.get(chat_id)
    return party and user_id in party["members"]


def get_party_info(chat_id):
    """Returns a list of character names in the party and number of slots filled."""
    party = parties.get(chat_id)
    if not party:
        return "No party found in this chat."

    member_ids = party["members"]
    characters = [Character.load(user_id) for user_id in member_ids if Character.load(user_id)]
    character_names = [char.name for char in characters]
    slots_filled = len(character_names)

    info = f"Party Members ({slots_filled}/{MAX_PARTY_SIZE} slots filled):\n"
    for name in character_names:
        info += f" - {name}\n"
    return info

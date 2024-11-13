import json
import os
from config import CHARACTER_DATA_FILE, DEFAULT_HP, DEFAULT_GOLD

class Character:
    def __init__(self, user_id, name):
        self.user_id = str(user_id)  # Ensure user_id is consistently a string
        self.name = name
        self.level = 1
        self.experience = 0
        self.gold = DEFAULT_GOLD
        self.current_hp = DEFAULT_HP
        self.max_hp = DEFAULT_HP
        self.power_base = 5
        self.grace_base = 5
        self.knowledge_base = 5
        self.actions = ["attack", "defend", "heal"]

    def save(self):
        """Save character data to a JSON file."""
        all_characters = load_all_characters()
        all_characters[self.user_id] = self.__dict__
        with open(CHARACTER_DATA_FILE, 'w') as file:
            json.dump(all_characters, file, indent=4)
        print(f"Character {self.name} (ID: {self.user_id}) saved successfully.")

    @classmethod
    def load(cls, user_id):
        """Load a character from the JSON file if it exists."""
        all_characters = load_all_characters()
        user_id = str(user_id)  # Ensure user_id is treated as a string consistently
        if user_id in all_characters:
            data = all_characters[user_id]
            character = cls(user_id, data["name"])
            character.__dict__.update(data)
            print(f"Character {character.name} (ID: {character.user_id}) loaded successfully.")
            return character
        print(f"No character found for user ID {user_id}.")
        return None

    def get_info(self):
        """Returns a formatted string with all character details."""
        return (
            f"Character Info:\n"
            f"Name: {self.name}\n"
            f"Level: {self.level}\n"
            f"Experience: {self.experience}\n"
            f"Gold: {self.gold}\n"
            f"HP: {self.current_hp}/{self.max_hp}\n"
            f"Power: {self.power_base}\n"
            f"Grace: {self.grace_base}\n"
            f"Knowledge: {self.knowledge_base}\n"
            f"Actions: {', '.join(self.actions)}"
        )

def load_all_characters():
    """Load all character data from the JSON file, returning an empty dictionary if the file is empty or malformed."""
    if os.path.exists(CHARACTER_DATA_FILE):
        try:
            with open(CHARACTER_DATA_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Warning: character_data.json is empty or contains invalid JSON. Initializing with empty data.")
            return {}
    return {}

def create_character(user_id, name):
    """Creates a new character if one doesn't already exist for the user."""
    user_id = str(user_id)  # Ensure user_id is treated as a string
    if Character.load(user_id):
        print(f"Character for user ID {user_id} already exists.")
        return None
    new_character = Character(user_id, name)
    new_character.save()
    print(f"Character '{name}' created for user ID {user_id}.")
    return new_character

def delete_character(user_id):
    """Deletes a character if it exists for the user."""
    user_id = str(user_id)  # Ensure user_id is treated as a string
    all_characters = load_all_characters()
    if user_id in all_characters:
        del all_characters[user_id]
        with open(CHARACTER_DATA_FILE, 'w') as file:
            json.dump(all_characters, file, indent=4)
        print(f"Character for user ID {user_id} deleted.")
        return True
    print(f"No character found for user ID {user_id} to delete.")
    return False

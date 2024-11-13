# commands.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import character_manager

# Define constants for ConversationHandler stages
ASK_NAME = 1

# Main menu keyboard options
main_menu_keyboard = [
    ["Create Character", "Character Info"],
    ["Quests", "Store"]
]
main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)

# Display the main menu
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the RPG Game! Choose an option:",
        reply_markup=main_menu_markup
    )

# Initiate character creation
async def initiate_create_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if str(update.effective_user.id) in character_manager.character_data:
        await update.message.reply_text("You already have a character. Use 'Character Info' to view it.", reply_markup=main_menu_markup)
        return ConversationHandler.END
    await update.message.reply_text("Please enter a name for your character:")
    return ASK_NAME

# Handle the character name input
async def create_character_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.effective_user.id)
    character_name = update.message.text
    result = character_manager.create_character(user_id, character_name)
    await update.message.reply_text(result, reply_markup=main_menu_markup)
    return ConversationHandler.END

# View character info
async def character_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    character = character_manager.character_data.get(user_id)
    if not character:
        await update.message.reply_text(
            "No character found. Use 'Create Character' to make one.",
            reply_markup=main_menu_markup
        )
    else:
        info = (
            f"Name: {character['name']}\n"
            f"Level: {character['level']}\n"
            f"HP: {character['hp']}\n"
            f"EXP: {character['experience']}/{character['exp_threshold']}\n"
            f"Gold: {character['gold']}\n"
            f"Attack Level: {character['attack_level']}\n"
            f"Defense Level: {character['defense_level']}\n"
            f"Support Level: {character['support_level']}\n"
            f"Stat Points: {character['stat_points']}\n"
            f"Skills: {', '.join(character['skills']) if character['skills'] else 'None'}\n"
            f"Inventory: {', '.join(character['inventory']) if character['inventory'] else 'Empty'}"
        )
        await update.message.reply_text(info, reply_markup=main_menu_markup)

# Command for handling menu selections
async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Create Character":
        await initiate_create_character(update, context)
    elif text == "Character Info":
        await character_info(update, context)
    elif text == "Quests":
        await update.message.reply_text("Quests feature coming soon!", reply_markup=main_menu_markup)
    elif text == "Store":
        await update.message.reply_text("Store feature coming soon!", reply_markup=main_menu_markup)
    else:
        await update.message.reply_text("Unknown option. Please choose from the menu.", reply_markup=main_menu_markup)

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Here are the available commands:\n\n"
        "/menu - Show the main menu with options\n"
        "/create_character - Create a new character (only if you don't already have one)\n"
        "/character_info - View your character's stats and inventory\n"
        "/quests - View available quests (coming soon)\n"
        "/store - Access the item store (coming soon)\n"
        "/help - Show this help message with a list of available commands"
    )
    await update.message.reply_text(help_text, reply_markup=main_menu_markup)

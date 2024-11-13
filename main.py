import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from config import TELEGRAM_API_KEY
from character_manager import create_character, Character, delete_character
from party_manager import create_party, join_party, get_party_info, leave_party, is_in_party
from quest_manager import get_quests_list, post_quest, player_ready, player_decline

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
CHARACTER_NAME = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bem-vindo ao jogo de aventura! Use /criar para criar um grupo.")


async def criar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    party = create_party(chat_id, user_id)

    if party:
        await update.message.reply_text("Grupo criado! Use /entrar para entrar no grupo.")
        await entrar_grupo(chat_id, user_id, update, context)  # Automaticamente entra o criador no grupo
    else:
        await update.message.reply_text("Já existe um grupo neste chat.")


async def entrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    await entrar_grupo(chat_id, user_id, update, context)


async def entrar_grupo(chat_id, user_id, update, context):
    """Função auxiliar para adicionar um jogador ao grupo."""
    character = Character.load(user_id)

    if not character:
        await update.message.reply_text(
            "Você precisa de um personagem para entrar no grupo. Mande uma mensagem privada para mim com /criarpersonagem para criar um."
        )
    elif not join_party(chat_id, user_id):
        await update.message.reply_text("O grupo está cheio ou você já está nele.")
    else:
        await update.message.reply_text(f"{update.effective_user.first_name} entrou no grupo!")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎉 {character.name} se juntou à aventura!"
        )


async def sair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if leave_party(chat_id, user_id):
        await update.message.reply_text(f"{update.effective_user.first_name} saiu do grupo.")
    else:
        await update.message.reply_text("Você não está em um grupo.")


async def grupo_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    info = get_party_info(chat_id)
    await update.message.reply_text(info)


async def personagem_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    character = Character.load(user_id)

    if character:
        await update.message.reply_text(character.get_info())
    else:
        await update.message.reply_text(
            "Você ainda não tem um personagem. Mande uma mensagem privada para mim com /criarpersonagem para criar um.")


async def criar_personagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("Por favor, use este comando em um chat privado.")
        return ConversationHandler.END

    user_id = update.effective_user.id
    character = Character.load(user_id)

    if character:
        await update.message.reply_text("Você já tem um personagem. Use /personageminfo para checar as informações.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Qual nome você gostaria de dar ao seu personagem?")
        return CHARACTER_NAME


async def personagem_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    name = update.message.text.strip()

    if create_character(user_id, name):
        await update.message.reply_text(f"Personagem '{name}' criado! Agora você pode entrar em grupos nos chats.")
    else:
        await update.message.reply_text("Falha na criação do personagem. Tente novamente.")
    return ConversationHandler.END


async def deletar_personagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("Por favor, use este comando em um chat privado.")
        return

    user_id = update.effective_user.id
    if is_in_party(update.effective_chat.id, user_id):
        await update.message.reply_text("Você não pode deletar um personagem enquanto estiver em um grupo.")
    elif delete_character(user_id):
        await update.message.reply_text("Seu personagem foi deletado.")
    else:
        await update.message.reply_text("Você não tem um personagem para deletar.")


# Funções relacionadas a missões
async def missoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Verifica se o jogador está em um grupo
    if not is_in_party(chat_id, user_id):
        await update.message.reply_text("Você precisa estar em um grupo para ver as missões disponíveis.")
        return

    quest_list = get_quests_list()
    await update.message.reply_text(quest_list)


async def missao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    player_name = update.effective_user.first_name

    # Verifica se o jogador está em um grupo
    if not is_in_party(chat_id, user_id):
        await update.message.reply_text("Você precisa estar em um grupo para postar uma missão.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Por favor, forneça o ID da missão. Exemplo: /missao 1")
        return

    try:
        quest_id = int(context.args[0])
        quest_info = post_quest(quest_id, player_name)
        await update.message.reply_text(quest_info)
    except ValueError:
        await update.message.reply_text("ID de missão inválido. Use um número válido.")


async def pronto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    party_size = len(get_party_info(chat_id).splitlines()) - 1  # Número de jogadores na party

    if is_in_party(chat_id, user_id):
        status = player_ready(user_id, party_size)
        await update.message.reply_text(status)
    else:
        await update.message.reply_text("Você não está em um grupo.")


async def recusar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = player_decline()
    await update.message.reply_text(response)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📝 *Comandos Disponíveis:*\n\n"
        "🎲 *Gerenciamento de Grupo*\n"
        "/criar - Cria um novo grupo no chat atual.\n"
        "/entrar - Entra no grupo existente, caso você já tenha um personagem.\n"
        "/sair - Sai do grupo atual.\n"
        "/grupoinfo - Exibe informações sobre os membros do grupo.\n\n"

        "👤 *Comandos de Personagem*\n"
        "/criarpersonagem - Cria um novo personagem (somente em chat privado).\n"
        "/personageminfo - Exibe todas as informações do seu personagem.\n"
        "/deletarpersonagem - Deleta seu personagem (somente em chat privado).\n\n"

        "🏆 *Comandos de Missões*\n"
        "/missoes - Exibe a lista de missões disponíveis (necessário estar em um grupo).\n"
        "/missao <id> - Posta a missão especificada pelo ID (necessário estar em um grupo).\n"
        "/pronto - Marca você como pronto para iniciar a missão.\n"
        "/recusar - Recusa a missão atual.\n\n"

        "ℹ️ *Comandos de Ajuda*\n"
        "/help - Exibe esta lista de comandos.\n"
    )

    # Enviar a mensagem de ajuda como uma mensagem privada
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=help_text,
        parse_mode='Markdown'
    )

    # Notificar o usuário no grupo para checar a mensagem privada, se o comando for usado em um grupo
    if update.effective_chat.type != "private":
        await update.message.reply_text("📬 Cheque suas mensagens privadas para ver a lista de comandos.")


def main():
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    # Comandos principais
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("criar", criar))
    application.add_handler(CommandHandler("entrar", entrar))
    application.add_handler(CommandHandler("sair", sair))
    application.add_handler(CommandHandler("grupoinfo", grupo_info))
    application.add_handler(CommandHandler("personageminfo", personagem_info))
    application.add_handler(CommandHandler("help", help))

    # Comandos de missões
    application.add_handler(CommandHandler("missoes", missoes))
    application.add_handler(CommandHandler("missao", missao))
    application.add_handler(CommandHandler("pronto", pronto))
    application.add_handler(CommandHandler("recusar", recusar))

    # Criação de personagem em privado
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("criarpersonagem", criar_personagem, filters=filters.ChatType.PRIVATE)],
        states={
            CHARACTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, personagem_nome)]
        },
        fallbacks=[CommandHandler("cancelar",
                                  lambda update, context: update.message.reply_text(
                                      "Criação de personagem cancelada."))],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("deletarpersonagem", deletar_personagem, filters=filters.ChatType.PRIVATE))

    application.run_polling()


if __name__ == "__main__":
    main()

from telegram import Update
from telegram.ext import CallbackContext
from services.fortune_service import get_fortune

CATEGORIES = ["деньги", "удача", "отношения", "здоровье"]

async def fortune(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text(
            "🔮 *Введите категорию предсказания:*\n"
            "`/fortune деньги`  `/fortune удача`  `/fortune отношения`  `/fortune здоровье`",
            parse_mode="Markdown"
        )
        return

    category = context.args[0].lower()

    if category not in CATEGORIES:
        await update.message.reply_text(
            "⚠️ Неверная категория! Выберите одну из:\n"
            "`деньги`, `удача`, `отношения`, `здоровье`",
            parse_mode="Markdown"
        )
        return

    fortune_text = get_fortune(category)
    await update.message.reply_text(fortune_text, parse_mode="Markdown")

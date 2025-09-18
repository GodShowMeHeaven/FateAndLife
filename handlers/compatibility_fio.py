from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown  # Правильный импорт
from services.numerology_service import calculate_life_path_number
from utils.validation import validate_date
import logging

logger = logging.getLogger(__name__)

async def compatibility_fio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat в update")
        return
    if not context.args or len(context.args) < 6:
        await update.message.reply_text(
            escape_markdown("⚠️ Укажите данные: имя1 фамилия1 дата1 имя2 фамилия2 дата2", version=2),
            parse_mode="MarkdownV2"
        )
        return

    try:
        name1, surname1, birth_date1, name2, surname2, birth_date2 = context.args[:6]
        if not validate_date(birth_date1) or not validate_date(birth_date2):
            await update.message.reply_text(
                escape_markdown("⚠️ Неверный формат даты рождения! Используйте ДД.ММ.ГГГГ (например, 12.05.1990).", version=2),
                parse_mode="MarkdownV2"
            )
            return

        life_path1 = calculate_life_path_number(birth_date1)
        life_path2 = calculate_life_path_number(birth_date2)
        compatibility_score = abs(life_path1 - life_path2) % 100

        result = (
            f"Совместимость между {name1} {surname1} и {name2} {surname2}:\n"
            f"Число жизненного пути {name1}: {life_path1}\n"
            f"Число жизненного пути {name2}: {life_path2}\n"
            f"Процент совместимости: {compatibility_score}%"
        )
        await update.message.reply_text(escape_markdown(result, version=2), parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка расчета совместимости по ФИО: {e}")
        await update.message.reply_text(
            escape_markdown("⚠️ Ошибка при расчете совместимости. Попробуйте позже.", version=2),
            parse_mode="MarkdownV2"
        )
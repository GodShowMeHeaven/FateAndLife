from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown  # Правильный импорт
from services.user_profile import save_user_profile, get_user_profile
from utils.validation import validate_date, validate_time
from keyboards.main_menu import main_menu_keyboard
import logging

logger = logging.getLogger(__name__)

async def set_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat в update")
        return
    if not context.args or len(context.args) < 4:
        await update.message.reply_text(
            escape_markdown("⚠️ Укажите данные: имя дата_рождения время_рождения место_рождения", version=2),
            parse_mode="MarkdownV2"
        )
        return

    name, birth_date, birth_time, birth_place = context.args[:4]
    if not validate_date(birth_date) or not validate_time(birth_time):
        await update.message.reply_text(
            escape_markdown("⚠️ Неверный формат даты (ДД.ММ.ГГГГ) или времени (ЧЧ:ММ).", version=2),
            parse_mode="MarkdownV2"
        )
        return

    try:
        await save_user_profile(update.effective_chat.id, name, birth_date, birth_time, birth_place)
        await update.message.reply_text(
            escape_markdown(f"✅ Профиль сохранен: {name}, {birth_date}, {birth_time}, {birth_place}", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка сохранения профиля: {e}")
        await update.message.reply_text(
            escape_markdown("⚠️ Ошибка при сохранении профиля. Попробуйте позже.", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )

async def get_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat в update")
        return
    try:
        profile = await get_user_profile(update.effective_chat.id)
        if profile:
            name, birth_date, birth_time, birth_place = profile
            await update.message.reply_text(
                escape_markdown(f"📋 Ваш профиль:\nИмя: {name}\nДата рождения: {birth_date}\nВремя рождения: {birth_time}\nМесто рождения: {birth_place}", version=2),
                parse_mode="MarkdownV2",
                reply_markup=main_menu_keyboard
            )
        else:
            await update.message.reply_text(
                escape_markdown("⚠️ Профиль не найден. Установите профиль с помощью /set_profile", version=2),
                parse_mode="MarkdownV2",
                reply_markup=main_menu_keyboard
            )
    except Exception as e:
        logger.error(f"Ошибка получения профиля: {e}")
        await update.message.reply_text(
            escape_markdown("⚠️ Ошибка при получении профиля. Попробуйте позже.", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
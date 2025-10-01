import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler,
    ConversationHandler
)

# Установите уровень логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# --- КОНФИГУРАЦИЯ ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
CREATOR_USERNAME = os.environ.get("CREATOR_USERNAME", "@MrCrabYT")

# --- СОСТОЯНИЯ ДИАЛОГА (для ConversationHandler) ---
CHOOSE_ROLE, MESSAGE_WAITING = range(2) 

# --- ШАБЛОНЫ ЗАЯВОК ---

# Шаблон заявки для YouTube
YOUTUBE_TEMPLATE = """
**ЗАЯВКА НА ДОЛЖНОСТЬ YOUTUBE**
Заполните анкету и ответьте на все вопросы, скопируйте и отправьте ее боту:

1) Имя:
2) Ваш возраст: 
3) Ваш игровой ник:
4) Количество отыгранных часов на сервере:
5) Ваш Дискорд:
6) Кол-во подписчиков:
7) Сколько часов в день Вы готовы уделять нашему проекту?
8) Расскажите про свой канал, как Вы его ведете? 
9) Ссылка на Ваш канал:
10) Оценка Ваших видео (качество видео) от 1 до 10:
"""

# Шаблон заявки для TikTok (ОБНОВЛЕН)
TIKTOK_TEMPLATE = """
**ЗАЯВКА НА ДОЛЖНОСТЬ TIKTOK**
Заполните анкету и ответьте на все вопросы, скопируйте и отправьте ее боту:

1) Имя:
2) Ваш возраст: 
3) Ваш игровой ник:
4) Количество отыгранных часов на сервере:
5) Ваш Дискорд:
6) Кол-во подписчиков:
7) Сколько часов в день готовы уделять нашему проекту?
8) Как Вы видите себя на посту? 
9) Расскажите о своем канале:
"""

# Шаблон заявки для Helper (ОБНОВЛЕН)
HELPER_TEMPLATE = """
**ЗАЯВКА НА ДОЛЖНОСТЬ HELPER**
Заполните анкету и ответьте на все вопросы, скопируйте и отправьте ее боту:

1) Имя:
2) Ваш возраст:
3) Ваш игровой ник:
4) Количество отыгранных часов на сервере:
5) Ваш Дискорд:
6) Есть ли у Вас опыт работы? Если да, то какой, на каком сервере?:
7) Сколько часов в день готовы уделять нашему проекту?:
8) Почему вы хотите занять этот пост? (Постарайтесь дать как можно более подробный ответ):
9) Напишите о себе:
10) Как вы понимаете понятия слов: Адекватность, рассудок?:
"""

# --- КЛАВИАТУРЫ И КОНСТАНТЫ (Остаются без изменений) ---

# 1. Словарь привилегий (инлайн-кнопки)
PRIVILEGES = {
    "start_buy": "START - 15 UAH",
    "top_buy": "TOP - 30 UAH",
    "lord_buy": "LORD - 45 UAH",
    "giperlord_buy": "GIPERLORD - 75 UAH",
    "master_buy": "MASTER - 95 UAH",
    "legend_buy": "LEGEND - 110 UAH",
    "wirher_buy": "WIRHER - 150 UAH",
}

# 2. Кнопки главного меню (вертикальный вид)
MAIN_MENU_BUTTONS = [
    ["💲 Приобрести привилегию"],
    ["💡 Написать идею"],
    ["✨ Подать заявку"],
    ["📝 Написать жалобу"],
]
MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True, one_time_keyboard=False)

# 3. Кнопки для выбора роли в заявке
APPLICATION_ROLE_BUTTONS = [
    ["YouTube"],
    ["Helper"],
    ["TikTok"],
    ["Отмена"], # Кнопка для выхода из диалога
]
APPLICATION_ROLE_KEYBOARD = ReplyKeyboardMarkup(APPLICATION_ROLE_BUTTONS, resize_keyboard=True, one_time_keyboard=True)


# --- ФУНКЦИИ БОТА (Логика обработки не изменена) ---

# 1. Точка входа и команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Приветствует пользователя и показывает главное меню, завершая любой активный диалог."""
    await update.message.reply_text(
        "Добро пожаловать в чат-бот Minecraft-сервера CrabMine!\nВыберите нужный пункт меню ниже:",
        reply_markup=MAIN_MENU_KEYBOARD,
    )
    return ConversationHandler.END 

# 2. Обработчик нажатия кнопки "Приобрести привилегию"
async def show_privilege_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показывает инлайн-кнопки привилегий и сообщение о покупке."""
    keyboard = []
    for callback_data, text in PRIVILEGES.items():
        keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Выберите привилегию из списка:",
        reply_markup=reply_markup
    )
    return ConversationHandler.END 

# 3. Обработчик нажатия инлайн-кнопок привилегий
async def handle_privilege_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатия на инлайн-кнопки привилегий."""
    query = update.callback_query
    await query.answer() 
    
    callback_data = query.data
    
    if callback_data in PRIVILEGES:
        privilege_name = PRIVILEGES[callback_data]
        
        response_message = (
            f"Вы выбрали: **{privilege_name}**.\n\n"
            f"**За покупкой напишите создателю в ЛС: {CREATOR_USERNAME}**"
        )
        
        # Редактируем сообщение, чтобы убрать инлайн-кнопки
        await query.edit_message_text(
            response_message, 
            parse_mode='Markdown',
            reply_markup=None # Убираем кнопки после выбора
        )

# 4. Начало диалога для "Идея" или "Жалоба"
async def start_message_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запускает диалог с запросом текста идеи или жалобы."""
    text = update.message.text
    context.user_data['message_type'] = text
    
    if text == "Написать идею":
        prompt = "💡 **Отлично!** Опишите Вашу идею, которую Вы хотите видеть на сервере:"
    elif text == "Написать жалобу":
        prompt = "🚨 **Жалоба.** Пожалуйста, опишите Вашу жалобу максимально подробно и прикрипите к ней скриншоты доказательств (если имеются):"
    
    await update.message.reply_text(
        prompt,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove() # Скрываем главное меню
    )
    
    return MESSAGE_WAITING # Переходим в состояние ожидания текста

# 5. Начало диалога для "Заявка" (выбор роли)
async def start_application_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запускает диалог выбора роли для заявки."""
    await update.message.reply_text(
        "Кем Вы хотите стать на нашем сервере?",
        reply_markup=APPLICATION_ROLE_KEYBOARD
    )
    return CHOOSE_ROLE # Переходим в состояние выбора роли

# 6. Выбор роли в заявке (использует обновленные шаблоны)
async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор роли пользователем, показывает шаблон и переходит в режим ожидания текста."""
    role = update.message.text
    
    if role == "Отмена":
        return await cancel(update, context)

    # Выбираем нужный шаблон
    if role == "YouTube":
        template = YOUTUBE_TEMPLATE
    elif role == "TikTok":
        template = TIKTOK_TEMPLATE
    elif role == "Helper":
        template = HELPER_TEMPLATE
    else:
        # Этого не должно случиться, но на всякий случай
        return await cancel(update, context) 

    # Сохраняем тип сообщения для отправки админу
    context.user_data['message_type'] = f"Заявка на должность: {role}"
    
    # Отправляем шаблон пользователю
    await update.message.reply_text(
        f"Вы выбрали: **{role}**.\n\n"
        f"**ВНИМАНИЕ!** Чтобы подать заявку, Вам нужно:\n"
        f"1. **СКОПИРОВАТЬ** шаблон ниже.\n"
        f"2. Заполнить его.\n"
        f"3. **ОТПРАВИТЬ** заполненный текст боту.\n\n"
        f"--- ШАБЛОН ---\n\n"
        f"{template}",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    
    return MESSAGE_WAITING # Переходим в состояние ожидания текста заявки

# 7. Финальная отправка сообщения (идея, жалоба, детали заявки)
async def send_message_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пересылает сообщение пользователя администратору."""
    
    message_type = context.user_data.get('message_type', 'Сообщение')
    user_id = update.effective_user.id
    username = update.effective_user.username
    full_name = update.effective_user.full_name
    message_text = update.message.text
    
    # Формируем сообщение для администратора
    admin_message = (
        f"***НОВОЕ {message_type.upper()}***\n\n"
        f"**От:** {full_name} (@{username if username else 'Нет юзернейма'})\n"
        f"**ID Пользователя:** `{user_id}`\n"
        f"**Тип:** {message_type}\n\n"
        f"**Текст:**\n{message_text}"
    )
    
    try:
        # Отправляем сообщение администратору
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode='Markdown'
        )
        
        # Уведомляем пользователя
        await update.message.reply_text(
            f"✅ Ваше сообщение ('{message_type}') успешно отправлено администрации. Спасибо!",
            reply_markup=MAIN_MENU_KEYBOARD
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения администратору: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при отправке сообщения.",
            reply_markup=MAIN_MENU_KEYBOARD
        )
        
    # Очищаем данные и завершаем диалог
    context.user_data.clear()
    return ConversationHandler.END

# 8. Отмена диалога
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Прерывает текущий диалог, если нажата кнопка 'Отмена' или команда /cancel."""
    await update.message.reply_text(
        'Действие отменено. Вы вернулись в главное меню.',
        reply_markup=MAIN_MENU_KEYBOARD
    )
    context.user_data.clear()
    return ConversationHandler.END

# 9. Обработчик неизвестных команд в состоянии ожидания текста
async def unknown_in_message_waiting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отвечает, если в состоянии ожидания текста приходит команда, отличная от /cancel."""
    message_type = context.user_data.get('message_type', 'сообщения')
    await update.message.reply_text(
        f"Пожалуйста, введите **текст** Вашего {message_type.lower()} или нажмите /cancel для отмены.",
        parse_mode='Markdown'
    )
    # Остаемся в текущем состоянии, чтобы пользователь мог ввести текст
    return MESSAGE_WAITING 

# 10. Обработчик всех сообщений, которые не были обработаны (защита от мусора)
async def fallback_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ответ на случайный текст или неизвестные команды вне диалога."""
    # Обрабатываем только если нет текущего диалога (для чистоты)
    if not context.user_data.get('message_type') or context.current_state == ConversationHandler.END: 
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки главного меню, чтобы начать взаимодействие.",
            reply_markup=MAIN_MENU_KEYBOARD
        )

# --- ЗАПУСК БОТА ---
def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(TOKEN).build()

    # ConversationHandler для Идей, Жалоб и Заявок (многошаговые запросы)
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Написать идею$"), start_message_dialog),
            MessageHandler(filters.Regex("^Написать жалобу$"), start_message_dialog),
            MessageHandler(filters.Regex("^Подать заявку$"), start_application_dialog),
        ],
        states={
            CHOOSE_ROLE: [
                # Принимаем только кнопки ролей (YouTube, Helper, TikTok, Отмена)
                MessageHandler(filters.Regex("^(YouTube|Helper|TikTok|Отмена)$"), choose_role),
                # Любой другой текст, кроме команд, не пропускаем
                MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u,c: u.message.reply_text("Пожалуйста, выберите одну из ролей или 'Отмена'.")),
            ],
            MESSAGE_WAITING: [
                # Принимаем только обычный текст для отправки
                MessageHandler(filters.TEXT & ~filters.COMMAND, send_message_to_admin),
                # Отлавливаем любые команды, кроме /cancel, и остаемся в состоянии
                MessageHandler(filters.COMMAND & ~filters.Regex("^/cancel$"), unknown_in_message_waiting),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', start_command) # Сбрасывает диалог при команде /start
        ],
        allow_reentry=True
    )
    
    # 1. Основные команды и обработчики, работающие вне диалога
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.Regex("^Приобрести привилегию$"), show_privilege_menu))
    application.add_handler(CallbackQueryHandler(handle_privilege_callback, pattern=r'.*_buy'))
    
    # 2. Добавляем ConversationHandler
    application.add_handler(conv_handler)

    # 3. Запасная сеть: обрабатывает ЛЮБОЙ текст или команду, если все предыдущие обработчики его пропустили.
    application.add_handler(MessageHandler(filters.ALL, fallback_message))
    
    print("Бот успешно запущен и работает...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
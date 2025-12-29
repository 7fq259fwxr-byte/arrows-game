#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Bot for Arrows Pro Ultra Game
Author: Your Name
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from telegram.constants import ParseMode

# ====================== КОНФИГУРАЦИЯ ======================
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
GAME_URL = "https://7fq259fwxr-byte.github.io/arrows-game/"  # Измените на ваш реальный URL
SUPPORT_BOT = "@arrow_game_support_bot"  # Бот поддержки

# ====================== ЛОГИРОВАНИЕ ======================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ====================== ТЕКСТЫ СООБЩЕНИЙ ======================
WELCOME_MESSAGE = f"""
🎮 *Добро пожаловать в Arrows Pro Ultra!* 

*ИГРА В СТРЕЛОЧКИ* - увлекательная головоломка, где нужно убирать стрелки с поля, не допуская их столкновений.

🌟 *ОСОБЕННОСТИ:*
• 100+ уровней с растущей сложностью
• Динамическое увеличение игрового поля
• Система жизней и восстановления
• Эффекты победы с конфетти
• Поддержка русского, английского и китайского языков
• Работает офлайн после загрузки

📱 *КАК ЗАПУСТИТЬ НА iOS:*
1. Нажмите кнопку "🎮 НАЧАТЬ ИГРУ" ниже
2. В открывшемся окне нажмите ⋯ (в правом верхнем углу)
3. Выберите "На экран 'Домой'"
4. Нажмите "Добавить"

🔄 *УПРАВЛЕНИЕ:*
• Нажимайте на стрелки, чтобы убрать их
• Избегайте столкновений стрелок
• Проходите уровни и открывайте новые!

⚡ *Игра сохраняет прогресс автоматически!*

🆘 *Помощь и поддержка:* {SUPPORT_BOT}
"""

HELP_MESSAGE = f"""
📚 *КОМАНДЫ БОТА:*
/start - Запустить бота и показать меню
/game - Открыть игру напрямую
/help - Показать эту справку
/stats - Статистика игры
/about - Информация об игре
/support - Связаться с поддержкой

❓ *ЧАСТЫЕ ВОПРОСЫ:*

*Q: Игра не открывается на iPhone?*
A: Используйте Safari браузер и добавьте на домашний экран.

*Q: Прогресс не сохраняется?*
A: Игра использует localStorage браузера. Не очищайте данные сайта.

*Q: Как играть?*
A: Нажимайте на стрелки в правильном порядке, чтобы избежать столкновений.

*Q: Нашел баг или есть предложение?*
A: Напишите в поддержку: {SUPPORT_BOT}

🆘 *Техническая поддержка:* {SUPPORT_BOT}
"""

STATS_MESSAGE = f"""
📊 *СТАТИСТИКА ARROWS PRO ULTRA:*

• Уровни сложности: 100+
• Максимальный размер поля: 9x9
• Поддерживаемые языки: 3
• Система жизней: 3 + восстановление
• Эффекты: 15+ анимаций

🎯 *ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ:*
• Платформа: Web (PWA)
• Размер: ~50KB
• Совместимость: iOS 12+, Android 8+
• Офлайн-режим: Да

🔄 *ПОСЛЕДНЕЕ ОБНОВЛЕНИЕ:*
• Исправлена генерация уровней
• Добавлены новые эффекты
• Улучшена производительность
• Исправлены ошибки на iOS

🌟 *Игра полностью бесплатна и без рекламы!*

🆘 *Поддержка:* {SUPPORT_BOT}
"""

# ====================== ОБРАБОТЧИКИ КОМАНД ======================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    # Создаем клавиатуру с Web App кнопкой
    keyboard = [
        [InlineKeyboardButton(
            text="🎮 НАЧАТЬ ИГРУ",
            web_app=WebAppInfo(url=GAME_URL)
        )],
        [
            InlineKeyboardButton("📊 Статистика", callback_data='stats'),
            InlineKeyboardButton("❓ Помощь", callback_data='help')
        ],
        [
            InlineKeyboardButton("🆘 Поддержка", url=f"https://t.me/{SUPPORT_BOT[1:]}"),
            InlineKeyboardButton("⭐ Оценить", callback_data='rate')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем приветственное сообщение
    await update.message.reply_text(
        text=f"Привет, {user.first_name}! 👋\n\n{WELCOME_MESSAGE}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def game_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /game - прямая ссылка на игру"""
    keyboard = [
        [InlineKeyboardButton("🚀 ЗАПУСТИТЬ ИГРУ", web_app=WebAppInfo(url=GAME_URL))],
        [InlineKeyboardButton("🆘 Поддержка", url=f"https://t.me/{SUPPORT_BOT[1:]}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Нажмите кнопку ниже, чтобы сразу начать игру:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    keyboard = [
        [InlineKeyboardButton("🆘 Написать в поддержку", url=f"https://t.me/{SUPPORT_BOT[1:]}")],
        [InlineKeyboardButton("🎮 Открыть игру", web_app=WebAppInfo(url=GAME_URL))]
    ]
    
    await update.message.reply_text(
        text=HELP_MESSAGE,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /stats"""
    keyboard = [
        [InlineKeyboardButton("🆘 Поддержка", url=f"https://t.me/{SUPPORT_BOT[1:]}")],
        [InlineKeyboardButton("🎮 Вернуться к игре", web_app=WebAppInfo(url=GAME_URL))]
    ]
    
    await update.message.reply_text(
        text=STATS_MESSAGE,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /about"""
    about_text = f"""
🎮 *Arrows Pro Ultra v19*

*РАЗРАБОТЧИК:* Ваше Имя
*ВЕРСИЯ:* 1.0.0
*ОБНОВЛЕНО:* 2024

*ТЕХНОЛОГИИ:*
• HTML5, CSS3, JavaScript
• PWA (Progressive Web App)
• GitHub Pages для хостинга

*ОСОБЕННОСТИ:*
• Адаптивный дизайн
• Кроссплатформенность
• Офлайн-режим
• Бесплатно навсегда

🆘 *Техническая поддержка:* {SUPPORT_BOT}
🔗 *GitHub:* github.com/ваш_логин

*Спасибо за игру!* ❤️
    """
    
    keyboard = [[InlineKeyboardButton("🆘 Связаться с поддержкой", url=f"https://t.me/{SUPPORT_BOT[1:]}")]]
    
    await update.message.reply_text(
        text=about_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /support - связь с поддержкой"""
    keyboard = [
        [InlineKeyboardButton("📨 Написать в поддержку", url=f"https://t.me/{SUPPORT_BOT[1:]}")],
        [InlineKeyboardButton("📋 Шаблон сообщения", callback_data='support_template')],
        [InlineKeyboardButton("🎮 Вернуться к игре", web_app=WebAppInfo(url=GAME_URL))]
    ]
    
    support_text = f"""
🆘 *ТЕХНИЧЕСКАЯ ПОДДЕРЖКА*

Для быстрого решения проблемы:
1. Нажмите кнопку ниже для связи
2. Опишите проблему подробно
3. Укажите ваше устройство и браузер
4. Приложите скриншот (если можно)

*ЧТО УКАЗАТЬ В СООБЩЕНИИ:*
• Описание проблемы
• Устройство (iPhone 12, Samsung S21 и т.д.)
• Браузер (Safari, Chrome)
• Версия ОС
• Что вы делали перед ошибкой

*ОТВЕТ:*
• Обычно в течение 24 часов
• Рабочие дни: Пн-Пт, 10:00-18:00

*БЫСТРАЯ СВЯЗЬ:* {SUPPORT_BOT}

*Можно использовать шаблон ниже:*
    """
    
    await update.message.reply_text(
        text=support_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

# ====================== ОБРАБОТЧИКИ КНОПОК ======================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на inline-кнопки"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    logger.info(f"User {user.id} pressed button: {query.data}")
    
    if query.data == 'stats':
        keyboard = [
            [InlineKeyboardButton("🎮 Вернуться к игре", web_app=WebAppInfo(url=GAME_URL))],
            [InlineKeyboardButton("🆘 Поддержка", url=f"https://t.me/{SUPPORT_BOT[1:]}")]
        ]
        await query.edit_message_text(
            text=STATS_MESSAGE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )
        
    elif query.data == 'help':
        keyboard = [
            [InlineKeyboardButton("🎮 Открыть игру", web_app=WebAppInfo(url=GAME_URL))],
            [InlineKeyboardButton("🆘 Поддержка", url=f"https://t.me/{SUPPORT_BOT[1:]}")]
        ]
        await query.edit_message_text(
            text=HELP_MESSAGE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )
        
    elif query.data == 'rate':
        keyboard = [
            [InlineKeyboardButton("🎮 Продолжить игру", web_app=WebAppInfo(url=GAME_URL))],
            [InlineKeyboardButton("📢 Поделиться", url="https://t.me/share/url?url=https://t.me/ArrowsProUltraBot&text=🎮 Попробуй крутую игру Arrows Pro Ultra!")],
            [InlineKeyboardButton("🆘 Сообщить о проблеме", url=f"https://t.me/{SUPPORT_BOT[1:]}")]
        ]
        await query.edit_message_text(
            text="⭐ *Оцените игру!*\n\n"
                 "Если вам нравится игра, поделитесь ей с друзьями!\n\n"
                 "*Ваша оценка помогает развитию игры!* ❤️\n\n"
                 "Нашли баг или есть предложение? Напишите в поддержку!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    elif query.data == 'support_template':
        template = f"""
*ШАБЛОН ДЛЯ ТЕХПОДДЕРЖКИ:*

*Проблема:* [Опишите проблему]
*Устройство:* [Например: iPhone 13]
*Браузер:* [Например: Safari]
*Версия ОС:* [Например: iOS 16.5]
*Действия перед ошибкой:* [Что вы делали]

*Дополнительно:*
• Скриншоты приложены: [Да/Нет]
• Уровень игры: [Номер уровня]
• Описание бага: [Подробно]

*Ожидаемое поведение:* [Как должно работать]

*Контакт для связи:* @{user.username if user.username else 'не указан'}

---
Отправьте это сообщение в поддержку: {SUPPORT_BOT}
        """
        
        keyboard = [
            [InlineKeyboardButton("📨 Отправить в поддержку", url=f"https://t.me/{SUPPORT_BOT[1:]}?text=Проблема с игрой Arrows Pro Ultra")],
            [InlineKeyboardButton("🎮 Вернуться к игре", web_app=WebAppInfo(url=GAME_URL))]
        ]
        
        await query.edit_message_text(
            text=template,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ====================== ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ======================

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    text = update.message.text.lower()
    user = update.effective_user
    
    # Ключевые слова для определения проблем
    error_keywords = [
        'ошибка', 'баг', 'не работает', 'сломалось', 'глюк', 'глючит',
        'проблема', 'не открывается', 'зависает', 'вылетает', 'crash',
        'error', 'bug', 'not working', 'broken', 'glitch', 'problem',
        'не могу', 'не получается', 'помогите', 'help', 'support'
    ]
    
    game_keywords = ['игра', 'game', 'arrows', 'стрелки', 'начать', 'start']
    thanks_keywords = ['спасибо', 'thanks', 'благодарю', 'круто', 'класс', 'супер']
    
    if any(word in text for word in error_keywords):
        # Пользователь сообщает о проблеме
        logger.warning(f"User {user.id} reported a problem: {text}")
        
        keyboard = [
            [InlineKeyboardButton("🆘 Написать в поддержку", url=f"https://t.me/{SUPPORT_BOT[1:]}")],
            [InlineKeyboardButton("📋 Шаблон для поддержки", callback_data='support_template')],
            [InlineKeyboardButton("🔄 Перезапустить игру", web_app=WebAppInfo(url=GAME_URL))]
        ]
        
        reply_text = f"""
⚠️ *Похоже, у вас возникла проблема с игрой!*

Для быстрого решения:
1. Напишите в поддержку: {SUPPORT_BOT}
2. Опишите проблему подробно
3. Укажите устройство и браузер

*Частые решения:*
• Очистите кэш браузера
• Перезагрузите страницу
• Обновите браузер
• Добавьте игру на домашний экран (iOS)

*Поддержка ответит в течение 24 часов!*
        """
        
        await update.message.reply_text(
            text=reply_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )
    
    elif any(word in text for word in game_keywords):
        keyboard = [[InlineKeyboardButton("🎮 ИГРАТЬ СЕЙЧАС", web_app=WebAppInfo(url=GAME_URL))]]
        await update.message.reply_text(
            "Хотите поиграть? Нажмите кнопку ниже! 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif any(word in text for word in thanks_keywords):
        keyboard = [[InlineKeyboardButton("⭐ Оценить игру", callback_data='rate')]]
        await update.message.reply_text(
            "Спасибо за отзыв! Рады, что вам нравится! ❤️\n"
            "Не забудьте поделиться игрой с друзьями!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    else:
        # Общий ответ на другие сообщения
        keyboard = [
            [InlineKeyboardButton("🎮 Открыть игру", web_app=WebAppInfo(url=GAME_URL))],
            [InlineKeyboardButton("❓ Помощь", callback_data='help')],
            [InlineKeyboardButton("🆘 Поддержка", url=f"https://t.me/{SUPPORT_BOT[1:]}")]
        ]
        
        await update.message.reply_text(
            f"Я бот для игры Arrows Pro Ultra! 🎮\n\n"
            f"Используйте команды или кнопки для навигации.\n"
            f"Если есть проблемы - пишите в поддержку: {SUPPORT_BOT}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ====================== ОБРАБОТЧИК ОШИБОК ======================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок бота"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    try:
        # Пытаемся отправить сообщение об ошибке пользователю
        if update and update.effective_message:
            keyboard = [
                [InlineKeyboardButton("🆘 Сообщить об ошибке", url=f"https://t.me/{SUPPORT_BOT[1:]}")],
                [InlineKeyboardButton("🔄 Перезапустить бота", callback_data='refresh')]
            ]
            
            error_text = f"""
⚠️ *Произошла внутренняя ошибка бота!*

*Что делать:*
1. Попробуйте команду /start
2. Если ошибка повторяется, сообщите в поддержку
3. Опишите, что вы делали перед ошибкой

*Техническая поддержка:* {SUPPORT_BOT}

*Приносим извинения за неудобства!*
            """
            
            await update.effective_message.reply_text(
                text=error_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Failed to send error message: {e}")

# ====================== ОСНОВНАЯ ФУНКЦИЯ ======================

def main() -> None:
    """Запуск бота"""
    # Создаем Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("game", game_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("support", support_command))
    
    # Добавляем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("=" * 60)
    print("🤖 БОТ ARROWS PRO ULTRA ЗАПУЩЕН!")
    print("=" * 60)
    print(f"🔗 Ссылка на бота: https://t.me/{application.bot.username}")
    print(f"🎮 URL игры: {GAME_URL}")
    print(f"🆘 Бот поддержки: {SUPPORT_BOT}")
    print(f"📝 Логи пишутся в файл: bot.log")
    print("=" * 60)
    print("НАСТРОЙКИ ПОДДЕРЖКИ:")
    print(f"• Все ошибки перенаправляются в: {SUPPORT_BOT}")
    print("• Пользователи получают шаблон для обращения")
    print("• Кнопка поддержки в каждом меню")
    print("=" * 60)
    print("Нажмите Ctrl+C для остановки")
    print("=" * 60)
    
    # Запускаем polling
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

# ====================== ТОЧКА ВХОДА ======================

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Бот остановлен пользователем")
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Критическая ошибка: {e}")
        print(f"🆘 Сообщите в поддержку: {SUPPORT_BOT}")

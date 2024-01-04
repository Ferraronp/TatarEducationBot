from imports.imports import *
from imports.imports_modules import *
import tg.database.sql_commands as sql_commands


def close_keyboard(update, context):
    """Убирает клавиатуру"""
    username = str(update.message.chat_id)
    blacklist = sql_commands.get_users_of_blacklist()
    if username in blacklist:
        logging.info(f"User in blacklist write message: {username}, {update.message.text}")
        return
    sent = False
    while not sent:
        try:
            update.message.reply_text(
                "Клавиатура скрыта",
                reply_markup=ReplyKeyboardRemove()
            )
            sent = True
        except Exception as ex:
            logging.warning(f"Something going wrong in handlers.py in close_keyboard: {ex}")
            time.sleep(10)


def get_handlers():
    handlers = []

    text_handler = MessageHandler(Filters.text, echo,
                                  run_async=True)

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start,
                                     run_async=True),
                      PrefixHandler('🖋️', "Изменить", start,
                                    run_async=True)],

        states={
            1: [MessageHandler(Filters.text, get_login,
                               run_async=True)],
            2: [MessageHandler(Filters.text, get_password,
                               run_async=True)]
        },
        fallbacks=[]
    )
    handlers += [start_handler]

    handlers += [
        CommandHandler("marks", print_marks,
                       run_async=True),
        CommandHandler("homework", print_homework,
                       run_async=True),
        CommandHandler("schedule", print_schedule,
                       run_async=True),
        CommandHandler("set", set_timer,
                       pass_args=True,
                       pass_job_queue=True,
                       pass_chat_data=True,
                       run_async=True),
        CommandHandler("unset", unset_timer,
                       pass_chat_data=True,
                       run_async=True),
        CommandHandler("close", close_keyboard,
                       run_async=True),
        CommandHandler("rating", print_rating,
                       run_async=True),
    ]

    handlers += [
        PrefixHandler('🖋️', "Изменить", start,
                      run_async=True),
        PrefixHandler('📊', 'Оценки', print_marks,
                      run_async=True),
        PrefixHandler('📚', 'Домашние', print_homework,
                      run_async=True),
        PrefixHandler('📖', 'Расписание', print_schedule,
                      run_async=True),
        PrefixHandler("⏰✅", "Вкл.", set_timer,
                      pass_args=True,
                      pass_job_queue=True,
                      pass_chat_data=True,
                      run_async=True),
        PrefixHandler("⏰❌", "Выкл.", unset_timer,
                      pass_chat_data=True,
                      run_async=True),
        PrefixHandler('🏆', 'Рейтинг', print_rating,
                      run_async=True)
    ]

    callback_handler = CallbackQueryHandler(callback,
                                            run_async=True)
    handlers += [callback_handler]

    handlers += [text_handler]
    return handlers


def unsleep_on(dp) -> None:
    """Добавляет задачу для быстроты ответа на другие запросы"""
    context = CallbackContext(dp)
    context.job_queue.run_repeating(
        unsleep,
        interval=300,
        first=5,
        context=604831762,
        name='604831762'
    )


def unsleep(context) -> None:
    """Отправляет "test" для быстроты ответа"""
    userid = context.job.context
    msg = context.bot.send_message(userid, text='test')
    context.bot.delete_message(msg.chat.id, msg.message_id)


def error_handler(update, context):
    logging.error(f"Error: {context.error}")

from imports.imports import *
from imports.imports_modules import *


def close_keyboard(update, context):
    userid = str(update.message.chat_id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if userid in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(userid, update.message.text)
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
            print(f"\033[91m{datetime.datetime.now()} Error bot.send_message in tg.py in close_keyboard\033[0m\n{ex}")
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

    '''add_note_schedule_handler = ConversationHandler(
        entry_points=[CommandHandler('addnote', add_note_to_schedule,
                                     run_async=True),
                      PrefixHandler("📝", "Создать", add_note_to_schedule,
                                    run_async=True)],

        states={
            1: [MessageHandler(Filters.text, get_day_add_note_schedule,
                               run_async=True)],
            2: [MessageHandler(Filters.text, get_num_of_lesson_add_note_schedule,
                               run_async=True)],
            3: [MessageHandler(Filters.text, get_msg_note_schedule,
                               run_async=True)]
        },
        fallbacks=[]
    )
    handlers += [add_note_schedule_handler]

    delete_note_schedule_handler = ConversationHandler(
        entry_points=[CommandHandler('delnote', delete_schedule_note,
                                     run_async=True),
                      PrefixHandler('🗑️', 'Удалить', delete_schedule_note,
                                    run_async=True)],

        states={
            1: [MessageHandler(Filters.text, get_day_del_note_schedule,
                               run_async=True)],
            2: [MessageHandler(Filters.text, get_num_of_lesson_del_note_schedule,
                               run_async=True)]
        },
        fallbacks=[]
    )
    handlers += [delete_note_schedule_handler]'''

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
    context = CallbackContext(dp)
    job = context.job_queue.run_repeating(
        unsleep,
        interval=300,
        first=5,
        context=604831762,
        name='604831762'
    )


def unsleep(context) -> None:
    userid = context.job.context
    msg = context.bot.send_message(userid, text='test')
    context.bot.delete_message(msg.chat.id, msg.message_id)


def callback(update, context):
    dict_ = update.to_dict()
    text_button = dict_['callback_query']['data']
    if text_button == 'next_day_homework' or text_button == 'previous_day_homework':
        userid = update.effective_user['id']
        message_id = dict_['callback_query']['message']['message_id']
        message = dict_['callback_query']['message']['text']

        date = get_day_from_homework(message)
        text = get_day_homework(userid, date + datetime.timedelta(days=1 if text_button == 'next_day_homework' else -1))
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='Предыдущий день',
                                                             callback_data='previous_day_homework'),
                                        InlineKeyboardButton(text='Следующий день',
                                                             callback_data='next_day_homework')]])
        context.bot.edit_message_text(text=text, chat_id=userid, message_id=message_id, reply_markup=markup)


def error_handler(update, context):
    print(f"\033[91m{datetime.datetime.now()} Error\033[0m\n{context.error}")
    try:
        print(update.message.from_user.id)
        print(update.message.text)
    except Exception:
        pass

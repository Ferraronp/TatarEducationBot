from tg.imports.imports import *


def wrap_signs_with_backslash(text: str) -> str:
    """
    Ставит обратный слэш перед символами =, -, ., (, ), +, <, >, !, *
    """
    text = text.replace('=', '\\=').replace('-', '\\-').replace(".", "\\.")
    text = text.replace("(", "\\(").replace(")", "\\)").replace('+', '\\+')
    text = text.replace('<', '\\<').replace('>', '\\>').replace('!', '\\!')
    return text


def send_msg(update, msg: str, markup=None) -> int:
    """
    :param update:
    :param msg: str
    :param markup:
    :param context:
    :return: message_id
    """
    error = False
    logging_msg = f"Server send message to user: "
    if 'channel_post' in update:
        return 0
    try:
        username = str(update.message.from_user.id)
    except Exception:
        username = 'None'
    logging_text = '["' + msg.replace('\n', '\\n') + '"]'
    logging_msg += f"{username}, {logging_text}"
    logging.info(logging_msg)
    sent = False
    while not sent:
        try:
            message = update.message.reply_text(msg, reply_markup=markup)
            sent = True
        except Exception as ex:
            logging.error(f"Server cannot send message to user: {username}, {ex}")
            try:
                if 'blocked' in str(ex) or 'user is deactivated' in str(ex):
                    raise RuntimeError
            except Exception:
                pass
            time.sleep(10)
            error = True
    if error:
        logging.info(f"Server send message to user after error: {username}")
    return message['message_id']


def update_message(context, message_id: int, chat_id: str, text: str, markup=None, parse_mode=None):
    logging_msg = f"Server update message in user chat: "
    logging_text = '["' + text.replace('\n', '\\n') + '"]'
    logging_msg += f"{chat_id}, {logging_text}"
    logging.info(logging_msg)
    if parse_mode:
        text = wrap_signs_with_backslash(text)
    context.bot.edit_message_text(text=text,
                                  chat_id=chat_id,
                                  message_id=message_id,
                                  reply_markup=markup,
                                  parse_mode=parse_mode)


def send_msg_with_parse_mode(context, username, msg: str, markup=None) -> int:
    """
    :param context:
    :param username:
    :param msg:
    :param markup:
    :param update:
    :return: message_id
    """
    error = False
    msg = wrap_signs_with_backslash(msg)
    logging_msg = f"Server send message to user: "
    logging_msg += f"{username}, " + '["' + msg.replace('\n', '\\n') + '"]'
    logging.info(logging_msg)
    sent = False
    while not sent:
        try:
            message = context.bot.send_message(username, text=msg, reply_markup=markup, parse_mode=ParseMode.MARKDOWN_V2)
            sent = True
        except Exception as ex:
            logging.error(f"Server cannot send message to user: {username}, {ex}")
            try:
                if 'blocked' in str(ex) or 'user is deactivated' in str(ex):
                    raise RuntimeError
            except Exception:
                pass
            time.sleep(10)
            error = True
    if error:
        logging.info(f"Server send message to user after error: {username}")
    return message['message_id']

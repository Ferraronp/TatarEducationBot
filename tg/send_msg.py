from imports.imports import *


def send_msg(update, msg, markup=None):
    error = False
    print(f"\033[93m{datetime.datetime.now()}\033[0m", end=' ')
    try:
        print(update.message.from_user.id)
    except Exception:
        pass
    print([msg])
    sent = False
    while not sent:
        try:
            update.message.reply_text(msg, reply_markup=markup)
            sent = True
        except Exception as ex:
            print(f"\033[91m{datetime.datetime.now()} Error in send_msg\033[0m\n{ex}")
            time.sleep(10)
            error = True
    if error:
        print("Отправлено")


def send_msg_with_parse_mode(context, userid, msg: str):
    error = False
    msg = msg.replace('=', '\\=').replace('-', '\\-').replace(".", "\\.").replace('!', '\\!')
    msg = msg.replace("(", "\\(").replace(")", "\\)").replace('+', '\\+')
    msg = msg.replace('<', '\\<').replace('>', '\\>')
    print(f"\033[93m{datetime.datetime.now()}\033[0m", end=' ')
    try:
        print(userid)
    except Exception:
        pass
    print([msg])
    sent = False
    while not sent:
        try:
            # update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)
            context.bot.send_message(userid, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
            sent = True
        except Exception as ex:
            print(f"\033[91m{datetime.datetime.now()} Error"
                  f" in send_msg_with_parse_mode\033[0m"
                  f"\n{ex}\n{userid}\n{[msg]}")
            try:
                if 'blocked' in str(ex):
                    break
            except Exception:
                pass
            time.sleep(10)
            error = True
    if error:
        print("Отправлено")


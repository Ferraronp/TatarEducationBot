from setup import *
from gevent import monkey as curious_george
logging.basicConfig(filename=f'logs/{str(datetime.datetime.now().date())}.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
curious_george.patch_all(thread=True, select=False)


def main():
    logging.info("Application has been launched")
    token = open('parametrs.txt', mode='r').read()
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    sql_setup(dp)
    init_handlers(dp)
    unsleep_on(dp)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        logging.info("Application has been finished")

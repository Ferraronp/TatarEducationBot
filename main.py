from imports.imports import *
from imports.imports_modules import *
from tg.handlers.setup import *
from gevent import monkey as curious_george
curious_george.patch_all(thread=True, select=False)


def main():
    setup()


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(f"\033[91m{datetime.datetime.now()} Error in main.py\033[0m")
        print(ex)

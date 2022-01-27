from BotController import dp
from settings import *

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    # 确保日志文件所在的目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

bot_logger = setup_logger('bot_logger', 'data/bot.log')

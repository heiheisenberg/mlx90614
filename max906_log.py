# 日志模块
import logging

logger = logging.getLogger(__name__)
fh = logging.FileHandler('max906.log', encoding='utf-8')  # 创建一个handler,写入日志
ch = logging.StreamHandler()                              # 再创建一个handler, 用于输出到控制台
logging.root.setLevel(logging.NOTSET)                     # 这行代码解决setLevel无效问题

formatter = logging.Formatter('%(asctime)s-%(filename)s[line:%(lineno)d]-%(levelname)s-%(message)s')
fh.setLevel(logging.DEBUG)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# 提供的接口
log = logger.log

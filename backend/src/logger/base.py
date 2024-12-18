import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 設定日誌格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# 創建 FileHandler，將日誌寫入 app.log
file_handler = logging.FileHandler('app.log', mode='a')  # 'a' 表示追加日誌到文件中
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 創建 StreamHandler，將日誌輸出到控制台
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

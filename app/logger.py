import os, logging
from logging.handlers import RotatingFileHandler

def setup_logger(app):
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # 設定 logger 格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    # 檔案 handler (輪轉日誌，最大 10MB，保留 10 個檔案)
    file_handler = RotatingFileHandler(
        'logs/api.log', maxBytes=10*1024*1024, backupCount=10, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)
    
    # 設定 app logger
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # 避免重複記錄
    app.logger.propagate = False

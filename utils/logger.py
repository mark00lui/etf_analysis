import logging
import os
from datetime import datetime

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """設定日誌記錄器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 避免重複添加 handler
    if logger.handlers:
        return logger
    
    # 建立格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台輸出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 檔案輸出
    if log_file:
        # 確保日誌目錄存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

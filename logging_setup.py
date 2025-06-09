import logging
from datetime import datetime
from pathlib import Path

class RequestLogger:
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
    def create_request_log(self, request_id):
        """Create a new logger for a specific request"""
        log_file = self.log_dir / f"request_{request_id}.log"
        
        logger = logging.getLogger(f"request_{request_id}")
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()
            
        handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s\n%(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.propagate = False
        
        return logger

    @staticmethod
    def generate_request_id():
        """Generate a unique ID for each request"""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

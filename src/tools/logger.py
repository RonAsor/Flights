import logging

class SingletonLogger:
    '''
    Name:Ron Asor
    Date:23/01/2024
    Description:Basic logger singleton class
    '''
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonLogger, cls).__new__(cls, *args, **kwargs)
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return cls._instance

    def get_logger(self):
        """
        Get the logger instance.
        """
        return logging.getLogger()
import logging
import os
import time
import glob
from datetime import datetime, timedelta

def setup_logger():
    # Create a logger object.
    logger = logging.getLogger(__name__)

    # Set the level of the logger. This can be DEBUG, INFO, WARNING, ERROR, or CRITICAL.
    logger.setLevel(logging.DEBUG)

    # Create a file handler for outputting log messages to a file.
    # Include the current date in the filename.
    handler = logging.FileHandler('/home/pi/touchUI_{}.log'.format(datetime.now().strftime('%Y_%m_%d')))

    # Set the level of the file handler. This can be DEBUG, INFO, WARNING, ERROR, or CRITICAL.
    handler.setLevel(logging.DEBUG)

    # Create a formatter.
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to the handler.
    handler.setFormatter(formatter)

    # Add the handler to the logger.
    logger.addHandler(handler)

    # Create a stream handler for outputting log messages to the console.
    console_handler = logging.StreamHandler()

    # Set the level of the console handler. This can be DEBUG, INFO, WARNING, ERROR, or CRITICAL.
    console_handler.setLevel(logging.DEBUG)

    # Add the formatter to the console handler.
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger.
    logger.addHandler(console_handler)

    return logger

def delete_old_logs(logs_path='/home/pi/', max_age_days=5):
    """
    Deletes all log files in the given directory that are older than `max_age_days` days.
    """
    current_time = time.time()

    for file in glob.glob(os.path.join(logs_path, 'touchUI_*.log')):
        creation_time = os.path.getctime(file)

        if (current_time - creation_time) // (24 * 3600) >= max_age_days:
            os.unlink(file)
            print('{} removed'.format(file))
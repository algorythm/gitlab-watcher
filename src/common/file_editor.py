import uuid, subprocess, os
from src.common.logging_helper import get_logger

def write_temp_file(file_extension: str, initial_content: str = None, default_editor = 'vim') -> str:
    logger = get_logger(__name__)
    filename = f'/tmp/{str(uuid.uuid4())}.{file_extension}'

    logger.debug(f'creating file {filename}')

    try:
        with open(filename, 'w') as tf:
            if initial_content != None:
                tf.writelines(initial_content)
                tf.flush()

            logger.debug(f'editing {filename} with {default_editor}')
            subprocess.call([default_editor, filename])

        with open(filename, 'r') as tf:
            return tf.read()

    finally:
        if os.path.exists(filename):
            logger.debug(f'removing file {filename}')
            os.remove(filename)

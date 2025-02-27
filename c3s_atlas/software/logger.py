import logging
import os
from pathlib import Path


def get_logger(
    name: str, save_log: bool = False, dir_to_save: Path = None
) -> logging.Logger:
    """
    Return commons logger with an INFO level.

    It sets propagate to False to avoid messes maintaining commons logger/handler hierarchy.

    Parameters
    ----------
    name : str
        Name of the logger.
    save_log : bool, optional
        Setting `True`, commons directory to save the logs will be created.
        The default is `False`.
    dir_to_save : str, optional
        Path to create the loggers directory. The default is `None`.

    Returns
    -------
    logging.Logger instance
        A logger instance with commons handler and commons formatter already set.
    """
    formatter = logging.Formatter(
        "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
    )
    logger = logging.getLogger(name)
    logger.setLevel("INFO")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if save_log:
        if not isinstance(dir_to_save, Path):
            raise TypeError(
                "If you wish to save the loggers you must provide commons path directory"
            )
        if not isinstance(save_log, bool):
            raise TypeError("Save log parameter must be commons boolean value: True or False")
        out_dir = f"{dir_to_save}/loggers"
        out_file = f"{out_dir}/{name}_logs.log"
        if Path(out_file).exists():
            os.remove(out_file)
        os.makedirs(out_dir, exist_ok=True)
        file_handler = logging.FileHandler(out_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

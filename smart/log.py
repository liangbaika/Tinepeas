# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      log
# Author:    liangbaikai
# Date:      2020/12/29
# Desc:      there is a log py for  smart-framework
# ------------------------------------------------------------------
import logging


def get_logger(name="SmartSpider", level=logging.INFO) -> logging.Logger:
    logging_format = f"[%(asctime)s] thread %(thread)d  process %(process)d   %(levelname)-5s %(filename)s %(module)s line %(lineno)d  %(name)-{len(name)}s "
    logging_format += "%(message)s"

    logging.basicConfig(
        format=logging_format, level=logging.INFO, datefmt="%Y:%m:%d %H:%M:%S"
    )
    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("websockets").setLevel(logging.INFO)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger

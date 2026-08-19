from __future__ import annotations
import logging,sys
from config import get_settings
def build_logger()->logging.Logger:
    settings=get_settings();logger=logging.getLogger('aks_upgrade_agent')
    if logger.handlers:return logger
    logger.setLevel(getattr(logging,settings.log_level.upper(),logging.INFO));handler=logging.StreamHandler(sys.stdout);handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'));logger.addHandler(handler);return logger
logger=build_logger()

import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from logging import StreamHandler
import requests
from datetime import timedelta, datetime
from yaml import safe_load

from utils.helper_functions import get_conf_key
from pathlib import Path


def start_logger(logger):
    # load config and configure logging
    config_file = os.getenv("LOGGING_CONFIG")
    assert Path(config_file).is_file(), f"Error: Logging config file {config_file} does not exist"

    assert (config_file is not None), "Error: Environment variable LOGGING_CONFIG is not set"
    with open(config_file, "r") as f:
        conf = safe_load(f)

    setup_logging(conf, logger)

    for k, v in get_conf_key(conf, 'module_logging_levels').items():
        logging.getLogger(k).setLevel(v.upper())


def setup_logging(log_config, log):
    """Configure logging"""

    if log.hasHandlers():
        log.handlers.clear()

    dfmt = "%(asctime)s [%(levelname)s] %(name)s | %(message)s"
    fmt = logging.Formatter(get_conf_key(log_config, 'logging.format', default=dfmt))
    log.setLevel(get_conf_key(log_config, 'logging.level', default='INFO').upper())

    if get_conf_key(log_config, 'logging.enable_stderr', default=True):
        hdlr = logging.StreamHandler(sys.stderr)
        hdlr.setFormatter(fmt)
        log.addHandler(hdlr)

    if get_conf_key(log_config, 'logging.enable_stdout', default=False):
        hdlr = logging.StreamHandler(sys.stdout)
        hdlr.setFormatter(fmt)
        log.addHandler(hdlr)

    if get_conf_key(log_config, 'logging.enable_file', default=False):
        os.mkdir('logs/')
        hdlr = RotatingFileHandler('logs/pyservice.log', maxBytes=1000000, backupCount=10)
        hdlr.setFormatter(fmt)
        log.addHandler(hdlr)

    if get_conf_key(log_config, 'logging.enable_slack', default=False):
        # use with caution, will log to slack channel if enabled
        # useful for receiving critical messages
        auth = get_conf_key(log_config, 'logging.enable_slack.auth', required=True)
        hdlr = SlackHandler(auth=auth, timeout=timedelta(minutes=120))
        hdlr.setLevel(get_conf_key(log_config, 'logging.enable_slack.level', defualt='ERROR').upper())
        hdlr.setFormatter(fmt)
        log.addHandler(hdlr)



class SlackHandler(StreamHandler):
    """
    See, https://api.slack.com/messaging/webhooks.

    Has a timeout option to temporarily mute duplicated message
    and avoid slack channel getting spammed with a repeating message.
    """
    def __init__(self, auth, timeout=timedelta(seconds=0)):
        """
        Initialize the handler.

        Args:
            auth (string)): slack webhook api token
            timeout (datetime.timedelta, optional): mute duplicate messages until timeout expires.
        """
        super().__init__(self)
        self._url_auth = auth
        self._timeout = timeout
        self._timed_out = {}
        self._last_proc = datetime.now() - self._timeout


    def emit(self, record):
        if self._eval_timeout(record):
            msg = self.format(record)
            try:
                requests.post(self._url_auth, str({"text":msg}))
                self._last_proc = datetime.now()
            except requests.Timeout:
                # back off and retry
                pass
            except requests.ConnectionError:
                pass


    def _eval_timeout(self, record):
        """
        Check is record.msg timed out.

        Args:
            record (obj): a LogRecord object being logged

        Returns:
            bool: True for emit message
        """

        if record.msg not in self._timed_out.keys():
            self._timed_out[record.msg] = datetime.now() - self._timeout

        if (datetime.now()-self._timed_out[record.msg]) > self._timeout:
            self._timed_out[record.msg] = datetime.now()
            return True
        else:
            # msg is timed out out do not emit!!!
            return False

logger = logging.getLogger(os.getenv('ROOT_LOGGER_NAME'))
start_logger(logger)
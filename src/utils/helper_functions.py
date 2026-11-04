import logging, os
logger = logging.getLogger(os.getenv('ROOT_LOGGER_NAME')).getChild('utils')

def get_conf_key(conf, key, required=True, default=None, parse_func=None):
    """
    Get config keys from dict, raise ValueError if required key is missing.

    If key exists in conf, parse_func can be used to parse loaded value.
    """
    c = conf
    ks = []
    for k in key.split("."):
        ks.append(k)
        if k not in c:
            if required:
                msg = f"Config is missing key: \"{'.'.join(ks)}\""
                raise ValueError(msg)
            else:
                logger.warning(f'{key} not in config, using: {default}')
                return default
        c = c[k]
    logger.debug(f'{key} in config: {c}')
    if parse_func is not None:
        c = parse_func(c)
    return c

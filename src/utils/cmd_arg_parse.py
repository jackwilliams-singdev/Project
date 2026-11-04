"""
Generic command line argument parsing for python services.

Use argparse to parse command line arguments, specifically:
  - --config / -c : path(s) to YAML config file(s)
     if multiple config files are provided, they will be merged into a single dict, preserving structure and nesting under 
     identical keys
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from deep_chainmap import DeepChainMap
from utils.setup_logging import logger

logger = logger.getChild('CMDL_ARGS')

def cmd_line_config(description=None, parser=argparse.ArgumentParser()):
    """
    load one (or more) config.yaml files from command line arguments. Should be string paths.
    Merges multiple config files into s single dict with DeepChainMap, preserving structure and nesting.
    
    :param description: Optional, Description 
    :param parser: Optional, argparse.ArgumentParser if you want to use a custom parser
    
    usage:
        $python py_module.py --config ./path/to/config1.yaml ./path/to/additional/config.yaml ./...more/configs.yaml
    """
    if description is not None:
        parser.description = description
    
    # allow -c/--config to accept one or more config file paths and preload them
    parser.add_argument(
        '-c', '--config',
        nargs='+', 
        action=LoadConfigs,
        help='Path(s) to config file(s). Provide one or multiple files to load and merge.',
        required=True)
    
    args = parser.parse_args()
    
    return args.config

class LoadConfigs(argparse.Action):
    """
    Custom argparse Action to load one or more YAML config files and merge them into a single dict.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        logger.info("LoadConfig - argparse.Action")
        
        loaded = []
        for p in values:
            with open(p, 'r') as fh:
                logger.info('\t- %s', p)
                loaded.append(yaml.safe_load(fh) or {})
                
        # Make a merged mapping: later files override earlier ones.
        # DeepChainMap looks up in the first mapping first, so reverse to give precedence to later files.
        if len(loaded) == 1:
            namespace.config = loaded[0]
        else:
            logger.debug('deep chain map configs')
            # using *list to unpack items into arguments
            namespace.config = DeepChainMap(*loaded).to_dict()


def parse_args(argv: Optional[list[str]] = None, msg: str = 'Parse command line arguments', nargs='+') -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Handle multiple or a single config file:
        nargs='+': Requires at least one value.
        nargs='*': Accepts zero or more values.
        nargs=N: Requires exactly N values.
    
    Args:
        argv: List of command line arguments to parse
        msg: Hint. Description of the command line argument parser
    """
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument(
        "-c",
        "--config",
        nargs=nargs,
        required=True,
        type=str,
        help="Path to YAML configuration file",
    )
    return parser.parse_args(argv)

def read_config(config_path: str) -> Dict[str, Any]:

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError("Config file does not exist:\n\t- {config_path}" )

    try:
        with config_path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
            config: Dict[str, Any] = raw if isinstance(raw, dict) else {}
    except Exception as exc:  # broad catch to report parsing/read errors
        logger.exception("Failed to read/parse config: %s", exc)
        sys.exit(3)
        
    return config
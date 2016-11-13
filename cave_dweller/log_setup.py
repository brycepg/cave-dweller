"""Setup python logger"""
import logging
import sys

from .util import game_path

def setup_logger(verbose=False):
    """Setup logging -
        Only output INFO and higher to console
        Output everything to gamelog.txt
        TODO: Have an actual game log with game events
              and a separate log for debugging"""
    if verbose:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    my_format = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s| %(message)s")
    #logging.basicConfig()
    fh = logging.FileHandler(game_path("gamelog.txt"))
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(my_format)
    log.addHandler(fh)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(console_level)
    ch.setFormatter(my_format)
    log.addHandler(ch)

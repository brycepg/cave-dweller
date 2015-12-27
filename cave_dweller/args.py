import argparse

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', help="set world seed", default=None)
    parser.add_argument('--selected-path', help="select data folder(ignore seed)", default=None)
    parser.add_argument('--skip', help="skip main menu to new game", action="store_true")
    parser.add_argument('-v', dest='verbose', help='debug output log', action="store_true")
    args = parser.parse_args()
    return args


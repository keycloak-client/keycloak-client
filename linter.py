#! /usr/bin/env python


# For details about this script, please see the following
# https://github.com/PyCQA/pylint/issues/2242
# https://github.com/Meeshkan/meeshkan-client/pull/31


import sys
import argparse
from pylint import lint


if __name__ == '__main__':
    """ entrypoint """
    parser = argparse.ArgumentParser(description='pass score for pylint', allow_abbrev=False)
    parser.add_argument('--fail-under', dest='threshold', type=float, default=8)
    args, remaining_args = parser.parse_known_args()
    run = lint.Run(remaining_args, do_exit=False)
    score = run.linter.stats['global_note']
    if score < args.threshold:
        sys.exit(run.linter.msg_status)

#!/usr/bin/env python
'''
    Main entry for goephor
'''
from __future__ import absolute_import
from goephor.core.Chain import Run
import argparse


def menu():
    parser = argparse.ArgumentParser(
        description='A yaml friendly build management tool')
    parser.add_argument('-f',
                        action="store",
                        dest="file",
                        help='json file containing build instructions')
    parser.add_argument('-e',
                        action="store_true",
                        dest="execute",
                        default=False,
                        help='execute all values in the chain')
    parser.add_argument('-E',
                        action="store",
                        dest="envs",
                        default="",
                        help='Add env vars delimiter:"," '
                        'example.'
                        ' "BASE_PATH=/tmp,WORKPATH=/${BASE_PATH}/addon"')
    parser.add_argument('-s',
                        action="store_false",
                        dest="silent",
                        default=True,
                        help='do not print any additional info')

    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s 1.0')
    return parser.parse_args()


def parse_envs(options):
    envs = options.envs.split(',')
    envs_dict = {}
    for env in envs:
        if '=' in env:
            env = env.split('=', 1)
            envs_dict[env[0]] = env[1]
    return envs_dict


def main():
    options = menu()
    if options.execute:
        main_actions = Run(options.file,options.silent)
        main_actions.add_envs(**parse_envs(options))
        main_actions.set_envs()
        main_actions.execute_actions()
    

if __name__ == '__main__':
    main()
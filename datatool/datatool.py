"""
datatool - to make cleaning data easier and faster,

Created by: Scott Walton
"""

import sys
import os
import argparse

from PyQt5.QtWidgets import QApplication

import software
import procedures
from gui.Controller import MyWorkingCode


if __name__ == '__main__':

    # Handle arguments

    parser = argparse.ArgumentParser(description="Cleans up messy data files.")
    parser.add_argument('-f', '--filepath', default=os.getcwd(), type=str, metavar='', help='Path to file')
    parser.add_argument('-t', '--type', type=str, metavar='', help='Type of data file, e.g. RM, PM',
                        choices=['RM', 'KS', 'PM', 'MB', 'ASF', 'ZP', 'MS'])
    parser.add_argument('-e', '--extract', action='store_true', help='Convert from Excel to CSV')
    parser.add_argument('-g', '--gui', action='store_false', help='Disable the GUI')
    parser.add_argument('filename', help='Csv file to clean', nargs='?', default=None)
    args = parser.parse_args()

    if args.extract:
        procedures.csv_from_excel(args.filepath)

    elif args.type == 'ZP':
        software.ZP_fix()

    elif args.type == 'PM':
        software.PM_fix()

    elif args.type == 'MB':
        software.MB_fix()

    elif args.type == 'KS':
        software.KS_fix()

    elif args.type == 'ASF':
        software.ASF_fix()

    elif args.type == 'MS':
        software.MS_fix()

    elif args.type == 'RM':

        if args.filename is None:
            print('You need to specify the filename.')
        else:
            mainPath = os.path.join(args.filepath, args.filename)
            try:
                parentPath = os.path.join(args.filepath, 'ParentsNames.csv')
                software.RM_fix(mainPath, parentPath)
            except FileNotFoundError:
                software.RM_fix(mainPath)

    elif args.gui and args.filename is not None:
        app = QApplication(sys.argv)
        window = MyWorkingCode(args.filename, path=args.filepath)
        window.show()
        sys.exit(app.exec_())

    elif args.gui and args.filename is None:
        app = QApplication(sys.argv)
        window = MyWorkingCode()
        window.show()
        sys.exit(app.exec_())

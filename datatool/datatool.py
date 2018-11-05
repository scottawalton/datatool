from PyQt5 import QtWidgets
from gui.Controller import MyWorkingCode
import pandas as pd
import sys, os
import argparse
import software
import procedures


if __name__ == '__main__':

    # Handle arguments

    parser = argparse.ArgumentParser(description="Cleans up messy data files.")
    parser.add_argument('-f', '--filepath', default=os.getcwd(), type=str, metavar='', help='Path to file')
    parser.add_argument('-t', '--type', type=str, metavar='', choices=['RM','KS', 'PM', 'MB', 'ASF', 'ZP', 'MS'],help='Type of data file, e.g. RM, PM')
    parser.add_argument('-e', '--extract', action='store_true', help='Convert from Excel to CSV')
    parser.add_argument('-g', '--gui', action='store_false', help='Disable the GUI')
    parser.add_argument('filename', help='Csv file to clean', nargs='?', default=None)
    args = parser.parse_args()

    if args.extract == True:
        procedures.csv_from_excel(args.filepath)

    elif args.type == 'ZP':
        software.ZenPlannerMash.ZPfix()

    elif args.type == 'PM':
        software.PerfectMindMash.PMfix()

    elif args.type == 'MB':
        software.MindBodyMash.MBfix()

    elif args.type == 'KS':
        software.KicksiteMash.KSfix()

    elif args.type == 'ASF':
        software.ASFmash.ASFfix()

    elif args.type == 'MS':
        software.MemberSolutionsMash.MSfix()

    elif args.type == 'RM':

        if args.filename == None:
            print('You need to specify the filename.')
        else:
            df = procedures.load(args.filename, args.filepath)
            try:
                parents = procedures.load('ParentsNames.csv', args.filepath)
                software.RainMakerFix.RMfix(df, parents)
            except:
                software.RainMakerFix.RMfix(df)

    elif args.gui == True and args.filename != None:
        app = QtWidgets.QApplication(sys.argv)
        window = MyWorkingCode(args.filename, path=args.filepath)
        window.show()
        sys.exit(app.exec_())
    
    elif args.gui == True and args.filename == None:
        app = QtWidgets.QApplication(sys.argv)
        window = MyWorkingCode()
        window.show()
        sys.exit(app.exec_())
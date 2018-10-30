from PyQt5 import QtCore, QtWidgets, QtGui
from gui.Ui_View import Ui_DataTool
import os
import sys
import pandas as pd
from gui import Model
import numpy as np
import procedures

# This is the controller

class MyWorkingCode(QtWidgets.QMainWindow, Ui_DataTool):

    def __init__(self, filename=None, path=os.getcwd()):
        super(QtWidgets.QMainWindow, self).__init__()

        self.setupUi(self)

        # If a file was specified, load it up. If not, load empty.
        if filename != None:
            data = procedures.load(filename, path)
            self.panda = Model.PandasTable(data)
        else:
            self.panda = Model.PandasTable(pd.DataFrame())

        self.tableView.setModel(self.panda)

        # File Menu Actions
        self.actionExit.triggered.connect(self.Exit)
        self.actionLoad.triggered.connect(self.loadData)
        self.actionSave.triggered.connect(self.saveData)


        # Operations Menu Actions
        self.actionClear_Whitespace.triggered.connect(self.clearWhitespace)
        self.actionRemove_Non_Numberic.triggered.connect(self.removeNonNumeric)
        self.actionCorrect_Date_Format.triggered.connect(self.correctDateFormat)
        self.actionDisperse_Ranks_By_Program.triggered.connect(self.ranksByProgram)

        # Run button
        self.runButton.clicked.connect(self.runCommand)


    def runCommand(self):

        command = self.textEdit.toPlainText()

        self.panda.runCommand(command)
        self.panda.layoutChanged.emit()

    #region File Menu
    def loadData(self):     

        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME'), 'CSV(*.csv)')
        
        self.panda.loadData(path)
        self.panda.layoutChanged.emit()

    def saveData(self):

        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', os.getenv('$HOME'))
        self.panda.saveData(path)

    def Exit(self):
        QtCore.QCoreApplication.exit()
    #endregion

    #region Operations Menu

    def clearWhitespace(self):

        # A selection model to get the current selection
        selectionModel = self.tableView.selectionModel()

        # Pass it to the panda model to deal with
        self.panda.clearWhitespace(selectionModel)

    def removeNonNumeric(self):

        # A selection model to get the current selection
        selectionModel = self.tableView.selectionModel()

        # Pass it to the panda model to deal with
        self.panda.removeNonNumeric(selectionModel)

    def correctDateFormat(self):

        # A selection model to get the current selection
        selectionModel = self.tableView.selectionModel()

        # Pass it to the panda model to deal with
        self.panda.correctDateFormat(selectionModel)

    def ranksByProgram(self):

        dialog = QtWidgets.QDialog()
        layout = QtWidgets.QGridLayout()
        rankSelect = QtWidgets.QComboBox()
        rankSelect.addItems(self.panda.df.columns.values)
        programSelect = QtWidgets.QComboBox()
        programSelect.addItems(self.panda.df.columns.values)
        layout.addWidget(programSelect, 1, 1)
        layout.addWidget(QtWidgets.QLabel('Program Column:'), 1, 0)
        layout.addWidget(rankSelect, 0, 1)
        layout.addWidget(QtWidgets.QLabel('Rank Column:'), 0, 0)
        confirm = QtWidgets.QPushButton('Confirm')
        layout.addWidget(confirm, 3, 1)
        def confirmClicked():
            rank = str(rankSelect.currentText())
            program  = str(programSelect.currentText())
            self.panda.df = procedures.fix_ranks(self.panda.df, ranks=rank, programs=program)
            dialog.reject()
            self.panda.layoutChanged.emit()
        confirm.clicked.connect(confirmClicked)
        cancel = QtWidgets.QPushButton('Cancel')
        def cancelClicked():
            dialog.reject()
        cancel.clicked.connect(cancelClicked)
        layout.addWidget(cancel, 3, 0)
        dialog.setLayout(layout)
        dialog.setWindowTitle('Ranks by Program')
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.exec()

    #endregion

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWorkingCode()
    window.show()
    sys.exit(app.exec_())
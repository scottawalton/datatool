from PyQt5 import QtCore, QtWidgets, QtGui
from gui.Ui_View import Ui_DataTool
import os
import sys
import pandas as pd
from gui import Model
import numpy as np
import procedures
import re
import traceback

# This is the controller

class MyWorkingCode(QtWidgets.QMainWindow, Ui_DataTool):

    def __init__(self, filename=None, path=os.getcwd()):
        super(QtWidgets.QMainWindow, self).__init__()

        self.setupUi(self)

        # If a file was specified, load it up. If not, load empty.
        if filename != None:
            data = procedures.load(filename, path)
            panda = Model.PandasTable(data)
            self.createTab(panda)
        else:
            panda = Model.PandasTable(pd.DataFrame())
            self.createTab(panda)

        # File Menu Actions
        self.actionExit.triggered.connect(self.Exit)
        self.actionLoad.triggered.connect(self.loadData)
        self.actionSave.triggered.connect(self.saveData)
        self.actionOpen.triggered.connect(self.openData)


        # Edit Menu Actions
        self.actionDelete.triggered.connect(self.deleteData)

        # Operations Menu Actions
        self.actionClear_Whitespace.triggered.connect(self.clearWhitespace)
        self.actionRemove_Non_Numberic.triggered.connect(self.removeNonNumeric)
        self.actionCorrect_Date_Format.triggered.connect(self.correctDateFormat)
        self.actionDisperse_Ranks_By_Program.triggered.connect(self.ranksByProgram)
        self.actionFind_and_Replace.triggered.connect(self.findAndReplace)

        # Run button
        self.runButton.clicked.connect(self.runCommand)

    # Translates and runs commands entered through the text area
    def runCommand(self):

        command = self.textEdit.toPlainText()

        if command == '':
            self.notifyUser("No command entered.")
        else:

            # Allows us to use df to specify the first tab's dataframe
            command = re.sub( r'df(?!\d)' , 'self.getPanda(0).df', command)

            # This allows us to use df2 df3 etc.. to refer to the proceding tabs' dataframes
            match = re.findall(r'df\d', str(command))
            if match is not None:
                for x in match:
                    num = int(re.search(r'\d', x)[0]) - 1
                    command = command.replace( x , 'self.getPanda(' + str(num) + ').df')

            try:
                exec(command)
                self.getCurrentPanda().layoutChanged.emit()
            
            # Lets user know they messed up and how
            except:
                errorMsg = 'There was a problem with the command entered. ' + \
                           'See stack trace or show Scott: \n\n' + traceback.format_exc()
                self.notifyUser(errorMsg)

    # A simple message box to let the user know about something
    def notifyUser(self, message):
        msg = QtWidgets.QMessageBox()
        msg.setText(message)
        msg.exec()

    #region Tab Functionality
    # Gets the tableView currently in focus
    def getCurrentView(self):

        currentTab = self.tabWidget.currentWidget()
        
        View = currentTab.findChild(QtWidgets.QTableView)

        return View

    # Gets the PandaTable currently in focus
    def getCurrentPanda(self):

        view = self.getCurrentView()

        if view != None:
            panda = view.model()
            return panda
        else:
            return None

    # Gets the PandaTable at the given index
    def getPanda(self, index):
        tab = self.tabWidget.widget(index)
        view = tab.findChild(QtWidgets.QTableView)
        panda = view.model()
        return panda

    # Creates a new tab with the given PandaTable
    def createTab(self, panda):

        tab = QtWidgets.QWidget()
        tab.setObjectName("tab")
        verticalLayout = QtWidgets.QVBoxLayout(tab)
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.setSpacing(10)
        verticalLayout.setObjectName("verticalLayout")
        tableView = QtWidgets.QTableView(tab)
        tableView.setSortingEnabled(False)
        tableView.setObjectName("tableView")
        tableView.verticalHeader().setDefaultSectionSize(30)
        tableView.verticalHeader().setMinimumSectionSize(30)
        verticalLayout.addWidget(tableView)
        tableView.setModel(panda)
        self.tabWidget.addTab(tab, "Tab")

    # Deletes all tabs in the tabWidget
    def deleteAllTabs(self):
        
        # Iterate through all tabs, removing each
        for i in range(0,self.tabWidget.count()):
            self.tabWidget.removeTab(i)

        # For whatever reason, this one likes to stay, so we delete it explicitly
        self.tabWidget.removeTab(self.tabWidget.currentIndex())

    #endregion

    #region File Menu
    def loadData(self):     

        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME'), 'CSV(*.csv)')

        # If a file was specified, load it up. If not, tell the user to pick a valid file
        if path[0] != '':

            if os.path.exists(path[0]) and os.path.getsize(path[0]):

                self.OriginalData = pd.read_csv(path[0], index_col=None, dtype=object)

                panda = Model.PandasTable(self.OriginalData)

                self.deleteAllTabs()
                self.createTab(panda)

            else:
                self.notifyUser("Please pick a valid file.")

    def openData(self):

        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME'), 'CSV(*.csv)')

        # If a file was specified, load it up. If not, tell the user to pick a valid file
        if path[0] != None:

            if os.path.exists(path[0]) and os.path.getsize(path[0]):

                self.OriginalData = pd.read_csv(path[0], index_col=None, dtype=object)

                panda = Model.PandasTable(self.OriginalData)

                self.createTab(panda)

            else:
                self.notifyUser("Please pick a valid file.")

    def saveData(self):

        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', os.getenv('$HOME'))

        self.getCurrentPanda().saveData(path)

    def Exit(self):
        QtCore.QCoreApplication.exit()
    #endregion

    #region Edit Menu

    def deleteData(self):

        # A selection model to get the current selection
        selectionModel = self.getCurrentView().selectionModel()

        # Pass it to the panda model to deal with
        self.getCurrentPanda().deleteData(selectionModel)

    #endregion

    #region Operations Menu

    def clearWhitespace(self):

        # A selection model to get the current selection
        selectionModel = self.getCurrentView().selectionModel()

        # Pass it to the panda model to deal with
        self.getCurrentPanda().clearWhitespace(selectionModel)

    def removeNonNumeric(self):

        # A selection model to get the current selection
        selectionModel = self.getCurrentView().selectionModel()

        # Pass it to the panda model to deal with
        self.getCurrentPanda().removeNonNumeric(selectionModel)

    def correctDateFormat(self):

        # A selection model to get the current selection
        selectionModel = self.getCurrentView().selectionModel()

        # Pass it to the panda model to deal with
        self.getCurrentPanda().correctDateFormat(selectionModel)

    def ranksByProgram(self):

        # Prompts user and gets a set of values
        ranks, programs = Model.RanksByProgramsDialogBox.getResults(self.panda, self)

        # Passes values to PandaModel to be validated and acted upon
        self.getCurrentPanda().ranksByPrograms(ranks, programs)

    def findAndReplace(self):

        # Prompts user for find regex and replace text
        findText, replaceText = Model.FindAndReplaceDialogBox.getResults(self)
        
        # Gets the current selection from the current tab
        selectionModel = self.getCurrentView().selectionModel()

        # Pass to panda
        self.getCurrentPanda().findAndReplace(findText, replaceText, selectionModel)

    #endregion

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWorkingCode()
    window.show()
    sys.exit(app.exec_())
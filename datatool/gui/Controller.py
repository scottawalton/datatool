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

class MyWorkingCode(QtWidgets.QMainWindow, Ui_DataTool):
    """
    This is the main window of the application.
    Upon initialization, we bind all of the signals to functions and initialize the UI.
    
        :param filename=None: 
            The filename of the file we are opening, if we load one on launch.
        :param path=os.getcwd(: 
            The path to the file we want to open, if we load one on launch.
    """   

    def __init__(self, filename=None, path=os.getcwd()):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        if filename != None:
            pandaData = procedures.load(filename, path)
            self.createTab(pandaData)
        else:
            self.newEmptyTab()

        # File Menu Actions
        self.actionExit.triggered.connect(self.Exit)
        self.actionLoad.triggered.connect(self.loadData)
        self.actionSave.triggered.connect(self.saveData)
        self.actionOpen.triggered.connect(self.openData)
        self.actionClose_Tab.triggered.connect(self.closeTab)
        self.actionNew_Tab.triggered.connect(self.newEmptyTab)

        # Edit Menu Actions
        self.actionDelete.triggered.connect(self.deleteData)
        self.actionUndo.triggered.connect(self.undo)
        self.actionRedo.triggered.connect(self.redo)

        # Operations Menu Actions
        self.actionClear_Whitespace.triggered.connect(self.clearWhitespace)
        self.actionRemove_Non_Numberic.triggered.connect(self.removeNonNumeric)
        self.actionCorrect_Date_Format.triggered.connect(self.correctDateFormat)
        self.actionDisperse_Ranks_By_Program.triggered.connect(self.ranksByProgram)
        self.actionFind_and_Replace.triggered.connect(self.findAndReplace)

        # Run button
        self.runButton.clicked.connect(self.runCommand)

    def runCommand(self):
        """
        Handles all python code entered into the text area on the bottom half of the application.
        It automatically converts df, df2, df3, etc.. into valid code representing the open sheets,
        based on the index of their tab.

        You will be notified if the code has any syntax errors via a message box.
        """


        command = self.textEdit.toPlainText()

        if command == '':
            self.notifyUser("No command entered.")
        else:

            command = re.sub( r'df(?!\d)' , 'self.getPanda(0).df', command)

            match = re.findall(r'df\d', str(command))
            if match is not None:
                for x in match:
                    num = int(re.search(r'\d', x)[0]) - 1
                    command = command.replace( x , 'self.getPanda(' + str(num) + ').df')

            try:
                exec(command)
                self.getCurrentPanda().layoutChanged.emit()
                self.getCurrentPanda().appendState()
            
            except:
                errorMsg = 'There was a problem with the command entered. ' + \
                           'See stack trace: \n\n' + traceback.format_exc()
                self.notifyUser(errorMsg)

    def undo(self):
        self.getCurrentPanda().backwardState()

    def redo(self):
        self.getCurrentPanda().forwardState()

    def notifyUser(self, message):
        """
        A simple message box to tell the user something.
        They cannot proceed until they press 'Ok'.

            :param message: 
                The message you want to share with the user.
        """   


        msg = QtWidgets.QMessageBox(self)
        msg.setText(message)
        msg.exec_()

    #region Tab Functionality
    def getCurrentView(self):
        """
        Retrieves the currently visible tab's TableView.

        Returns:
            PyQt5 QTableView
        """


        currentTab = self.tabWidget.currentWidget()
        
        View = currentTab.findChild(QtWidgets.QTableView)

        return View

    def getCurrentPanda(self):
        """
        Retrieves the currently visible tab's PandasTable model.

        Returns:
            PandasTable model
        """


        view = self.getCurrentView()

        if view != None:
            panda = view.model()
            return panda
        else:
            return None

    def getPanda(self, index):
        """
        Retrieves the PandasTable model at the given tab index.

            :param index: 
                The index of the tab of the desired PandasTable
        
        Returns:
            PandasTable model
        """
        

        tab = self.tabWidget.widget(index)
        view = tab.findChild(QtWidgets.QTableView)
        panda = view.model()
        return panda

    def createTab(self, pandaData):
        """
        Creates a new tab with the given PandasTable model displayed in a TableView.
        Automatically appends it to the end of the tab bar.

            :param panda: 
                The PandasTable model you wish to display
        
        """

        # We create the panda here so we can set the parent to be the tab
        # When we kill the tab, the panda dies as well

        tab = QtWidgets.QWidget(self.tabWidget)
        tab.setObjectName("tab")
        verticalLayout = QtWidgets.QVBoxLayout(tab)
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.setSpacing(10)
        verticalLayout.setObjectName("verticalLayout")
        tableView = QtWidgets.QTableView(tab)
        tableView.setHorizontalHeader(Model.PandaTableHorizontalHeader(parent=tableView))
        tableView.setSortingEnabled(False)
        tableView.setObjectName("tableView")
        tableView.verticalHeader().setDefaultSectionSize(30)
        tableView.verticalHeader().setMinimumSectionSize(30)
        verticalLayout.addWidget(tableView)
        panda = Model.PandasTable(pandaData, parent=tab)
        tableView.setModel(panda)
        self.tabWidget.addTab(tab, "Tab")

    def newEmptyTab(self):
        """
        Creates a new tab without any data and axi labels from 1-100.
        """
        pandaData = pd.DataFrame(columns=list(map(str, range(0,100))), index=range(0,100))
        self.createTab(pandaData)

    def closeTab(self):
        """
        Closes the active tab, releases the memory, and deletes the C++ object.

        TODO: Isn't releasing the memory for some reason.
        """

        self.tabWidget.currentWidget().deleteLater()
        self.tabWidget.removeTab(self.tabWidget.currentIndex())
    #endregion

    #region File Menu
    def loadData(self):
        """
        Prompts the user to select a file to load into view. Deletes all other open tabs upon successful load.
        If an invalid path is given, the user is notified.
        """


        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getcwd(), 'CSV(*.csv)')

        # If a file was specified, load it up. If not, tell the user to pick a valid file
        if path[0] != '':

            if os.path.exists(path[0]) and os.path.getsize(path[0]):

                filepath, filename = os.path.split(path[0])
                pandaData = procedures.load(filename, filepath)

                while self.tabWidget.count() != 0:
                    self.closeTab()
                self.createTab(pandaData)

            else:
                self.notifyUser("Please pick a valid file.")

    def openData(self):
        """
        Prompts the user for a file to load into view, instantiates a new PandasTable 
        with the user's selection and opens it in a new tab. If an invalid path is given, the user is notified.
        """


        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getcwd(), 'CSV(*.csv)')

        # If a file was specified, load it up. If not, tell the user to pick a valid file
        if path[0] != '':

            if os.path.exists(path[0]) and os.path.getsize(path[0]):

                filepath, filename = os.path.split(path[0])
                pandaData = procedures.load(filename, filepath)

                self.createTab(pandaData)

            else:
                self.notifyUser("Please pick a valid file.")

    def saveData(self):
        """
        Prompts the user to pick a place to save the active PandasTable as a CSV file
        and passes the location to the active PandasTable to save to disk.
        """


        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', os.getcwd())

        if path[0] != '':
    
            filepath, filename = os.path.split(path[0])

            if os.path.exists(filepath):

                self.getCurrentPanda().saveData(path[0])

    def Exit(self):
        """
        Quits the application.
        """   
        

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
        """
        Prompts the user to select a column of unique values 
        (programs) to distribute the other column's (ranks) values into.

        Passes the selected values to the active Panda to deal with.
        """

        # Prompts user and gets a set of values
        ranks, programs = Model.RanksByProgramsDialogBox.getResults(self.getCurrentPanda(), self)

        # Passes values to PandaModel to be validated and acted upon
        self.getCurrentPanda().ranksByPrograms(ranks, programs)

    def findAndReplace(self):
        """
        Prompts the user to input text to search for and text to replace it with.
        Accepts regex by default.

        Passes the given values to the active Panda to deal with.
        """

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
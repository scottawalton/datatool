import os
import random
import string as st

import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtGui

import procedures

class PandasTable(QtCore.QAbstractTableModel):
    """
    An instance of a pandas dataframe that can be displayed in a PyQt TableView,
    as well as have procedures applied to it. It requires a dataframe to be initialized.

        :param data:
            The pandas dataframe you wish to load in
    """

    #region Constructor
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)

        # Store the given parent in an attribute so don't have to pass it to every function
        self.parent = parent

        # Store the pandas dataframe in an attribute
        self.df = data

        # Initialize the Undo/Redo stack of states
        self.initiateStack()

    def rowCount(self, parent):
        return len(self.df)

    def columnCount(self, parent):
        return len(self.df.columns)

    def data(self, index, role):
        """
        This is called whenever a layoutChanged or dataChanged signal is emitted.
        Returns the data stored in the df attribute at the given index.

            :param index:
                Passed to us by the TableView, a PyQt QModelIndex
            :param role:
                Passed to us by the TableView, a Qt.DisplayRole
        """

        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.df.iat[row, column]
            if pd.isnull(value):
                return str('')
            else:
                return str(value)

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        Interprets the data we enter when we submit data through the TableView.
        Appends a state to the stack.

            :param index:
                A QIndexModel specifying the coordinates of the changed cell.
            :param value:
                A QItemModel storing the new data.
            :param role=QtCore.Qt.EditRole:
                The role of the passed signal.
        """

        if role == QtCore.Qt.EditRole:
            col = index.column()
            row = index.row()
            try:
                self.df.iat[row, col] = value
                self.dataChanged.emit(index, index)
                self.appendState()
                return True
            except:
                return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.df.columns[section]
            else:
                return section
    #endregion

    #region State Functionality

    # Implements undo-redo functionality with a stack of states
    def initiateStack(self):
        self.stateStack = [self.df.copy()]
        self.stateStackCurrent = 0

    def appendState(self):
        # If a chance is made on a state other than the most recent one,
        # that state becomes the most recent one.
        if self.stateStackCurrent == len(self.stateStack) -1:
            self.stateStack.append(self.df.copy())
            self.stateStackCurrent += 1
        else:
            self.stateStackCurrent += 1
            self.stateStack = self.stateStack[:self.stateStackCurrent]
            self.stateStack.append(self.df.copy())

    def backwardState(self):

        # This block checks if the latest state is saved.
        # If it isn't, we add it to the stack
        if self.stateStackCurrent == len(self.stateStack) -1 and not \
                self.stateStack[self.stateStackCurrent].equals(self.df):
            self.appendState()
            self.stateStackCurrent -= 1
            self.df = self.stateStack[self.stateStackCurrent].copy()
            self.layoutChanged.emit()

        elif self.stateStackCurrent != 0:
            self.stateStackCurrent -= 1
            self.df = self.stateStack[self.stateStackCurrent].copy()
            self.layoutChanged.emit()

        else:
            self.parent.window().notifyUser("Already at earliest change.")
            self.layoutChanged.emit()

    def forwardState(self):
        if self.stateStackCurrent != (len(self.stateStack) - 1):
            self.stateStackCurrent += 1
            self.df = self.stateStack[self.stateStackCurrent].copy()
            self.layoutChanged.emit()
        else:
            self.parent.window().notifyUser("Already at most recent change.")

    #endregion

    #region Operations
    def saveData(self, path):
        self.df.to_csv(path, quoting=1, index=False)

    def deleteData(self, selectionModel):
        """
        Deletes the selected columns/rows from the table.
        Adds a state to the Undo/Redo stack and refreshes the view upon success.

            :param selectionModel:
                The current selection, supplied in a QItemSelectionModel
        """


        cols, rows = self.translateSelection(selectionModel)

        # If columns are selected, do the operation on each of them,
        if cols is not None:

            # python pandas method to drop the columns
            self.df = self.df.drop(cols, axis=1)
            self.layoutChanged.emit()
            selectionModel.clear()
            self.appendState()

        # otherwise: check if rows are selected
        elif rows is not None:

            self.df = self.df.drop(rows)
            self.df = self.df.reset_index(drop=True)
            self.layoutChanged.emit()
            selectionModel.clear()
            self.appendState()

        else:
            self.parent.window().notifyUser("No columns or rows selected.")

    def translateSelection(self, selectionModel):
        """
        Translates a selection model into column labels and row indexes.

            :param selectionModel:
                A QItemSelectionModel


        Returns:
            A tuple of column names and row indexes
        """

        selectionColumns = selectionModel.selectedColumns()
        selectionRows = selectionModel.selectedRows()

        if selectionColumns != []:
            # loops through all selected columns
            colNames = []
            for i in selectionColumns:
                # gets the name of the column and appends it to the list
                colNames.append(self.df.columns.values[i.column()])

            return colNames, None
        if selectionRows != []:
            # loops through all selected rows
            rowIndexes = []
            for i in selectionRows:
                # append it to the list
                rowIndexes.append(i.row())

            return None, rowIndexes

        return None, None

    def insertBlank(self, selectionModel):
        """
        Inserts a blank row/column based on current selection.
        """

        columns, rows = self.translateSelection(selectionModel)

        if rows is not None:
            rowMaxIndex = max(rows) + .5
            row = pd.DataFrame(columns=self.df.columns.values, index=[rowMaxIndex])
            self.df = self.df.append(row, ignore_index=False)
            self.df = self.df.sort_index().reset_index(drop=True)
            self.appendState()

        if columns is not None:
            if len(columns) > 1:
                colMaxIndex = 0
                for x in columns:
                    val = int(((self.df.columns == x).nonzero())[0][0])
                    if val > colMaxIndex:
                        colMaxIndex = val
            else:
                colMaxIndex = int(((self.df.columns == columns[0]).nonzero())[0][0])

            try:
                colName = str(random.choice(st.ascii_letters))
                self.df.insert(loc=colMaxIndex + 1, value=pd.Series(), column=colName)
                self.appendState()
            except ValueError:
                colName = str(random.choice(st.ascii_letters.pop(colName)))
                self.df.insert(loc=colMaxIndex + 1, value=pd.Series(), column=colName)
                self.appendState()

            self.layoutChanged.emit()

    def duplicateSelected(self, selectionModel):
        """
        Duplicates the selected row or column and inserts it directly after.
        """

        columns, rows = self.translateSelection(selectionModel)

        if rows is not None:
            rowMaxIndex = max(rows) + .5
            row = self.df.ix[rows]
            self.df = self.df.append(row, ignore_index=False)
            self.df = self.df.sort_index().reset_index(drop=True)
            self.appendState()

        if columns is not None:
            if len(columns) > 1:
                colMaxIndex = 0
                for x in columns:
                    val = int(((self.df.columns == x).nonzero())[0][0])
                    if val > colMaxIndex:
                        colMaxIndex = val
            else:
                colMaxIndex = int(((self.df.columns == columns[0]).nonzero())[0][0])

            try:
                colName = str(random.choice(st.ascii_letters))
                if len(columns) > 1:
                    for i in columns:
                        colName = '_' + i
                        self.df.insert(loc=colMaxIndex + 1, value=self.df[i], column=colName)
                    self.appendState()
            except:
                pass

            self.layoutChanged.emit()

    def clearWhitespace(self, selectionModel):
        """
        Removes all newlines, leading and trailing whitespace, carriage returns, and invisible
        tab-breaks from the selected column(s).
        If no columns are selected, acts on entire dataframe. \n
        Adds a state to the Undo/Redo stack and refreshes the view upon success.
        """

        selection = self.translateSelection(selectionModel)
        # If columns are selected, do the operation on each of them,
        if selection[0] is not None:
            procedures.strip_whitespace(self.df, column=selection[0])
            self.appendState()
        # otherwise: do it on the entire dataframe
        else:
            self.df = procedures.strip_whitespace(self.df)
            self.appendState()

        selectionModel.clear()

    def removeNonNumeric(self, selectionModel):
        """
        Removes everything but numeric characters from a column. \n
        A column selection is required; user is alerted upon failure to select a column. \n
        Adds a state to the Undo/Redo stack and refreshes the view upon success.
        """

        selection = self.translateSelection(selectionModel)

        # If columns are selected, do the operation on each of them,
        if selection[0] is not None:
            procedures.remove_non_numeric(self.df, selection[0])
            self.appendState()
        # otherwise: let the user know they need to select a column
        else:
            self.parent.window().notifyUser("No column selected.")

        selectionModel.clear()

    def correctDateFormat(self, selectionModel):
        """
        Accepts almost any date format and convert it to MM/DD/YYYY. \n
        A column selection is required; user is alerted upon failure to select a column. \n
        Adds a state to the Undo/Redo stack and refreshes the view upon success.
        """

        selection = self.translateSelection(selectionModel)

        if selection[0] is not None:
            procedures.fix_dates(self.df, selection[0])
            self.appendState()
        else:
            self.parent.window().notifyUser("No column selected.")

        selectionModel.clear()

    def ranksByPrograms(self, ranks, programs):
        """
        Distributes values in ranks column into columns created based on unique values in programs column. \n
        Adds a state to the Undo/Redo stack and refreshes the view upon success.

            :param ranks:
                The values that need to be distributed.
            :param programs:
                The values to create columns of.
        """

        if ranks == '' or programs == '':
            self.parent.window().notifyUser("One or more of the selections are invalid.")

        elif ranks is None or programs is None:
            pass

        else:
            self.df = procedures.fix_ranks(self.df, ranks, programs)
            self.appendState()
            self.layoutChanged.emit()

    def findAndReplace(self, findText, replaceText, selectionModel):
        """
        Finds all findText in currently selected columns and replaces with given replaceText.
        Regex is enabled by default. \n

        Adds a state to the Undo/Redo stack and refreshes the view upon success.

            :param findText:
                The text to search for.
            :param replaceText:
                The text to replace the found text with.

        If no selection is given, it will prompt if you wish to apply to the entire dataframe.
        """

        selection = self.translateSelection(selectionModel)

        if findText is None and replaceText is None:
            return

        if selection[0] is not None:
            for col in selection[0]:
                self.df[col] = self.df[col].str.replace(findText, replaceText, regex=True)
            self.appendState()
        else:
            # TODO: This should all be passed to the Controller. Needs revision.
            reply = QtWidgets.QMessageBox.question(self.parent, 'No Columns Selected',
                'There are no selected columns. Would you like to apply this operation to the entire sheet?',
                QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.df.replace({findText : replaceText}, regex=True, inplace=True)
                self.appendState()

            else:
                pass

        selectionModel.clear()

    def newRowsOnSeparator(self, column, separator):
        """
        Creates new rows from the given column determined by the given separator.

        :param column:
            The column to pull data from.

        :param separator:
            The characters that separate the data.
        """

        if separator is None:
            return

        self.df = procedures.tidy_split(self.df, column, separator)
        self.appendState()

    #endregion

class PandaTableHorizontalHeader(QtWidgets.QHeaderView):
    """
    A custom implementation of a QHeaderView that allows us to doubleclick and edit
    the column names. This is passed to our TableView upon tab creation.

        :todo:
            Allow dragging and dropping columns when Alt modifier is pressed
    """

    def __init__(self, orientation=QtCore.Qt.Horizontal, parent=None):
        QtWidgets.QHeaderView.__init__(self, orientation, parent)
        self.setSectionsClickable(True)
        self.line = QtWidgets.QLineEdit(parent=self.viewport())  #Create
        self.line.setAlignment(QtCore.Qt.AlignTop)
        self.line.setHidden(True) # Hide it till its needed
        self.sectionedit = 0
        self.sectionDoubleClicked.connect(self.editHeader)
        self.line.editingFinished.connect(self.doneEditing)
        self.sectionPressed.connect(self.handlePressed)
        self.sectionMoved.connect(self.handleMoved)

    def handleMoved(self, logical, visualOld, visualNew):
        """
        Changes order of columns in underlying model to match the visual appearance
        """
        self.setSectionsMovable(False)
        cols = list(self.model().df.columns.values)

        cols[logical], cols[visualNew] = cols[visualNew], cols[logical]

        self.model().df = self.model().df[cols]
        self.model().appendState()
        self.model().layoutChanged.emit()

    def handlePressed(self):
        """
        Allows us to move the column if the Alt modifier is pressed.
        """
        modifier = QtGui.QGuiApplication.keyboardModifiers()
        if modifier == QtCore.Qt.AltModifier:
            self.setSectionsMovable(True)

    def doneEditing(self):
        """
        Called when the user presses Enter in the QLineEdit
        Note: is called twice every time because of bug in Qt
        """

        self.line.setHidden(True)
        oldName = self.model().df.columns.values[self.sectionedit]
        newName = str(self.line.text())
        # this is required because of a bug with Qt where
        # the editing finished signal is called twice
        if oldName != newName:
            # Cannot rename a column to another column's name
            if not newName in self.model().df.columns.values:
                self.model().df.rename(columns={oldName: newName}, inplace=True)
                self.model().appendState()
                self.model().layoutChanged.emit()
                self.setCurrentIndex(QtCore.QModelIndex())
                self.parentWidget().setFocus()
            else:
                self.window().notifyUser('Column name already exists.')

    def editHeader(self, section):
        """
        Makes the existing QLineEdit visible and changes the geometry to fit the header cell.
        Called when the user double clicks a header cell.

            :param section:
                The index of the header cell
        """

        # Sets up the geometry for the line edit
        edit_geometry = self.line.geometry()
        edit_geometry.setWidth(self.sectionSize(section))
        edit_geometry.moveLeft(self.sectionViewportPosition(section))
        self.line.setGeometry(edit_geometry)

        self.line.setText(self.model().df.columns.values[section])
        self.line.setHidden(False)
        self.line.setFocus()
        self.line.selectAll()
        self.sectionedit = section

#region Operation Models

class RanksByProgramsDialogBox(QtWidgets.QDialog):
    """
    A dialog box to get the information required by the ranksbyPrograms function.
    """

    def __init__(self, pandaTable, parent):
        """
        Initializes the UI and sets the two dropdowns to display column names of the active Panda.
        """

        QtWidgets.QDialog.__init__(self)

        self.df = pandaTable

        self.layout = QtWidgets.QGridLayout(self)
        self.rankSelect = QtWidgets.QComboBox()
        self.rankSelect.addItems(self.df.columns.values)
        self.programSelect = QtWidgets.QComboBox()
        self.programSelect.addItems(self.df.columns.values)
        self.layout.addWidget(self.programSelect, 1, 1)
        self.layout.addWidget(QtWidgets.QLabel('Program Column:'), 1, 0)
        self.layout.addWidget(self.rankSelect, 0, 1)
        self.layout.addWidget(QtWidgets.QLabel('Rank Column:'), 0, 0)
        self.confirm = QtWidgets.QPushButton('Confirm')
        self.layout.addWidget(self.confirm, 3, 1)
        self.confirm.clicked.connect(self.accept)
        self.cancel = QtWidgets.QPushButton('Cancel')
        self.cancel.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel, 3, 0)
        self.setWindowTitle('Ranks by Program')
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    def getResults(self, parent=None):
        """
        Returns the user's input
        """

        dialog = RanksByProgramsDialogBox(self.df, parent)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            return dialog.rankSelect.currentText(), dialog.programSelect.currentText()
        else:
            return None, None

class NewRowsOnSeparatorDialogBox(QtWidgets.QDialog):
    """
    A dialog box to get the information required by the newRowsOnSeparator function.
    """

    def __init__(self, pandaTable, parent):
        """
        Initializes the UI and sets the two dropdowns to display column names of the active Panda.
        """

        QtWidgets.QDialog.__init__(self)

        self.df = pandaTable

        self.layout = QtWidgets.QGridLayout(self)
        self.columnSelect = QtWidgets.QComboBox()
        self.columnSelect.addItems(self.df.columns.values)
        self.layout.addWidget(self.columnSelect, 0, 1)
        self.layout.addWidget(QtWidgets.QLabel('Column:'), 0, 0)
        self.separatorLine = QtWidgets.QLineEdit()
        self.layout.addWidget(self.separatorLine, 1, 1)
        self.layout.addWidget(QtWidgets.QLabel('Separator:'), 1, 0)
        self.confirm = QtWidgets.QPushButton('Confirm')
        self.layout.addWidget(self.confirm, 3, 1)
        self.confirm.clicked.connect(self.accept)
        self.cancel = QtWidgets.QPushButton('Cancel')
        self.cancel.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel, 3, 0)
        self.setWindowTitle('New Rows from Column by Separator')
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    def getResults(self, parent=None):
        """
        Returns the user's input
        """

        dialog = NewRowsOnSeparatorDialogBox(self.df, parent)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            return dialog.columnSelect.currentText(), dialog.separatorLine.text()
        else:
            return None, None

class FindAndReplaceDialogBox(QtWidgets.QDialog):
    """
    A dialog box to retrieve the two text values required by the findAndReplace function.
    """

    # TODO: Add Find only option

    def __init__(self, parent):
        """
        Initializes the UI and sets the properties.
        """

        QtWidgets.QDialog.__init__(self)

        self.findText = QtWidgets.QLineEdit()
        self.replaceText = QtWidgets.QLineEdit()
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.findText, 0, 1)
        self.layout.addWidget(QtWidgets.QLabel('Text to Find:'), 0, 0)
        self.layout.addWidget(self.replaceText, 1, 1)
        self.layout.addWidget(QtWidgets.QLabel('Text to Replace with:'), 1, 0)
        self.confirm = QtWidgets.QPushButton('Confirm')
        self.layout.addWidget(self.confirm, 3, 1)
        self.confirm.clicked.connect(self.accept)
        self.cancel = QtWidgets.QPushButton('Cancel')
        self.cancel.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel, 3, 0)
        self.setWindowTitle('Find and Replace')
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    def getResults(self, parent=None):
        """
        Returns the user's input
        """

        dialog = FindAndReplaceDialogBox(parent)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            return dialog.findText.text(), dialog.replaceText.text()

        return None, None

#endregion

#region Software Models

class RainmakerDialogBox(QtWidgets.QDialog):
    """
    A dialog box to get the location of the exported file, extra reports, and the date.
    Anything and everything may be left blank.
    """

    def __init__(self, parent):
        """
        Initializes the UI and sets the properties.
        """

        QtWidgets.QDialog.__init__(self)

        self.mainExportLine = QtWidgets.QLineEdit()
        self.parentsNamesLine = QtWidgets.QLineEdit()
        self.customFieldsLine = QtWidgets.QLineEdit()
        self.mainButton = QtWidgets.QPushButton()
        self.parentButton = QtWidgets.QPushButton()
        self.customButton = QtWidgets.QPushButton()
        self.mainButton.clicked.connect(self.getMain)
        self.parentButton.clicked.connect(self.getParent)
        self.customButton.clicked.connect(self.getCustom)
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.mainExportLine, 0, 1)
        self.layout.addWidget(self.mainButton, 0, 2)
        self.layout.addWidget(QtWidgets.QLabel('Main File:'), 0, 0)
        self.layout.addWidget(self.parentsNamesLine, 1, 1)
        self.layout.addWidget(self.parentButton, 1, 2)
        self.layout.addWidget(QtWidgets.QLabel('Parents Names:'), 1, 0)
        self.layout.addWidget(self.customFieldsLine, 2, 1)
        self.layout.addWidget(self.customButton, 2, 2)
        self.layout.addWidget(QtWidgets.QLabel('Custom Fields:'), 2, 0)
        self.confirm = QtWidgets.QPushButton('Confirm')
        self.layout.addWidget(self.confirm, 4, 1)
        self.confirm.clicked.connect(self.accept)
        self.cancel = QtWidgets.QPushButton('Cancel')
        self.cancel.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel, 4, 0)
        self.setWindowTitle('Rainmaker Export Handler')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.main = None
        self.parent = None
        self.custom = None

    def getMain(self):
        """
        Prompts the user for the main export file (provided by RM)
        """
        self.main = QtWidgets.QFileDialog.getOpenFileName(self, 'Select File', os.getcwd(), 'All Support Files (*.xls *.csv *.xlsx)')
        self.mainExportLine.setText(self.main[0])

    def getParent(self):
        """
        Prompts the user for the Parents Names export file.
        (expected to only contain ID and Parents Names)
        """
        self.parent = QtWidgets.QFileDialog.getOpenFileName(self, 'Select File', os.getcwd(), 'All Support Files (*.xls *.csv *.xlsx)')
        self.parentsNamesLine.setText(self.parent[0])

    def getCustom(self):
        """
        Prompts the user for the Custom Fields export file.
        (expected to only contain ID and Custom Fields)
        """
        self.custom = QtWidgets.QFileDialog.getOpenFileName(self, 'Select File', os.getcwd(), 'All Support Files (*.xls *.csv *.xlsx)')
        self.customFieldsLine.setText(self.custom[0])

    def getResponse(self, parent=None):
        dialog = RainmakerDialogBox(parent)
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:

            if dialog.main is not None and dialog.parent is not None and dialog.custom is not None:
                return dialog.main[0], dialog.parent[0], dialog.custom[0]
            elif dialog.main is not None and dialog.parent is not None and dialog.custom is None:
                return dialog.main[0], dialog.parent[0], None
            elif dialog.main is not None and dialog.parent is None and dialog.custom is None:
                return dialog.main[0], None, None

        return None, None, None

#endregion

#region Help Dialog

class HelpModel(QtWidgets.QDialog):
    """
    A help wiki to teach the user about the program and how to use it.
    """

    def __init__(self, parent=None):
        """
        Initializes the UI and sets the properties.
        """

        QtWidgets.QDialog.__init__(self)
        self.resize(1000, 700)

        self.topicList = QtWidgets.QListWidget()
        self.topicList.setFixedWidth(200)
        self.topicList.addItem("General Use")
        self.topicList.addItem("File Menu")
        self.topicList.addItem("Operations")
        self.topicList.currentItemChanged.connect(self.displayHelp)

        self.pageView = QtWidgets.QTextBrowser()
        self.pageView.setText("Work in progress")

        self.closeButton = QtWidgets.QPushButton("Close")
        self.closeButton.clicked.connect(self.reject)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.topicList, 0, 0)
        self.layout.addWidget(self.pageView, 0, 1)
        self.layout.addWidget(self.closeButton, 1, 1)
        self.setWindowTitle('Help')

        self.helpDict = {
            "General Use": "General Use \n\n" +\
                            "To start using the program, you'll want to load a file. " +\
                            "You can do this from File > Load. \n\nIf you'd like to open additional files"+\
                            "afterwards, you can use File > Open. \n\nDouble click in any cell to edit the data it contains. \n"+\
                            "You can edit column names by double clicking on them. You can move columns by holding the Alt key and dragging the headers."+\
                            "\n\nYou may reference any open tab as 'df' for use in the python code entry box.\n"+\
                            "This means that the first tab would be df, the second df2, the third df3, etc.."+\
                            "\n\nYou can use Cnt+Z and Cnt+Y to undo and redo, respectively."+\
                            "\n\nWhen you're finished working and you'd like to save your file, you can do so from File > Save.",
            "File Menu": "Load -- Clears all other open windows and opens the selected file. \n\n"+\
                          "Open -- Opens the selected file as the newest tab. \n\n"+\
                          "Save -- Saves the visible sheet at the given location with the given name.",

            "Operations": "Find and Replace -- Searches the selected area for the find text and replaces it with the replace text. Accepts Regex.. \n\n"+\
                          "Correct Date Format -- Converts any date format to MM-DD-YYYY. \n\n"+\
                          "Remove Non-Numeric -- Removes all alphasymbolic characters from the selected area.",
        }

    def help(self, parent=None):
        """
        Present knowledge to the user
        """

        dialog = HelpModel(parent)
        dialog.exec_()
        return

    def displayHelp(self):
        """
        Gets active selection and queries dictionary for linked help text.
        """
        category = self.topicList.currentItem().text()
        helpText = self.helpDict.get(category, "General Use")
        self.pageView.setText(helpText)

#endregion
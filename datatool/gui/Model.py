
from PyQt5 import QtCore, QtWidgets, QtGui
import os
import sys
import pandas as pd
import numpy as np
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
                self.df.iloc[row][col] = value
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
        self.stateStack.append(self.df.copy())
        self.stateStackCurrent += 1
    
    def backwardState(self):
        if self.stateStackCurrent != 0:
            self.stateStackCurrent -= 1
            self.df = self.stateStack[self.stateStackCurrent]
            self.layoutChanged.emit()
        else:
            QtWidgets.QMessageBox.about(self.parent, "Notice" , "Already at earliest change." )
            self.layoutChanged.emit()

    def forwardState(self):
        if self.stateStackCurrent != (len(self.stateStack) - 1):
            self.stateStackCurrent += 1
            self.df = self.stateStack[self.stateStackCurrent]
            self.layoutChanged.emit()
        else:
            QtWidgets.QMessageBox.about(self.parent, "Notice", "Already at most recent change.")

    #endregion

    #region Operations
    def saveData(self, path):
        self.df.to_csv(path[0], quoting=1, index=False)

    def deleteData(self, selectionModel):
        """
        Deletes the selected columns/rows from the table.
        Adds a state to the Undo/Redo stack and refreshes the view upon success.

            :param selectionModel: 
                The current selection, supplied in a QItemSelectionModel
        """


        cols, rows = self.translateSelection(selectionModel)       

        # If columns are selected, do the operation on each of them, 
        if cols != None:

            # python pandas method to drop the columns
            self.df = self.df.drop(cols, axis=1)
            self.layoutChanged.emit()
            selectionModel.clear()
            self.appendState()

        # otherwise: check if rows are selected
        elif rows != None:

            self.df = self.df.drop(rows)
            self.df = self.df.reset_index(drop=True)
            self.layoutChanged.emit()
            selectionModel.clear()
            self.appendState()
        
        else:
            QtWidgets.QMessageBox.about(self.parent, "Notice", "No columns or rows selected.")

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
        else:
            return None, None

    def clearWhitespace(self, selectionModel):
        """
        Removes all newlines, leading and trailing whitespace, carriage returns, and invisible tab-breaks from the selected column(s).
        If no columns are selected, acts on entire dataframe. \n
        Adds a state to the Undo/Redo stack and refreshes the view upon success.
        """

        selection = self.translateSelection(selectionModel)       
        # If columns are selected, do the operation on each of them, 
        if selection[0] != None:
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
        if selection[0] != None:
            procedures.clean_phones(self.df, selection[0])
            self.appendState()
        # otherwise: let the user know they need to select a column
        else:
            QtWidgets.QMessageBox.about(self.parent, "Notice", "No column selected.")

        selectionModel.clear()

    def correctDateFormat(self, selectionModel):
        """
        Accepts almost any date format and convert it to MM/DD/YYYY. \n
        A column selection is required; user is alerted upon failure to select a column. \n
        Adds a state to the Undo/Redo stack and refreshes the view upon success.
        """
        
        selection = self.translateSelection(selectionModel)

        if selection[0] != None:
            procedures.fix_dates(self.df, selection[0])
            self.appendState()
        else:
            QtWidgets.QMessageBox.about(self.parent, "Notice", "No column selected.")

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
            QtWidgets.QMessageBox.critical(self.parent, "Notice", "One or more of the selections are invalid.")
        
        elif ranks == None or programs == None:
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

        if selection[0] != None:
            for col in selection[0]:
                self.df[col] = self.df[col].str.replace(findText, replaceText, regex=True)
            self.appendState()
        else:
            reply = QtWidgets.QMessageBox.question(self.parent, 'No Columns Selected', \
                'There are no selected columns. Would you like to apply this operation to the entire sheet?',
                QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.df.replace({findText : replaceText}, regex=True, inplace=True)
                self.appendState()
            
            else:
                pass

        selectionModel.clear()
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
        cols  = list(self.model().df.columns.values)

        cols[logical], cols[visualNew] = cols[visualNew], cols[logical]

        self.model().df = self.model().df[cols]
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
        """

        self.line.setHidden(True)
        oldName = self.model().df.columns.values[self.sectionedit]
        newName = str(self.line.text())
        self.model().df.rename(columns={oldName: newName}, inplace=True)
        self.setCurrentIndex(QtCore.QModelIndex())
 
    def editHeader(self,section):
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

class FindAndReplaceDialogBox(QtWidgets.QDialog):
    """
    A dialog box to retrieve the two text values required by the findAndReplace function.
    """
    
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
            return dialog.findText.text() , dialog.replaceText.text()
        else:
            return None, None
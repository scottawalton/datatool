
from PyQt5 import QtCore, QtWidgets, QtGui
import os
import sys
import pandas as pd
import numpy as np
import procedures

# This is the model

class PandasTable(QtCore.QAbstractTableModel):
    #region Constructor
    def __init__(self, data, tabNumber=1, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.df = data

    def rowCount(self, parent):
        return len(self.df)

    def columnCount(self, parent):
        return len(self.df.columns)
    
    def data(self, index, role):
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
        if role == QtCore.Qt.EditRole:
            col = index.column()
            row = index.row()
            try:
                self.df.iloc[row][col] = value
                self.dataChanged.emit(index, index)
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
    
    def saveData(self, path):

        self.df.to_csv(path[0], quoting=1, index=False)

    def deleteData(self, selectionModel):

        cols, rows = self.translateSelection(selectionModel)       

        # If columns are selected, do the operation on each of them, 
        if cols != None:

            # python pandas method to drop the columns
            self.df = self.df.drop(cols, axis=1)
            self.layoutChanged.emit()
            selectionModel.clear()

        # otherwise: check if rows are selected
        elif rows != None:

            self.df = self.df.drop(rows)
            self.df = self.df.reset_index(drop=True)
            self.layoutChanged.emit()
            selectionModel.clear()
        
        else:
            msg = QtWidgets.QMessageBox()
            msg.setText("No columns or rows selected.")
            msg.exec()

    # Translates a selection model into column names
    # Eventually want to implement foreach functionality into this and refactor
    def translateSelection(self, selectionModel):

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

        cols = self.translateSelection(selectionModel)       
        # If columns are selected, do the operation on each of them, 
        if cols != None:
            for col in cols[0]:
                self.df = procedures.strip_whitespace(self.df, col)
        # otherwise: do it on the entire dataframe
        else:
            self.df = procedures.strip_whitespace(self.df)
        
        selectionModel.clear()

    def removeNonNumeric(self, selectionModel):

        cols = self.translateSelection(selectionModel)

        # If columns are selected, do the operation on each of them, 
        if cols != None:
            for col in cols[0]:
                procedures.clean_phones(self.df, col)
        # otherwise: let the user know they need to select a column
        else:
            msg = QtWidgets.QMessageBox()
            msg.setText("No column selected.")
            msg.exec()

        selectionModel.clear()

    def correctDateFormat(self, selectionModel):
        
        cols = self.translateSelection(selectionModel)

        # If columns are selected, do the operation on each of them, 
        if cols != None:
            for col in cols[0]:
                procedures.fix_zp_dates(self.df, col)
        # otherwise: let the user know they need to select a column
        else:
            msg = QtWidgets.QMessageBox()
            msg.setText("No column selected.")
            msg.exec()

        selectionModel.clear()
    
    def ranksByPrograms(self, ranks, programs):

        if ranks == '' or programs == '':
            msg = QtWidgets.QMessageBox()
            msg.setText("Both selecions need to be valid.")
            msg.exec()
        
        elif ranks == None or programs == None:
            pass

        else:
            procedures.fix_ranks(self.df, ranks, programs)
            self.layoutChanged.emit()

    def findAndReplace(self, findText, replaceText, selectionModel):
        #TODO: 
        pass

class RanksByProgramsDialogBox(QtWidgets.QDialog):
    
    def __init__(self, pandaTable, parent):
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
        dialog = RanksByProgramsDialogBox(self.df, parent)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            return dialog.rankSelect.currentText(), dialog.programSelect.currentText()
        else:
            return None, None

class FindAndReplaceDialogBox(QtWidgets.QDialog):
    
    def __init__(self, parent):
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
        dialog = FindAndReplaceDialogBox(parent)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            return dialog.findText.text() , dialog.replaceText.text()
        else:
            return None, None
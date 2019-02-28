# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/vesi/documents/bin/datatool/datatool/gui/View.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DataTool(object):
    def setupUi(self, DataTool):
        DataTool.setObjectName("DataTool")
        DataTool.resize(928, 778)
        self.centralwidget = QtWidgets.QWidget(DataTool)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabBarAutoHide(True)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout.addWidget(self.tabWidget)
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.runButton = QtWidgets.QPushButton(self.centralwidget)
        self.runButton.setWhatsThis("")
        self.runButton.setObjectName("runButton")
        self.verticalLayout.addWidget(self.runButton)
        DataTool.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(DataTool)
        self.statusbar.setObjectName("statusbar")
        DataTool.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(DataTool)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 928, 30))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuOperations = QtWidgets.QMenu(self.menubar)
        self.menuOperations.setObjectName("menuOperations")
        self.menuSoftware = QtWidgets.QMenu(self.menuOperations)
        self.menuSoftware.setObjectName("menuSoftware")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        DataTool.setMenuBar(self.menubar)
        self.actionExit = QtWidgets.QAction(DataTool)
        self.actionExit.setObjectName("actionExit")
        self.actionLoad = QtWidgets.QAction(DataTool)
        self.actionLoad.setObjectName("actionLoad")
        self.actionSave = QtWidgets.QAction(DataTool)
        self.actionSave.setObjectName("actionSave")
        self.actionClear_Whitespace = QtWidgets.QAction(DataTool)
        self.actionClear_Whitespace.setObjectName("actionClear_Whitespace")
        self.actionRemove_Non_Numberic = QtWidgets.QAction(DataTool)
        self.actionRemove_Non_Numberic.setObjectName("actionRemove_Non_Numberic")
        self.actionSplit_Phones = QtWidgets.QAction(DataTool)
        self.actionSplit_Phones.setObjectName("actionSplit_Phones")
        self.actionSplit_Emails = QtWidgets.QAction(DataTool)
        self.actionSplit_Emails.setObjectName("actionSplit_Emails")
        self.actionDisperse_Ranks_By_Program = QtWidgets.QAction(DataTool)
        self.actionDisperse_Ranks_By_Program.setObjectName("actionDisperse_Ranks_By_Program")
        self.actionNew_Rows_On_Separator = QtWidgets.QAction(DataTool)
        self.actionNew_Rows_On_Separator.setObjectName("actionNew_Rows_On_Separator")
        self.actionDisplay_Command_Prompt = QtWidgets.QAction(DataTool)
        self.actionDisplay_Command_Prompt.setObjectName("actionDisplay_Command_Prompt")
        self.actionCorrect_Date_Format = QtWidgets.QAction(DataTool)
        self.actionCorrect_Date_Format.setObjectName("actionCorrect_Date_Format")
        self.actionDelete = QtWidgets.QAction(DataTool)
        self.actionDelete.setObjectName("actionDelete")
        self.actionAdd_Column = QtWidgets.QAction(DataTool)
        self.actionAdd_Column.setObjectName("actionAdd_Column")
        self.actionAdd_Row = QtWidgets.QAction(DataTool)
        self.actionAdd_Row.setObjectName("actionAdd_Row")
        self.actionDuplicate = QtWidgets.QAction(DataTool)
        self.actionDuplicate.setObjectName("actionDuplicate")
        self.actionOpen = QtWidgets.QAction(DataTool)
        self.actionOpen.setObjectName("actionOpen")
        self.actionFind_and_Replace = QtWidgets.QAction(DataTool)
        self.actionFind_and_Replace.setObjectName("actionFind_and_Replace")
        self.actionUndo = QtWidgets.QAction(DataTool)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QtWidgets.QAction(DataTool)
        self.actionRedo.setObjectName("actionRedo")
        self.actionClose_Tab = QtWidgets.QAction(DataTool)
        self.actionClose_Tab.setObjectName("actionClose_Tab")
        self.actionNew_Tab = QtWidgets.QAction(DataTool)
        self.actionNew_Tab.setObjectName("actionNew_Tab")
        self.actionRainmaker = QtWidgets.QAction(DataTool)
        self.actionRainmaker.setObjectName("actionRainmaker")
        self.actionMindBody = QtWidgets.QAction(DataTool)
        self.actionMindBody.setObjectName("actionMindBody")
        self.actionZenPlanner = QtWidgets.QAction(DataTool)
        self.actionZenPlanner.setObjectName("actionZenPlanner")
        self.actionMemberSolutions = QtWidgets.QAction(DataTool)
        self.actionMemberSolutions.setObjectName("actionMemberSolutions")
        self.actionASF = QtWidgets.QAction(DataTool)
        self.actionASF.setObjectName("actionASF")
        self.actionPerfectMind = QtWidgets.QAction(DataTool)
        self.actionPerfectMind.setObjectName("actionPerfectMind")
        self.actionKickSite = QtWidgets.QAction(DataTool)
        self.actionKickSite.setObjectName("actionKickSite")
        self.actionHelp = QtWidgets.QAction(DataTool)
        self.actionHelp.setObjectName("actionHelp")
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionNew_Tab)
        self.menuFile.addAction(self.actionClose_Tab)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuSoftware.addAction(self.actionASF)
        self.menuSoftware.addAction(self.actionKickSite)
        self.menuSoftware.addAction(self.actionMemberSolutions)
        self.menuSoftware.addAction(self.actionMindBody)
        self.menuSoftware.addAction(self.actionPerfectMind)
        self.menuSoftware.addAction(self.actionRainmaker)
        self.menuSoftware.addAction(self.actionZenPlanner)
        self.menuOperations.addAction(self.actionFind_and_Replace)
        self.menuOperations.addAction(self.actionCorrect_Date_Format)
        self.menuOperations.addAction(self.actionDisperse_Ranks_By_Program)
        self.menuOperations.addAction(self.actionNew_Rows_On_Separator)
        self.menuOperations.addSeparator()
        self.menuOperations.addAction(self.actionClear_Whitespace)
        self.menuOperations.addAction(self.actionRemove_Non_Numberic)
        self.menuOperations.addSeparator()
        self.menuOperations.addAction(self.actionSplit_Phones)
        self.menuOperations.addAction(self.actionSplit_Emails)
        self.menuOperations.addSeparator()
        self.menuOperations.addAction(self.menuSoftware.menuAction())
        self.menuView.addAction(self.actionDisplay_Command_Prompt)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionAdd_Row)
        self.menuEdit.addAction(self.actionAdd_Column)
        self.menuEdit.addAction(self.actionDelete)
        self.menuEdit.addAction(self.actionDuplicate)
        self.menuHelp.addAction(self.actionHelp)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuOperations.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(DataTool)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(DataTool)

    def retranslateUi(self, DataTool):
        _translate = QtCore.QCoreApplication.translate
        DataTool.setWindowTitle(_translate("DataTool", "DataTool"))
        self.textEdit.setWhatsThis(_translate("DataTool", "Enter Python code here."))
        self.textEdit.setPlaceholderText(_translate("DataTool", "Enter Python code here."))
        self.runButton.setText(_translate("DataTool", "Run"))
        self.menuFile.setTitle(_translate("DataTool", "File"))
        self.menuOperations.setTitle(_translate("DataTool", "Operation"))
        self.menuSoftware.setTitle(_translate("DataTool", "Software"))
        self.menuView.setTitle(_translate("DataTool", "View"))
        self.menuEdit.setTitle(_translate("DataTool", "Edit"))
        self.menuHelp.setTitle(_translate("DataTool", "Help"))
        self.actionExit.setText(_translate("DataTool", "Exit"))
        self.actionExit.setShortcut(_translate("DataTool", "Ctrl+Q"))
        self.actionLoad.setText(_translate("DataTool", "Load"))
        self.actionSave.setText(_translate("DataTool", "Save"))
        self.actionSave.setShortcut(_translate("DataTool", "Ctrl+S"))
        self.actionClear_Whitespace.setText(_translate("DataTool", "Remove Whitespace"))
        self.actionClear_Whitespace.setToolTip(_translate("DataTool", "Removes leading and trailing whitespace, as well as all line-breaks"))
        self.actionRemove_Non_Numberic.setText(_translate("DataTool", "Remove Non-Numeric"))
        self.actionRemove_Non_Numberic.setToolTip(_translate("DataTool", "Removes everything but numbers from a column."))
        self.actionSplit_Phones.setText(_translate("DataTool", "Split Phones"))
        self.actionSplit_Phones.setToolTip(_translate("DataTool", "Splits a column of phones based on their suffix. E.g. (M), (C), (H)..."))
        self.actionSplit_Emails.setText(_translate("DataTool", "Split Emails"))
        self.actionSplit_Emails.setToolTip(_translate("DataTool", "Splits a column of comma separated emails into a max of 3 Email columns"))
        self.actionDisperse_Ranks_By_Program.setText(_translate("DataTool", "Ranks By Program"))
        self.actionDisperse_Ranks_By_Program.setToolTip(_translate("DataTool", "Creates new columns based on unique entries in a column (programs) and assigns values (ranks) respectively."))
        self.actionNew_Rows_On_Separator.setText(_translate("DataTool", "New Rows On Separator"))
        self.actionNew_Rows_On_Separator.setToolTip(_translate("DataTool", "Splits a column\'s values up over multiple identical rows."))
        self.actionDisplay_Command_Prompt.setText(_translate("DataTool", "Display Command Prompt"))
        self.actionCorrect_Date_Format.setText(_translate("DataTool", "Correct Date Format"))
        self.actionDelete.setText(_translate("DataTool", "Delete"))
        self.actionDelete.setToolTip(_translate("DataTool", "Deletes selected Row/Column"))
        self.actionDelete.setShortcut(_translate("DataTool", "Del"))
        self.actionAdd_Column.setText(_translate("DataTool", "Add Column"))
        self.actionAdd_Row.setText(_translate("DataTool", "Add Row"))
        self.actionDuplicate.setText(_translate("DataTool", "Duplicate"))
        self.actionOpen.setText(_translate("DataTool", "Open"))
        self.actionFind_and_Replace.setText(_translate("DataTool", "Find and Replace"))
        self.actionUndo.setText(_translate("DataTool", "Undo"))
        self.actionUndo.setShortcut(_translate("DataTool", "Ctrl+Z"))
        self.actionRedo.setText(_translate("DataTool", "Redo"))
        self.actionRedo.setShortcut(_translate("DataTool", "Ctrl+Y"))
        self.actionClose_Tab.setText(_translate("DataTool", "Close Tab"))
        self.actionClose_Tab.setShortcut(_translate("DataTool", "Ctrl+W"))
        self.actionNew_Tab.setText(_translate("DataTool", "New Tab"))
        self.actionRainmaker.setText(_translate("DataTool", "Rainmaker"))
        self.actionMindBody.setText(_translate("DataTool", "MindBody"))
        self.actionZenPlanner.setText(_translate("DataTool", "ZenPlanner"))
        self.actionMemberSolutions.setText(_translate("DataTool", "MemberSolutions"))
        self.actionASF.setText(_translate("DataTool", "ASF"))
        self.actionPerfectMind.setText(_translate("DataTool", "PerfectMind"))
        self.actionKickSite.setText(_translate("DataTool", "KickSite"))
        self.actionHelp.setText(_translate("DataTool", "Help"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DataTool = QtWidgets.QMainWindow()
    ui = Ui_DataTool()
    ui.setupUi(DataTool)
    DataTool.show()
    sys.exit(app.exec_())

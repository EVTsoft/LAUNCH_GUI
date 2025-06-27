import sys
from io import StringIO

from PyQt5 import QtCore

import resources
import subprocess

from PyQt5.QtCore import Qt, QObject, QSettings
from PyQt5.QtGui import QBrush, QIcon, QPixmap, QFont, QColor, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMdiSubWindow, QPlainTextEdit, \
    QTreeWidgetItem, QAction, QTextEdit
from modfab_ui import Ui_mainWindow
from CLaunch import CLaunch


# class EmittingStream(QtCore.QObject):
#
#     textWritten = QtCore.pyqtSignal(str)
#
#     def write(self, text):
#         self.textWritten.emit(str(text))
#
#
# class QDbgConsole(QTextEdit):
#     '''
#     A simple QTextEdit, with a few pre-set attributes and a file-like
#     interface.
#     '''
#     # Feel free to adjust those
#     WIDTH = 480
#     HEIGHT = 320
#
#     def __init__(self, parent=None):
#         super(QDbgConsole, self).__init__(parent)
#
#         self._buffer = StringIO()
#
#         self.setReadOnly(True)
#
#     def write(self, msg):
#         '''Add msg to the console's output, on a new line.'''
#         self.insertPlainText(msg)
#         # Autoscroll
#         self.moveCursor(QTextCursor.End)
#         self._buffer.write(msg)
#
#     def __getattr__(self, attr):
#         '''
#         Fall back to the buffer object if an attribute can't be found.
#         '''
#         return getattr(self._buffer, attr)

class Window(QMainWindow, Ui_mainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('Team-R', 'MODFAB')
        self.setupUi(self)
        self.setGeometry(200, 100, 1500, 800)
        self.tableWidget.setGeometry(595, 0, 500, 585)
        self.mdiArea.setGeometry(420, 0, 900, 585)
        self.setCentralWidget(self.splitter_2)
        self.zapusk = None
        self.state = None
        self.report_state = None
        self.launch_file_name = ''
        self.treeWidget.setHeaderLabel('')
        spec_icon = QIcon(QPixmap(':icons/spec.png'))
        mod_icon = QIcon(QPixmap(':icons/mod.png'))
        pack_type_icon = QIcon(QPixmap(':icons/pack_type.png'))
        stanok_icon = QIcon(QPixmap(':icons/stanok.png'))
        self.spec_action = QAction(spec_icon, 'Полная спецификация', self)
        self.mod_action = QAction(mod_icon, 'Спецификация по модулям', self)
        self.pack_type_action = QAction(pack_type_icon, 'Спецификация по типам упаковки', self)
        self.stanok_action = QAction(stanok_icon, 'Спецификация по станкам', self)
        self.toolBar.addAction(self.spec_action)
        self.toolBar.addAction(self.mod_action)
        self.toolBar.addAction(self.pack_type_action)
        self.toolBar.addAction(self.stanok_action)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.monospace_font = QFont('Courier', 8)
        self.text.setFont(self.monospace_font)
        self.text.setGeometry(0, 0, 1500, 480)
        self.text.setLineWrapMode(0)
        self.connect_signals()
        self.restore_state()

    def connect_signals(self):
        self.action.triggered.connect(self.open_file_selection)
        self.treeWidget.itemClicked.connect(self.test)
        self.spec_action.triggered.connect(self.print_rpt)
        self.mod_action.triggered.connect(self.print_rpt_allMS)
        self.pack_type_action.triggered.connect(self.print_rpt_SMD_pack)
        self.stanok_action.triggered.connect(self.print_rpt_stanoks)

    def restore_state(self):
        geometry = self.settings.value('windowGeometry')
        if geometry:
            self.setGeometry(geometry)
        window_state = self.settings.value('windowState')
        if window_state:
            self.setWindowState(window_state)
        self.launch_file_name = self.settings.value('lastOpenedFile')
        if self.launch_file_name:
            subwindow = QMdiSubWindow()
            subwindow.setWindowTitle(self.launch_file_name)
            subwindow.setObjectName(self.launch_file_name)
            self.mdiArea.addSubWindow(subwindow)
            subwindow.setGeometry(0, 0, 887, 671)
            subwindow.showMaximized()
            self.mdiArea.setActiveSubWindow(subwindow)
            self.zapusk = CLaunch(self.launch_file_name)
            self.launch_tree()
        self.state = self.settings.value('lastState')
        if self.state:
            self.statusbar.showMessage(self.state)
        self.report_state = self.settings.value('lastReportState')
        if self.report_state:
            if self.report_state == 'zapusk':
                self.print_rpt()
            elif self.report_state == 'mod':
                self.print_rpt_allMS()
            elif self.report_state == 'pack_type':
                self.print_rpt_SMD_pack()
            elif self.report_state == 'stanoks':
                self.print_rpt_stanoks()
            self.mdiArea.activeSubWindow().setWidget(self.text)

    def open_file_selection(self):
        dialog = QFileDialog()
        file = dialog.getOpenFileName(
            None,
            '',
            'Выберите файл запуска',
            '"ZAP" files (*.zap)'
        )
        self.launch_file_name = file[0].split('/')[-1]
        subwindow = QMdiSubWindow()
        subwindow.setWindowTitle(self.launch_file_name)
        subwindow.setObjectName(self.launch_file_name)
        self.mdiArea.addSubWindow(subwindow)
        subwindow.setGeometry(0, 0, 887, 671)
        subwindow.showMaximized()
        self.zapusk = CLaunch(self.launch_file_name)
        self.launch_tree()

    def launch_tree(self):
        data = self.zapusk.mod_bom
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setHeaderLabels(['Запуски', 'Кол-во'])
        self.treeWidget.setColumnWidth(0, 190)
        self.treeWidget.setColumnWidth(1, 40)
        self.treeWidget.setAlternatingRowColors(True)
        stylesheet = '''
        QTreeWidget { 
                alternate-background-color: #edf6fa;
                background: white
            }
        QHeaderView::section {
                background-color: #c5e1eb
            }
        QHeaderView::section:last {
                background-color: #adadad
            }
        QColumnView {
                background: #b7bbbd     
        '''
        self.treeWidget.setStyleSheet(stylesheet)
        zap = QTreeWidgetItem()
        zap.setText(0, self.zapusk.launch_fn.split('/')[-1])
        zap.setBackground(1, QBrush(QColor('#d6d6d6')))
        lst_stanok = list(set([st['Stanok'] for st in data]))
        for st in lst_stanok:
            st_child = QTreeWidgetItem()
            st_child.setText(0, f'Станок {st}')
            st_child.setBackground(1, QBrush(QColor('#d6d6d6')))
            lst_mod_dict = [el for el in data if el['Stanok'] == st]
            mod_dict = {}
            for el in lst_mod_dict:
                var_list = []
                for elem in el['mtypes']:
                    var_list.append((elem['var'], elem['quantity']))
                mod_dict[el['bommod']] = var_list
            for key, values in mod_dict.items():
                mod_child = QTreeWidgetItem()
                mod_child.setText(0, key)
                for value in values:
                    var_child = QTreeWidgetItem()
                    var_child.setText(0, f'исп. {value[0]}: ')
                    var_child.setTextAlignment(0, Qt.AlignRight)
                    var_child.setText(1, value[1])
                    var_child.setBackground(1, QBrush(QColor('#f2f2f2')))
                    mod_child.addChild(var_child)
                mod_children_list = []
                mod_value = 0
                for i in [0, 1]:
                    if mod_child.child(i):
                        mod_children_list.append(mod_child.child(i))
                for var in mod_children_list:
                    mod_value += int(var.text(1))
                mod_child.setText(1, str(mod_value))
                mod_child.setForeground(1, QBrush(Qt.darkGray))
                mod_child.setBackground(1, QBrush(QColor('#d6d6d6')))
                st_child.addChild(mod_child)
            zap.addChild(st_child)
        self.treeWidget.addTopLevelItem(zap)
        zap.setExpanded(True)
        c = zap.childCount()
        for st in range(c):
            zap.child(st).setExpanded(True)
            for mod in range(zap.child(st).childCount()):
                zap.child(st).child(mod).setExpanded(True)
                for var in range(zap.child(st).child(mod).childCount()):
                    zap.child(st).child(mod).child(var).setExpanded(True)

    def test(self, item):
        if item.text(0)[-1:-5:-1] == 'paz.':
            self.state = 'Режим работы с запуском'
            self.statusbar.showMessage(self.state)
            self.mdiArea.activeSubWindow().setWidget(self.text)
            if self.report_state is None:
                self.text.clear()
                self.text.insertPlainText(self.zapusk.rpt())

    def print_rpt(self):
        self.report_state = 'zapusk'
        self.text.clear()
        self.text.insertPlainText(self.zapusk.rpt())

    def print_rpt_allMS(self):
        self.report_state = 'mod'
        self.text.clear()
        self.text.insertPlainText(self.zapusk.rpt_allMS())

    def print_rpt_SMD_pack(self):
        self.report_state = 'pack_type'
        self.text.clear()
        self.text.insertPlainText(self.zapusk.rpt_SMD_pack())

    def print_rpt_stanoks(self):
        self.report_state = 'stanoks'
        self.text.clear()
        self.text.insertPlainText(self.zapusk.rpt_stanoks())

    def closeEvent(self, event):
        self.settings.setValue('windowGeometry', self.geometry())
        self.settings.setValue('windowState', self.windowState())
        self.settings.setValue('lastOpenedFile', self.launch_file_name)
        self.settings.setValue('lastState', self.state)
        self.settings.setValue('lastReportState', self.report_state)
        self.settings.sync()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())



import sys
from cProfile import label
from io import StringIO
from tkinter.filedialog import dialogstates

from PyQt5 import QtCore

import resources
import subprocess

from PyQt5.QtCore import Qt, QObject, QSettings, QLocale, QTranslator
from PyQt5.QtGui import QBrush, QIcon, QPixmap, QFont, QColor, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMdiSubWindow, QPlainTextEdit, \
    QTreeWidgetItem, QAction, QTextEdit, QMdiArea, QMenu, QDialog, QLabel, QFontDialog, QHBoxLayout, QVBoxLayout, \
    QPushButton, QWidget, QToolButton
from modfab_ui import Ui_mainWindow
from CLaunch import CLaunch

I18N_QT_PATH = '/usr/share/qt/translations/'

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
class ActionButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

    def setAction(self, action):
        icon = action.icon()
        text = action.text()
        self.setIcon(icon)
        self.setText(text)

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
        plus_icon = QIcon(QPixmap(':icons/plus.png'))
        font_icon = QIcon(QPixmap(':icons/font.png'))
        save_icon = QIcon(QPixmap(':icons/save.png'))
        close_icon = QIcon(QPixmap(':icons/close.png'))
        self.spec_action = QAction(spec_icon, 'Полная', self)
        self.mod_action = QAction(mod_icon, 'По модулям', self)
        self.pack_type_action = QAction(pack_type_icon, 'По типам упаковки', self)
        self.stanok_action = QAction(stanok_icon, 'По станкам', self)
        self.add_stanok_action = QAction(plus_icon, 'Добавить станок', self)
        self.change_font_action = QAction(font_icon, 'Изменить шрифт', self)
        self.save_zapusk_action = QAction(save_icon, 'Сохранить', self)
        self.close_zapusk_action = QAction(close_icon, 'Закрыть запуск', self)
        self.spec_label = QLabel()
        self.spec_label.setText('Спецификации')
        self.spec_label.setAlignment(Qt.AlignHCenter)
        self.spec_button = ActionButton()
        self.mod_button = ActionButton()
        self.pack_type_button = ActionButton()
        self.stanok_button = ActionButton()
        self.spec_button.setAction(self.spec_action)
        self.mod_button.setAction(self.mod_action)
        self.pack_type_button.setAction(self.pack_type_action)
        self.stanok_button.setAction(self.stanok_action)
        self.container = QWidget()
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.spec_button)
        self.h_layout.addWidget(self.mod_button)
        self.h_layout.addWidget(self.pack_type_button)
        self.h_layout.addWidget(self.stanok_button)
        self.v_layout = QVBoxLayout(self.container)
        self.v_layout.addWidget(self.spec_label)
        self.v_layout.addLayout(self.h_layout)
        self.toolBar.addAction(self.save_zapusk_action)
        self.toolBar.addAction(self.add_stanok_action)
        self.toolBar.addAction(self.change_font_action)
        self.toolBar.addAction(self.close_zapusk_action)
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.container)
        # self.toolBar.addAction(self.spec_action)
        # self.toolBar.addAction(self.mod_action)
        # self.toolBar.addAction(self.pack_type_action)
        # self.toolBar.addAction(self.stanok_action)
        # self.toolBar.insertSeparator(self.spec_action)
        self.add_stanok_action.setVisible(False)
        self.change_font_action.setVisible(False)
        self.save_zapusk_action.setVisible(False)
        self.close_zapusk_action.setVisible(False)
        self.spec_label.setVisible(False)
        self.spec_button.setVisible(False)
        self.mod_button.setVisible(False)
        self.pack_type_button.setVisible(False)
        self.stanok_button.setVisible(False)
        # self.spec_action.setVisible(False)
        # self.mod_action.setVisible(False)
        # self.pack_type_action.setVisible(False)
        # self.stanok_action.setVisible(False)
        self.toolBar.setStyleSheet('QToolBar { spacing: 5px; }')
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.monospace_font = QFont('Courier', 8)
        self.text.setFont(self.monospace_font)
        self.text.setGeometry(0, 0, 1500, 480)
        self.text.setLineWrapMode(0)
        self.connect_signals()
        self.restore_state()
        self.mdiArea.setViewMode(QMdiArea.TabbedView)


    def connect_signals(self):
        self.action.triggered.connect(self.open_file_selection)
        self.treeWidget.itemClicked.connect(self.test)
        self.spec_action.triggered.connect(self.print_rpt)
        self.mod_action.triggered.connect(self.print_rpt_allMS)
        self.pack_type_action.triggered.connect(self.print_rpt_SMD_pack)
        self.stanok_action.triggered.connect(self.print_rpt_stanoks)
        self.spec_button.clicked.connect(self.print_rpt)
        self.mod_button.clicked.connect(self.print_rpt_allMS)
        self.pack_type_button.clicked.connect(self.print_rpt_SMD_pack)
        self.stanok_button.clicked.connect(self.print_rpt_stanoks)
        # self.add_stanok_action.triggered.connect(self.add_stanok)
        self.change_font_action.triggered.connect(self.change_font)
        # self.save_zapusk_action.triggered.connect(self.save_zapusk)
        # self.close_zapusk_action.triggered.connect(self.close_zapusk)

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
            if self.state == 'Режим работы с запуском':
                self.add_stanok_action.setVisible(True)
                self.change_font_action.setVisible(True)
                self.save_zapusk_action.setVisible(True)
                self.close_zapusk_action.setVisible(True)
                self.spec_label.setVisible(True)
                self.spec_button.setVisible(True)
                self.mod_button.setVisible(True)
                self.pack_type_button.setVisible(True)
                self.stanok_button.setVisible(True)
                # self.spec_action.setVisible(True)
                # self.mod_action.setVisible(True)
                # self.pack_type_action.setVisible(True)
                # self.stanok_action.setVisible(True)
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

    # def contextMenuEvent(self, event):
    #     menu = QMenu(self.centralwidget)
    #     # if '.zap' in self.treeWidget.itemAt(event.globalPos()).text(0):
    #     add_stanok_action = QAction('Добавить станок', self)
    #     close_action = QAction('Закрыть запуск', self)
    #     menu.addAction(add_stanok_action)
    #     menu.addAction(close_action)
    #     menu.exec(event.globalPos())

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
            self.add_stanok_action.setVisible(True)
            self.change_font_action.setVisible(True)
            self.save_zapusk_action.setVisible(True)
            self.close_zapusk_action.setVisible(True)
            self.spec_label.setVisible(True)
            self.spec_button.setVisible(True)
            self.mod_button.setVisible(True)
            self.pack_type_button.setVisible(True)
            self.stanok_button.setVisible(True)
            # self.spec_action.setVisible(True)
            # self.mod_action.setVisible(True)
            # self.pack_type_action.setVisible(True)
            # self.stanok_action.setVisible(True)
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

    def change_font(self):
        dialog = QFontDialog()
        default_font = QFont('Courier', 8)
        # dialog.setCurrentFont(default_font)
        font, ok = dialog.getFont(default_font)
        if ok:
            self.text.setFont(font)

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
    locale = QLocale.system().name()
    translator = QTranslator(app)
    translator.load('{}qtbase_{}.qm'.format(I18N_QT_PATH, locale))
    app.installTranslator(translator)
    w = Window()
    w.show()
    sys.exit(app.exec_())



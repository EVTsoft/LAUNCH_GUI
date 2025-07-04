import sys
import os
from io import StringIO

from PyQt5 import QtCore

import resources
import subprocess
import json

from PyQt5.QtCore import Qt, QObject, QSettings, QLocale, QTranslator, QSize
from PyQt5.QtGui import QBrush, QIcon, QPixmap, QFont, QColor, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMdiSubWindow, QPlainTextEdit, \
    QTreeWidgetItem, QAction, QTextEdit, QMdiArea, QMenu, QDialog, QLabel, QFontDialog, QHBoxLayout, QVBoxLayout, \
    QPushButton, QWidget, QToolButton, QTreeWidget, QMessageBox
from modfab_ui import Ui_mainWindow
from CLaunch import CLaunch
from CElModule import CElModule


class ActionButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

    def setAction(self, action):
        icon = action.icon()
        text = action.text()
        self.setIcon(icon)
        self.setText(text)


class MyTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.InternalMove)


class Window(QMainWindow, Ui_mainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('Team-R', 'MODFAB')
        self.setupUi(self)
        self.setGeometry(200, 100, 1500, 800)
        self.tableWidget.setGeometry(595, 0, 400, 585)
        self.mdiArea.setGeometry(420, 0, 1200, 585)
        self.setCentralWidget(self.splitter_2)
        self.zapusk = None
        self.state = None
        self.report_state = None
        self.selected_mod = None
        self.temp_file_name = None
        self.temp_json = None
        self.launch_file_name = ''
        self.my_treeWidget = MyTreeWidget()
        self.my_treeWidget.setHeaderLabel('')
        self.my_treeWidget.setGeometry(0, 0, 310, 585)
        self.splitter.insertWidget(0, self.my_treeWidget)
        spec_icon = QIcon(QPixmap(':icons/spec.png'))
        mod_icon = QIcon(QPixmap(':icons/mod.png'))
        pack_type_icon = QIcon(QPixmap(':icons/pack_type.png'))
        stanok_icon = QIcon(QPixmap(':icons/stanok.png'))
        plus_icon = QIcon(QPixmap(':icons/plus.png'))
        font_icon = QIcon(QPixmap(':icons/font.png'))
        save_icon = QIcon(QPixmap(':icons/save.png'))
        close_icon = QIcon(QPixmap(':icons/close.png'))
        move_icon = QIcon(QPixmap(':icons/move.png'))
        self.spec_action = QAction(spec_icon, 'Полная', self)
        self.mod_action = QAction(mod_icon, 'Модули', self)
        self.pack_type_action = QAction(pack_type_icon, 'Упаковка', self)
        self.stanok_action = QAction(stanok_icon, 'Станки', self)
        self.add_stanok_action = QAction(plus_icon, 'Добавить', self)
        self.change_font_action = QAction(font_icon, 'Шрифт', self)
        self.save_zapusk_action = QAction(save_icon, 'Сохранить', self)
        self.close_zapusk_action = QAction(close_icon, 'Удалить', self)
        self.move_mod_action = QAction(move_icon, 'Переместить', self)
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
        self.spec_button.setIconSize(QSize(30, 30))
        self.mod_button.setIconSize(QSize(30, 30))
        self.pack_type_button.setIconSize(QSize(30, 30))
        self.stanok_button.setIconSize(QSize(30, 30))
        self.container = QWidget()
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.spec_button)
        self.h_layout.addWidget(self.mod_button)
        self.h_layout.addWidget(self.pack_type_button)
        self.h_layout.addWidget(self.stanok_button)
        self.v_layout = QVBoxLayout(self.container)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.spec_label)
        self.toolBar.addAction(self.save_zapusk_action)
        self.toolBar.addAction(self.add_stanok_action)
        self.toolBar.addAction(self.change_font_action)
        self.toolBar.addAction(self.close_zapusk_action)
        self.toolBar.addAction(self.move_mod_action)
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.container)
        self.save_zapusk_action.setEnabled(False)
        self.move_mod_action.setVisible(False)
        self.spec_label.setVisible(False)
        self.spec_button.setVisible(False)
        self.mod_button.setVisible(False)
        self.pack_type_button.setVisible(False)
        self.stanok_button.setVisible(False)
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
        self.my_treeWidget.itemPressed.connect(self.handle_tree_items)
        self.my_treeWidget.itemChanged.connect(self.recount_vars)
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
        self.save_zapusk_action.triggered.connect(self.save_zapusk)
        # self.close_zapusk_action.triggered.connect(self.close_zapusk)

    def restore_state(self):
        geometry = self.settings.value('windowGeometry')
        if geometry:
            self.setGeometry(geometry)
        window_state = self.settings.value('windowState')
        if window_state:
            self.setWindowState(window_state)
        self.temp_json = self.settings.value('json')
        self.temp_file_name = self.settings.value('tempFile')
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
                self.move_mod_action.setVisible(False)
                self.spec_label.setVisible(True)
                self.spec_button.setVisible(True)
                self.mod_button.setVisible(True)
                self.pack_type_button.setVisible(True)
                self.stanok_button.setVisible(True)
            elif self.state == 'Режим работы с модулями':
                self.selected_mod = self.settings.value('lastSelectedModule')
                if self.selected_mod:
                    self.mdiArea.activeSubWindow().setWidget(self.text)
                    self.spec_label.setVisible(False)
                    self.spec_button.setVisible(False)
                    self.mod_button.setVisible(False)
                    self.pack_type_button.setVisible(False)
                    self.stanok_button.setVisible(False)
                    self.move_mod_action.setVisible(True)
                    self.text.clear()
                    self.text.insertPlainText(self.selected_mod.report())
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
        parts = self.launch_file_name.split('.')
        parts.insert(1, '_tmp.')
        self.temp_file_name = ''.join(parts)
        new_file = open(self.temp_file_name, 'w+', encoding='utf-16')
        with open(self.launch_file_name, 'r', encoding='utf-16') as file:
            lines = file.readlines()
            file.close()
        new_file.write(''.join(lines))
        self.temp_json = json.loads(''.join(lines))
        print(self.temp_json)
        new_file.close()
        self.launch_tree()

    def launch_tree(self):
        data = self.zapusk.mod_bom
        self.my_treeWidget.setColumnCount(2)
        self.my_treeWidget.setHeaderLabels(['Запуски', 'Кол-во'])
        self.my_treeWidget.setColumnWidth(0, 190)
        self.my_treeWidget.setColumnWidth(1, 40)
        self.my_treeWidget.setAlternatingRowColors(True)
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
        self.my_treeWidget.setStyleSheet(stylesheet)
        zap = QTreeWidgetItem()
        zap.setText(0, self.zapusk.launch_fn.split('/')[-1])
        zap.setBackground(1, QBrush(QColor('#d6d6d6')))
        zap.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        lst_stanok = list(set([st['Stanok'] for st in data]))
        for st in lst_stanok:
            st_child = QTreeWidgetItem()
            st_child.setText(0, f'Станок {st}')
            st_child.setBackground(1, QBrush(QColor('#d6d6d6')))
            st_child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled)
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
                    var_child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
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
                mod_child.setFlags((Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled) & ~Qt.ItemIsDropEnabled)
                st_child.addChild(mod_child)
            zap.addChild(st_child)
        self.my_treeWidget.addTopLevelItem(zap)
        zap.setExpanded(True)
        c = zap.childCount()
        for st in range(c):
            zap.child(st).setExpanded(True)
            for mod in range(zap.child(st).childCount()):
                zap.child(st).child(mod).setExpanded(True)
                for var in range(zap.child(st).child(mod).childCount()):
                    zap.child(st).child(mod).child(var).setExpanded(True)

    def handle_tree_items(self, item):
        if item.text(0)[-1:-5:-1] == 'paz.':
            self.state = 'Режим работы с запуском'
            self.statusbar.showMessage(self.state)
            self.mdiArea.activeSubWindow().setWidget(self.text)
            self.move_mod_action.setVisible(False)
            self.spec_label.setVisible(True)
            self.spec_button.setVisible(True)
            self.mod_button.setVisible(True)
            self.pack_type_button.setVisible(True)
            self.stanok_button.setVisible(True)
            print(self.spec_button.size())
            print(self.mod_button.size())
            print(self.pack_type_button.size())
            print(self.stanok_button.size())
            if self.report_state is None:
                self.text.clear()
                self.text.insertPlainText(self.zapusk.rpt())
        elif 'Станок' in item.parent().text(0):
            self.state = 'Режим работы с модулями'
            self.report_state = None
            self.statusbar.showMessage(self.state)
            self.mdiArea.activeSubWindow().setWidget(self.text)
            self.spec_label.setVisible(False)
            self.spec_button.setVisible(False)
            self.mod_button.setVisible(False)
            self.pack_type_button.setVisible(False)
            self.stanok_button.setVisible(False)
            self.move_mod_action.setVisible(True)
            print(item.parent().indexOfChild(item))
            self.selected_mod = CElModule(item.text(0), 'launch')
            self.text.clear()
            self.text.insertPlainText(self.selected_mod.report())

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
        font, ok = dialog.getFont(default_font)
        if ok:
            self.text.setFont(font)

    def recount_vars(self, item):
        self.save_zapusk_action.setEnabled(True)
        mod = item.parent()
        total = int(mod.text(1))
        summa = 0
        for i in range(mod.childCount()):
            var = mod.child(i)
            summa += int(var.text(1))
        diff = total - summa
        try:
            new_value = int(mod.child(mod.indexOfChild(item) + 1).text(1)) + diff
            mod.child(mod.indexOfChild(item) + 1).setText(1, str(new_value))
        except Exception:
            new_value = int(mod.child(mod.indexOfChild(item) - 1).text(1)) + diff
            mod.child(mod.indexOfChild(item) - 1).setText(1, str(new_value))
        needed_index = 0
        for item in self.temp_json:
            if item['bommod'] == mod.text(0):
                needed_index = self.temp_json.index(item)
                break
        inc = 0
        for var in self.temp_json[needed_index]['mtypes']:
            var['quantity'] = mod.child(inc).text(1)
            inc += 1
        with open(self.temp_file_name, 'w+', encoding='utf-16') as temp_file:
            s = json.dumps(self.temp_json, indent=0)
            temp_file.write(s)
            temp_file.close()

    def save_zapusk(self):
        q = QMessageBox()
        q.setWindowTitle('Сохранение')
        q.setText(f'Сохранить изменения в файле {self.launch_file_name}?')
        q.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        q.setIcon(QMessageBox.Question)
        button = q.exec()
        if button == QMessageBox.Ok:
            with open(self.temp_file_name, 'r', encoding='utf-16') as temp_file:
                with open(self.launch_file_name, 'w', encoding='utf-16') as file:
                    lines = temp_file.readlines()
                    file.write(''.join(lines))
                    file.close()
                    temp_file.close()
            self.zapusk = CLaunch(self.launch_file_name)
            self.text.clear()
            self.state = 'Режим работы с запуском'
            self.statusbar.showMessage(self.state)
            if self.report_state:
                if self.report_state == 'zapusk':
                    self.text.insertPlainText(self.zapusk.rpt())
                elif self.report_state == 'mod':
                    self.text.insertPlainText(self.zapusk.rpt_allMS())
                elif self.report_state == 'pack_type':
                    self.text.insertPlainText(self.zapusk.rpt_SMD_pack())
                elif self.report_state == 'stanoks':
                    self.text.insertPlainText(self.zapusk.rpt_stanoks())
            else:
                self.report_state = 'zapusk'
                self.text.insertPlainText(self.zapusk.rpt())
            self.save_zapusk_action.setEnabled(False)

    def closeEvent(self, event):
        if self.save_zapusk_action.isEnabled():
            save_dlg = QMessageBox()
            save_dlg.setWindowTitle('Закрыть запуск')
            save_dlg.setText(f'Сохранить несохранённые изменения в файле {self.launch_file_name} перед закрытием?')
            save_dlg.setIcon(QMessageBox.Question)
            save_dlg.setStandardButtons(QMessageBox.Save | QMessageBox.Close)
            button = save_dlg.exec()
            if button == QMessageBox.Save:
                with open(self.temp_file_name, 'r', encoding='utf-16') as temp_file:
                    with open(self.launch_file_name, 'w', encoding='utf-16') as file:
                        lines = temp_file.readlines()
                        file.write(''.join(lines))
                        file.close()
                        temp_file.close()
                self.zapusk = CLaunch(self.launch_file_name)
        self.settings.setValue('windowGeometry', self.geometry())
        self.settings.setValue('windowState', self.windowState())
        self.settings.setValue('lastOpenedFile', self.launch_file_name)
        self.settings.setValue('lastState', self.state)
        self.settings.setValue('lastReportState', self.report_state)
        self.settings.setValue('lastSelectedModule', self.selected_mod)
        self.settings.setValue('json', self.temp_json)
        self.settings.setValue('tempFile', self.temp_file_name)
        self.settings.sync()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())

import sys

import resources

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMdiSubWindow, QPlainTextEdit, \
    QTreeWidgetItem, QAction
from modfab_ui import Ui_mainWindow
from CLaunch import CLaunch


class Window(QMainWindow, Ui_mainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setGeometry(200, 100, 1500, 800)
        self.tableWidget.setGeometry(595, 0, 500, 585)
        # self.treeWidget.setGeometry(0, 0, 320, 585)
        self.mdiArea.setGeometry(420, 0, 900, 585)
        self.setCentralWidget(self.splitter_2)
        self.connect_signals()
        self.zapusk = None
        self.treeWidget.setHeaderLabel('')

    def connect_signals(self):
        self.action.triggered.connect(self.open_file_selection)
        self.treeWidget.itemClicked.connect(self.test)


    def open_file_selection(self):
        dialog = QFileDialog()
        file = dialog.getOpenFileName(
            None,
            '',
            'Выберите файл запуска',
            '"ZAP" files (*.zap)'
        )
        launch_file_name = file[0]
        subwindow = QMdiSubWindow()
        subwindow.setWindowTitle(launch_file_name.split('/')[-1])
        subwindow.setObjectName(launch_file_name.split('/')[-1])
        self.mdiArea.addSubWindow(subwindow)
        subwindow.setGeometry(0, 0, 887, 671)
        subwindow.show()
        self.zapusk = CLaunch(launch_file_name)
        self.launch_tree()

    def launch_tree(self):
        data = self.zapusk.mod_bom
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setHeaderLabels(['Запуски', 'Кол-во'])
        self.treeWidget.setColumnWidth(0, 190)
        self.treeWidget.setColumnWidth(1, 40)
        zap = QTreeWidgetItem()
        zap.setText(0, self.zapusk.launch_fn.split('/')[-1])
        lst_stanok = list(set([st['Stanok'] for st in data]))
        for st in lst_stanok:
            st_child = QTreeWidgetItem()
            st_child.setText(0, f'Станок {st}')
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
                    mod_child.addChild(var_child)
                mod_children_list = []
                mod_value = 0
                for i in [0, 1]:
                    if mod_child.child(i):
                        mod_children_list.append(mod_child.child(i))
                for var in mod_children_list:
                    mod_value += int(var.text(1))
                mod_child.setText(1, str(mod_value))
                mod_child.setForeground(1, QBrush(Qt.gray))
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
            text = QPlainTextEdit()
            text.setReadOnly(True)
            self.mdiArea.activeSubWindow().setWidget(text)
            # spec_icon = QIcon(QPixmap(':/spec.png'))
            # spec_action = QAction(spec_icon, '')
            # mod_icon = QIcon(QPixmap(':/mod.png'))
            # mod_action = QAction(mod_icon, '')
            # pack_type_icon = QIcon(QPixmap(':/pack_type.png'))
            # pack_type_action = QAction(pack_type_icon, '')
            # stanok_icon = QIcon(QPixmap(':/stanok.png'))
            # stanok_action = QAction(stanok_icon, '')
            # self.toolBar.addActions([spec_action, mod_action, pack_type_action, stanok_action])
            text.clear()
            text.insertPlainText(self.zapusk.rpt())



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())



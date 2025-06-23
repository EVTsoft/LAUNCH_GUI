import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMdiSubWindow, QTextBrowser, QPlainTextEdit, \
    QTreeWidgetItem
from modfab_ui import Ui_mainWindow
from CLaunch import CLaunch
from CElModule import CElModule
from CSpecification import CSpecification


class Window(QMainWindow, Ui_mainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setCentralWidget(self.splitter_2)
        self.connect_signals()
        self.zapusk = None
        self.treeWidget.setHeaderLabel('')

    def connect_signals(self):
        self.action.triggered.connect(self.open_file_selection)


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
        text = QPlainTextEdit()
        text.setReadOnly(True)
        subwindow.setWindowTitle(launch_file_name.split('/')[-1])
        subwindow.setObjectName(launch_file_name.split('/')[-1])
        subwindow.setWidget(text)
        self.mdiArea.addSubWindow(subwindow)
        subwindow.showMaximized()
        self.zapusk = CLaunch(launch_file_name)
        # text.insertPlainText(self.zapusk.rpt())
        self.launch_tree()

    def launch_tree(self):
        data = self.zapusk.mod_bom
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setHeaderLabels(['Запуски', 'Кол-во'])
        zap = QTreeWidgetItem()
        zap.setText(0, self.zapusk.launch_fn.split('/')[-1])
        lst_stanok = list(set([st['Stanok'] for st in data]))
        for st in lst_stanok:
            st_child = QTreeWidgetItem()
            st_child.setText(0, f'Станок {st}')
            lst_mod = [el['bommod'] for el in data if el['Stanok'] == st]
            lst_mod_dict = [el for el in data if el['Stanok'] == st]
            print(lst_mod_dict)
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
                    var_child.setText(0, f'исп. {value[0]}')
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



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())



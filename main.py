from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtGui import QKeySequence
import sys
from PIL import Image, UnidentifiedImageError
from copy import copy, deepcopy

from manager import Manager
from ui import *
from find_recipes import find_recipes
import urllib.request
# from search import *


class Search(QWidget):
    def __init__(self, i, j, parent):
        super().__init__()
        self.parent = parent
        self.i = i
        self.j = j

        self.resize(605, 630)
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.search_bar = QtWidgets.QLineEdit(self.centralwidget)
        self.search_bar.setGeometry(QtCore.QRect(40, 40, 425, 50))
        self.search_bar.setStyleSheet("font-size: 30px;\n"
"color: black;")
        self.search_bar.setObjectName("search_bar")
        self.ingredients_search = QtWidgets.QScrollArea(self.centralwidget)
        self.ingredients_search.setGeometry(QtCore.QRect(40, 115, 525, 475))
        self.ingredients_search.setWidgetResizable(True)
        self.ingredients_search.setObjectName("ingredients_search")
        self.ingredients_search_contents = QtWidgets.QWidget()
        self.ingredients_search_contents.setGeometry(QtCore.QRect(0, 0, 523, 473))
        self.ingredients_search_contents.setObjectName("ingredients_search_contents")
        self.ingredients_search_grid = QGridLayout(self.ingredients_search_contents)
        self.ingredients_search.setWidget(self.ingredients_search_contents)

        self.search_button = QtWidgets.QPushButton(self.centralwidget)
        self.search_button.setGeometry(QtCore.QRect(490, 40, 75, 50))
        self.search_button.setObjectName("search_button")

        self.search_button.setText("Search")
        # layout = QVBoxLayout()
        # self.label = QLabel("Search")
        # layout.addWidget(self.label)
        # self.setLayout(layout)
        # self.ui = Ui_SearchWindow()
        # self.ui.setupUi(self)

        self.search_button.clicked.connect(lambda: self.search_ingredient(self.ui.search_bar.text()))
        # self.connect(self.ui.search_button, QtCore.SIGNAL("clicked()"), lambda: self.search_ingredient(self.ui.search_bar.text()))
        self.search_bar.returnPressed.connect(lambda: self.search_ingredient(self.search_bar.text()))

    def search_ingredient(self, query):
        self.search_bar.setText("")
        for i in reversed(range(self.ingredients_search_grid.count())):
            self.ingredients_search_grid.itemAt(i).widget().setParent(None)

        ingredients = self.parent.man.closest_ingredients(query, 100)
        for ingredient in ingredients:
            self.add_search_item(ingredient[1], query)

    def add_search_item(self, ingredient, query):
        num_rows = self.ingredients_search_grid.rowCount()

        t = QLabel(ingredient)
        t.setStyleSheet("color: black")
        self.ingredients_search_grid.addWidget(t, num_rows, 0)

        b = QPushButton("Select")
        b.setStyleSheet("color: green")
        b.pressed.connect(lambda: self.choose_ingredient(ingredient))
        self.ingredients_search_grid.addWidget(b, num_rows, 1)

    def choose_ingredient(self, ingredient):
        self.parent.added_ingredients[self.i] = ingredient
        if self.j == 4:
            col = 5
        else:
            col = 2
        btn = self.parent.grid.itemAtPosition(self.i, col).wid
        btn.setText(f"Other ({ingredient})")
        self.close()

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        loadJsonStyle(self, self.ui)

        self.cq = ""

        self.man = Manager()

        QShortcut(QKeySequence(Qt.Key_Left), self, activated=self.ui.pages.slideToPreviousWidget)
        QShortcut(QKeySequence(Qt.Key_Right), self, activated=self.ui.pages.slideToNextWidget)
        self.connect(self.ui.upload_button, QtCore.SIGNAL("clicked()"), self.upload_receipt)
        self.connect(self.ui.submit_ingredients, QtCore.SIGNAL("clicked()"), self.submit_clicked)

        self.connect(self.ui.search_button, QtCore.SIGNAL("clicked()"), lambda: self.manual_ingredient(self.ui.search_bar.text()))
        self.ui.search_bar.returnPressed.connect(lambda: self.manual_ingredient(self.ui.search_bar.text()))

        self.connect(self.ui.recipe_refresh_button, QtCore.SIGNAL("clicked()"), self.find_recipes)

    def upload_receipt(self):

        # Stage 1
        filename = QFileDialog.getOpenFileName(self, 'Open File', filter = "Image Files (*.png *.jpg *.jpeg;;All Files (*)")[0]

        try:
            receipt = Image.open(filename)
        except UnidentifiedImageError as e:
            print("Not an Image")
            return

        # Stage 2
        self.ui.receipt_widget.setCurrentIndex(1)

        gen = self.man.guess_ingredients(receipt)
        while True:
            progress = next(gen)
            self.ui.progress.setValue(progress)
            if progress == 100:
                break

        self.result = next(gen)
        print(self.result)
        # Stage 3
        self.ui.receipt_widget.setCurrentIndex(2)

        self.grid = QGridLayout()

        self.added_ingredients = [None for i in range(len(self.result))]
        for i in range(len(self.result)):
            self.make_confirm_btns(i)

        self.ui.confirm_widget.setLayout(self.grid)


    def make_confirm_btns(self, i):
        label = QLabel(self.result[i][0])
        label.setStyleSheet("color: black;");
        self.grid.addWidget(label, i, 0)

        group = QButtonGroup(self)
        group.buttonPressed.connect(lambda x: self.confirm_button_clicked(x, i, group.id(x)))


        btn_css = "QPushButton {background-color: #7C9498; border-radius: 5px; color: black;} QPushButton:checked {background-color: #6C797C;}"

        if self.result[i][1] == None:
            none_btn = QPushButton("None")
            none_btn.setCheckable(True)
            none_btn.setChecked(True)
            none_btn.setStyleSheet(btn_css);
            self.grid.addWidget(none_btn, i, 1)
            group.addButton(none_btn, 3)


            other_btn = QPushButton("Add")
            other_btn.setCheckable(True)
            other_btn.setStyleSheet(btn_css)
            self.grid.addWidget(other_btn, i, 2)
            group.addButton(other_btn, 5)
            return



        for j in range(3):
            btn = QPushButton(self.result[i][1][j][1])
            btn.setCheckable(True)
            if j == 0:
                btn.setChecked(True)
                self.added_ingredients[i] = self.result[i][1][j][1]
            btn.setStyleSheet(btn_css)
            self.grid.addWidget(btn, i, j+2)
            group.addButton(btn, j)

        none_btn = QPushButton("None")
        none_btn.setCheckable(True)
        none_btn.setStyleSheet(btn_css)
        self.grid.addWidget(none_btn, i, 1)
        group.addButton(none_btn, 3)

        other_btn = QPushButton("Other")
        other_btn.setCheckable(True)
        other_btn.setStyleSheet(btn_css)
        self.grid.addWidget(other_btn, i, 5)
        group.addButton(other_btn, 4)

    def confirm_button_clicked(self, btn, i, j):

        if j < 3:
            self.added_ingredients[i] = self.result[i][1][j][1]
            print(self.added_ingredients[i])
            return

        if j == 3:
            self.added_ingredients[i] = None
            print(self.added_ingredients[i])
            return

        if j == 4 or j == 5:
            search = Search(i, j, self)
            search.show()

    def submit_clicked(self):
        for i in self.added_ingredients:
            if i == None:
                continue

            self.add_ingredient(i)

        self.added_ingredients = None
        self.ui.receipt_widget.layout().deleteLater()
        self.result = None
        self.ui.receipt_widget.setCurrentIndex(0)

    def add_ingredient(self, ingredient):
        old = copy(self.man.ingredients)
        self.man.add_ingredient(ingredient)
        if old != self.man.get_ingredients():
        # num_rows = self.ui.ingredients_list_grid.rowCount()
        #
        # t = QLabel(ingredient)
        # t.setStyleSheet("color: black")
        # self.ui.ingredients_list_grid.addWidget(t, num_rows, 0)
        #
        # b = QPushButton("Remove")
        # b.setStyleSheet("color: red")
        # b.pressed.connect(lambda: self.remove_ingredient(ingredient))
        # self.ui.ingredients_list_grid.addWidget(b, num_rows, 1)
            self.display_ingredient(ingredient)

        self.manual_ingredient(self.cq)

    def display_ingredient(self, ingredient):
        num_rows = self.ui.ingredients_list_grid.rowCount()

        t = QLabel(ingredient)
        t.setStyleSheet("color: black")
        self.ui.ingredients_list_grid.addWidget(t, num_rows, 0)

        b = QPushButton("Remove")
        b.setStyleSheet("color: red")
        b.pressed.connect(lambda: self.remove_ingredient(ingredient))
        self.ui.ingredients_list_grid.addWidget(b, num_rows, 1)

    def remove_ingredient(self, ingredient):
        self.man.remove_ingredient(ingredient)

        for i in reversed(range(self.ui.ingredients_list_grid.count())):
            self.ui.ingredients_list_grid.itemAt(i).widget().setParent(None)

        for i in self.man.get_ingredients():
            self.display_ingredient(i)

        self.manual_ingredient(self.cq)

    def manual_ingredient(self, query):
        self.cq = query
        self.ui.search_bar.setText("")
        for i in reversed(range(self.ui.ingredients_search_grid.count())):
            self.ui.ingredients_search_grid.itemAt(i).widget().setParent(None)

        ingredients = self.man.closest_ingredients(query, 100)
        for ingredient in ingredients:
            self.add_search_item(ingredient[1], query)
        # for i, ingredient in enumerate(ingredients):
            # t = QLabel(ingredient[1])
            # t.setStyleSheet("color: black")
            # self.ui.ingredients_search_grid.addWidget(t, i, 0)
            #
            # b = QPushButton("Add")
            # b.setStyleSheet("color: green")
            # b.pressed.connect(lambda: self.add_ingredient(ingredient[1]))
            # self.ui.ingredients_search_grid.addWidget(b, i, 1)

    def add_search_item(self, ingredient, query):
        num_rows = self.ui.ingredients_search_grid.rowCount()

        t = QLabel(ingredient)
        t.setStyleSheet("color: black")
        self.ui.ingredients_search_grid.addWidget(t, num_rows, 0)

        if ingredient in self.man.get_ingredients():
            b = QPushButton("Already Added")
            b.setStyleSheet("color: red")
        else:
            b = QPushButton("Add")
            b.setStyleSheet("color: green")
            b.pressed.connect(lambda: self.add_ingredient(ingredient))
        self.ui.ingredients_search_grid.addWidget(b, num_rows, 1)

    def find_recipes(self):
        recipes = find_recipes(self.man.get_ingredients())

        for i in reversed(range(self.ui.recipe_list_grid.count())):
            self.ui.recipe_list_grid.itemAt(i).widget().setParent(None)

        for i, recipe in enumerate(recipes):
            if i == 15:
                break
            self.display_recipe(recipe)

    def display_recipe(self, recipe):
        num_rows = self.ui.recipe_list_grid.rowCount()

        try:
            img_data = urllib.request.urlopen(recipe["img_link"]).read()
            img = QImage()
            img.loadFromData(img_data)
            img_lbl = QLabel(self)
            img_lbl.setPixmap(QPixmap(img))
            self.ui.recipe_list_grid.addWidget(img_lbl, num_rows, 0)

            w = QWidget()
            vl = QVBoxLayout(w)
            title = QLabel(recipe["title"])
            title.setStyleSheet("color: black; font-size: 40px")
            vl.addWidget(title)
            website = QLabel("Website: " + recipe["website"])
            website.setStyleSheet("color: black; font-size: 15px")
            vl.addWidget(website)
            iu = QLabel("Ingredients Used: " + recipe["ingredients_used"].replace(",", ", "))
            iu.setStyleSheet("color: black; font-size: 15px")
            vl.addWidget(iu)
            # title.setText(_translate("MainWindow", request["title"]))
            # website.setText(_translate("MainWindow", "Website: " + request["website"]))
            self.ui.recipe_list_grid.addWidget(w, num_rows, 1)

        except:
            pass
        # w = QWidget()
        # vl = QVBoxLayout(w)
        # title = QLabel(recipe["title"])
        # title.setStyleSheet("color: black; font-size: 40px")
        # vl.addWidget(title)
        # website = QLabel("Website: " + recipe["website"])
        # website.setStyleSheet("color: black; font-size: 15px")
        # vl.addWidget(website)
        # # title.setText(_translate("MainWindow", request["title"]))
        # # website.setText(_translate("MainWindow", "Website: " + request["website"]))
        # self.ui.recipe_list_grid.addWidget(w, num_rows, 1)

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Qt.Key_Left:
    #         self.pages.setCurrentIndex((self.pages.currentIndex() - 1) % 3)
    #     elif event.key() == Qt.Qt.Key_Right:
    #         self.pages.setCurrentIndex((self.pages.currentIndex() + 1) % 3)

app = QApplication(sys.argv)
window = Window()
window.show()
app.exec_()

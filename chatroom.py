# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chatroomwd.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(480, 640)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(210, 70, 101, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(50, 220, 151, 16))
        self.label_3.setObjectName("label_3")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(280, 220, 113, 22))
        self.lineEdit.setObjectName("lineEdit")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(110, 300, 271, 16))
        self.label_4.setObjectName("label_4")
        self.btn_create = QtWidgets.QPushButton(Form)
        self.btn_create.setGeometry(QtCore.QRect(200, 350, 93, 28))
        self.btn_create.setObjectName("btn_create")
        self.btn_join = QtWidgets.QPushButton(Form)
        self.btn_join.setGeometry(QtCore.QRect(200, 260, 93, 28))
        self.btn_join.setObjectName("btn_join")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_2.setText(_translate("Form", "CHAT ROOM"))
        self.label_3.setText(_translate("Form", "Enter your room id:"))
        self.label_4.setText(_translate("Form", "You don\'t have room id? Create your new room"))
        self.btn_create.setText(_translate("Form", "Create"))
        self.btn_join.setText(_translate("Form", "Join"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

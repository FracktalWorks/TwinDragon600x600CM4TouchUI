from MainUIClass.gui_elements import ClickableLineEdit
from PyQt5 import QtCore, QtGui
from MainUIClass.config import _fromUtf8
import styles
import mainGUI
from logger import *
import dialog

class lineEdits(mainGUI.Ui_MainWindow):
    def __init__(self):
        try:
            log_info("Starting line edits init.")
            super().__init__()
            log_info("Completed line edits init.")
        except Exception as e:
            error_message = f"Error in lineEdits __init__: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass
    
    def setup(self):
        """
        Sets up various line edits for UI elements.
        """
        try:
            log_info("Setting up line edits.")

            font = QtGui.QFont()
            font.setFamily(_fromUtf8("Gotham"))
            font.setPointSize(15)

            # Setup WiFi password line edit
            self.wifiPasswordLineEdit = ClickableLineEdit(self.wifiSettingsPage)
            self.wifiPasswordLineEdit.setGeometry(QtCore.QRect(300, 170, 400, 60))
            self.wifiPasswordLineEdit.setFont(font)
            self.wifiPasswordLineEdit.setStyleSheet(styles.textedit)
            self.wifiPasswordLineEdit.setObjectName(_fromUtf8("wifiPasswordLineEdit"))

            # Setup static IP line edits
            font.setPointSize(11)
            self.staticIPLineEdit = ClickableLineEdit(self.ethStaticSettings)
            self.staticIPLineEdit.setGeometry(QtCore.QRect(200, 15, 450, 40))
            self.staticIPLineEdit.setFont(font)
            self.staticIPLineEdit.setStyleSheet(styles.textedit)
            self.staticIPLineEdit.setObjectName(_fromUtf8("staticIPLineEdit"))

            self.staticIPGatewayLineEdit = ClickableLineEdit(self.ethStaticSettings)
            self.staticIPGatewayLineEdit.setGeometry(QtCore.QRect(200, 85, 450, 40))
            self.staticIPGatewayLineEdit.setFont(font)
            self.staticIPGatewayLineEdit.setStyleSheet(styles.textedit)
            self.staticIPGatewayLineEdit.setObjectName(_fromUtf8("staticIPGatewayLineEdit"))

            self.staticIPNameServerLineEdit = ClickableLineEdit(self.ethStaticSettings)
            self.staticIPNameServerLineEdit.setGeometry(QtCore.QRect(200, 155, 450, 40))
            self.staticIPNameServerLineEdit.setFont(font)
            self.staticIPNameServerLineEdit.setStyleSheet(styles.textedit)
            self.staticIPNameServerLineEdit.setObjectName(_fromUtf8("staticIPNameServerLineEdit"))

            log_info("Line edits setup completed.")
        except Exception as e:
            error_message = f"Error setting up line edits: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

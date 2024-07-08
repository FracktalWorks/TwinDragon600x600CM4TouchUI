import mainGUI
from MainUIClass.MainUIClasses.start_keyboard import startKeyboard
import subprocess
import dialog
import re
from MainUIClass.MainUIClasses.networking_package.wifiSettingsPage import ThreadRestartNetworking
from PyQt5 import QtWidgets
import mainGUI
from logger import *

class staticIPSettings(mainGUI.Ui_MainWindow):

    def init(self):
        try:
            super().__init__()
            log_info("Completed staticIPSettings init.")
        except Exception as e:
            error_message = f"Error in staticIPSettings init: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setup(self):
        try:
            log_info("Starting setup for staticIPSettings.")
            self.staticIPKeyboardButton.pressed.connect(lambda: self.staticIPShowKeyboard(self.staticIPLineEdit))                                                                            
            self.staticIPGatewayKeyboardButton.pressed.connect(lambda: self.staticIPShowKeyboard(self.staticIPGatewayLineEdit))
            self.staticIPNameServerKeyboardButton.pressed.connect(
                lambda: self.staticIPShowKeyboard(self.staticIPNameServerLineEdit))
            self.staticIPSettingsDoneButton.pressed.connect(self.staticIPSaveStaticNetworkInfo)
            self.staticIPSettingsCancelButton.pressed.connect(
                lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
            self.deleteStaticIPSettingsButton.pressed.connect(self.deleteStaticIPSettings)
            log_info("Completed setup for staticIPSettings.")
        except Exception as e:
            error_message = f"Error in staticIPSettings setup: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def staticIPSettings(self):
        try:
            log_info("Calling staticIPSettings method.")
            self.stackedWidget.setCurrentWidget(self.staticIPSettingsPage)
            self.staticIPComboBox.clear()
            self.staticIPComboBox.addItems(["eth0", "wlan0"])
            log_info("Completed staticIPSettings method.")
        except Exception as e:
            error_message = f"Error in staticIPSettings method: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def isIpErr(self, ip):
        try:
            log_info("Calling isIpErr method.")
            return (re.search(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$", ip) is None)
        except Exception as e:
            error_message = f"Error in isIpErr method: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def showIpErr(self, var):
        try:
            log_info("Calling showIpErr method.")
            return dialog.WarningOk(self, "Invalid input: {0}".format(var))
        except Exception as e:
            error_message = f"Error in showIpErr method: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def staticIPSaveStaticNetworkInfo(self):
        try:
            log_info("Starting staticIPSaveStaticNetworkInfo method.")
            txtStaticIPInterface = self.staticIPComboBox.currentText()
            txtStaticIPAddress = str(self.staticIPLineEdit.text())
            txtStaticIPGateway = str(self.staticIPGatewayLineEdit.text())
            txtStaticIPNameServer = str(self.staticIPNameServerLineEdit.text())
            if self.isIpErr(txtStaticIPAddress):
                return self.showIpErr("IP Address")
            if self.isIpErr(txtStaticIPGateway):
                return self.showIpErr("Gateway")
            if txtStaticIPNameServer is not "":
                if self.isIpErr(txtStaticIPNameServer):
                    return self.showIpErr("NameServer")
            Globaltxt = subprocess.Popen("cat /etc/dhcpcd.conf", stdout=subprocess.PIPE, shell=True).communicate()[0].decode('utf8')
            staticIPConfig = ""
            Globaltxt = re.sub(r"interface.*\n", "", Globaltxt)
            Globaltxt = re.sub(r"static.*\n", "", Globaltxt)
            Globaltxt = re.sub(r"^\s+", "", Globaltxt)                                                 
            staticIPConfig = "\ninterface {0}\nstatic ip_address={1}/24\nstatic routers={2}\nstatic domain_name_servers=8.8.8.8 8.8.4.4 {3}\n\n".format(
                txtStaticIPInterface, txtStaticIPAddress, txtStaticIPGateway, txtStaticIPNameServer)
            Globaltxt = staticIPConfig + Globaltxt
            with open("/etc/dhcpcd.conf", "w") as f:
                f.write(Globaltxt)
            if txtStaticIPInterface == 'eth0':
                log_info("Restarting networking for eth0.")
                self.restartStaticIPThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.ETH)
                self.restartStaticIPThreadObject.signal.connect(self.staticIPReconnectResult)
                self.restartStaticIPThreadObject.start()
                self.staticIPMessageBox = dialog.dialog(self,
                                                        "Restarting networking, please wait...",
                                                        icon="exclamation-mark.png",
                                                        buttons=QtWidgets.QMessageBox.Cancel)
                if self.staticIPMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
                    self.stackedWidget.setCurrentWidget(self.networkSettingsPage)
            elif txtStaticIPInterface == 'wlan0':
                log_info("Restarting networking for wlan0.")
                self.restartWifiThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.WLAN)
                self.restartWifiThreadObject.signal.connect(self.wifiReconnectResult)
                self.restartWifiThreadObject.start()
                self.wifiMessageBox = dialog.dialog(self,
                                                    "Restarting networking, please wait...",
                                                    icon="exclamation-mark.png",
                                                    buttons=QtWidgets.QMessageBox.Cancel)
                if self.wifiMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
                    self.stackedWidget.setCurrentWidget(self.networkSettingsPage)
            log_info("Completed staticIPSaveStaticNetworkInfo method.")
        except Exception as e:
            error_message = f"Error in staticIPSaveStaticNetworkInfo method: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def deleteStaticIPSettings(self):
        try:
            log_info("Starting deleteStaticIPSettings method.")
            Globaltxt = subprocess.Popen("cat /etc/dhcpcd.conf", stdout=subprocess.PIPE, shell=True).communicate()[0].decode('utf8')
            Globaltxt = re.sub(r"interface.*\n", "", Globaltxt)
            Globaltxt = re.sub(r"static.*\n", "", Globaltxt)
            Globaltxt = re.sub(r"^\s+", "", Globaltxt)
            with open("/etc/dhcpcd.conf", "w") as f:
                f.write(Globaltxt)
            self.stackedWidget.setCurrentWidget(self.networkSettingsPage)
            log_info("Completed deleteStaticIPSettings method.")
        except Exception as e:
            error_message = f"Error in deleteStaticIPSettings method: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def staticIPReconnectResult(self, x):
        try:
            log_info("Starting staticIPReconnectResult method.")
            self.staticIPMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            if x is not None:
                self.staticIPMessageBox.setLocalIcon('success.png')
                self.staticIPMessageBox.setText('Connected, IP: ' + x)
            else:
                self.staticIPMessageBox.setText("Not able to set Static IP")
            log_info("Completed staticIPReconnectResult method.")
        except Exception as e:
            error_message = f"Error in staticIPReconnectResult method: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def staticIPShowKeyboard(self, textbox):
        try:
            log_info("Calling staticIPShowKeyboard method.")
            startKeyboard(self, textbox.setText, onlyNumeric=True, noSpace=True, text=str(textbox.text()))
            log_info("Completed staticIPShowKeyboard method.")
        except Exception as e:
            error_message = f"Error in staticIPShowKeyboard method: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

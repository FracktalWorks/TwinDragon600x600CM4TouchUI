import mainGUI
from start_keyboard import startKeyboard
import subprocess
import dialog
import re
from MainUIClass.MainUIClasses.networking_package.wifiSettingsPage import ThreadRestartNetworking
from PyQt5 import QtWidgets
import mainGUI

class staticIPSettings(mainGUI.Ui_MainWindow):

    def init(self):
        super().__init__()

    def setup(self):
        self.staticIPKeyboardButton.pressed.connect(lambda: self.staticIPShowKeyboard(self.staticIPLineEdit))                                                                            
        self.staticIPGatewayKeyboardButton.pressed.connect(lambda: self.staticIPShowKeyboard(self.staticIPGatewayLineEdit))
        self.staticIPNameServerKeyboardButton.pressed.connect(
            lambda: self.staticIPShowKeyboard(self.staticIPNameServerLineEdit))
        self.staticIPSettingsDoneButton.pressed.connect(self.staticIPSaveStaticNetworkInfo)
        self.staticIPSettingsCancelButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
        self.deleteStaticIPSettingsButton.pressed.connect(self.deleteStaticIPSettings)

        # # Display settings
        # self.rotateDisplay.pressed.connect(self.showRotateDisplaySettingsPage)
        # self.calibrateTouch.pressed.connect(self.touchCalibration)
        self.displaySettingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))
        #
        # # Rotate Display Settings
        # self.rotateDisplaySettingsDoneButton.pressed.connect(self.saveRotateDisplaySettings)
        # self.rotateDisplaySettingsCancelButton.pressed.connect(
        #     lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))


    def staticIPSettings(self):
        self.stackedWidget.setCurrentWidget(self.staticIPSettingsPage)
        #add "eth0" and "wlan0" to staticIPComboBox:
        self.staticIPComboBox.clear()
        self.staticIPComboBox.addItems(["eth0", "wlan0"])

    def isIpErr(self, ip):
        return (re.search(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$", ip) is None)

    def showIpErr(self, var):
        return dialog.WarningOk(self, "Invalid input: {0}".format(var))

    def staticIPSaveStaticNetworkInfo(self):
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
        Globaltxt = subprocess.Popen("cat /etc/dhcpcd.conf", stdout=subprocess.PIPE, shell=True).communicate()[
            0].decode('utf8')
        staticIPConfig = ""
        # using regex remove all lines staring with "interface" and "static" from txt
        Globaltxt = re.sub(r"interface.*\n", "", Globaltxt)
        Globaltxt = re.sub(r"static.*\n", "", Globaltxt)
        Globaltxt = re.sub(r"^\s+", "", Globaltxt)                                                 
        staticIPConfig = "\ninterface {0}\nstatic ip_address={1}/24\nstatic routers={2}\nstatic domain_name_servers=8.8.8.8 8.8.4.4 {3}\n\n".format(
            txtStaticIPInterface, txtStaticIPAddress, txtStaticIPGateway, txtStaticIPNameServer)
        Globaltxt = staticIPConfig + Globaltxt
        with open("/etc/dhcpcd.conf", "w") as f:
            f.write(Globaltxt)

        if txtStaticIPInterface == 'eth0':
            print("Restarting networking for eth0")
            self.restartStaticIPThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.ETH)
            self.restartStaticIPThreadObject.signal.connect(self.staticIPReconnectResult)
            self.restartStaticIPThreadObject.start()
            # self.connect(self.restartStaticIPThreadObject, QtCore.SIGNAL(signal), self.staticIPReconnectResult)
            self.staticIPMessageBox = dialog.dialog(self,
                                                    "Restarting networking, please wait...",
                                                    icon="exclamation-mark.png",
                                                    buttons=QtWidgets.QMessageBox.Cancel)
            if self.staticIPMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
                self.stackedWidget.setCurrentWidget(self.networkSettingsPage)
        elif txtStaticIPInterface == 'wlan0':
            print("Restarting networking for wlan0")
            self.restartWifiThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.WLAN)
            self.restartWifiThreadObject.signal.connect(self.wifiReconnectResult)
            self.restartWifiThreadObject.start()
            self.wifiMessageBox = dialog.dialog(self,
                                                "Restarting networking, please wait...",
                                                icon="exclamation-mark.png",
                                                buttons=QtWidgets.QMessageBox.Cancel)
            if self.wifiMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
                self.stackedWidget.setCurrentWidget(self.networkSettingsPage)

    def deleteStaticIPSettings(self):
        Globaltxt = subprocess.Popen("cat /etc/dhcpcd.conf", stdout=subprocess.PIPE, shell=True).communicate()[
            0].decode('utf8')
        # using regex remove all lines staring with "interface" and "static" from txt
        Globaltxt = re.sub(r"interface.*\n", "", Globaltxt)
        Globaltxt = re.sub(r"static.*\n", "", Globaltxt)
        Globaltxt = re.sub(r"^\s+", "", Globaltxt)
        with open("/etc/dhcpcd.conf", "w") as f:
            f.write(Globaltxt)
        self.stackedWidget.setCurrentWidget(self.networkSettingsPage)                                                  
                                                                                                  
    def staticIPReconnectResult(self, x):
        self.staticIPMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        if x is not None:
            self.staticIPMessageBox.setLocalIcon('success.png')
            self.staticIPMessageBox.setText('Connected, IP: ' + x)
        else:

            self.staticIPMessageBox.setText("Not able to set Static IP")

    def staticIPShowKeyboard(self, textbox):
        startKeyboard(self, textbox.setText, onlyNumeric=True, noSpace=True, text=str(textbox.text()))

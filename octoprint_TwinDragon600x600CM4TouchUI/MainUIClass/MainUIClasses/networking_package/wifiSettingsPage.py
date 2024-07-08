import io
import subprocess
from PyQt5 import QtWidgets, QtCore
import dialog
from MainUIClass.network_utils import *
import time
import mainGUI
from MainUIClass.decorators import run_async
from MainUIClass.MainUIClasses.start_keyboard import startKeyboard
from MainUIClass.MainUIClasses.lineEdits import lineEdits
from logger import *
from MainUIClass.MainUIClasses.start_keyboard import startKeyboard

class wifiSettingsPage(lineEdits, mainGUI.Ui_MainWindow):
    def __init__(self):
        """
        Initializes the WiFi settings page.

        """
        try:
            log_info("Starting wifi settings init.")
            super().__init__()
        except Exception as e:
            error_message = f"Error in wifiSettingsPage init: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setup(self):
        """
        Sets up connections for GUI elements and buttons related to WiFi settings.

        """
        try:
            log_info("Setting up wifiSettingsPage.")
            self.wifiPasswordLineEdit.clicked_signal.connect(lambda: startKeyboard(self, self.wifiPasswordLineEdit.setText))
            self.staticIPLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPLineEdit))
            self.staticIPGatewayLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPGatewayLineEdit))
            self.staticIPNameServerLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPNameServerLineEdit))

            self.wifiSettingsSSIDKeyboardButton.pressed.connect(
                lambda: startKeyboard(self, self.wifiSettingsComboBox.addItem))
            self.wifiSettingsCancelButton.pressed.connect(
                lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
            self.wifiSettingsDoneButton.pressed.connect(self.acceptWifiSettings)
            log_info("Completed setup for wifiSettingsPage.")
        except Exception as e:
            error_message = f"Error in wifiSettingsPage setup: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def acceptWifiSettings(self):
        try:
            log_info("Accepting WiFi settings.")
            wlan0_config_file = io.open("/etc/wpa_supplicant/wpa_supplicant.conf", "r+", encoding='utf8')
            wlan0_config_file.truncate()
            ascii_ssid = self.wifiSettingsComboBox.currentText()
            wlan0_config_file.write(u"country=IN\n")
            wlan0_config_file.write(u"ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
            wlan0_config_file.write(u"update_config=1\n")
            wlan0_config_file.write(u"network={\n")
            wlan0_config_file.write(u'ssid="' + str(ascii_ssid) + '"\n')
            if self.hiddenCheckBox.isChecked():
                wlan0_config_file.write(u'scan_ssid=1\n')
            if str(self.wifiPasswordLineEdit.text()) != "":
                wlan0_config_file.write(u'psk="' + str(self.wifiPasswordLineEdit.text()) + '"\n')
            wlan0_config_file.write(u'}')
            wlan0_config_file.close()

            self.restartWifiThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.WLAN)
            self.restartWifiThreadObject.signal.connect(self.wifiReconnectResult)
            self.restartWifiThreadObject.start()
            self.wifiMessageBox = dialog.dialog(self,
                                                "Restarting networking, please wait...",
                                                icon="exclamation-mark.png",
                                                buttons=QtWidgets.QMessageBox.Cancel)
            if self.wifiMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
                self.stackedWidget.setCurrentWidget(self.networkSettingsPage)
            log_info("Completed WiFi settings acceptance.")
        except Exception as e:
            error_message = f"Error in accepting WiFi settings: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def wifiReconnectResult(self, x):
        try:
            log_info("Starting WiFi reconnect result.")
            self.wifiMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            if x is not None:
                print("Ouput from signal " + x)
                self.wifiMessageBox.setLocalIcon('success.png')
                self.wifiMessageBox.setText('Connected, IP: ' + x)
                self.wifiMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
                self.ipStatus.setText(x) #sets the IP addr. in the status bar
            else:
                self.wifiMessageBox.setText("Not able to connect to WiFi")
            log_info("Completed WiFi reconnect result.")
        except Exception as e:
            error_message = f"Error in WiFi reconnect result: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def networkInfo(self):
        try:
            log_info("Displaying network information.")
            ipWifi = getIP(ThreadRestartNetworking.WLAN)
            ipEth = getIP(ThreadRestartNetworking.ETH)

            self.hostname.setText(getHostname())
            self.wifiAp.setText(getWifiAp())
            self.wifiIp.setText("Not connected" if not ipWifi else ipWifi)
            self.ipStatus.setText("Not connected" if not ipWifi else ipWifi)
            self.lanIp.setText("Not connected" if not ipEth else ipEth)
            self.wifiMac.setText(getMac(ThreadRestartNetworking.WLAN).decode('utf8'))
            self.lanMac.setText(getMac(ThreadRestartNetworking.ETH).decode('utf8'))
            self.stackedWidget.setCurrentWidget(self.networkInfoPage)
            log_info("Completed displaying network information.")
        except Exception as e:
            error_message = f"Error in displaying network information: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def wifiSettings(self):
        try:
            log_info("Starting WiFi settings.")
            self.stackedWidget.setCurrentWidget(self.wifiSettingsPage)
            self.wifiSettingsComboBox.clear()
            self.wifiSettingsComboBox.addItems(self.scan_wifi())
            log_info("Completed WiFi settings.")
        except Exception as e:
            error_message = f"Error in WiFi settings: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def scan_wifi(self):
        try:
            log_info("Scanning available WiFi networks.")
            scan_result = subprocess.Popen("iwlist wlan0 scan | grep 'ESSID'", stdout=subprocess.PIPE, shell=True).communicate()[0]
            scan_result = scan_result.decode('utf8').split('ESSID:')
            scan_result = [s.strip() for s in scan_result]
            scan_result = [s.strip('"') for s in scan_result]
            scan_result = list(filter(None, scan_result))
            return scan_result
        except Exception as e:
            error_message = f"Error in scanning WiFi networks: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                return []

    @run_async
    def setIPStatus(self):
        try:
            log_info("Updating IP address status.")
            while True:
                if getIP("eth0"):
                    self.ipStatus.setText(getIP("eth0"))
                elif getIP("wlan0"):
                    self.ipStatus.setText(getIP("wlan0"))
                else:
                    self.ipStatus.setText("Not connected")
                time.sleep(60)
        except Exception as e:
            error_message = f"Error in updating IP address status: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass


class ThreadRestartNetworking(QtCore.QThread):
    WLAN = "wlan0"
    ETH = "eth0"
    signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self, interface):
        """
        Initializes the thread for restarting networking.

        Args:
            interface (str): Interface name ('wlan0' or 'eth0').

        """
        try:
            log_info(f"Starting ThreadRestartNetworking for interface {interface}.")
            super(ThreadRestartNetworking, self).__init__()
            self.interface = interface
        except Exception as e:
            error_message = f"Error in ThreadRestartNetworking init: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(None, error_message, overlay=True):
                pass

    def run(self):
        try:
            log_info(f"Running ThreadRestartNetworking for interface {self.interface}.")
            self.restart_interface()
            attempt = 0
            while attempt < 3:
                if getIP(self.interface):
                    self.signal.emit(getIP(self.interface))
                    break
                else:
                    attempt += 1
                    time.sleep(5)
            if attempt >= 3:
                self.signal.emit(None)
            log_info(f"Completed ThreadRestartNetworking for interface {self.interface}.")
        except Exception as e:
            error_message = f"Error in ThreadRestartNetworking run method: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(None, error_message, overlay=True):
                pass

    def restart_interface(self):
        try:
            log_info(f"Restarting network interface {self.interface}.")
            if self.interface == "wlan0":
                subprocess.call(["wpa_cli", "-i",  self.interface, "reconfigure"], shell=False)
            elif self.interface == "eth0":
                subprocess.call(["ifconfig",  self.interface, "down"], shell=False)
                time.sleep(1)
                subprocess.call(["ifconfig", self.interface, "up"], shell=False)
            time.sleep(5)
            log_info(f"Completed restarting network interface {self.interface}.")
        except Exception as e:
            error_message = f"Error in restarting network interface {self.interface}: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(None, error_message, overlay=True):
                pass

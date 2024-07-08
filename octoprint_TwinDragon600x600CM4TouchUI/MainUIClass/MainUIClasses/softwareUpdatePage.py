import mainGUI
from logger import *
from MainUIClass.MainUIClasses.controlScreen import controlScreen
import dialog
import requests
from MainUIClass.config import apiKey, ip
from PyQt5 import QtCore

class softwareUpdatePage(mainGUI.Ui_MainWindow):
    def __init__(self):
        log_info("Starting software update init.")
        self.octopiclient = None
        super().__init__()

    def setup(self):
        try:
            log_debug("Octopiclient inside class softwareUpdatePage: " + str(self.octopiclient))
            self.softwareUpdateBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))
            self.performUpdateButton.pressed.connect(lambda: self.octopiclient.performSoftwareUpdate())
        except Exception as e:
            error_message = f"Error in setup function of softwareUpdatePage: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def getFirmwareVersion(self):
        try:
            headers = {'X-Api-Key': apiKey}
            req = requests.get(f'http://{ip}/plugin/JuliaFirmwareUpdater/hardware/version', headers=headers)
            data = req.json()
            if req.status_code == requests.codes.ok:
                info = u'\u2713' if not data["update_available"] else u"\u2717"    # icon
                info += " Firmware: "
                info += "Unknown" if not data["variant_name"] else data["variant_name"]
                info += "\n"
                if data["variant_name"]:
                    info += "   Installed: "
                    info += "Unknown" if not data["version_board"] else data["version_board"]
                info += "\n"
                info += "" if not data["version_repo"] else "   Available: " + data["version_repo"]
                return info
        except Exception as e:
            error_message = f"Error in getFirmwareVersion function of softwareUpdatePage: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass
        return u'\u2713' + "Firmware: Unknown\n"

    def displayVersionInfo(self):
        try:
            self.updateListWidget.clear()
            updateAvailable = False
            self.performUpdateButton.setDisabled(True)
            data = self.octopiclient.getSoftwareUpdateInfo()
            if data:
                for item in data["information"]:
                    plugin = data["information"][item]
                    info = u'\u2713' if not plugin["updateAvailable"] else u"\u2717"    # icon
                    info += plugin["displayName"] + "  " + plugin["displayVersion"] + "\n"
                    info += "   Available: "
                    if "information" in plugin and "remote" in plugin["information"] and plugin["information"]["remote"]["value"] is not None:
                        info += plugin["information"]["remote"]["value"]
                    else:
                        info += "Unknown"
                    self.updateListWidget.addItem(info)

                    if plugin["updateAvailable"]:
                        updateAvailable = True
            if updateAvailable:
                self.performUpdateButton.setDisabled(False)
            self.stackedWidget.setCurrentWidget(self.OTAUpdatePage)
        except Exception as e:
            error_message = f"Error in displayVersionInfo function of softwareUpdatePage: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def softwareUpdateResult(self, data):
        try:
            messageText = ""
            for item in data:
                messageText += item + ": " + data[item][0] + ".\n"
            messageText += "Restart required"
            self.askAndReboot(messageText)
        except Exception as e:
            error_message = f"Error in softwareUpdateResult function of softwareUpdatePage: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def softwareUpdateProgress(self, data):
        try:
            self.stackedWidget.setCurrentWidget(self.softwareUpdateProgressPage)
            self.logTextEdit.setTextColor(QtCore.Qt.red)
            self.logTextEdit.append("---------------------------------------------------------------\n"
                                    "Updating " + data["name"] + " to " + data["version"] + "\n"
                                    "---------------------------------------------------------------")
        except Exception as e:
            error_message = f"Error in softwareUpdateProgress function of softwareUpdatePage: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def softwareUpdateProgressLog(self, data):
        try:
            self.logTextEdit.setTextColor(QtCore.Qt.white)
            for line in data:
                self.logTextEdit.append(line["line"])
        except Exception as e:
            error_message = f"Error in softwareUpdateProgressLog function of softwareUpdatePage: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def updateFailed(self, data):
        try:
            self.stackedWidget.setCurrentWidget(self.settingsPage)
            messageText = (data["name"] + " failed to update\n")
            if dialog.WarningOkCancel(self, messageText, overlay=True):
                pass
        except Exception as e:
            error_message = f"Error in updateFailed function of softwareUpdatePage: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def softwareUpdate(self):
        try:
            data = self.octopiclient.getSoftwareUpdateInfo()
            updateAvailable = False
            if data:
                for item in data["information"]:
                    if data["information"][item]["updateAvailable"]:
                        updateAvailable = True
            if updateAvailable:
                print('Update Available')
                if dialog.SuccessYesNo(self, "Update Available! Update Now?", overlay=True):
                    self.octopiclient.performSoftwareUpdate()
            else:
                if dialog.SuccessOk(self, "System is Up To Date!", overlay=True):
                    print('Update Unavailable')
        except Exception as e:
            error_message = f"Error in softwareUpdate function of softwareUpdatePage: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

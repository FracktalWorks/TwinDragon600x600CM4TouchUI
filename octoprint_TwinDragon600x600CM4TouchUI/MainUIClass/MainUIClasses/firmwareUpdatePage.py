import dialog
from MainUIClass.config import ip, apiKey
import requests
import mainGUI
from logger import *

class firmwareUpdatePage(mainGUI.Ui_MainWindow):
    isFirmwareUpdateInProgress = False

    def __init__(self):
        log_info("Starting firmware update init.")
        super().__init__()

    def setup(self):
        log_info("Setting up firmware update.")
        try:
            self.firmwareUpdateBackButton.pressed.connect(self.firmwareUpdateBack)
            log_info("Firmware update setup complete.")
        except Exception as e:
            error_message = f"Error setting up firmware update: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass


    def firmwareUpdateCheck(self):
        headers = {'X-Api-Key': apiKey}
        requests.get('http://{}/plugin/JuliaFirmwareUpdater/update/check'.format(ip), headers=headers)

    def firmwareUpdateStart(self):
        headers = {'X-Api-Key': apiKey}
        requests.get('http://{}/plugin/JuliaFirmwareUpdater/update/start'.format(ip), headers=headers)

    def firmwareUpdateStartProgress(self):
        self.stackedWidget.setCurrentWidget(self.firmwareUpdateProgressPage)
        # self.firmwareUpdateLog.setTextColor(QtCore.Qt.yellow)
        self.firmwareUpdateLog.setText("<span style='color: cyan'>Julia Firmware Updater<span>")
        self.firmwareUpdateLog.append("<span style='color: cyan'>---------------------------------------------------------------</span>")
        self.firmwareUpdateBackButton.setEnabled(False)

    def firmwareUpdateProgress(self, text, backEnabled=False):
        self.stackedWidget.setCurrentWidget(self.firmwareUpdateProgressPage)
        # self.firmwareUpdateLog.setTextColor(QtCore.Qt.yellow)
        self.firmwareUpdateLog.append(str(text))
        self.firmwareUpdateBackButton.setEnabled(backEnabled)

    def firmwareUpdateBack(self):
        self.isFirmwareUpdateInProgress = False
        self.firmwareUpdateBackButton.setEnabled(False)
        self.stackedWidget.setCurrentWidget(self.homePage)

    def firmwareUpdateHandler(self, data):
        if "type" not in data or data["type"] != "status":
            return

        if "status" not in data:
            return

        status = data["status"]
        subtype = data["subtype"] if "subtype" in data else None

        if status == "update_check":    # update check
            if subtype == "error":  # notify error in ok diag
                self.isFirmwareUpdateInProgress = False
                if "message" in data:
                    dialog.WarningOk(self, "Firmware Updater Error: " + str(data["message"]), overlay=True)
            elif subtype == "success":
                if dialog.SuccessYesNo(self, "Firmware update found.\nPress yes to update now!", overlay=True):
                    self.isFirmwareUpdateInProgress = True
                    self.firmwareUpdateStart()
        elif status == "update_start":  # update started
            if subtype == "success":    # update progress
                self.isFirmwareUpdateInProgress = True
                self.firmwareUpdateStartProgress()
                if "message" in data:
                    message = "<span style='color: yellow'>{}</span>".format(data["message"])
                    self.firmwareUpdateProgress(message)
            else:   # show error
                self.isFirmwareUpdateInProgress = False
                # self.firmwareUpdateProgress(data["message"] if "message" in data else "Unknown error!", backEnabled=True)
                if "message" in data:
                    dialog.WarningOk(self, "Firmware Updater Error: " + str(data["message"]), overlay=True)
        elif status == "flasherror" or status == "progress":    # show software update dialog and update textview
            if "message" in data:
                message = "<span style='color: {}'>{}</span>".format("teal" if status == "progress" else "red", data["message"])
                self.firmwareUpdateProgress(message, backEnabled=(status == "flasherror"))
        elif status == "success":    # show ok diag to show done
            self.isFirmwareUpdateInProgress = False
            message = data["message"] if "message" in data else "Flash successful!"
            message = "<span style='color: green'>{}</span>".format(message)
            message = message + "<br/><br/><span style='color: white'>Press back to continue...</span>"
            self.firmwareUpdateProgress(message, backEnabled=True)


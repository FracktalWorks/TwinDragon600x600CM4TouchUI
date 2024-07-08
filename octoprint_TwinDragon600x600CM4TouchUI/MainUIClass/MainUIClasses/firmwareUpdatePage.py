import dialog
from MainUIClass.config import ip, apiKey
import requests
import mainGUI
from logger import *

class firmwareUpdatePage(mainGUI.Ui_MainWindow):
    isFirmwareUpdateInProgress = False

    def __init__(self):
        try:
            log_info("Starting firmware update init.")
            super().__init__()
        except Exception as e:
            error_message = f"Error in firmwareUpdatePage __init__: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setup(self):
        try:
            log_info("Setting up firmware update.")
            self.firmwareUpdateBackButton.pressed.connect(self.firmwareUpdateBack)
            log_info("Firmware update setup complete.")
        except Exception as e:
            error_message = f"Error setting up firmware update: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def firmwareUpdateCheck(self):
        try:
            headers = {'X-Api-Key': apiKey}
            requests.get(f'http://{ip}/plugin/JuliaFirmwareUpdater/update/check', headers=headers)
        except Exception as e:
            error_message = f"Error in firmwareUpdateCheck: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def firmwareUpdateStart(self):
        try:
            headers = {'X-Api-Key': apiKey}
            requests.get(f'http://{ip}/plugin/JuliaFirmwareUpdater/update/start', headers=headers)
        except Exception as e:
            error_message = f"Error in firmwareUpdateStart: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def firmwareUpdateStartProgress(self):
        try:
            log_info("Starting firmware update progress.")
            self.stackedWidget.setCurrentWidget(self.firmwareUpdateProgressPage)
            self.firmwareUpdateLog.setText("<span style='color: cyan'>Julia Firmware Updater<span>")
            self.firmwareUpdateLog.append("<span style='color: cyan'>---------------------------------------------------------------</span>")
            self.firmwareUpdateBackButton.setEnabled(False)
            log_info("Firmware update progress started.")
        except Exception as e:
            error_message = f"Error in firmwareUpdateStartProgress: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def firmwareUpdateProgress(self, text, backEnabled=False):
        try:
            log_info("Updating firmware update progress.")
            self.stackedWidget.setCurrentWidget(self.firmwareUpdateProgressPage)
            self.firmwareUpdateLog.append(str(text))
            self.firmwareUpdateBackButton.setEnabled(backEnabled)
            log_info("Firmware update progress updated.")
        except Exception as e:
            error_message = f"Error in firmwareUpdateProgress: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def firmwareUpdateBack(self):
        try:
            log_info("Returning from firmware update.")
            self.isFirmwareUpdateInProgress = False
            self.firmwareUpdateBackButton.setEnabled(False)
            self.stackedWidget.setCurrentWidget(self.homePage)
            log_info("Returned from firmware update.")
        except Exception as e:
            error_message = f"Error in firmwareUpdateBack: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def firmwareUpdateHandler(self, data):
        try:
            log_info("Handling firmware update.")
            if "type" not in data or data["type"] != "status":
                return

            if "status" not in data:
                return

            status = data["status"]
            subtype = data.get("subtype", None)

            if status == "update_check":
                if subtype == "error":
                    self.isFirmwareUpdateInProgress = False
                    if "message" in data:
                        dialog.WarningOk(self, f"Firmware Updater Error: {data['message']}", overlay=True)
                elif subtype == "success":
                    if dialog.SuccessYesNo(self, "Firmware update found.\nPress yes to update now!", overlay=True):
                        self.isFirmwareUpdateInProgress = True
                        self.firmwareUpdateStart()
            elif status == "update_start":
                if subtype == "success":
                    self.isFirmwareUpdateInProgress = True
                    self.firmwareUpdateStartProgress()
                    if "message" in data:
                        message = f"<span style='color: yellow'>{data['message']}</span>"
                        self.firmwareUpdateProgress(message)
                else:
                    self.isFirmwareUpdateInProgress = False
                    if "message" in data:
                        dialog.WarningOk(self, f"Firmware Updater Error: {data['message']}", overlay=True)
            elif status == "flasherror" or status == "progress":
                if "message" in data:
                    color = "teal" if status == "progress" else "red"
                    message = f"<span style='color: {color}'>{data['message']}</span>"
                    self.firmwareUpdateProgress(message, backEnabled=(status == "flasherror"))
            elif status == "success":
                self.isFirmwareUpdateInProgress = False
                message = data.get("message", "Flash successful!")
                message = f"<span style='color: green'>{message}</span><br/><br/><span style='color: white'>Press back to continue...</span>"
                self.firmwareUpdateProgress(message, backEnabled=True)

            log_info("Finished handling firmware update.")
        except Exception as e:
            error_message = f"Error in firmwareUpdateHandler: {str(e)}"
            log_error(error_message)
            print(e)  
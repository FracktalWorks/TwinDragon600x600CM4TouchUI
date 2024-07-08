from MainUIClass.network_utils import getIP
import qrcode
from MainUIClass.MainUIClasses.networking_package.wifiSettingsPage import ThreadRestartNetworking
from MainUIClass.gui_elements import Image
import dialog
import os
import mainGUI
from MainUIClass.MainUIClasses.dialog_methods import askAndReboot, tellAndReboot
from MainUIClass.config import ip, apiKey
import requests
from logger import *

class settingsPage(mainGUI.Ui_MainWindow):
    def __init__(self):
        log_info("Starting settings init.")
        self.octopiclient = None
        super().__init__()

    def setup(self):
        try:
            log_debug("Octopiclient inside class settingsPage: " + str(self.octopiclient))
            self.settingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
            self.networkSettingsButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
            self.displaySettingsButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))
            self.pairPhoneButton.pressed.connect(self.pairPhoneApp)
            self.OTAButton.pressed.connect(self.softwareUpdate)
            self.versionButton.pressed.connect(self.displayVersionInfo)
            self.restartButton.pressed.connect(lambda: askAndReboot(self))
            self.restoreFactoryDefaultsButton.pressed.connect(self.restoreFactoryDefaults)
            self.restorePrintSettingsButton.pressed.connect(self.restorePrintDefaults)
            self.QRCodeBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))
            log_info("Settings page setup completed.")
        except Exception as e:
            error_message = f"Error in setup function of settingsPage class: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def displayVersionInfo(self):
        try:
            log_debug("Displaying version info.")
            self.updateListWidget.clear()
            updateAvailable = False
            self.performUpdateButton.setDisabled(True)

            self.updateListWidget.addItem(self.getFirmwareVersion())

            data = self.octopiclient.getSoftwareUpdateInfo()
            if data:
                for item in data["information"]:
                    plugin = data["information"][item]
                    info = u'\u2713' if not plugin["updateAvailable"] else u'\u2717'
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
            log_info("Version info displayed.")
        except Exception as e:
            error_message = f"Error in displayVersionInfo function: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def softwareUpdate(self):
        try:
            log_info("Initiating software update.")
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
                log_info("Software update performed.")
            else:
                if dialog.SuccessOk(self, "System is Up To Date!", overlay=True):
                    print('Update Unavailable')
                log_info("System is up to date.")
        except Exception as e:
            error_message = f"Error in softwareUpdate function: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def pairPhoneApp(self):
        try:
            log_info("Pairing phone app.")
            if getIP(ThreadRestartNetworking.ETH) is not None:
                qrip = getIP(ThreadRestartNetworking.ETH)
            elif getIP(ThreadRestartNetworking.WLAN) is not None:
                qrip = getIP(ThreadRestartNetworking.WLAN)
            else:
                if dialog.WarningOk(self, "Network Disconnected"):
                    return
            self.QRCodeLabel.setPixmap(
                qrcode.make("http://" + qrip, image_factory=Image).pixmap())
            self.stackedWidget.setCurrentWidget(self.QRCodePage)
            log_info("Phone app paired successfully.")
        except Exception as e:
            error_message = f"Error in pairPhoneApp function: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def restoreFactoryDefaults(self):
        try:
            if dialog.WarningYesNo(self, "Are you sure you want to restore machine state to factory defaults?\nWarning: Doing so will also reset printer profiles, WiFi & Ethernet config.", overlay=True):
                os.system('sudo cp -f config/dhcpcd.conf /etc/dhcpcd.conf')
                os.system('sudo cp -f config/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf')
                os.system('sudo rm -rf /home/pi/.octoprint/users.yaml')
                os.system('sudo cp -f config/users.yaml /home/pi/.octoprint/users.yaml')
                os.system('sudo rm -rf /home/pi/.octoprint/printerProfiles/*')
                os.system('sudo rm -rf /home/pi/.octoprint/scripts/gcode')
                os.system('sudo rm -rf /home/pi/.octoprint/print_restore.json')
                os.system('sudo cp -f config/config.yaml /home/pi/.octoprint/config.yaml')
                self.tellAndReboot("Settings restored. Rebooting...")
                log_info("Factory defaults restored and reboot initiated.")
        except Exception as e:
            error_message = f"Error in restoreFactoryDefaults function: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def restorePrintDefaults(self):
        try:
            if dialog.WarningYesNo(self, "Are you sure you want to restore default print settings?\nWarning: Doing so will erase offsets and bed leveling info", overlay=True):
                os.system('sudo cp -f firmware/GCodes.cfg /home/pi/GCodes.cfg')
                log_info("Copied GCodes.cfg")
                os.system('sudo cp -f firmware/IDEX_mode.cfg /home/pi/IDEX_mode.cfg')
                log_info("Copied IDEX_mode.cfg")
                os.system('sudo cp -f firmware/printer.cfg /home/pi/printer.cfg')
                log_info("Copied printer.cfg")
                os.system('sudo cp -f firmware/variables.cfg /home/pi/variables.cfg')
                log_info("Copied variables.cfg")
                self.octopiclient.gcode(command='M502')
                self.octopiclient.gcode(command='M500')
                self.octopiclient.gcode(command='FIRMWARE_RESTART')
                log_info("Default print settings restored and firmware restarted.")
        except Exception as e:
            error_message = f"Error in restorePrintDefaults function: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def getFirmwareVersion(self):
        """
        This is currently getting Marlin fimrware, unnecessary for Klipper based printers.
        """
        pass

        # try:
        #     log_info("Fetching firmware version.")
        #     headers = {'X-Api-Key': apiKey}
        #     req = requests.get(f'http://{ip}/plugin/JuliaFirmwareUpdater/hardware/version', headers=headers)
        #     log_info("Req: " + str(req))
        #     data = req.json()
        #     if req.status_code == requests.codes.ok:
        #         info = u'\u2713' if not data["update_available"] else u"\u2717"
        #         info += " Firmware: "
        #         info += "Unknown" if not data["variant_name"] else data["variant_name"]
        #         info += "\n"
        #         if data["variant_name"]:
        #             info += "   Installed: "
        #             info += "Unknown" if not data["version_board"] else data["version_board"]
        #         info += "\n"
        #         info += "" if not data["version_repo"] else "   Available: " + data["version_repo"]
        #         return info
        # except Exception as e:
        #     error_message = f"Error in getFirmwareVersion function: {str(e)}"
        #     log_error(error_message)
        #     if dialog.WarningOk(self, error_message, overlay=True):
        #         pass
        # return u'\u2713' + "Firmware: Unknown\n"

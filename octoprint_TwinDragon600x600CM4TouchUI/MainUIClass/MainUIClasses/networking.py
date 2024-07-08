from MainUIClass.MainUIClasses.networking_package.wifiSettingsPage import wifiSettingsPage
from MainUIClass.MainUIClasses.networking_package.staticIPSettings import staticIPSettings
from logger import *
import dialog

class networking(wifiSettingsPage, staticIPSettings):
    def __init__(self):
        log_info("Starting networking init.")
        super().__init__()

    def setup(self):
        """
        Sets up signal connections for networking settings UI elements.
        """
        try:
            log_info("Starting setup in networking class.")
            wifiSettingsPage.setup(self)
            staticIPSettings.setup(self)

            # Network settings page
            self.networkInfoButton.pressed.connect(self.networkInfo)
            self.configureWifiButton.pressed.connect(self.wifiSettings)
            self.configureStaticIPButton.pressed.connect(self.staticIPSettings)
            self.networkSettingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

            # Network Info Page
            self.networkInfoBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))

            log_info("Networking setup completed.")
        except Exception as e:
            error_message = f"Error setting up networking: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def networkInfo(self):
        """
        Handles displaying network information page.
        """
        try:
            log_info("Displaying network information page.")
            self.stackedWidget.setCurrentWidget(self.networkInfoPage)
        except Exception as e:
            error_message = f"Error navigating to network info page: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def wifiSettings(self):
        """
        Handles displaying WiFi settings page.
        """
        try:
            log_info("Displaying WiFi settings page.")
            self.stackedWidget.setCurrentWidget(self.wifiSettingsPage)
        except Exception as e:
            error_message = f"Error navigating to WiFi settings page: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def ethSettings(self):
        """
        Handles displaying Ethernet settings page.
        """
        try:
            log_info("Displaying Ethernet settings page.")
            self.stackedWidget.setCurrentWidget(self.ethernetSettingsPage)
        except Exception as e:
            error_message = f"Error navigating to Ethernet settings page: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

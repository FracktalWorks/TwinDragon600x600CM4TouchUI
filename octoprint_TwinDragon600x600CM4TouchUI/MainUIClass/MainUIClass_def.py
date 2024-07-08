from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow

from MainUIClass.MainUIClasses.printerName import printerName
from MainUIClass.MainUIClasses.changeFilamentRoutine import changeFilamentRoutine
from MainUIClass.MainUIClasses.controlScreen import controlScreen
from MainUIClass.MainUIClasses.displaySettings import displaySettings
from MainUIClass.MainUIClasses.filamentSensor import filamentSensor
from MainUIClass.MainUIClasses.firmwareUpdatePage import firmwareUpdatePage
from MainUIClass.MainUIClasses.getFilesAndInfo import getFilesAndInfo
from MainUIClass.MainUIClasses.homePage import homePage
from MainUIClass.MainUIClasses.menuPage import menuPage
from MainUIClass.MainUIClasses.printLocationScreen import printLocationScreen
from MainUIClass.MainUIClasses.printRestore import printRestore
from MainUIClass.MainUIClasses.settingsPage import settingsPage
from MainUIClass.MainUIClasses.softwareUpdatePage import softwareUpdatePage
from MainUIClass.MainUIClasses.start_keyboard import startKeyboard
from MainUIClass.MainUIClasses.calibrationPage import calibrationPage
from MainUIClass.MainUIClasses.networking import networking
from MainUIClass.MainUIClasses.threads import ThreadSanityCheck
from MainUIClass.MainUIClasses.lineEdits import lineEdits
from MainUIClass.MainUIClasses.socketConnections import socketConnections
from MainUIClass.MainUIClasses.activeExtruder import activeExtruder
from MainUIClass.MainUIClasses.doorLock import doorLock
from MainUIClass.MainUIClasses.idexConfig import idexConfig
# from MainUIClass.MainUIClasses.lockSettings import lockSettings
from MainUIClass.config import _fromUtf8, setCalibrationPosition, setTool0PurgePositions, setTool1PurgePosition, getCalibrationPosition, getTool0PurgePosition, getTool1PurgePosition, Development
import logging
from MainUIClass.socket_qt import QtWebsocket
from logger import *
import dialog
import os
import subprocess
import glob

class MainUIClass(QMainWindow, activeExtruder, doorLock, idexConfig, printerName, changeFilamentRoutine, controlScreen, displaySettings, filamentSensor, firmwareUpdatePage, getFilesAndInfo, homePage, menuPage, printLocationScreen, printRestore, settingsPage, softwareUpdatePage, calibrationPage, networking, lineEdits, socketConnections):
    
    def __init__(self):
        try:
            log_info("Starting mainUI init.")
            

            '''
            This method gets called when an object of type MainUIClass is defined
            '''
            log_info("Initialising all.")
            super(MainUIClass, self).__init__()
            log_info("Done initialising all mainUI classes.")

            # raise Exception("Ono error happened :'(")
            
            if not Development:
                formatter = logging.Formatter("%(asctime)s %(message)s")
                self._logger = logging.getLogger("TouchUI")
                file_handler = logging.FileHandler("/home/pi/ui.log")
                file_handler.setFormatter(formatter)
                stream_handler = logging.StreamHandler()
                stream_handler.setFormatter(formatter)
                file_handler.setLevel(logging.DEBUG)
                self._logger.addHandler(file_handler)
                self._logger.addHandler(stream_handler)
            try:
                # if not Development:
                    # self.__packager = asset_bundle.AssetBundle()
                    # self.__packager.save_time()
                    # self.__timelapse_enabled = self.__packager.read_match() if self.__packager.time_delta() else True
                    # self.__timelapse_started = not self.__packager.time_delta()

                    # self._logger.info("Hardware ID = {}, Unlocked = {}".format(self.__packager.hc(), self.__timelapse_enabled))
                    # print("Hardware ID = {}, Unlocked = {}".format(self.__packager.hc(), self.__timelapse_enabled))
                    # self._logger.info("File time = {}, Demo = {}".format(self.__packager.read_time(), self.__timelapse_started))
                    # print("File time = {}, Demo = {}".format(self.__packager.read_time(), self.__timelapse_started))
                self.setupUi(self)
                self.stackedWidget.setCurrentWidget(self.loadingPage)
                self.setStep(10)
                self.keyboardWindow = None
                self.changeFilamentHeatingFlag = False
                self.setHomeOffsetBool = False
                self.currentImage = None
                self.currentFile = None
                # if not Development:
                #     self.sanityCheck = ThreadSanityCheck(self._logger, virtual=not self.__timelapse_enabled)
                # else:
                self.sanityCheck = ThreadSanityCheck(virtual=False)
                self.sanityCheck.start()
                
                self.sanityCheck.loaded_signal.connect(self.proceed)
                self.sanityCheck.startup_error_signal.connect(self.handleStartupError)

                self.setNewToolZOffsetFromCurrentZBool = False
                self.setActiveExtruder(0)

                self.dialog_doorlock = None
                self.dialog_filamentsensor = None

                for spinbox in self.findChildren(QtWidgets.QSpinBox):
                    lineEdit = spinbox.lineEdit()
                    lineEdit.setReadOnly(True)
                    lineEdit.setDisabled(True)
                    p = lineEdit.palette()
                    p.setColor(QtGui.QPalette.Highlight, QtGui.QColor(40, 40, 40))
                    lineEdit.setPalette(p)


            except Exception as e:
                if not Development:
                    self._logger.error(e)
        except Exception as e:
            log_error(f"Error during init in MainUIClass: {str(e)}")
            if dialog.WarningOk(self, f"Error during init in MainUIClass: {str(e)}"):
                pass

    def setupUi(self, MainWindow):
        try:
            log_info("setup UI")
            
            super(MainUIClass, self).setupUi(MainWindow)

            lineEdits.setup(self)

            self.menuCartButton.setDisabled(True)
            self.testPrintsButton.setDisabled(True)

            printerName.setup(self)

            self.printerName = self.getPrinterName()
            log_info(str(self.printerName))

            self.setPrinterNameComboBox()
            setCalibrationPosition(self)
            setTool0PurgePositions(self)
            setTool1PurgePosition(self)

            self.calibrationPosition = getCalibrationPosition(self)
            self.tool0PurgePosition = getTool0PurgePosition(self)
            self.tool1PurgePosition = getTool1PurgePosition(self)

            if self.printerName == "Twin Dragon 600 x 600 x 400":
                self.movie = QtGui.QMovie("templates/img/loading-90.gif")

            self.loadingGif.setMovie(self.movie)
            self.movie.start()

        except Exception as e:
            log_error(f"Error during setupUi in MainUIClass: {str(e)}")
            if dialog.WarningOk(self, f"Error during setupUi in MainUIClass: {str(e)}"):
                pass

    def safeProceed(self, octopiclient):
        try:
            log_info("safe proceed")
            
            '''
            When Octoprint server cannot connect for whatever reason, still show the home screen to conduct diagnostics
            '''

            self.movie.stop()
            if not Development:
                self.stackedWidget.setCurrentWidget(self.homePage)
                # self.Lock_showLock()
                self.networkingInstance.setIPStatus()
            else:
                self.stackedWidget.setCurrentWidget(self.homePage)

            # Text Input events
            self.wifiPasswordLineEdit.clicked_signal.connect(lambda: self.startKeyboard(self.wifiPasswordLineEdit.setText))
            self.staticIPLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPLineEdit))
            self.staticIPGatewayLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPGatewayLineEdit))
            self.staticIPNameServerLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPNameServerLineEdit))

            # Button Events:

            # Home Screen:
            self.stopButton.setDisabled(True)
            # self.menuButton.pressed.connect(self.keyboardButton)
            self.menuButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
            self.controlButton.setDisabled(True)
            self.playPauseButton.setDisabled(True)

            # MenuScreen
            self.menuBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.homePage))
            self.menuControlButton.setDisabled(True)
            self.menuPrintButton.setDisabled(True)
            self.menuCalibrateButton.setDisabled(True)
            self.menuSettingsButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))


            # Settings Page
            self.networkSettingsButton.pressed.connect(
                lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
            self.displaySettingsButton.pressed.connect(
                lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))
            self.settingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
            self.pairPhoneButton.pressed.connect(self.pairPhoneApp)
            self.OTAButton.setDisabled(True)
            self.versionButton.setDisabled(True)

            self.restartButton.pressed.connect(self.askAndReboot)
            self.restoreFactoryDefaultsButton.pressed.connect(self.restoreFactoryDefaults)
            self.restorePrintSettingsButton.pressed.connect(self.restorePrintDefaults)

            # Network settings page
            self.networkInfoButton.pressed.connect(self.networkInfo)
            self.configureWifiButton.pressed.connect(self.wifiSettings)
            self.configureStaticIPButton.pressed.connect(self.staticIPSettings)
            self.networkSettingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

            # Network Info Page
            self.networkInfoBackButton.pressed.connect(
                lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))

            # WifiSetings page
            self.wifiSettingsSSIDKeyboardButton.pressed.connect(
                lambda: self.startKeyboard(self.wifiSettingsComboBox.addItem))
            self.wifiSettingsCancelButton.pressed.connect(
                lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
            self.wifiSettingsDoneButton.pressed.connect(self.acceptWifiSettings)

            # Static IP settings page
            self.staticIPKeyboardButton.pressed.connect(lambda: self.staticIPShowKeyboard(self.staticIPLineEdit))
            self.staticIPGatewayKeyboardButton.pressed.connect(
                lambda: self.staticIPShowKeyboard(self.staticIPGatewayLineEdit))
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

            # QR Code
            self.QRCodeBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

            # SoftwareUpdatePage
            self.softwareUpdateBackButton.setDisabled(True)
            self.performUpdateButton.setDisabled(True)

            # Firmware update page
            self.firmwareUpdateBackButton.setDisabled(True)

            # Filament sensor toggle
            self.toggleFilamentSensorButton.setDisabled(True)


        except Exception as e:
            log_error(f"Error during safeProceed in MainUIClass: {str(e)}")
            if dialog.WarningOk(self, f"Error during safeProceed in MainUIClass: {str(e)}"):
                pass
    
    def proceed(self):
        try:
            log_info("proceed")
            
            '''
            Startes websocket, as well as initialises button actions and callbacks. THis is done in such a manner so that the callbacks that dnepend on websockets
            load only after the socket is available which in turn is dependent on the server being available which is checked in the sanity check thread
            '''

            self.octopiclient = self.sanityCheck.get_octopiclient()
            log_debug("Octopiclient received in MainUIClass: " + str(self.octopiclient))

            self.QtSocket = QtWebsocket()
            self.QtSocket.start()
            self.setActions()
            self.movie.stop()
            if not Development:
                self.stackedWidget.setCurrentWidget(self.homePage)
                # self.Lock_showLock()
                self.setIPStatus()
            else:
                self.stackedWidget.setCurrentWidget(self.homePage)
            self.isFilamentSensorInstalled()
            self.onServerConnected()
            self.checkKlipperPrinterCFG()
        except Exception as e:
            log_error(f"Error during proceed in MainUIClass: {str(e)}")
            if dialog.WarningOk(self, f"Error during proceed in MainUIClass: {str(e)}"):
                pass

    def setActions(self): 
        try:       
            '''
            defines all the Slots and Button events.
            '''
            
            log_info("set actions")

            socketConnections.setup(self)
            calibrationPage.setup(self)
            changeFilamentRoutine.setup(self)
            controlScreen.setup(self)
            displaySettings.setup(self)
            filamentSensor.setup(self)
            firmwareUpdatePage.setup(self)
            getFilesAndInfo.setup(self)
            homePage.setup(self)
            menuPage.setup(self)
            printLocationScreen.setup(self)
            printRestore.setup(self)
            settingsPage.setup(self)
            softwareUpdatePage.setup(self)
            networking.setup(self)
            lineEdits.setup(self)
            activeExtruder.setup(self)
            idexConfig.setup(self)
            doorLock.setup(self)
            printerName.setup(self)
            self.QtSocket.connected_signal.connect(self.onServerConnected)

            log_info("set actions complete")

            #  # Lock settings
            #     if not Development:
            #         self.lockSettingsInstance = lockSettings(self)
        except Exception as e:
            log_error(f"Error during setActions in MainUIClass: {str(e)}")
            if dialog.WarningOk(self, f"Error during setActions in MainUIClass: {str(e)}"):
                pass
    
    def handleStartupError(self):
        try:
            log_info("Handle startup error")
            
            log_warning('Unable to connect to Octoprint Server')
            if dialog.WarningYesNo(self,  "Server Error, Restore failsafe settings?", overlay=True):
                os.system('sudo rm -rf /home/pi/.octoprint/users.yaml')
                os.system('sudo rm -rf /home/pi/.octoprint/config.yaml')
                os.system('sudo cp -f config/users.yaml /home/pi/.octoprint/users.yaml')
                os.system('sudo cp -f config/config.yaml /home/pi/.octoprint/config.yaml')
                subprocess.call(["sudo", "systemctl", "restart", "octoprint"])
                self.sanityCheck.start()
            else:
                self.safeProceed()
        except Exception as e:
            log_error(f"Error during handleStartUpError in MainUIClass: {str(e)}")
            if dialog.WarningOk(self, f"Error during handleStartUpError in MainUIClass: {str(e)}"):
                pass

    def onServerConnected(self):
        
        try:
            log_info("Starting onServerConnected init.")
            self.isFilamentSensorInstalled()
            # if not self.__timelapse_enabled:
            #     return
            # if self.__timelapse_started:
            #     return
            
            log_info("octopiclient at response = self.octopiclient.isFailureDetected(): " + str(self.octopiclient))
            response = self.octopiclient.isFailureDetected()
            if response["canRestore"] is True:
                # log_debug("response['canRestore'] is True")
                self.printRestoreMessageBox(response["file"])
            else:
                # log_debug("response['canRestore'] is False")
                self.firmwareUpdateCheck()

            log_info("Exiting on server connected.")

        except Exception as e:
            log_error(f"Error during onServerConnected in MainUIClass: {str(e)}")
            if dialog.WarningOk(self, f"Error during onServerConnected in MainUIClass: {str(e)}"):
                pass

    def checkKlipperPrinterCFG(self):
        '''
        Checks for valid printer.cfg and restores if needed
        '''
        try:
            # Open the printer.cfg file:
            try:
                with open('/home/pi/printer.cfg', 'r') as currentConfigFile:
                    currentConfig = currentConfigFile.read()
                    if "# MCU Config" in currentConfig:
                        configCorruptedFlag = False
                        print("Printer Config File OK")
                    else:
                        configCorruptedFlag = True
                        print("Printer Config File Corrupted")
            except:
                configCorruptedFlag = True
                print("Printer Config File Not Found")

            if configCorruptedFlag:
                backupFiles = sorted(glob.glob('/home/pi/printer-*.cfg'), key=os.path.getmtime, reverse=True)
                print("\n".join(backupFiles))
                for backupFile in backupFiles:
                    with open(str(backupFile), 'r') as backupConfigFile:
                        backupConfig = backupConfigFile.read()
                        if "# MCU Config" in backupConfig:
                            try:
                                os.remove('/home/pi/printer.cfg')
                            except:
                                print("Files does not exist for deletion")
                            try:
                                os.rename(backupFile, '/home/pi/printer.cfg')
                                print("Printer Config File Restored")
                                return()
                            except:
                                pass
                # If no valid backups found, show error dialog:
                dialog.WarningOk(self, "Printer Config File corrupted. Contact Fracktal support or raise a ticket at care.fracktal.in")
                print("Printer Config File corrupted. Contact Fracktal support or raise a ticket at care.fracktal.in")
                if self.printerStatus == "Printing":
                    self.octopiclient.cancelPrint()
                    self.coolDownAction()
            elif not configCorruptedFlag:
                backupFiles = sorted(glob.glob('/home/pi/printer-*.cfg'), key=os.path.getmtime, reverse=True)
                try:
                    for backupFile in backupFiles[5:]:
                        os.remove(backupFile)
                except:
                    pass
        except Exception as e:
            log_error(f"Error during checkKlipperPrinterCFG in MainUIClass: {str(e)}")
            if dialog.WarningOk(self, f"Error during checkKlipperPrinterCFG in MainUIClass: {str(e)}"):
                pass

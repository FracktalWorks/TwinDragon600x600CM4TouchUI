import dialog
import mainGUI
from MainUIClass.MainUIClasses.socketConnections import printerStatusText
from MainUIClass.MainUIClasses.controlScreen import controlScreen
from logger import *

class homePage(mainGUI.Ui_MainWindow):
    def __init__(self):
        log_info("Starting home page init.")
        self.octopiclient = None
        super().__init__()
    
    def setup(self):
        """
        Sets up signal connections for various UI elements.
        """
        log_info("Setting up homePage.")
        try:
            log_debug("Octopiclient inside class homePage: " + str(self.octopiclient))
            
            # Connect signals
            self.stopButton.pressed.connect(self.stopActionMessageBox)
            # self.menuButton.pressed.connect(self.keyboardButton)
            self.menuButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
            self.controlButton.pressed.connect(self.control)
            self.playPauseButton.clicked.connect(self.playPauseAction)
            self.doorLockButton.clicked.connect(self.doorLock)

            log_info("Setup for homePage complete.")
        except Exception as e:
            error_message = f"Error setting up homePage: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def stopActionMessageBox(self):
        '''
        Displays a message box asking if the user is sure if he wants to turn off the print
        '''
        if dialog.WarningYesNo(self, "Are you sure you want to stop the print?"):
            self.octopiclient.cancelPrint()

    def playPauseAction(self):
        '''
        Toggles Play/Pause of a print depending on the status of the print
        '''
        if self.printerStatusText == "Operational":
            if self.playPauseButton.isChecked:
                self.checkKlipperPrinterCFG()
                self.octopiclient.startPrint()
        elif self.printerStatusText == "Printing":
           self.octopiclient.pausePrint()
        elif self.printerStatusText == "Paused":
            self.octopiclient.pausePrint()

import dialog
from logger import *
import mainGUI
from PyQt5 import QtGui
from MainUIClass.config import _fromUtf8

class doorLock(mainGUI.Ui_MainWindow):
    def __init__(self):
        log_info("Starting door lock init.")
        self.octopiclient = None
        super().__init__()
    
    def setup(self):
        """
        Sets up signal connections for various UI elements.
        """
        log_info("Setting up homePage.")
        try:
            log_debug("Octopiclient inside class doorLock: " + str(self.octopiclient))
            
            self.doorLockButton.clicked.connect(self.doorLock)

            log_info("Setup for doorLock complete.")
        except Exception as e:
            error_message = f"Error setting up doorLock: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def doorLock(self):
        '''
        function that toggles locking and unlocking the front door
        :return:
        '''
        self.octopiclient.gcode(command='DoorToggle')

    def doorLockMsg(self, data):
        if "msg" not in data:
            return

        msg = data["msg"]

        if self.dialog_doorlock:
            self.dialog_doorlock.close()
            self.dialog_doorlock = None

        if msg is not None:
            self.dialog_doorlock = dialog.dialog(self, msg, icon="exclamation-mark.png")
            if self.dialog_doorlock.exec_() == QtGui.QMessageBox.Ok:
                self.dialog_doorlock = None
                return

    def doorLockHandler(self, data):
        door_lock_disabled = False
        door_lock = False
        # door_sensor = False
        # door_lock_override = False

        if 'door_lock' in data:
            door_lock_disabled = data["door_lock"] == "disabled"
            door_lock = data["door_lock"] == 1
        # if 'door_sensor' in data:
        #     door_sensor = data["door_sensor"] == 1
        # if 'door_lock_override' in data:
        #     door_lock_override = data["door_lock_override"] == 1

        # if self.dialog_doorlock:
        #     self.dialog_doorlock.close()
        #     self.dialog_doorlock = None

        self.doorLockButton.setVisible(not door_lock_disabled)
        if not door_lock_disabled:
            # self.doorLockButton.setChecked(not door_lock)
            self.doorLockButton.setText('Lock Door' if not door_lock else 'Unlock Door')

            icon = 'doorLock' if not door_lock else 'doorUnlock'
            self.doorLockButton.setIcon(QtGui.QIcon(_fromUtf8("templates/img/" + icon + ".png")))
        else:
            return

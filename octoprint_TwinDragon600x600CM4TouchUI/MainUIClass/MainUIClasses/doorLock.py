import dialog
from logger import *
import mainGUI
from PyQt5 import QtGui
from MainUIClass.config import _fromUtf8

class doorLock(mainGUI.Ui_MainWindow):
    def __init__(self):
        try:
            log_info("Starting door lock init.")
            self.octopiclient = None
            super().__init__()
        except Exception as e:
            error_message = f"Error in doorLock init: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(None, error_message, overlay=True):
                pass
    
    def setup(self):
        """
        Sets up signal connections for various UI elements.
        """
        try:
            log_info("Setting up doorLock.")
            log_debug("Octopiclient inside class doorLock: " + str(self.octopiclient))
            
            self.doorLockButton.clicked.connect(self.doorLock)

            log_info("Setup for doorLock complete.")
        except Exception as e:
            error_message = f"Error setting up doorLock: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(None, error_message, overlay=True):
                pass

    def doorLock(self):
        try:
            '''
            Function that toggles locking and unlocking the front door.
            '''
            log_info("Toggling door lock state.")
            self.octopiclient.gcode(command='DoorToggle')
        except Exception as e:
            error_message = f"Error toggling door lock state: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(None, error_message, overlay=True):
                pass

    def doorLockMsg(self, data):
        try:
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
        except Exception as e:
            error_message = f"Error handling door lock message: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(None, error_message, overlay=True):
                pass

    def doorLockHandler(self, data):
        try:
            door_lock_disabled = False
            door_lock = False

            if 'door_lock' in data:
                door_lock_disabled = data["door_lock"] == "disabled"
                door_lock = data["door_lock"] == 1

            self.doorLockButton.setVisible(not door_lock_disabled)
            if not door_lock_disabled:
                self.doorLockButton.setText('Lock Door' if not door_lock else 'Unlock Door')

                icon = 'doorLock' if not door_lock else 'doorUnlock'
                self.doorLockButton.setIcon(QtGui.QIcon(_fromUtf8("templates/img/" + icon + ".png")))
        except Exception as e:
            error_message = f"Error handling door lock data: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(None, error_message, overlay=True):
                pass

import mainGUI
import time
from PyQt5 import QtGui
from MainUIClass.config import _fromUtf8

class activeExtruder(mainGUI.Ui_MainWindow):
    def __init__(self):
        super().__init__()

    def setup(self):
        pass

    def selectToolChangeFilament(self):
        '''
        Selects the tool whose temperature needs to be changed. It accordingly changes the button text. it also updates the status of the other toggle buttons
        '''
        try:
            if self.toolToggleChangeFilamentButton.isChecked():
                self.setActiveExtruder(1)
                self.octopiclient.selectTool(1)
                time.sleep(1)
            else:
                self.setActiveExtruder(0)
                self.octopiclient.selectTool(0)
                time.sleep(1)
        except Exception as e:
            error_message = f"Error in selectToolChangeFilament: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def selectToolMotion(self):
        '''
        Selects the tool whose temperature needs to be changed. It accordingly changes the button text. it also updates the status of the other toggle buttons
        '''
        try:
            if self.toolToggleMotionButton.isChecked():
                self.setActiveExtruder(1)
                self.octopiclient.selectTool(1)
            else:
                self.setActiveExtruder(0)
                self.octopiclient.selectTool(0)
        except Exception as e:
            error_message = f"Error in selectToolMotion: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def selectToolTemperature(self):
        '''
        Selects the tool whose temperature needs to be changed. It accordingly changes the button text.it also updates the status of the other toggle buttons
        '''
        try:
            if self.toolToggleTemperatureButton.isChecked():
                print("extruder 1 Temperature")
                self.toolTempSpinBox.setProperty("value", float(self.tool1TargetTemperature.text()))
            else:
                print("extruder 0 Temperature")
                self.toolTempSpinBox.setProperty("value", float(self.tool0TargetTemperature.text()))
        except Exception as e:
            error_message = f"Error in selectToolTemperature: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setActiveExtruder(self, activeNozzle):
        try:
            activeNozzle = int(activeNozzle)
            if activeNozzle == 0:
                self.tool0Label.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/activeNozzle.png")))
                self.tool1Label.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/Nozzle.png")))
                self.toolToggleChangeFilamentButton.setChecked(False)
                self.toolToggleMotionButton.setChecked(False)
                self.toolToggleMotionButton.setText("0")
                self.activeExtruder = 0
            elif activeNozzle == 1:
                self.tool0Label.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/Nozzle.png")))
                self.tool1Label.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/activeNozzle.png")))
                self.toolToggleChangeFilamentButton.setChecked(True)
                self.toolToggleMotionButton.setChecked(True)
                self.toolToggleMotionButton.setText("1")
                self.activeExtruder = 1
        except Exception as e:
            error_message = f"Error in setActiveExtruder: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass
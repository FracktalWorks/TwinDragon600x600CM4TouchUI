from MainUIClass.config import filaments
import mainGUI
from MainUIClass.MainUIClasses.socketConnections import printerStatusText
from logger import *
import dialog
import time
from MainUIClass.decorators import run_async
from MainUIClass.config import ptfeTubeLength

class changeFilamentRoutine(mainGUI.Ui_MainWindow):
    def __init__(self):
        try:
            log_info("Starting change filament init.")
            self.octopiclient = None
            super().__init__()
            log_info("Completed change filament init.")
        except Exception as e:
            error_message = f"Error in changeFilamentRoutine __init__: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setup(self):
        try:
            log_info("Starting setup.")

            log_debug("Octopiclient inside class changeFilamentRoutine: " + str(self.octopiclient))
            self.changeFilamentButton.pressed.connect(self.changeFilament)
            self.toolToggleChangeFilamentButton.clicked.connect(self.selectToolChangeFilament)
            self.changeFilamentBackButton.pressed.connect(self.control)
            self.changeFilamentBackButton2.pressed.connect(self.changeFilamentCancel)
            self.changeFilamentBackButton3.pressed.connect(self.changeFilamentCancel)
            self.changeFilamentUnloadButton.pressed.connect(self.unloadFilament)
            self.changeFilamentLoadButton.pressed.connect(self.loadFilament)
            self.loadedTillExtruderButton.pressed.connect(self.changeFilamentExtrudePageFunction)
            self.loadDoneButton.pressed.connect(self.control)
            self.unloadDoneButton.pressed.connect(self.changeFilament)
            # self.retractFilamentButton.pressed.connect(lambda: self.octopiclient.extrude(-20))
            # self.ExtrudeButton.pressed.connect(lambda: self.octopiclient.extrude(20))

            log_info("Completed setup.")
        except Exception as e:
            error_message = f"Error in changeFilamentRoutine setup: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def calcExtrudeTime(self, length, speed):
        try:
            '''
            Calculate the time it takes to extrude a certain length of filament at a certain speed
            :param length: length of filament to extrude
            :param speed: speed at which to extrude
            :return: time in seconds
            '''
            return length / (speed/60)
        except Exception as e:
            error_message = f"Error in changeFilamentRoutine calcExtrudeTime: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def unloadFilament(self):
        try:
            # Update
            if self.printerStatusText not in ["Printing","Paused"]:
                if self.activeExtruder == 1:
                    self.octopiclient.jog(self.tool1PurgePosition['X'],self.tool1PurgePosition["Y"] ,absolute=True, speed=10000)
                else:
                    self.octopiclient.jog(self.tool0PurgePosition['X'],self.tool0PurgePosition["Y"] ,absolute=True, speed=10000)

            if self.changeFilamentComboBox.findText("Loaded Filament") == -1:
                self.octopiclient.setToolTemperature({"tool1": filaments[str(self.changeFilamentComboBox.currentText())]}) if self.activeExtruder == 1 else self.octopiclient.setToolTemperature({"tool0": filaments[str(self.changeFilamentComboBox.currentText())]})
            self.stackedWidget.setCurrentWidget(self.changeFilamentProgressPage)
            self.changeFilamentStatus.setText("Heating Tool {}, Please Wait...".format(str(self.activeExtruder)))
            self.changeFilamentNameOperation.setText("Unloading {}".format(str(self.changeFilamentComboBox.currentText())))
            # this flag tells the updateTemperature function that runs every second to update the filament change progress bar as well, and to load or unload after heating done
            self.changeFilamentHeatingFlag = True
            self.loadFlag = False
        except Exception as e:
            error_message = f"Error in changeFilamentRoutine unloadFilament: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def loadFilament(self):
        try:
            # Update
            if self.printerStatusText not in ["Printing","Paused"]:
                if self.activeExtruder == 1:
                    self.octopiclient.jog(self.tool1PurgePosition['X'],self.tool1PurgePosition["Y"] ,absolute=True, speed=10000)
                else:
                    self.octopiclient.jog(self.tool0PurgePosition['X'],self.tool0PurgePosition["Y"] ,absolute=True, speed=10000)

            if self.changeFilamentComboBox.findText("Loaded Filament") == -1:
                self.octopiclient.setToolTemperature({"tool1": filaments[str(self.changeFilamentComboBox.currentText())]}) if self.activeExtruder == 1 else self.octopiclient.setToolTemperature({"tool0": filaments[str(self.changeFilamentComboBox.currentText())]})
            self.stackedWidget.setCurrentWidget(self.changeFilamentProgressPage)
            self.changeFilamentStatus.setText("Heating Tool {}, Please Wait...".format(str(self.activeExtruder)))
            self.changeFilamentNameOperation.setText("Loading {}".format(str(self.changeFilamentComboBox.currentText())))
            # this flag tells the updateTemperature function that runs every second to update the filament change progress bar as well, and to load or unload after heating done
            self.changeFilamentHeatingFlag = True
            self.loadFlag = True
        except Exception as e:
            error_message = f"Error in changeFilamentRoutine loadFilament: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    @run_async
    def changeFilamentLoadFunction(self):
        try:
            '''
            This function is called once the heating is done, which slowly moves the extruder so that it starts pulling filament
            '''
            self.stackedWidget.setCurrentWidget(self.changeFilamentLoadPage)
            while self.stackedWidget.currentWidget() == self.changeFilamentLoadPage:
                self.octopiclient.gcode("G91")
                self.octopiclient.gcode("G1 E5 F500")
                self.octopiclient.gcode("G90")
                time.sleep(self.calcExtrudeTime(5, 500))
        except Exception as e:
            error_message = f"Error in changeFilamentRoutine changeFilamentLoadFunction: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    @run_async
    def changeFilamentExtrudePageFunction(self):
        try:
            '''
            once filament is loaded, this function is called to extrude filament till the toolhead
            '''
            self.stackedWidget.setCurrentWidget(self.changeFilamentExtrudePage)
            for i in range(int(ptfeTubeLength/150)):
                self.octopiclient.gcode("G91")
                self.octopiclient.gcode("G1 E150 F1500")
                self.octopiclient.gcode("G90")
                time.sleep(self.calcExtrudeTime(150, 1500))
                if self.stackedWidget.currentWidget() is not self.changeFilamentExtrudePage:
                    break

            while self.stackedWidget.currentWidget() == self.changeFilamentExtrudePage:
                self.octopiclient.gcode("G91")
                self.octopiclient.gcode("G1 E20 F600")
                self.octopiclient.gcode("G90")
                time.sleep(self.calcExtrudeTime(20, 600))
        except Exception as e:
            error_message = f"Error in changeFilamentRoutine changeFilamentExtrudePageFunction: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    @run_async
    def changeFilamentRetractFunction(self):
        try:
            '''
            Remove the filament from the toolhead
            '''
            self.stackedWidget.setCurrentWidget(self.changeFilamentRetractPage)
            # Tip Shaping to prevent filament jamming in nozzle
            self.octopiclient.gcode("G91")
            self.octopiclient.gcode("G1 E10 F600")
            time.sleep(self.calcExtrudeTime(10, 600))
            self.octopiclient.gcode("G1 E-20 F2400")
            time.sleep(self.calcExtrudeTime(20, 2400))
            time.sleep(10) # wait for filament to cool inside the nozzle
            self.octopiclient.gcode("G1 E-150 F2400")
            time.sleep(self.calcExtrudeTime(150, 2400))
            self.octopiclient.gcode("G90")
            for i in range(int(ptfeTubeLength/150)):
                self.octopiclient.gcode("G91")
                self.octopiclient.gcode("G1 E-150 F1500")
                self.octopiclient.gcode("G90")
                time.sleep(self.calcExtrudeTime(150, 1500))
                if self.stackedWidget.currentWidget() is not self.changeFilamentRetractPage:
                    break

            while self.stackedWidget.currentWidget() == self.changeFilamentRetractPage:
                self.octopiclient.gcode("G91")
                self.octopiclient.gcode("G1 E-5 F1000")
                self.octopiclient.gcode("G90")
                time.sleep(self.calcExtrudeTime(5, 1000))
        except Exception as e:
            error_message = f"Error in changeFilamentRoutine changeFilamentRetractFunction: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def changeFilament(self):
        try:
            time.sleep(1)
            if self.printerStatusText not in ["Printing","Paused"]:
                self.octopiclient.gcode("G28")

            self.stackedWidget.setCurrentWidget(self.changeFilamentPage)
            self.changeFilamentComboBox.clear()
            self.changeFilamentComboBox.addItems(filaments.keys())
            # Update
            print(self.tool0TargetTemperature)
            if self.tool0TargetTemperature  and self.printerStatusText in ["Printing","Paused"]:
                self.changeFilamentComboBox.addItem("Loaded Filament")
                index = self.changeFilamentComboBox.findText("Loaded Filament")
                if index >= 0 :
                    self.changeFilamentComboBox.setCurrentIndex(index)
        except Exception as e:
            error_message = f"Error in changeFilamentRoutine changeFilament: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def changeFilamentCancel(self):
        try:
            self.changeFilamentHeatingFlag = False
            self.firmwareUpdateCheck()
            self.coolDownAction()
            self.control()
        except Exception as e:
            error_message = f"Error in changeFilamentRoutine changeFilamentCancel: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

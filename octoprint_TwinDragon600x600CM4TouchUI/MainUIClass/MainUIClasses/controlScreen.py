import mainGUI
from logger import *
import dialog

class controlScreen(mainGUI.Ui_MainWindow):
    def __init__(self):
        try:
            log_info("Starting control screen init.")
            self.octopiclient = None
            super().__init__()
            log_info("Completed control screen init.")
        except Exception as e:
            error_message = f"Error in controlScreen __init__: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass
    
    def setup(self):
        try:
            log_info("Starting setup.")

            log_debug("Octopiclient inside class controlScreen: " + str(self.octopiclient))
            self.moveYPButton.pressed.connect(lambda: self.octopiclient.jog(y=self.step, speed=2000))
            self.moveYMButton.pressed.connect(lambda: self.octopiclient.jog(y=-self.step, speed=2000))
            self.moveXMButton.pressed.connect(lambda: self.octopiclient.jog(x=-self.step, speed=2000))
            self.moveXPButton.pressed.connect(lambda: self.octopiclient.jog(x=self.step, speed=2000))
            self.moveZPButton.pressed.connect(lambda: self.octopiclient.jog(z=self.step, speed=2000))
            self.moveZMButton.pressed.connect(lambda: self.octopiclient.jog(z=-self.step, speed=2000))
            self.extruderButton.pressed.connect(lambda: self.octopiclient.extrude(self.step))
            self.retractButton.pressed.connect(lambda: self.octopiclient.extrude(-self.step))
            self.motorOffButton.pressed.connect(lambda: self.octopiclient.gcode(command='M18'))
            self.fanOnButton.pressed.connect(lambda: self.octopiclient.gcode(command='M106 S255'))
            self.fanOffButton.pressed.connect(lambda: self.octopiclient.gcode(command='M107'))
            self.cooldownButton.pressed.connect(self.coolDownAction)
            self.step100Button.pressed.connect(lambda: self.setStep(100))
            self.step1Button.pressed.connect(lambda: self.setStep(1))
            self.step10Button.pressed.connect(lambda: self.setStep(10))
            self.homeXYButton.pressed.connect(lambda: self.octopiclient.home(['x', 'y']))
            self.homeZButton.pressed.connect(lambda: self.octopiclient.home(['z']))
            self.toolToggleTemperatureButton.clicked.connect(self.selectToolTemperature)
            self.toolToggleMotionButton.clicked.connect(self.selectToolMotion)
            self.controlBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.homePage))
            self.setToolTempButton.pressed.connect(self.setToolTemp)
            self.tool180PreheatButton.pressed.connect(lambda: self.octopiclient.gcode(command='M104 T1 S180') if self.toolToggleTemperatureButton.isChecked() else self.octopiclient.gcode(command='M104 T0 S180'))
            self.tool250PreheatButton.pressed.connect(lambda: self.octopiclient.gcode(command='M104 T1 S250') if self.toolToggleTemperatureButton.isChecked() else self.octopiclient.gcode(command='M104 T0 S250'))
            self.tool180PreheatButton.pressed.connect(lambda: self.preheatToolTemp(180))
            self.tool250PreheatButton.pressed.connect(lambda: self.preheatToolTemp(250))
            self.setBedTempButton.pressed.connect(lambda: self.octopiclient.setBedTemperature(self.bedTempSpinBox.value()))
            self.bed60PreheatButton.pressed.connect(lambda: self.preheatBedTemp(60))
            self.bed100PreheatButton.pressed.connect(lambda: self.preheatBedTemp(100))
            #self.chamber40PreheatButton.pressed.connect(lambda: self.preheatChamberTemp(40))
            #self.chamber70PreheatButton.pressed.connect(lambda: self.preheatChamberTemp(70))
            #self.setChamberTempButton.pressed.connect(lambda: self.octopiclient.gcode(command='M141 S{}'.format(self.chamberTempSpinBox.value())))
            self.setFlowRateButton.pressed.connect(lambda: self.octopiclient.flowrate(self.flowRateSpinBox.value()))
            self.setFeedRateButton.pressed.connect(lambda: self.octopiclient.feedrate(self.feedRateSpinBox.value()))

            self.moveZPBabyStep.pressed.connect(lambda: self.octopiclient.gcode(command='M290 Z0.025'))
            self.moveZMBabyStep.pressed.connect(lambda: self.octopiclient.gcode(command='M290 Z-0.025'))
            log_info("Completed controlScreen setup.")
        except Exception as e:
            error_message = f"Error in controlScreen setup: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def control(self):
        try:
            log_info("Calling control method.")
            self.stackedWidget.setCurrentWidget(self.controlPage)
            if self.toolToggleTemperatureButton.isChecked():
                self.toolTempSpinBox.setProperty("value", float(self.tool1TargetTemperature.text()))
            else:
                self.toolTempSpinBox.setProperty("value", float(self.tool0TargetTemperature.text()))
            self.bedTempSpinBox.setProperty("value", float(self.bedTargetTemperature.text()))
            log_info("Completed control method.")
        except Exception as e:
            error_message = f"Error in controlScreen control: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setStep(self, stepRate):
        try:
            log_info(f"Setting step rate to {stepRate}.")
            if stepRate == 100:
                self.step100Button.setFlat(True)
                self.step1Button.setFlat(False)
                self.step10Button.setFlat(False)
                self.step = 100
            if stepRate == 1:
                self.step100Button.setFlat(False)
                self.step1Button.setFlat(True)
                self.step10Button.setFlat(False)
                self.step = 1
            if stepRate == 10:
                self.step100Button.setFlat(False)
                self.step1Button.setFlat(False)
                self.step10Button.setFlat(True)
                self.step = 10
            log_info("Completed setStep method.")
        except Exception as e:
            error_message = f"Error in controlScreen setStep: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setToolTemp(self):
        try:
            log_info("Setting tool temperature.")
            if self.toolToggleTemperatureButton.isChecked():
                self.octopiclient.gcode(command='M104 T1 S' + str(self.toolTempSpinBox.value()))
            else:
                self.octopiclient.gcode(command='M104 T0 S' + str(self.toolTempSpinBox.value()))
            log_info("Completed setToolTemp method.")
        except Exception as e:
            error_message = f"Error in controlScreen setToolTemp: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def preheatToolTemp(self, temp):
        try:
            log_info(f"Preheating tool temperature to {temp}.")
            if self.toolToggleTemperatureButton.isChecked():
                self.octopiclient.gcode(command='M104 T1 S' + str(temp))
            else:
                self.octopiclient.gcode(command='M104 T0 S' + str(temp))
            self.toolTempSpinBox.setProperty("value", temp)
            log_info("Completed preheatToolTemp method.")
        except Exception as e:
            error_message = f"Error in controlScreen preheatToolTemp: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def preheatBedTemp(self, temp):
        try:
            log_info(f"Preheating bed temperature to {temp}.")
            self.octopiclient.gcode(command='M140 S' + str(temp))
            self.bedTempSpinBox.setProperty("value", temp)
            log_info("Completed preheatBedTemp method.")
        except Exception as e:
            error_message = f"Error in controlScreen preheatBedTemp: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def coolDownAction(self):
        try:
            log_info("Performing cooldown action.")
            self.octopiclient.gcode(command='M107')
            self.octopiclient.setToolTemperature({"tool0": 0, "tool1": 0})
            self.octopiclient.setBedTemperature(0)
            self.toolTempSpinBox.setProperty("value", 0)
            self.bedTempSpinBox.setProperty("value", 0)
            log_info("Completed coolDownAction method.")
        except Exception as e:
            error_message = f"Error in controlScreen coolDownAction: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

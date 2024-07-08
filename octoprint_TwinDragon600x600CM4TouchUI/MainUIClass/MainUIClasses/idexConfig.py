import dialog
import mainGUI
from MainUIClass.config import getCalibrationPosition
from MainUIClass.MainUIClasses.dialog_methods import tellAndReboot
from MainUIClass.MainUIClasses.printerName import printerName
from PyQt5 import QtGui
from logger import *

class idexConfig(mainGUI.Ui_MainWindow):
    def __init__(self):
        try:
            log_info("Starting idexCalibration init.")
            self.octopiclient = None
            self.printerName = None
            super().__init__()
            log_info("Completed idexCalibration init.")
        except Exception as e:
            error_message = f"Error in idexCalibrationPage __init__: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setup(self):
        try:
            log_info("Starting setup.")

            log_debug("Octopiclient inside class idexCalibrationPage: " + str(self.octopiclient))

            self.calibrationPosition = getCalibrationPosition(self)

            # Connect signals
            self.idexCalibrationWizardButton.clicked.connect(self.idexConfigStep1)
            self.idexConfigStep1NextButton.clicked.connect(self.idexConfigStep2)
            self.idexConfigStep2NextButton.clicked.connect(self.idexConfigStep3)
            self.idexConfigStep3NextButton.clicked.connect(self.idexConfigStep4)
            self.idexConfigStep4NextButton.clicked.connect(self.idexConfigStep5)
            self.idexConfigStep5NextButton.clicked.connect(self.idexDoneStep)
            self.idexConfigStep1CancelButton.pressed.connect(self.idexCancelStep)
            self.idexConfigStep2CancelButton.pressed.connect(self.idexCancelStep)
            self.idexConfigStep3CancelButton.pressed.connect(self.idexCancelStep)
            self.idexConfigStep4CancelButton.pressed.connect(self.idexCancelStep)
            self.idexConfigStep5CancelButton.pressed.connect(self.idexCancelStep)
            self.moveZMIdexButton.pressed.connect(lambda: self.octopiclient.jog(z=-0.1))
            self.moveZPIdexButton.pressed.connect(lambda: self.octopiclient.jog(z=0.1))
            self.toolOffsetXSetButton.pressed.connect(self.setToolOffsetX)
            self.toolOffsetYSetButton.pressed.connect(self.setToolOffsetY)
            self.toolOffsetZSetButton.pressed.connect(self.setToolOffsetZ)
            self.toolOffsetXYBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
            self.toolOffsetZBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
            self.toolOffsetXYButton.pressed.connect(self.updateToolOffsetXY)
            self.toolOffsetZButton.pressed.connect(self.updateToolOffsetZ)
            self.testPrintsButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.testPrintsPage1_6))
            self.testPrintsNextButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.testPrintsPage2_6))
            self.testPrintsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
            self.testPrintsCancelButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
            self.dualCaliberationPrintButton.pressed.connect(
                lambda: self.testPrint(str(self.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                    str(self.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'dualCalibration'))
            self.bedLevelPrintButton.pressed.connect(
                lambda: self.testPrint(str(self.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                    str(self.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'bedLevel'))
            self.movementTestPrintButton.pressed.connect(
                lambda: self.testPrint(str(self.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                    str(self.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'movementTest'))
            self.singleNozzlePrintButton.pressed.connect(
                lambda: self.testPrint(str(self.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                    str(self.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'dualTest'))
            self.dualNozzlePrintButton.pressed.connect(
                lambda: self.testPrint(str(self.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                    str(self.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'singleTest'))

            log_info("Completed idexConfig setup.")
        except Exception as e:
            error_message = f"Error in idexCalibrationPage setup: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def idexConfigStep1(self):
        '''
        Shows welcome message.
        Welcome Page, Give Info. Unlock nozzle and push down
        :return:
        '''
        try:
            self.octopiclient.gcode(command='M503')  # Gets old tool offset position
            self.octopiclient.gcode(command='M218 T1 Z0')  # set nozzle tool offsets to 0
            self.octopiclient.gcode(command='M104 S200')
            self.octopiclient.gcode(command='M104 T1 S200')
            self.octopiclient.home(['x', 'y', 'z'])
            self.octopiclient.gcode(command='G1 X10 Y10 Z20 F5000')
            self.octopiclient.gcode(command='T0')  # Set active tool to t0
            self.octopiclient.gcode(command='M420 S0')  # Disable mesh bed leveling for good measure
            self.stackedWidget.setCurrentWidget(self.idexConfigStep1Page)
        except Exception as e:
            error_message = f"Error in idexConfigStep1: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def idexConfigStep2(self):
        '''
        levels first position (RIGHT)
        :return:
        '''
        try:
            self.stackedWidget.setCurrentWidget(self.idexConfigStep2Page)
            self.octopiclient.jog(x=self.calibrationPosition['X1'], y=self.calibrationPosition['Y1'], absolute=True, speed=10000)
            self.octopiclient.jog(z=0, absolute=True, speed=1500)
        except Exception as e:
            error_message = f"Error in idexConfigStep2: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def idexConfigStep3(self):
        '''
        levels second leveling position (LEFT)
        '''
        try:
            self.stackedWidget.setCurrentWidget(self.idexConfigStep3Page)
            self.octopiclient.jog(z=10, absolute=True, speed=1500)
            self.octopiclient.jog(x=self.calibrationPosition['X2'], y=self.calibrationPosition['Y2'], absolute=True, speed=10000)
            self.octopiclient.jog(z=0, absolute=True, speed=1500)
        except Exception as e:
            error_message = f"Error in idexConfigStep3: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def idexConfigStep4(self):
        '''
        Set to Mirror mode and asks to loosen the carriage, push both doen to max
        :return:
        '''
        try:
            self.stackedWidget.setCurrentWidget(self.idexConfigStep4Page)
            self.octopiclient.jog(z=10, absolute=True, speed=1500)
            self.octopiclient.gcode(command='M605 S3')
            self.octopiclient.jog(x=self.calibrationPosition['X1'], y=self.calibrationPosition['Y1'], absolute=True, speed=10000)
        except Exception as e:
            error_message = f"Error in idexConfigStep4: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def idexConfigStep5(self):
        '''
        take bed up until both nozzles touch the bed. ASk to take nozzle up and down till nozzle just rests on the bed and tighten
        :return:
        '''
        try:
            self.stackedWidget.setCurrentWidget(self.idexConfigStep5Page)
            self.octopiclient.jog(z=1, absolute=True, speed=10000)
        except Exception as e:
            error_message = f"Error in idexConfigStep5: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def idexDoneStep(self):
        '''
        Exits leveling
        :return:
        '''
        try:
            self.octopiclient.jog(z=4, absolute=True, speed=1500)
            self.stackedWidget.setCurrentWidget(self.calibratePage)
            self.octopiclient.home(['z'])
            self.octopiclient.home(['x', 'y'])
            self.octopiclient.gcode(command='M104 S0')
            self.octopiclient.gcode(command='M104 T1 S0')
            self.octopiclient.gcode(command='M605 S1')
            self.octopiclient.gcode(command='M218 T1 Z0') # set nozzle offsets to 0
            self.octopiclient.gcode(command='M84')
            self.octopiclient.gcode(command='M500')  # store eeprom settings to get Z home offset, mesh bed leveling back
        except Exception as e:
            error_message = f"Error in idexDoneStep: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def idexCancelStep(self):
        try:
            self.stackedWidget.setCurrentWidget(self.calibratePage)
            self.octopiclient.gcode(command='M605 S1')
            self.octopiclient.home(['z'])
            self.octopiclient.home(['x', 'y'])
            self.octopiclient.gcode(command='M104 S0')
            self.octopiclient.gcode(command='M104 T1 S0')
            self.octopiclient.gcode(command='M218 T1 Z{}'.format(self.idexToolOffsetRestoreValue))
            self.octopiclient.gcode(command='M84')
        except Exception as e:
            error_message = f"Error in idexCancelStep: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

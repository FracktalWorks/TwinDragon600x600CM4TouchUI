from MainUIClass.config import getCalibrationPosition
from PyQt5 import QtGui
import mainGUI
from MainUIClass.MainUIClasses.dialog_methods import tellAndReboot
from MainUIClass.MainUIClasses.printerName import printerName
from logger import *
import dialog
from MainUIClass.MainUIClasses.getFilesAndInfo import ThreadFileUpload

class calibrationPage(mainGUI.Ui_MainWindow):
    def __init__(self):
        try:
            log_info("Starting calibration init.")
            self.octopiclient = None
            super().__init__()
            log_info("Completed calibration init.")
        except Exception as e:
            error_message = f"Error in calibrationPage __init__: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setup(self):
        try:
            log_info("Starting setup.")
            log_debug("Octopiclient inside class calibrationPage: " + str(self.octopiclient))

            self.calibrateBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
            self.nozzleOffsetButton.pressed.connect(self.requestEEPROMProbeOffset)
            self.nozzleOffsetSetButton.pressed.connect(
                lambda: self.setZProbeOffset(self.nozzleOffsetDoubleSpinBox.value()))
            self.nozzleOffsetBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))

            self.moveZMT1CaliberateButton.pressed.connect(lambda: self.octopiclient.jog(z=-0.025))
            self.moveZPT1CaliberateButton.pressed.connect(lambda: self.octopiclient.jog(z=0.025))

            self.calibrationWizardButton.clicked.connect(self.quickStep1)
            self.quickStep1NextButton.clicked.connect(self.quickStep2)
            self.quickStep2NextButton.clicked.connect(self.quickStep3)
            self.quickStep3NextButton.clicked.connect(self.quickStep4)
            self.quickStep4NextButton.clicked.connect(self.nozzleHeightStep1)
            self.nozzleHeightStep1NextButton.clicked.connect(self.nozzleHeightStep1)
            self.quickStep1CancelButton.pressed.connect(self.cancelStep)
            self.quickStep2CancelButton.pressed.connect(self.cancelStep)
            self.quickStep3CancelButton.pressed.connect(self.cancelStep)
            self.quickStep4CancelButton.pressed.connect(self.cancelStep)
            self.nozzleHeightStep1CancelButton.pressed.connect(self.cancelStep)
            self.inputShaperCalibrateButton.pressed.connect(self.inputShaperCalibrate)
            log_info("Completed calibrationPage setup.")
        except Exception as e:
            error_message = f"Error in calibrationPage setup: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def inputShaperCalibrate(self):
        try:
            dialog.WarningOk(self, "Wait for all calibration movements to finish before proceeding.", overlay= True)
            self.octopiclient.gcode(command='G28')
            self.octopiclient.gcode(command='SHAPER_CALIBRATE')
            self.octopiclient.gcode(command='SAVE_CONFIG')
            
        except Exception as e:
            error_message = f"Error in inptuShaperCalibrate: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setZToolOffset(self, offset, setOffset=False):
        '''
        Sets the home offset after the caliberation wizard is done, which is a callback to
        the response of M114 that is sent at the end of the Wizard in doneStep()
        :param offset: the value off the offset to set. is a str is coming from M114, and is float if coming from the nozzleOffsetPage
        :param setOffset: Boolean, is true if the function call is from the nozzleOFfsetPage
        :return:
        '''
        self.currentZPosition = offset
        try:
            if self.setNewToolZOffsetFromCurrentZBool:
                newToolOffsetZ = (float(self.toolOffsetZ) + float(self.currentZPosition))
                self.octopiclient.gcode(command='M218 T1 Z{}'.format(newToolOffsetZ))
                self.setNewToolZOffsetFromCurrentZBool = False
                self.octopiclient.gcode(command='SAVE_CONFIG')
        except Exception as e:
            error_message = f"Error in setZToolOffset: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def showProbingFailed(self, msg='Probing Failed, Calibrate bed again or check for hardware issue', overlay=True):
        try:
            if dialog.WarningOk(self, msg, overlay=overlay):
                self.octopiclient.cancelPrint()
                return True
            return False
        except Exception as e:
            error_message = f"Error in showProbingFailed: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass
            return False

    def showPrinterError(self, msg='Printer error, Check Terminal', overlay=False):
        try:
            if dialog.WarningOk(self, msg, overlay=overlay):
                return True
            return False
        except Exception as e:
            error_message = f"Error in showPrinterError: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass
            return False

    def updateEEPROMProbeOffset(self, offset):
        '''
        Sets the spinbox value to have the value of the Z offset from the printer.
        the value is -ve so as to be more intuitive.
        :param offset:
        :return:
        '''
        try:
            self.currentNozzleOffset.setText(str(float(offset)))
            self.nozzleOffsetDoubleSpinBox.setValue(0)
        except Exception as e:
            error_message = f"Error in updateEEPROMProbeOffset: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setZProbeOffset(self, offset):
        '''
        Sets Z Probe offset from spinbox
        :param offset:
        :return:
        '''
        try:
            self.octopiclient.gcode(command='M851 Z{}'.format(round(float(offset), 2)))
            self.nozzleOffsetDoubleSpinBox.setValue(0)
            _offset = float(self.currentNozzleOffset.text()) + float(offset)
            self.currentNozzleOffset.setText(str(float(self.currentNozzleOffset.text()) - float(offset)))
            self.octopiclient.gcode(command='M500')
        except Exception as e:
            error_message = f"Error in setZProbeOffset: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def requestEEPROMProbeOffset(self):
        '''
        Updates the value of M206 Z in the nozzle offset spinbox.
        Sends M503 so that the pritner returns the value as a websocket calback
        :return:
        '''
        try:
            self.octopiclient.gcode(command='M503')
            self.stackedWidget.setCurrentWidget(self.nozzleOffsetPage)
        except Exception as e:
            error_message = f"Error in requestEEPROMProbeOffset: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def nozzleOffset(self):
        '''
        Updates the value of M206 Z in the nozzle offset spinbox.
        Sends M503 so that the pritner returns the value as a websocket calback
        :return:
        '''
        try:
            self.octopiclient.gcode(command='M503')
            self.stackedWidget.setCurrentWidget(self.nozzleOffsetPage)
        except Exception as e:
            error_message = f"Error in nozzleOffset: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def updateToolOffsetXY(self):
        try:
            self.octopiclient.gcode(command='M503')
            self.stackedWidget.setCurrentWidget(self.toolOffsetXYPage)
        except Exception as e:
            error_message = f"Error in updateToolOffsetXY: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def updateToolOffsetZ(self):
        try:
            self.octopiclient.gcode(command='M503')
            self.stackedWidget.setCurrentWidget(self.toolOffsetZpage)
        except Exception as e:
            error_message = f"Error in updateToolOffsetZ: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setToolOffsetX(self):
        try:
            self.octopiclient.gcode(command='M218 T1 X{}'.format(round(self.toolOffsetXDoubleSpinBox.value(), 2)))
            self.octopiclient.gcode(command='M500')
        except Exception as e:
            error_message = f"Error in setToolOffsetX: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setToolOffsetY(self):
        try:
            self.octopiclient.gcode(command='M218 T1 Y{}'.format(round(self.toolOffsetYDoubleSpinBox.value(), 2)))
            self.octopiclient.gcode(command='M500')
        except Exception as e:
            error_message = f"Error in setToolOffsetY: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setToolOffsetZ(self):
        try:
            self.octopiclient.gcode(command='M218 T1 Z{}'.format(round(self.toolOffsetZDoubleSpinBox.value(), 2)))
            self.octopiclient.gcode(command='M500')
        except Exception as e:
            error_message = f"Error in setToolOffsetZ: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def getToolOffset(self, M218Data):
        try:
            self.toolOffsetZ = M218Data[M218Data.index('Z') + 1:].split(' ', 1)[0]
            self.toolOffsetX = M218Data[M218Data.index('X') + 1:].split(' ', 1)[0]
            self.toolOffsetY = M218Data[M218Data.index('Y') + 1:].split(' ', 1)[0]
            self.toolOffsetXDoubleSpinBox.setValue(float(self.toolOffsetX))
            self.toolOffsetYDoubleSpinBox.setValue(float(self.toolOffsetY))
            self.toolOffsetZDoubleSpinBox.setValue(float(self.toolOffsetZ))
            self.idexToolOffsetRestoreValue = float(self.toolOffsetZ)
        except Exception as e:
            error_message = f"Error in getToolOffset: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def quickStep1(self):
        try:
            self.toolZOffsetCaliberationPageCount = 0
            self.octopiclient.gcode(command='M104 S200')
            self.octopiclient.gcode(command='M104 T1 S200')
            self.octopiclient.gcode(command='T0')
            self.octopiclient.gcode(command='M503')
            self.octopiclient.gcode(command='M420 S0')
            self.stackedWidget.setCurrentWidget(self.quickStep1Page)
            self.octopiclient.home(['x', 'y', 'z'])
            self.octopiclient.gcode(command='T0')
            self.octopiclient.jog(x=40, y=40, absolute=True, speed=2000)
        except Exception as e:
            error_message = f"Error in quickStep1: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def quickStep2(self):
        try:
            self.stackedWidget.setCurrentWidget(self.quickStep2Page)
            self.octopiclient.jog(x=self.calibrationPosition['X1'], y=self.calibrationPosition['Y1'], absolute=True, speed=10000)
            self.octopiclient.jog(z=0, absolute=True, speed=1500)
        except Exception as e:
            error_message = f"Error in quickStep2: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def quickStep3(self):
        try:
            self.stackedWidget.setCurrentWidget(self.quickStep3Page)
            self.octopiclient.jog(z=10, absolute=True, speed=1500)
            self.octopiclient.jog(x=self.calibrationPosition['X2'], y=self.calibrationPosition['Y2'], absolute=True, speed=10000)
            self.octopiclient.jog(z=0, absolute=True, speed=1500)
        except Exception as e:
            error_message = f"Error in quickStep3: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def quickStep4(self):
        try:
            self.stackedWidget.setCurrentWidget(self.quickStep4Page)
            self.octopiclient.jog(z=10, absolute=True, speed=1500)
            self.octopiclient.jog(x=self.calibrationPosition['X3'], y=self.calibrationPosition['Y3'], absolute=True, speed=10000)
            self.octopiclient.jog(z=0, absolute=True, speed=1500)
        except Exception as e:
            error_message = f"Error in quickStep4: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def nozzleHeightStep1(self):
        try:
            if self.toolZOffsetCaliberationPageCount == 0:
                self.toolZOffsetLabel.setText("Move the bed up or down to the First Nozzle , testing height using paper")
                self.stackedWidget.setCurrentWidget(self.nozzleHeightStep1Page)
                self.octopiclient.jog(z=10, absolute=True, speed=1500)
                self.octopiclient.jog(x=self.calibrationPosition['X4'], y=self.calibrationPosition['Y4'], absolute=True, speed=10000)
                self.octopiclient.jog(z=1, absolute=True, speed=1500)
                self.toolZOffsetCaliberationPageCount = 1
            elif self.toolZOffsetCaliberationPageCount == 1:
                self.toolZOffsetLabel.setText("Move the bed up or down to the Second Nozzle , testing height using paper")
                self.octopiclient.gcode(command='G92 Z0')
                self.octopiclient.jog(z=1, absolute=True, speed=1500)
                self.octopiclient.gcode(command='T1')
                self.octopiclient.jog(x=self.calibrationPosition['X4'], y=self.calibrationPosition['Y4'], absolute=True, speed=10000)
                self.toolZOffsetCaliberationPageCount = 2
            else:
                self.doneStep()
        except Exception as e:
            error_message = f"Error in nozzleHeightStep1: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def doneStep(self):
        try:
            self.setNewToolZOffsetFromCurrentZBool = True
            self.octopiclient.gcode(command='M114')
            self.octopiclient.jog(z=4, absolute=True, speed=1500)
            self.octopiclient.gcode(command='T0')
            self.stackedWidget.setCurrentWidget(self.calibratePage)
            self.octopiclient.home(['x', 'y', 'z'])
            self.octopiclient.gcode(command='M104 S0')
            self.octopiclient.gcode(command='M104 T1 S0')
            self.octopiclient.gcode(command='M84')
            self.octopiclient.gcode(command='M500')
        except Exception as e:
            error_message = f"Error in doneStep: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def cancelStep(self):
        try:
            self.stackedWidget.setCurrentWidget(self.calibratePage)
            self.octopiclient.home(['x', 'y', 'z'])
            self.octopiclient.gcode(command='M104 S0')
            self.octopiclient.gcode(command='M104 T1 S0')
            self.octopiclient.gcode(command='M84')
        except Exception as e:
            error_message = f"Error in cancelStep: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def testPrint(self, tool0Diameter, tool1Diameter, gcode):
        '''
        Prints a test print
        :param tool0Diameter: Diameter of tool 0 nozzle.04,06 or 08
        :param tool1Diameter: Diameter of tool 1 nozzle.40,06 or 08
        :param gcode: type of gcode to print, dual nozzle calibration, bed leveling, movement or samaple prints in
        single and dual. bedLevel, dualCalibration, movementTest, dualTest, singleTest
        :return:
        '''
        try:
            if gcode == 'bedLevel':
                self.printFromPath('gcode/' + tool0Diameter + '_BedLeveling.gcode', True)
            elif gcode == 'dualCalibration':
                self.printFromPath(
                    'gcode/' + tool0Diameter + '_' + tool1Diameter + '_dual_extruder_calibration_Idex.gcode',
                    True)
            elif gcode == 'movementTest':
                self.printFromPath('gcode/movementTest.gcode', True)
            elif gcode == 'dualTest':
                self.printFromPath(
                    'gcode/' + tool0Diameter + '_' + tool1Diameter + '_Fracktal_logo_Idex.gcode',
                    True)
            elif gcode == 'singleTest':
                self.printFromPath('gcode/' + tool0Diameter + '_Fracktal_logo_Idex.gcode', True)
            else:
                print("gcode not found")
        except Exception as e:
            error_message = f"Error in testPrint: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def printFromPath(self, path, prnt=True):
        '''
        Transfers a file from a specific to octoprint's watched folder so that it gets automatically detected by Octoprint.
        Warning: If the file is read-only, octoprint API for reading the file crashes.
        '''
        try:
            self.uploadThread = ThreadFileUpload(path, prnt=prnt)
            self.uploadThread.start()
            if prnt:
                self.stackedWidget.setCurrentWidget(self.homePage)
        except Exception as e:
            error_message = f"Error in printFromPath: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

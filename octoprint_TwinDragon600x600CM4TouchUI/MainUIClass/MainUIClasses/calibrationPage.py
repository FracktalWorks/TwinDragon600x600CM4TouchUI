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
            # the -ve sign is such that its converted to home offset and not just distance between nozzle and bed
            self.nozzleOffsetSetButton.pressed.connect(
                lambda: self.setZProbeOffset(self.nozzleOffsetDoubleSpinBox.value()))
            self.nozzleOffsetBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))

            # --Dual Caliberation Addition--
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
            log_info("Completed setup.")
        except Exception as e:
            error_message = f"Error in calibrationPage setup: {str(e)}"
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

        #TODO can make this simpler, asset the offset value to string float to begin with instead of doing confitionals
        '''
        self.currentZPosition = offset #gets the current z position, used to set new tool offsets.
        # clean this shit up.
        #fuck you past vijay for not cleaning this up
        try:
            if self.setNewToolZOffsetFromCurrentZBool:
                print(self.toolOffsetZ)
                print(self.currentZPosition)
                newToolOffsetZ = (float(self.toolOffsetZ) + float(self.currentZPosition))
                self.octopiclient.gcode(command='M218 T1 Z{}'.format(newToolOffsetZ))  # restore eeprom settings to get Z home offset, mesh bed leveling back
                self.setNewToolZOffsetFromCurrentZBool =False
                self.octopiclient.gcode(command='SAVE_CONFIG')  # store eeprom settings to get Z home offset, mesh bed leveling back
        except Exception as e:
                    print("error: " + str(e))

    def showProbingFailed(self,msg='Probing Failed, Calibrate bed again or check for hardware issue',overlay=True):
        if dialog.WarningOk(self, msg, overlay=overlay):
            self.octopiclient.cancelPrint()
            return True
        return False

    def showPrinterError(self,msg='Printer error, Check Terminal',overlay=False): #True
        if dialog.WarningOk(self, msg, overlay=overlay):
            pass
            return True
        return False

    def updateEEPROMProbeOffset(self, offset):
        '''
        Sets the spinbox value to have the value of the Z offset from the printer.
        the value is -ve so as to be more intuitive.
        :param offset:
        :return:
        '''
        self.currentNozzleOffset.setText(str(float(offset)))
        self.nozzleOffsetDoubleSpinBox.setValue(0)

    def setZProbeOffset(self, offset):
        '''
        Sets Z Probe offset from spinbox

        #TODO can make this simpler, asset the offset value to string float to begin with instead of doing confitionals
        '''

        self.octopiclient.gcode(command='M851 Z{}'.format(round(float(offset),2))) #M851 only ajusts nozzle offset
        self.nozzleOffsetDoubleSpinBox.setValue(0)
        _offset=float(self.currentNozzleOffset.text())+float(offset)
        self.currentNozzleOffset.setText(str(float(self.currentNozzleOffset.text())-float(offset))) # show nozzle offset after adjustment
        self.octopiclient.gcode(command='M500')

    def requestEEPROMProbeOffset(self):
        '''
        Updates the value of M206 Z in the nozzle offset spinbox. Sends M503 so that the pritner returns the value as a websocket calback
        :return:
        '''
        self.octopiclient.gcode(command='M503')
        self.stackedWidget.setCurrentWidget(self.nozzleOffsetPage)

    def nozzleOffset(self):
        '''
        Updates the value of M206 Z in the nozzle offset spinbox. Sends M503 so that the pritner returns the value as a websocket calback
        :return:
        '''
        self.octopiclient.gcode(command='M503')
        self.stackedWidget.setCurrentWidget(self.nozzleOffsetPage)

    def updateToolOffsetXY(self):
        self.octopiclient.gcode(command='M503')
        self.stackedWidget.setCurrentWidget(self.toolOffsetXYPage)

    def updateToolOffsetZ(self):
        self.octopiclient.gcode(command='M503')
        self.stackedWidget.setCurrentWidget(self.toolOffsetZpage)

    def setToolOffsetX(self):
        self.octopiclient.gcode(command='M218 T1 X{}'.format(round(self.toolOffsetXDoubleSpinBox.value(),2)))  # restore eeprom settings to get Z home offset, mesh bed leveling back
        self.octopiclient.gcode(command='M500')

    def setToolOffsetY(self):
        self.octopiclient.gcode(command='M218 T1 Y{}'.format(round(self.toolOffsetYDoubleSpinBox.value(),2)))  # restore eeprom settings to get Z home offset, mesh bed leveling back
        self.octopiclient.gcode(command='M500')
        self.octopiclient.gcode(command='M500')

    def setToolOffsetZ(self):
        self.octopiclient.gcode(command='M218 T1 Z{}'.format(round(self.toolOffsetZDoubleSpinBox.value(),2)))  # restore eeprom settings to get Z home offset, mesh bed leveling back
        self.octopiclient.gcode(command='M500')

    def getToolOffset(self, M218Data):

        #if float(M218Data[M218Data.index('X') + 1:].split(' ', 1)[0] ) > 0:
        self.toolOffsetZ = M218Data[M218Data.index('Z') + 1:].split(' ', 1)[0]
        self.toolOffsetX = M218Data[M218Data.index('X') + 1:].split(' ', 1)[0]
        self.toolOffsetY = M218Data[M218Data.index('Y') + 1:].split(' ', 1)[0]
        self.toolOffsetXDoubleSpinBox.setValue(float(self.toolOffsetX))
        self.toolOffsetYDoubleSpinBox.setValue(float(self.toolOffsetY))
        self.toolOffsetZDoubleSpinBox.setValue(float(self.toolOffsetZ))
        self.idexToolOffsetRestoreValue = float(self.toolOffsetZ)

    def quickStep1(self):
        '''
        Shows welcome message.
        Homes to MAX
        goes to position where leveling screws can be opened
        :return:
        '''
        self.toolZOffsetCaliberationPageCount = 0
        self.octopiclient.gcode(command='M104 S200')
        self.octopiclient.gcode(command='M104 T1 S200')
        #self.octopiclient.gcode(command='M211 S0')  # Disable software endstop
        self.octopiclient.gcode(command='T0')  # Set active tool to t0
        self.octopiclient.gcode(command='M503')  # makes sure internal value of Z offset and Tool offsets are stored before erasing
        self.octopiclient.gcode(command='M420 S0')  # Dissable mesh bed leveling for good measure
        self.stackedWidget.setCurrentWidget(self.quickStep1Page)
        self.octopiclient.home(['x', 'y', 'z'])
        self.octopiclient.gcode(command='T0')
        self.octopiclient.jog(x=40, y=40, absolute=True, speed=2000)

    def quickStep2(self):
        '''
        levels first position (RIGHT)
        :return:
        '''
        self.stackedWidget.setCurrentWidget(self.quickStep2Page)
        self.octopiclient.jog(x=self.calibrationPosition['X1'], y=self.calibrationPosition['Y1'], absolute=True, speed=10000)
        self.octopiclient.jog(z=0, absolute=True, speed=1500)

    def quickStep3(self):
        '''
        levels second leveling position (LEFT)
        '''
        self.stackedWidget.setCurrentWidget(self.quickStep3Page)
        self.octopiclient.jog(z=10, absolute=True, speed=1500)
        self.octopiclient.jog(x=self.calibrationPosition['X2'], y=self.calibrationPosition['Y2'], absolute=True, speed=10000)
        self.octopiclient.jog(z=0, absolute=True, speed=1500)

    def quickStep4(self):
        '''
        levels third leveling position  (BACK)
        :return:
        '''
        # sent twice for some reason
        self.stackedWidget.setCurrentWidget(self.quickStep4Page)
        self.octopiclient.jog(z=10, absolute=True, speed=1500)
        self.octopiclient.jog(x=self.calibrationPosition['X3'], y=self.calibrationPosition['Y3'], absolute=True, speed=10000)
        self.octopiclient.jog(z=0, absolute=True, speed=1500)

    # def quickStep5(self):
    #     '''
    #     Nozzle Z offset calc
    #     '''
    #     self.stackedWidget.setCurrentWidget(self.quickStep5Page)
    #     self.octopiclient.jog(z=15, absolute=True, speed=1500)
    #     self.octopiclient.gcode(command='M272 S')

    def nozzleHeightStep1(self):
        if self.toolZOffsetCaliberationPageCount == 0 :
            self.toolZOffsetLabel.setText("Move the bed up or down to the First Nozzle , testing height using paper")
            self.stackedWidget.setCurrentWidget(self.nozzleHeightStep1Page)
            self.octopiclient.jog(z=10, absolute=True, speed=1500)
            self.octopiclient.jog(x=self.calibrationPosition['X4'], y=self.calibrationPosition['Y4'], absolute=True, speed=10000)
            self.octopiclient.jog(z=1, absolute=True, speed=1500)
            self.toolZOffsetCaliberationPageCount = 1
        elif self.toolZOffsetCaliberationPageCount == 1:
            self.toolZOffsetLabel.setText("Move the bed up or down to the Second Nozzle , testing height using paper")
            self.octopiclient.gcode(command='G92 Z0')#set the current Z position to zero
            self.octopiclient.jog(z=1, absolute=True, speed=1500)
            self.octopiclient.gcode(command='T1')
            self.octopiclient.jog(x=self.calibrationPosition['X4'], y=self.calibrationPosition['Y4'], absolute=True, speed=10000)
            self.toolZOffsetCaliberationPageCount = 2
        else:
            self.doneStep()

    def doneStep(self):
        '''
        Exits leveling
        :return:
        '''
        self.setNewToolZOffsetFromCurrentZBool = True
        self.octopiclient.gcode(command='M114')
        self.octopiclient.jog(z=4, absolute=True, speed=1500)
        self.octopiclient.gcode(command='T0')
        #self.octopiclient.gcode(command='M211 S1')  # Disable software endstop
        self.stackedWidget.setCurrentWidget(self.calibratePage)
        self.octopiclient.home(['x', 'y', 'z'])
        self.octopiclient.gcode(command='M104 S0')
        self.octopiclient.gcode(command='M104 T1 S0')
        self.octopiclient.gcode(command='M84')
        self.octopiclient.gcode(command='M500')  # store eeprom settings to get Z home offset, mesh bed leveling back

    def cancelStep(self):
        self.stackedWidget.setCurrentWidget(self.calibratePage)
        self.octopiclient.home(['x', 'y', 'z'])
        self.octopiclient.gcode(command='M104 S0')
        self.octopiclient.gcode(command='M104 T1 S0')
        self.octopiclient.gcode(command='M84')
    
    def testPrint(self,tool0Diameter,tool1Diameter,gcode):
        '''
        Prints a test print
        :param tool0Diameter: Diameter of tool 0 nozzle.04,06 or 08
        :param tool1Diameter: Diameter of tool 1 nozzle.40,06 or 08
        :param gcode: type of gcode to print, dual nozzle calibration, bed leveling, movement or samaple prints in
        single and dual. bedLevel, dualCalibration, movementTest, dualTest, singleTest
        :return:
        '''
        try:
            if gcode is 'bedLevel':
                self.printFromPath('gcode/' + tool0Diameter + '_BedLeveling.gcode', True)
            elif gcode is 'dualCalibration':
                self.printFromPath(
                    'gcode/' + tool0Diameter + '_' + tool1Diameter + '_dual_extruder_calibration_Idex.gcode',
                    True)
            elif gcode is 'movementTest':
                self.printFromPath('gcode/movementTest.gcode', True)
            elif gcode is 'dualTest':
                self.printFromPath(
                    'gcode/' + tool0Diameter + '_' + tool1Diameter + '_Fracktal_logo_Idex.gcode',
                    True)
            elif gcode is 'singleTest':
                self.printFromPath('gcode/' + tool0Diameter + '_Fracktal_logo_Idex.gcode',True)

            else:
                print("gcode not found")
        except Exception as e:
            print("Eror:" + e)

    def printFromPath(self,path,prnt=True):
        '''
        Transfers a file from a specific to octoprint's watched folder so that it gets automatically detected by Octoprint.
        Warning: If the file is read-only, octoprint API for reading the file crashes.
        '''

        self.uploadThread = ThreadFileUpload(path, prnt=prnt)
        self.uploadThread.start()
        if prnt:
            self.stackedWidget.setCurrentWidget(self.homePage)

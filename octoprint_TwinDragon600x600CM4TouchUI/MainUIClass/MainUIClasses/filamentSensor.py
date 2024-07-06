import requests
from MainUIClass.config import apiKey, ip, _fromUtf8
from PyQt5 import QtGui
import mainGUI
from logger import *
from dialog import WarningOk
import dialog

class filamentSensor(mainGUI.Ui_MainWindow):
    def __init__(self):
        '''
        Constructor for the filamentSensor class.
        '''
        try:
            log_info("Starting filament sensor init.")
            super().__init__()
            log_info("Completed filament sensor init.")
        except Exception as e:
            error_message = f"Error in filamentSensor __init__: {str(e)}"
            log_error(error_message)
            if WarningOk(self, error_message, overlay=True):
                pass

    def setup(self):
        '''
        Sets up the filament sensor UI and connects button signals.
        
        Parameters:
        - octopiclient: The OctoPrint client instance.
        '''
        try:
            log_info("Starting setup.")
            self.toggleFilamentSensorButton.clicked.connect(self.toggleFilamentSensor)
            log_info("Completed setup.")
        except Exception as e:
            error_message = f"Error in filamentSensor setup: {str(e)}"
            log_error(error_message)
            if WarningOk(self, error_message, overlay=True):
                pass

    def isFilamentSensorInstalled(self):
        '''
        Checks if the filament sensor plugin is installed and sets button state accordingly.
        
        Returns:
        - bool: True if filament sensor is installed and connection successful, False otherwise.
        '''
        success = False
        try:
            headers = {'X-Api-Key': apiKey}
            req = requests.get(f'http://{ip}/plugin/Julia2018FilamentSensor/status', headers=headers)
            success = req.status_code == requests.codes.ok
        except Exception as e:
            error_message = f"Error in isFilamentSensorInstalled: {str(e)}"
            log_error(error_message)
            if WarningOk(self, error_message, overlay=True):
                pass
        # self.toggleFilamentSensorButton.setEnabled(success)
        return success

    def toggleFilamentSensor(self):
        '''
        Toggles the filament sensor state using a HTTP GET request to the plugin endpoint.
        '''
        try:
            # headers = {'X-Api-Key': apiKey}
            # # payload = {'sensor_enabled': self.toggleFilamentSensorButton.isChecked()}
            # requests.get('http://{}/plugin/Julia2018FilamentSensor/toggle'.format(ip), headers=headers)   # , data=payload)
            icon = 'filamentSensorOn' if self.toggleFilamentSensorButton.isChecked() else 'filamentSensorOff'
            self.toggleFilamentSensorButton.setIcon(QtGui.QIcon(_fromUtf8("templates/img/" + icon)))
            #self.octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=SFS_T0 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
            #self.octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=SFS_T1 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
            self.octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=switch_sensor_T0 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
            self.octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=encoder_sensor_T0 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
            self.octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=switch_sensor_T1 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
            self.octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=encoder_sensor_T1 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
        
        except Exception as e:
            error_message = f"Error in toggleFilamentSensor: {str(e)}"
            log_error(error_message)
            if WarningOk(self, "Failed to toggle filament sensor", overlay=True):
                pass

    def filamentSensorHandler(self, data):
        try:
            # sensor_enabled = False
            # # print(data)
            #
            # if 'sensor_enabled' in data:
            #     sensor_enabled = data["sensor_enabled"] == 1
            print(data)

            icon = 'filamentSensorOn' if self.toggleFilamentSensorButton.isChecked() else 'filamentSensorOff'
            self.toggleFilamentSensorButton.setIcon(QtGui.QIcon(_fromUtf8("templates/img/" + icon)))

            if not self.toggleFilamentSensorButton.isChecked():  
                return

            triggered_extruder0 = False
            triggered_extruder1 = False
            # triggered_door = False
            # pause_print = False
            # triggered_door = False
            # pause_print = False

            if '0' in data:
                triggered_extruder0 = True

            if '1' in data:
                triggered_extruder1 = True

            # if 'door' in data:
            #     triggered_door = data["door"] == 0
            # if 'pause_print' in data:
            #     pause_print = data["pause_print"]
                
            # if 'door' in data:
            #     triggered_door = data["door"] == 0
            # if 'pause_print' in data:
            #     pause_print = data["pause_print"]

            if triggered_extruder0 and self.stackedWidget.currentWidget() not in [self.changeFilamentPage, self.changeFilamentProgressPage,
                                    self.changeFilamentExtrudePage, self.changeFilamentRetractPage,self.changeFilamentLoadPage]:
                self.octopiclient.gcode(command='PAUSE')
                if dialog.WarningOk(self, "Filament outage or clog detected in Extruder 0. Please check the external motors. Print paused"):
                    pass

            if triggered_extruder1 and self.stackedWidget.currentWidget() not in [self.changeFilamentPage, self.changeFilamentProgressPage,
                                    self.changeFilamentExtrudePage, self.changeFilamentRetractPage,self.changeFilamentLoadPage]:
                self.octopiclient.gcode(command='PAUSE')
                if dialog.WarningOk(self, "Filament outage or clog detected in Extruder 1. Please check the external motors. Print paused"):
                    pass

            # if triggered_door:
            #     if self.printerStatusText == "Printing":
            #         no_pause_pages = [self.controlPage, self.changeFilamentPage, self.changeFilamentProgressPage,
            #                           self.changeFilamentExtrudePage, self.changeFilamentRetractPage,self.changeFilamentLoadPage,]
            #         if not pause_print or self.stackedWidget.currentWidget() in no_pause_pages:
            #             if dialog.WarningOk(self, "Door opened"):
            #                 return
            #         self.octopiclient.pausePrint()
            #         if dialog.WarningOk(self, "Door opened. Print paused.", overlay=True):
            #             return
            #     else:
            #         if dialog.WarningOk(self, "Door opened"):
            #             return
            # if triggered_door:
            #     if self.printerStatusText == "Printing":
            #         no_pause_pages = [self.controlPage, self.changeFilamentPage, self.changeFilamentProgressPage,
            #                           self.changeFilamentExtrudePage, self.changeFilamentRetractPage,self.changeFilamentLoadPage,]
            #         if not pause_print or self.stackedWidget.currentWidget() in no_pause_pages:
            #             if dialog.WarningOk(self, "Door opened"):
            #                 return
            #         self.octopiclient.pausePrint()
            #         if dialog.WarningOk(self, "Door opened. Print paused.", overlay=True):
            #             return
            #     else:
            #         if dialog.WarningOk(self, "Door opened"):
            #             return
        except Exception as e:
            print(e)

import json
import os
from PyQt5 import QtCore
import sys
import mainGUI
from MainUIClass.MainUIClasses.dialog_methods import askAndReboot
from logger import *
import dialog
from MainUIClass.config import Development

if not Development:
    json_file_name = '/home/pi/printer_name.json'
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    json_file_name = os.path.join(parent_dir, 'printer_name.json')

allowed_names = ["Twin Dragon 300 x 300 x 300", "Twin Dragon 400 x 400 x 400", "Twin Dragon 600 x 600 x 400"]
default_name = "Twin Dragon 600 x 600 x 400"

class printerName(mainGUI.Ui_MainWindow):
    def __init__(self):
        log_info("Starting printer name init.")
        log_debug("Printer name self parameter passed: " + str(self))
        try:
            self.initialisePrinterNameJson()
        except Exception as e:
            error_message = "Error initializing printerName JSON: " + str(e)
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass
        super().__init__()

    def setup(self):
        try:
            log_info("Setting up printer name.")
            self.printerName = self.getPrinterName()
            self.enterPrinterName.clicked.connect(self.enterPrinterName_function)
            self.setPrinterNameComboBox()
            log_info("Printer name setup completed.")
        except Exception as e:
            error_message = "Error setting up printer name: " + str(e)
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def enterPrinterName_function(self):
        try:
            log_info("Entering printer name function.")
            temp_printerName = self.getPrinterName()
            new_printerName = self.printerNameComboBox.currentText()
            if temp_printerName != new_printerName:
                self.setPrinterName(new_printerName)
                if Development:
                    sys.exit()
                else:
                    if not askAndReboot(self, "Reboot to reflect changes?"):
                        self.setPrinterName(temp_printerName)
            log_info("Printer name function completed.")
        except Exception as e:
            error_message = "Error updating printer name: " + str(e)
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def initialisePrinterNameJson(self):
        try:
            log_info("Initializing printer name JSON.")
            if not os.path.exists(json_file_name):
                data = {'printer_name': default_name}
                self.writePrinterNameJson(data)
            else:
                try:
                    with open(json_file_name, 'r') as file:
                        data = json.load(file)
                    if data.get('printer_name') not in allowed_names:
                        self.setPrinterName(default_name)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    error_message = "Error loading printerName JSON: " + str(e)
                    log_error(error_message)
                    self.setPrinterName(default_name)
            log_info("Printer name JSON initialization completed.")
        except Exception as e:
            error_message = "Error initializing printerName JSON: " + str(e)
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setPrinterName(self, name):
        try:
            log_info(f"Setting printer name to {name}.")
            data = {"printer_name": name}
            self.writePrinterNameJson(data)
            self.setPrinterNameComboBox()
        except Exception as e:
            error_message = "Error setting printer name: " + str(e)
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def writePrinterNameJson(self, data):
        try:
            log_info(f"Writing printer name JSON: {data}.")
            with open(json_file_name, 'w') as file:
                json.dump(data, file, indent=4)
            log_info("Printer name JSON written successfully.")
        except Exception as e:
            error_message = "Error writing printerName JSON: " + str(e)
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def setPrinterNameComboBox(self):
        try:
            log_info("Setting printer name combo box.")
            current_printer_name = self.getPrinterName()
            index = self.printerNameComboBox.findText(current_printer_name, QtCore.Qt.MatchFixedString)
            if index != -1:  # Check if a valid index was found
                self.printerNameComboBox.setCurrentIndex(index)
            log_info("Printer name combo box set successfully.")
        except Exception as e:
            error_message = "Error setting printer name combo box: " + str(e)
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    @classmethod
    def getPrinterName(cls):
        try:
            log_info("Getting printer name from JSON.")
            with open(json_file_name, 'r') as file:
                data = json.load(file)
                printer_name = data.get('printer_name', default_name) 
                log_info(f"Printer name retrieved: {printer_name}")
                return printer_name
        except (FileNotFoundError, json.JSONDecodeError) as e:
            error_message = "Error loading printerName JSON: " + str(e)
            log_error(error_message)
            return default_name
        except Exception as e:
            error_message = "Unexpected error while loading printerName JSON: " + str(e)
            log_error(error_message)

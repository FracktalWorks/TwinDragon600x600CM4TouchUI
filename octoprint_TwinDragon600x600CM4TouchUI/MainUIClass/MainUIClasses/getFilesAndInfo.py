import dialog
import os
import subprocess
from datetime import datetime
from PyQt5 import QtGui, QtCore
from MainUIClass.config import _fromUtf8
from hurry.filesize import size
import mainGUI
from logger import *
from MainUIClass.decorators import run_async
import base64

class getFilesAndInfo(mainGUI.Ui_MainWindow):
    def __init__(self):
        try:
            log_info("Starting get files init.")
            self.octopiclient = None
            super().__init__()
        except Exception as e:
            error_message = f"Error in getFilesAndInfo __init__: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass
    
    def setup(self):
        """
        Sets up signal connections for various UI elements.
        """
        log_info("Setting up getFilesAndInfo.")
        try:
            log_debug("Octopiclient inside class getFilesAndInfo: " + str(self.octopiclient))

            # fileListLocalScreen
            self.localStorageBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.printLocationPage))
            self.localStorageScrollUp.pressed.connect(
                lambda: self.fileListWidget.setCurrentRow(self.fileListWidget.currentRow() - 1))
            self.localStorageScrollDown.pressed.connect(
                lambda: self.fileListWidget.setCurrentRow(self.fileListWidget.currentRow() + 1))
            self.localStorageSelectButton.pressed.connect(self.printSelectedLocal)
            self.localStorageDeleteButton.pressed.connect(self.deleteItem)

            # selectedFile Local Screen
            self.fileSelectedBackButton.pressed.connect(self.fileListLocal)
            self.fileSelectedPrintButton.pressed.connect(self.printFile)

            # filelistUSBPage
            self.USBStorageBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.printLocationPage))
            self.USBStorageScrollUp.pressed.connect(
                lambda: self.fileListWidgetUSB.setCurrentRow(self.fileListWidgetUSB.currentRow() - 1))
            self.USBStorageScrollDown.pressed.connect(
                lambda: self.fileListWidgetUSB.setCurrentRow(self.fileListWidgetUSB.currentRow() + 1))
            self.USBStorageSelectButton.pressed.connect(self.printSelectedUSB)
            self.USBStorageSaveButton.pressed.connect(lambda: self.transferToLocal(prnt=False))

            # selectedFile USB Screen
            self.fileSelectedUSBBackButton.pressed.connect(self.fileListUSB)
            self.fileSelectedUSBTransferButton.pressed.connect(lambda: self.transferToLocal(prnt=False))
            self.fileSelectedUSBPrintButton.pressed.connect(lambda: self.transferToLocal(prnt=True))

            log_info("Setup for getFilesAndInfo complete.")
        except Exception as e:
            error_message = f"Error setting up getFilesAndInfo: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def fileListLocal(self):
        '''
        Gets the file list from octoprint server, displays it on the list, as well as
        sets the stacked widget page to the file list page
        '''
        try:
            self.stackedWidget.setCurrentWidget(self.fileListLocalPage)
            files = []
            for file in self.octopiclient.retrieveFileInformation()['files']:
                if file["type"] == "machinecode":
                    files.append(file)

            self.fileListWidget.clear()
            files.sort(key=lambda d: d['date'], reverse=True)
            self.fileListWidget.addItems([f['name'] for f in files])
            self.fileListWidget.setCurrentRow(0)
        except Exception as e:
            error_message = f"Error in fileListLocal: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def fileListUSB(self):
        '''
        Gets the file list from USB drive, displays it on the list, as well as
        sets the stacked widget page to the file list page
        '''
        try:
            self.stackedWidget.setCurrentWidget(self.fileListUSBPage)
            self.fileListWidgetUSB.clear()
            files = subprocess.Popen("ls /media/usb0 | grep gcode", stdout=subprocess.PIPE, shell=True).communicate()[0]
            files = files.decode('utf-8').split('\n')
            files = filter(None, files)
            self.fileListWidgetUSB.addItems(files)
            self.fileListWidgetUSB.setCurrentRow(0)
        except Exception as e:
            error_message = f"Error in fileListUSB: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def printSelectedLocal(self):
        '''
        Displays detailed information about the selected file and sets the current page to the print selected page.
        Also displays preview image if available.
        '''
        try:
            self.fileSelected.setText(self.fileListWidget.currentItem().text())
            self.stackedWidget.setCurrentWidget(self.printSelectedLocalPage)
            file = self.octopiclient.retrieveFileInformation(self.fileListWidget.currentItem().text())
            try:
                self.fileSizeSelected.setText(size(file['size']))
            except KeyError:
                self.fileSizeSelected.setText('-')
            try:
                self.fileDateSelected.setText(datetime.fromtimestamp(file['date']).strftime('%d/%m/%Y %H:%M:%S'))
            except KeyError:
                self.fileDateSelected.setText('-')
            try:
                m, s = divmod(file['gcodeAnalysis']['estimatedPrintTime'], 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                self.filePrintTimeSelected.setText("%dd:%dh:%02dm:%02ds" % (d, h, m, s))
            except KeyError:
                self.filePrintTimeSelected.setText('-')
            try:
                self.filamentVolumeSelected.setText(
                    ("%.2f cm" % file['gcodeAnalysis']['filament']['tool0']['volume']) + chr(179))
            except KeyError:
                self.filamentVolumeSelected.setText('-')
            try:
                self.filamentLengthFileSelected.setText(
                    "%.2f mm" % file['gcodeAnalysis']['filament']['tool0']['length'])
            except KeyError:
                self.filamentLengthFileSelected.setText('-')

            self.displayThumbnail(self.printPreviewSelected, str(self.fileListWidget.currentItem().text()), usb=False)

        except Exception as e:
            error_message = f"Error in printSelectedLocal: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def printSelectedUSB(self):
        '''
        Displays detailed information about the selected file from USB drive and sets the current page to the print selected page.
        Also displays preview image if available.
        '''
        try:
            self.fileSelectedUSBName.setText(self.fileListWidgetUSB.currentItem().text())
            self.stackedWidget.setCurrentWidget(self.printSelectedUSBPage)
            self.displayThumbnail(self.printPreviewSelectedUSB, '/media/usb0/' + str(self.fileListWidgetUSB.currentItem().text()), usb=True)
        except Exception as e:
            error_message = f"Error in printSelectedUSB: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def transferToLocal(self, prnt=False):
        '''
        Transfers a file from USB mounted at /media/usb0 to octoprint's watched folder so that it gets automatically detected by Octoprint.
        '''
        try:
            file = '/media/usb0/' + str(self.fileListWidgetUSB.currentItem().text())
            self.uploadThread = ThreadFileUpload(file, prnt=prnt)
            self.uploadThread.start()
            if prnt:
                self.stackedWidget.setCurrentWidget(self.homePage)
        except Exception as e:
            error_message = f"Error in transferToLocal: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def printFile(self):
        '''
        Prints the file selected from printSelectedLocal().
        '''
        try:
            self.octopiclient.home(['x', 'y', 'z'])
            self.octopiclient.selectFile(self.fileListWidget.currentItem().text(), True)
            self.checkKlipperPrinterCFG()
            self.stackedWidget.setCurrentWidget(self.homePage)
        except Exception as e:
            error_message = f"Error in printFile: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def deleteItem(self):
        '''
        Deletes a selected gcode file and its associated image file from Octoprint.
        '''
        try:
            self.octopiclient.deleteFile(self.fileListWidget.currentItem().text())
            self.octopiclient.deleteFile(self.fileListWidget.currentItem().text().replace(".gcode", ".png"))
            self.fileListLocal()
        except Exception as e:
            error_message = f"Error in deleteItem: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    def getImageFromGcode(self, gcodeLocation):
        '''
        Retrieves an image embedded in a gcode file.
        '''
        try:
            with open(gcodeLocation, 'rb') as f:
                content = f.readlines()[:500]
                content = b''.join(content)
            start = content.find(b'; thumbnail begin')
            end = content.find(b'; thumbnail end')
            if start != -1 and end != -1:
                thumbnail = content[start:end]
                thumbnail = base64.b64decode(thumbnail[thumbnail.find(b'\n') + 1:].replace(b'; ', b'').replace(b'\r\n', b''))
                return thumbnail
            else:
                return False
        except Exception as e:
            error_message = f"Error in getImageFromGcode: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

    @run_async
    def displayThumbnail(self, labelObject, fileLocation, usb=False):
        '''
        Displays an image thumbnail on the specified label object.
        '''
        try:
            pixmap = QtGui.QPixmap()
            if usb:
                img = self.getImageFromGcode(fileLocation)
            else:
                img = self.octopiclient.getImage(fileLocation)
            if img:
                pixmap.loadFromData(img)
                labelObject.setPixmap(pixmap)
            else:
                labelObject.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/thumbnail.png")))
        except Exception as e:
            error_message = f"Error in displayThumbnail: {str(e)}"
            log_error(error_message)
            labelObject.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/thumbnail.png")))

class ThreadFileUpload(QtCore.QThread):
    def __init__(self, file, prnt=False):
        super(ThreadFileUpload, self).__init__()
        self.file = file
        self.prnt = prnt

    def run(self):
        '''
        Uploads a file to Octoprint and optionally prints it.
        '''
        try:
            try:
                exists = os.path.exists(self.file.replace(".gcode", ".png"))
            except:
                exists = False
            if exists:
                self.octopiclient.uploadImage(self.file.replace(".gcode", ".png"))

            if self.prnt:
                self.octopiclient.uploadGcode(file=self.file, select=True, prnt=True)
            else:
                self.octopiclient.uploadGcode(file=self.file, select=False, prnt=False)

            log_info("File upload completed successfully.")
        except Exception as e:
            error_message = f"Error in ThreadFileUpload run: {str(e)}"
            log_error(error_message)
            if dialog.WarningOk(self, error_message, overlay=True):
                pass

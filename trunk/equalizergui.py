"""
equalizergui: Equalizer graphical user interface.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class EqualizerWidget(QWidget):
    """
    The EqualizerWidget class defines the equalizer GUI and interfaces with
    the XMMS2 equalizer settings.
    """
    def __init__(self, sonus, parent=None):
        QWidget.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.mlibgui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Equalizer'))
        self.resize(QSize(640, 360))

        # XMMS Broadcast -- need to move to mlib somewhere?
        self.sonus.broadcast_configval_changed(self.updateView)

        self.dialogVbox = QVBoxLayout(self)
        self.sliderWidget = QWidget(self)
        self.optionsWidget = QWidget(self)
        self.sliderHbox = QHBoxLayout(self.sliderWidget)
        self.optionsHbox = QHBoxLayout(self.optionsWidget)
        self.setLayout(self.dialogVbox)
        self.dialogVbox.addWidget(self.sliderWidget)
        self.dialogVbox.addWidget(self.optionsWidget)

        self.preampSlider = QSlider(self.sliderWidget)
        self.preampSlider.setRange(-20,20)
        self.sliderHbox.addWidget(self.preampSlider)

        self.bandsSlider = []
        for i in range(31):
            self.bandsSlider.insert(i, QSlider(self.sliderWidget))
            self.connect(self.bandsSlider[i],
                         SIGNAL('sliderMoved(int)'), self.setGain)
            self.bandsSlider[i].setRange(-20,20)
            self.sliderHbox.addWidget(self.bandsSlider[i])

        self.enableCheckbox = QCheckBox(self.tr('Enabled'), self)
        self.optionsHbox.addWidget(self.enableCheckbox)

        self.extraFilteringCheckbox = QCheckBox(self.tr('Extra Filtering'),
                                                  self)
        self.optionsHbox.addWidget(self.extraFilteringCheckbox)

        self.bandsCombobox = QComboBox(self.optionsWidget)
        self.optionsHbox.addWidget(self.bandsCombobox)
        self.bandsCombobox.addItem('10')
        self.bandsCombobox.addItem('15')
        self.bandsCombobox.addItem('25')
        self.bandsCombobox.addItem('31')

        self.legacyCheckBox = QCheckBox(self.tr('Use Legacy'), self)
        self.legacyCheckBox.setChecked(False)
        self.optionsHbox.addWidget(self.legacyCheckBox)

        self.resetButton = QPushButton(self.tr('Reset'), self)
        self.optionsHbox.addWidget(self.resetButton)

        # getConfigValList will replace getInitialvalues eventually
        self.sonus.configval_list(self.getConfigValList)
        self.getInitialValues()

        self.connect(self.enableCheckbox, SIGNAL('clicked()'),
                     self._updateEnabledCheckboxCb)
        self.connect(self.preampSlider, SIGNAL('sliderMoved(int)'),
                     self.setPreamp)
        self.connect(self.preampSlider, SIGNAL('sliderReleased(int)'),
                     self.setPreamp)
        self.connect(self.resetButton, SIGNAL('clicked()'),
                     self.resetEqualizer)
        self.connect(self.legacyCheckBox, SIGNAL('clicked()'),
                     self._updateLegacyCheckBoxCb)
        self.connect(self.bandsCombobox, SIGNAL('activated(int)'),
                     self._updateBandComboBoxCb)
        self.connect(self.extraFilteringCheckbox, SIGNAL('clicked()'),
                     self.setExtraFiltering)

        # Worst hack ever, just want to get this equalizer over with
        self.BandCounter = 0

    def getBandCount(self, result):
        #self.updateBandCount(int(result.value()))
        self.updateBandComboBox(result.value())

    def getConfigValList(self, result):
        """
        Adds equalizer to chain if not present
        Adapted from nano's eq.py handle_configval_list()
        """
        configList = result.value()
        chained = False
        order = 0
        for key in configList:
            if key.startswith('effect.order'):
                if configList[key] == 'equalizer':
                    chained = True
                elif len(configList[key]) == 0:
                    pass
                else:
                    order += 1
        if not chained:
            value = 'effect.order.%d' % order
            self.sonus.configval_set(value, 'equalizer')
            chained = True
            # Make sure equalizer is in chain
            self.sonus.playback_stop()
            self.sonus.playback_start()
            self.sonus.playback_stop()

    def getEnabled(self, result):
        if result.value() == '1':
            self.enableCheckbox.setChecked(True)
        else:
            self.enableCheckbox.setChecked(False)

    def getExtraFiltering(self, result):
        if result.value() == '1':
            self.extraFilteringCheckbox.setChecked(True)
        else:
            self.extraFilteringCheckbox.setChecked(False)

    def getGain(self, result):
        self.setSliderValue(self.BandCounter, float(result.value()))
        self.BandCounter = self.BandCounter + 1

    def getInitialValues(self):
        # TODO: Change getInitialValues() to use configval_list
        self.sonus.configval_get('equalizer.preamp', self.getPreamp)
        self.sonus.configval_get('equalizer.enabled', self.getEnabled)
        self.sonus.configval_get('equalizer.extra_filtering',
                                 self.getExtraFiltering)
        self.sonus.configval_get('equalizer.use_legacy', self.getLegacy)
        self.sonus.configval_get('equalizer.bands', self.getBandCount)
        if self.legacyCheckBox.isChecked() == True:
            for i in range(10):
                name = 'equalizer.legacy%d' % i
                self.sonus.configval_get(name, self.getGain)
        else:
            for i in range(31):
                name = 'equalizer.gain%02d' % i
                self.sonus.configval_get(name, self.getGain)

    def getLegacy(self, result):
        if result.value() == '0':
            self.legacyCheckBox.setChecked(False)
        else:
            self.legacyCheckBox.setChecked(True)

    def getPreamp(self, result):
        self.preampSlider.setValue(float(result.value()))

    def resetEqualizer(self):
        self.sonus.configval_set('equalizer.preamp', str(0))
        self.sonus.configval_set('equalizer.enabled', str(0))
        self.sonus.configval_set('equalizer.extra_filtering', str(0))
        for i in range(9):
            name = 'equalizer.legacy%d' % i
            self.sonus.configval_set(name, str(0))
        for i in range(31):
            name = 'equalizer.gain%02d' % i
            self.sonus.configval_set(name, str(0))

    def setBandCount(self, value):
        self.sonus.configval_set('equalizer.bands', value)

    def setEnabled(self):
        if self.enableCheckbox.isChecked():
            self.sonus.configval_set('equalizer.enabled', str(1))
        else:
           self.sonus.configval_set('equalizer.enabled', str(0))

    def setExtraFiltering(self):
        if self.extraFilteringCheckbox.isChecked():
            self.sonus.configval_set('equalizer.extra_filtering', str(1))
        else:
            self.sonus.configval_set('equalizer.extra_filtering', str(0))

    def setGain(self):
        activeSlider = self.sender()
        activeSliderId = self.bandsSlider.index(activeSlider)
        if self.legacyCheckBox.isChecked():
            name = 'equalizer.legacy%d' % activeSliderId
        else:
            name = 'equalizer.gain%02d' % activeSliderId
        self.sonus.configval_set(name, str(activeSlider.value()))

    def setLegacy(self, value):
        if value == 'True':
            self.sonus.configval_set('equalizer.use_legacy', str(1))
        else:
            self.sonus.configval_set('equalizer.use_legacy', str(0))

    def setPreamp(self):
        self.sonus.configval_set('equalizer.preamp',
                                 str(self.preampSlider.value()))

    def setSliderValue(self, sliderIndex, sliderValue):
        self.bandsSlider[sliderIndex].setValue(sliderValue)

    def updateBandCount(self, value):
        for i in range(31):
            if i < value:
                self.bandsSlider[i].show()
            else:
                self.bandsSlider[i].hide()

    def updateBandComboBox(self, value):
        if value == '10':
            self.bandsCombobox.setCurrentIndex(0)
        elif value == '15':
            self.bandsCombobox.setCurrentIndex(1)
        elif value == '25':
            self.bandsCombobox.setCurrentIndex(2)
        elif value == '31':
            self.bandsCombobox.setCurrentIndex(3)
        if self.legacyCheckBox.isChecked() == True:
            self.bandsCombobox.setEnabled(False)
            self.updateBandCount(10)
        else:
            self.updateBandCount(int(value))

    def _updateBandComboBoxCb(self):
        self.resetEqualizer()
        self.updateBandComboBox(self.bandsCombobox.currentText())
        self.setBandCount(str(self.bandsCombobox.currentText()))

    def updateEnabledCheckbox(self, value):
        if value == '1':
            self.enableCheckbox.setChecked(True)
        else:
            self.enableCheckbox.setChecked(False)

    def _updateEnabledCheckboxCb(self):
        self.setEnabled()

    def updateExtraCheckbox(self, value):
        if value == '1':
            self.extraFilteringCheckbox.setChecked(True)
        else:
            self.extraFilteringCheckbox.setChecked(False)

    def updateGainSlider(self):
        # TODO: Block xmms updating slider position while user is moving it
        if self.bandsComboBox.isEnabled():
            self.bandsComboBox.setEnabled(False)
            self.bandsComboBox.setCurrentIndex(0)
        else:
            self.bandsComboBox.setEnabled(True)

    def updateLegacyCheckBox(self, value=None):
        if self.legacyCheckBox.isChecked():
            self.bandsCombobox.setEnabled(False)
            self.updateBandComboBox(10)
        else:
            self.bandsCombobox.setEnabled(True)
            self.updateBandComboBox(self.bandsCombobox.currentText())

    def _updateLegacyCheckBoxCb(self):
        self.updateLegacyCheckBox()
        self.setLegacy(str(self.legacyCheckBox.isChecked()))

    def updatePreampSlider(self, value):
        self.preampSlider.setValue(value)

    def updateView(self, xmmsResult):
        value = xmmsResult.value()
        for key in value:
            if key == 'equalizer.preamp':
                self.updatePreampSlider(float(value[key]))
            elif key == 'equalizer.enabled':
                self.updateEnabledCheckbox(value[key])
            elif key == 'equalizer.extra_filtering':
                self.updateExtraCheckbox(value[key])
            elif key == 'equalizer.use_legacy':
                self.updateLegacyCheckBox(bool(value[key]))
            elif key == 'equalizer.bands':
                self.updateBandComboBox(value[key])
            elif key.startswith('equalizer.gain'):
                bandIndex = int(key[-2:])
                gainValue = float(value[key])
                self.setSliderValue(bandIndex, gainValue)
            elif key.startswith('equalizer.legacy'):
                bandIndex = int(key[-1:])
                gainValue = float(value[key])
                self.setSliderValue(bandIndex, gainValue)

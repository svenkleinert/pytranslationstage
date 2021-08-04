from . import QWidget, QFormLayout, QLineEdit, QPushButton, Slot, Signal
from .AbstractTranslationStageWidget import AbstractTranslationStageWidget
from .TranslationStageWorker import TranslationStageWorker

import numpy as np

class WedgeScanningWidget( AbstractTranslationStageWidget ):
    scanStepSignal = Signal( int )
    def __init__( self, parent=None, show_scan_button=False ):
        super( WedgeScanningWidget, self ).__init__( parent=None )

        self.form_widget = QWidget()
        self.form = QFormLayout()
        self.form_widget.setLayout( self.form )
        self.vbox.addWidget( self.form_widget )

        self.start_position_edit = QLineEdit("-40")
        self.form.addRow( "Start position (mm)", self.start_position_edit )

        self.stop_position_edit = QLineEdit("40")
        self.form.addRow( "Stop position (mm)", self.stop_position_edit )

        self.step_edit = QLineEdit("100")
        self.form.addRow( "Steps", self.step_edit )

        self.wedge_angle_edit = QLineEdit( "45" )
        self.form.addRow( "Wedge angle (°)", self.wedge_angle_edit )

        self.form_widget.hide()
        if show_scan_button:
            self.scan_button = QPushButton( "Scan!" )
            self.scan_button.hide()
            self.scan_button.clicked.connect( self.on_scan_button )
            self.vbox.addWidget( self.scan_button )
        else:
            self.scan_button = None

    def __iter__( self ):
        self.deactivate_input()

        start = float( self.start_position_edit.text() )
        end = float( self.stop_position_edit.text() )
        steps = int( self.step_edit.text() )

        self.z = np.linspace( start, end, steps )
        self.z *= self.dist_prefix
        self.insertions = np.tan( float( self.wedge_angle_edit.text() ) * np.pi / 180 ) * self.z
        self.i = 0
        return self

    def __next__( self ):
        if self.i == len(self.z):
            self.activate_input()
            raise StopIteration
        self.translation_stage_instance.move_absolute( self.z[self.i] )

        self.i += 1
        return self.insertions[self.i-1]

    def __len__( self ):
        return int( self.step_edit.text() )

    def _show_settings( self ):
        self.form_widget.show()
        if self.scan_button is not None:
            self.scan_button.show()

    def _hide_settings( self ):
        self.form_widget.hide()
        if self.scan_button is not None:
            self.scan_button.hide()

    def _deactivate_input( self ):
        for i in range(self.form.rowCount()):
            self.form.itemAt( i, QFormLayout.FieldRole ).widget().setReadOnly( True )
        if self.scan_button is not None:
            self.scan_button.clicked.disconnect()


    def _activate_input( self ):
        for i in range(self.form.rowCount()):
            self.form.itemAt( i, QFormLayout.FieldRole ).widget().setReadOnly( False )
        if self.scan_button is not None:
            self.scan_button.clicked.connect( self.on_scan_button )

    def on_scan_button( self ):
        assert self.translation_stage_instance
        self.deactivate_input()
        start = float( self.start_position_edit.text() )
        end = float( self.stop_position_edit.text() )
        steps = int( self.step_edit.text() )

        self.z = np.linspace( start, end, steps )
        self.z *= self.dist_prefix
        self.insertions = np.tan( float( self.wedge_angle_edit.text() ) * np.pi / 180 ) * self.z

        self.worker = TranslationStageWorker( self.translation_stage_instance.move_absolute, self.z)
        self.worker.updateSignal.connect( self.onScanUpdate )
        self.worker.start()

    def onScanUpdate( self, i ):
        if i == len( self.z ) - 1:
            self.activate_input()
        self.scanStepSignal.emit( i )

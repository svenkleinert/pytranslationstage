from . import USE_PYSIDE2

if USE_PYSIDE2:
    from PySide2.QtWidgets import QWidget, QComboBox, QVBoxLayout, QLabel, QPushButton, QGroupBox, QRadioButton, QMessageBox, QFormLayout, QLineEdit, QSlider
    from PySide2.QtCore import Slot, Qt
else:
    from PyQt5.QtWidgets import QWidget, QComboBox, QVBoxLayout, QLabel, QPushButton, QGroupBox, QRadioButton, QMessageBox, QFormLayout, QLineEdit, QSlider
    from PyQt5.QtCore import Slot, Qt

import ..

class TranslationStageWidget( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self )
        self.parent = parent
        self.vbox = QVBoxLayout()
        self.setLayout( self.vbox )

        self.translation_stage = None

        self.translation_stage_text = QLabel( "Translation stage:" )
        self.vbox.addWidget( self.translation_stage_text )

        self.translation_stage_choice = QComboBox( self )
        for stage in pytranslationstage.translation_stage_types:
            self.translation_stage_choice.addItem( stage )
        self.translation_stage_choice.currentIndexChanged.connect( self.on_choice_changed )

        self.vbox.addWidget( self.translation_stage_choice )
        self.group_box = QGroupBox( "Translation stage selection..." )
        self.group_box_vbox = QVBoxLayout()
        self.group_box.setLayout( self.group_box_vbox )
        self.on_choice_changed()
        self.vbox.addWidget( self.group_box )

        self.connect_button = QPushButton( "connect!" )
        self.connect_button.clicked.connect( self.connect_translation_stage )
        self.vbox.addWidget( self.connect_button )

        self.disconnect_button = QPushButton( "disconnect!" )
        self.disconnect_button.clicked.connect( self.disconnect_translation_stage )
        self.disconnect_button.hide()
        self.vbox.addWidget( self.disconnect_button )

        self.form = QFormLayout()
        self.vbox.addLayout( self.form )

        self.current_position_text = QLabel ("current position:")
        self.current_position_text.hide()
        self.vbox.addWidget( self.current_position_text )

        self.current_position_slider = QSlider( )
        self.current_position_slider.setOrientation( Qt.Horizontal )
        self.current_position_slider.setRange( -40, 40 )
        self.current_position_slider.hide()
        self.old_position = None
        self.current_position_slider.setTracking( False )
        self.current_position_slider.valueChanged.connect( self.slider_changed )

        self.vbox.addWidget( self.current_position_slider )



    @Slot()
    def on_choice_changed( self ):
        for i in range( self.group_box_vbox.count() ):
            item = self.group_box_vbox.itemAt(i)
            item.widget().hide()
            self.group_box_vbox.removeItem( item )

        self.repaint()
        self.devices_available = pytranslationstage.translation_stage_types[self.translation_stage_choice.currentText()].scan()
        if len( self.devices_available ) == 0:
            self.group_box_vbox.addWidget( QLabel("No device found") )
        else:
            for d in self.devices_available:
                self.group_box_vbox.addWidget( QRadioButton( d ) )

    @Slot()
    def connect_translation_stage( self ):
        if len( self.devices_available ) == 0:
            QMessageBox.warning( self, "Couldn't connect to translation stage", "There are no translation stages of the specified type available" )
            return

        selection = 0
        for i in range( len(self.devices_available) ):
            if self.group_box_vbox.itemAt(i).widget().isChecked():
                selection = i
                break

        try:
            self.translation_stage = pytranslationstage.translation_stage_types[self.translation_stage_choice.currentText()].from_device( self.devices_available[selection] )
        except:
            self.translation_stage = None
            QMessageBox.warning( self, "Couldn't connect to specified translation stage", "Failed to connect to the translation stage. Have you chosen the right device?" )
        if self.translation_stage is not None:
            self.show_translation_stage_settings()
            if self.parent is not None:
                self.parent.refresh_ui()


    @Slot()
    def disconnect_translation_stage( self ):
        self.translation_sate = None
        self.hide_translation_stage_settings()
        if self.parent is not None:
            self.parent.refresh_ui()

    def show_translation_stage_settings( self ):
        self.connect_button.hide()
        self.group_box.hide()
        self.translation_stage_choice.hide()
        self.disconnect_button.show()
        self.translation_stage_text.setText( "Translation stage " + self.translation_stage.name +":" )
        while self.form.rowCount() > 0:
            self.form.removeRow( 0 )

        self.start_position_edit = QLineEdit("-40")
        self.form.addRow( "Start position (mm)", self.start_position_edit )

        self.stop_position_edit = QLineEdit("40")
        self.form.addRow( "Stop position (mm)", self.stop_position_edit )

        self.step_edit = QLineEdit("100")
        self.form.addRow( "Steps", self.step_edit )

        self.wedge_angle_edit = QLineEdit( "45" )
        self.form.addRow( "Wedge angle (°)", self.wedge_angle_edit )
        self.current_position_text.show()
        self.current_position_slider.show()
        current_pos = float( self.translation_stage.get_position() )
        self.current_position_text.setText( "current position: " + str(current_pos) + " mm")
        self.current_position_slider.setValue( current_pos )

    def hide_translation_stage_settings( self ):
        self.connect_button.show()
        self.group_box.show()
        self.translation_stage_choice.show()
        self.disconnect_button.hide()
        self.current_position_text.hide()
        self.current_position_slider.hide()
        self.translation_stage_text.setText( "Translation stage:" )
        while self.form.rowCount() > 0:
            self.form.removeRow( 0 )

        self.start_pos_edit = None
        self.stop_pos_edit = None
        self.step_edit = None
        self.wedge_angle_edit = None

    @Slot()
    def slider_changed( self ):
        if self.old_position != self.current_position_slider.value():
            self.old_position = self.current_position_slider.value()
            self.translation_stage.move_absolute( self.old_position )
            self.current_position_text.setText( "Current position {0:d} mm".format( self.old_position ) )

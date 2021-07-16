from . import QWidget, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QRadioButton, QMessageBox, QLineEdit, Slot, Signal, Qt

import pytranslationstage
from .TranslationStageWorker import TranslationStageWorker
from .ROSlider import ROSlider
from .utils import find_unit_prefix



class AbstractTranslationStageWidget( QWidget ):
    translationstage_connected = Signal()
    translationstage_disconnected = Signal()
    def __init__( self, parent=None ):
        super( AbstractTranslationStageWidget, self ).__init__( parent=parent )

        self.translation_stage_instance = None

        self.vbox = QVBoxLayout()
        self.setLayout( self.vbox )

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

        self.hbox = QHBoxLayout()

        self.current_position_slider = ROSlider( )
        self.current_position_slider.setOrientation( Qt.Horizontal )
        self.current_position_slider.setRange( -100, 100 )
        self.current_position_slider.hide()
        self.current_position_slider.setTracking( False )
        self.hbox.addWidget( self.current_position_slider, stretch=1 )

        self.current_position_edit = QLineEdit("0")
        self.current_position_edit.hide()
        self.current_position_edit.setMaximumWidth( 32 )
        self.hbox.addWidget( self.current_position_edit )


        self.current_position_unit_text = QLabel()
        self.current_position_unit_text.hide()
        self.hbox.addWidget( self.current_position_unit_text )

        self.vbox.addLayout( self.hbox )

        self.current_position_slider.valueChanged.connect( self.slider_changed )
        self.current_position_edit.returnPressed.connect( self.edit_changed )

        self.position = None
        self.worker =None

    @Slot()
    def on_choice_changed( self ):
        for i in range( self.group_box_vbox.count() ):
            item = self.group_box_vbox.itemAt(0)
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
            self.worker = TranslationStageWorker( pytranslationstage.translation_stage_types[self.translation_stage_choice.currentText()].from_device, self.devices_available[selection] )
            self.worker.updateSignal.connect( self.translation_stage_connected )
            self.worker.start()
        except Exception as e:
            print( e )
            self.translation_stage_instance = None
            QMessageBox.warning( self, "Couldn't connect to specified translation stage", "Failed to connect to the translation stage. Have you chosen the right device?" )

    @Slot()
    def translation_stage_connected( self ):
        self.translation_stage_instance = self.worker.return_value
        if self.translation_stage_instance is not None:
            tl_limits = self.translation_stage_instance.translation_limits
            self.dist_prefix_str, self.dist_prefix = find_unit_prefix( tl_limits )
            self.current_position_slider.setRange( tl_limits[0]/self.dist_prefix,
                tl_limits[1]/self.dist_prefix )
            self.show_translation_stage_settings()
            self.translationstage_connected.emit()

    @Slot()
    def disconnect_translation_stage( self ):
        if self.worker is not None:
            assert not self.worker.isRunning()
        self.translation_sage_instance = None
        self.current_position_slider.setRange( -100, 100 )
        self.hide_translation_stage_settings()
        self.translationstage_disconnected.emit()

    def show_translation_stage_settings( self ):
        self.connect_button.hide()
        self.group_box.hide()
        self.translation_stage_choice.hide()
        self.disconnect_button.show()
        self.translation_stage_text.setText( "Translation stage " + self.translation_stage_instance.name +":" )
        self.current_position_unit_text.show()
        self.current_position_slider.show()
        self.position = float( self.translation_stage_instance.get_position() )
        self.current_position_unit_text.setText( self.dist_prefix_str + "m" )
        self.current_position_edit.show()
        self.current_position_slider.setValue( self.position )
        self._show_settings()

    def hide_translation_stage_settings( self ):
        self.connect_button.show()
        self.group_box.show()
        self.translation_stage_choice.show()
        self.disconnect_button.hide()
        self.current_position_unit_text.hide()
        self.current_position_edit.hide()
        self.current_position_slider.hide()
        self.translation_stage_text.setText( "Translation stage:" )
        self._hide_settings()

    @Slot()
    def slider_changed( self ):
        if self.position != self.current_position_slider.value() * self.dist_prefix:
            self.set_position( self.current_position_slider.value() * self.dist_prefix )

    @Slot()
    def edit_changed( self ):
        new_pos = self.current_position_edit.text()
        try:
            new_pos = float( new_pos )
            if self.position != new_pos * self.dist_prefix:
                self.set_position( new_pos * self.dist_prefix )
        except Exception as e:
            print( e )

    def get_position( self ):
        assert self.translation_stage_instance is not None
        return self.position

    def set_position( self, position ):
        assert self.translation_stage_instance is not None
        if self.worker is not None:
            assert not self.worker.isRunning()
        self.deactivate_input()
        self.position = position
        self.worker = TranslationStageWorker( self.translation_stage_instance.move_absolute, position )
        self.worker.updateSignal.connect( self.activate_input )
        self.current_position_edit.setText( "{0:.0f}".format( self.position / self.dist_prefix ) )
        self.current_position_slider.setValue( self.position / self.dist_prefix )
        self.worker.start()

        self._set_position( )

    def deactivate_input( self ):
        self.current_position_edit.setReadOnly( True )
        self.current_position_slider.setReadOnly( True )
        self._deactivate_input()

    def activate_input( self ):
        self.current_position_edit.setReadOnly( False )
        self.current_position_slider.setReadOnly( False )
        self._activate_input()

    # to be overwritten by child classes
    def _set_position( self ):
        pass

    def _show_settings( self ):
        pass

    def _hide_settings( self ):
        pass

    def _activate_input( self ):
        pass

    def _deactivate_input( self ):
        pass

#OP-1 Python Scripts V1.0.9

import Live
import time

from consts import *

# Ableton Live Framework imports

from _Framework.ControlSurface import ControlSurface
from _Framework.TransportComponent import TransportComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.DeviceComponent import DeviceComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.InputControlElement import *

# OP-1 imports

from OP1ModeSelectorComponent import OP1ModeSelectorComponent

class OP1(ControlSurface):
	def __init__(self, c_instance):
		ControlSurface.__init__(self, c_instance)
		self.c_instance = c_instance

		self.retries_count = 0
		self.device_connected = False

		self.clip_color_callbacks = {}
		self.slot_callbacks = {}

		self.text_start_sequence = (0xf0, 0x0, 0x20, 0x76, 0x00, 0x03)
		self.text_end_sequence = (0xf7,)
		self.enable_sequence = (0xf0, 0x00, 0x20, 0x76, 0x00, 0x01, 0x02, 0xf7)
		self.disable_sequence = (0xf0, 0x00, 0x20, 0x76, 0x00, 0x01, 0x00, 0xf7)

		self.id_sequence = (0xf0, 0x7e, 0x7f, 0x06, 0x01, 0xf7)

		self.text_color_start_sequence = (0xf0, 0x0, 0x20, 0x76, 0x00, 0x04)

		self.log('INITIALIZING')

		self.app = Live.Application.get_application()

		maj = self.app.get_major_version()
		min = self.app.get_minor_version()
		bug = self.app.get_bugfix_version()
		
		self.show_message(str(maj) + "." + str(min) + "." + str(bug))

		# reseting text
		self.write_text(' ')

		# reset display clips
		self.reset_display_clips()

		# getting browser visible state
		self.session_browser_visible = self.app.view.is_view_visible("Browser")
		
		# getting browser visible state
		self.arrange_browser_visible = self.app.view.is_view_visible("Browser")

		# getting session view visible state
		self.session_visible = self.app.view.is_view_visible("Session")

		# getting arrange view visible state
		self.arrange_visible = self.app.view.is_view_visible("Arranger")

		# getting detail view visible state
		self.detail_visible = self.app.view.is_view_visible("Detail")

		# getting back to arranger state
		self.back_to_arranger_state = self.song().back_to_arranger

		# initializing channel strip to null
		self._channel_strip = None

		# initializing transport component
		self._transport = TransportComponent()

		# initializing mixer component
		self._mixer = MixerComponent(NUM_TRACKS,2)

		# initializing session component
		self._session = SessionComponent(NUM_TRACKS,NUM_ROWS)
		self._session.add_offset_listener(self.session_offset_changed)

		# configuring operation mode selector buttons
		self._operation_mode_buttons = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_MODE_1_BUTTON), ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_MODE_2_BUTTON), ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_MODE_3_BUTTON), ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_MODE_4_BUTTON), 
		
		# initializing operation mode selector
		self._operation_mode_selector = OP1ModeSelectorComponent(self, self._transport, self._mixer, self._session)
		
		# setting operation mode selector buttons
		self._operation_mode_selector.set_mode_buttons(self._operation_mode_buttons)

		# adding value listener for operation mode index
		self._operation_mode_selector.add_mode_index_listener(self.mode_index_changed)

		# setting global transport assignments
		self._transport.set_record_button(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_REC_BUTTON))
		self._transport.set_play_button(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_PLAY_BUTTON))
		self._transport.set_stop_button(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_STOP_BUTTON))  
		self._transport.set_metronome_button(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_METRONOME_BUTTON))  
		self._transport.set_tap_tempo_button(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_HELP_BUTTON))
		self._transport.set_punch_buttons(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_SS1_BUTTON), ButtonElement(True,MIDI_CC_TYPE, CHANNEL, OP1_SS2_BUTTON))
		self._transport.set_loop_button(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_SS3_BUTTON))
		self._transport.set_overdub_button(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_SS4_BUTTON))

		# setting global session assignments
		self._session.set_scene_bank_buttons(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_COM),ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_MICRO))

		# setting misc listeners
		self.browser_toggle_button = ButtonElement(False, MIDI_CC_TYPE, CHANNEL, 15)
		self.browser_toggle_button.add_value_listener(self.browser_toggle_button_callback)

		self.mainview_toggle_button = ButtonElement(False, MIDI_CC_TYPE, CHANNEL, 16)
		self.mainview_toggle_button.add_value_listener(self.mainview_toggle_button_callback)

		self.detailview_toggle_button = ButtonElement(False, MIDI_CC_TYPE, CHANNEL, 17)
		self.detailview_toggle_button.add_value_listener(self.detailview_toggle_button_callback)

		self.clear_track_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, 25)
		self.clear_track_button.add_value_listener(self.clear_track_button_callback)

		self.back_to_arranger_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, 26)
		self.back_to_arranger_button.add_value_listener(self.back_to_arranger_button_callback)

		# adding value listener for selected track change
		self.song().view.add_selected_track_listener(self.selected_track_changed)

		# adding value listener for selected scene change
		self.song().view.add_selected_scene_listener(self.selected_scene_changed)

		# setting assignments for currently selected track
		self.selected_track_changed()

		# setting assignments for currently selected scene
		self.selected_scene_changed()

	def handle_sysex(self, midi_bytes):
		if ((midi_bytes[6]==32) and (midi_bytes[7]==118)):
			self.device_connected = True
			self.log("OP-1 CONNECTED. SENDING ABLETON LIVE MODE INIT SEQUENCE")
			self._send_midi(self.enable_sequence)

	def add_clip_slot_listeners(self):
		#self.log('ADDING CLIP SLOT LISTENERS')
		
		# creating an empty list for all clip slots
		clip_slots = []

		# getting a reference to all tracks
		tracks = self.song().tracks
		
		# appending all tracks clip slots to clip_slots
		for track in tracks:
			clip_slots.append(track.clip_slots)

		# iterating over all clip slots
		for t in range(len(clip_slots)):
			for c in range(len(clip_slots[t])):
				clip_slot = clip_slots[t][c]

				# adding has clip listener to clip slot
				self.add_slot_listener(clip_slot)

				# if clip slot has clip
				if clip_slot.has_clip:
					# adding clip listeners
					self.add_clip_listener(clip_slot.clip)

	def rem_clip_slot_listeners(self):
		#self.log('REMOVING CLIP SLOT LISTENERS')

		# iterate over all clip color change callbacks
		for c in self.clip_color_callbacks:
			# if clip still exists
			if c != None:
				# and it has a has clip listener
				if c.color_has_listener(self.clip_color_callbacks[c]) == 1:
					# remove it
					c.remove_color_listener(self.clip_color_callbacks[c])

		# iterate over all clip slot callbacks
		for cs in self.slot_callbacks:
			# if clip slot still exists
			if cs != None:
				# and it has a has clip listener
				if cs.has_clip_has_listener(self.slot_callbacks[cs]) == 1:
					# remove it
					cs.remove_has_clip_listener(self.slot_callbacks[cs])

	def add_slot_listener(self, cs):
		# setting has clip listener
		callback = lambda :self.has_clip_listener(cs)

		# if we don't have a clip slot has clip listener for this clip slot yet
		if not(self.slot_callbacks.has_key(cs)):
			# adding has clip callback to clip slot
			cs.add_has_clip_listener(callback)

			# saving callback for future release
			self.slot_callbacks[cs] = callback

	def add_clip_listener(self, clip):
		# setting callback for clip color change
		color_callback = lambda :self.update_display_clips()

		# if we don't have a clip color change callback for this clip yet
		if not(self.clip_color_callbacks.has_key(clip)):
			# adding clip color change callback
			clip.add_color_listener(color_callback)

			# saving callback for future release
			self.clip_color_callbacks[clip] = color_callback

	def has_clip_listener(self, cs):
		# clip slot has clip listener callback
		if cs.has_clip:
			# add clip listener
			self.add_clip_listener(cs.clip)
		else:
			# update display if clip slot was removed
			self.update_display_clips()

	def session_offset_changed(self):
		# if session component offset changes, update display
		self.update_display_clips()

	def selected_scene_changed(self):
		# if on clip mode update display
		if (self._operation_mode_selector.mode_index==OP1_MODE_CLIP):
			self.update_display_clip_mode()

	def mode_index_changed(self):
		# update display to current mode info
		if (self._operation_mode_selector.mode_index==OP1_MODE_PERFORM):
			self.update_display_perform_mode()
		elif (self._operation_mode_selector.mode_index==OP1_MODE_CLIP):
			self.update_display_clip_mode()
		elif (self._operation_mode_selector.mode_index==OP1_MODE_TRANSPORT):
			self.update_display_transport_mode()
		elif (self._operation_mode_selector.mode_index==OP1_MODE_MIXER):
			self.update_display_mixer_mode()

	def	clear_track_button_callback(self, value):
		# if clear track button was called, reset track
		if (value==127):
			for i in range(len(self.song().tracks)):
				self.song().tracks[i].arm = 0
				self.song().tracks[i].solo = 0
				self.song().tracks[i].mute = 0

			for i in range(len(self.song().return_tracks)):
				self.song().tracks[i].solo = 0
				self.song().tracks[i].mute = 0

	def clear_return_track_assignment(self, strip):
		# clear return track assingments
		strip.set_volume_control(None)
		strip.set_pan_control(None)
		strip.set_mute_button(None)
		strip.set_solo_button(None)
	
	def clear_track_assignment(self, strip):
		# clear track assignments
		strip.set_volume_control(None)
		strip.set_pan_control(None)
		strip.set_mute_button(None)
		strip.set_solo_button(None)
		strip.set_arm_button(None)

	def clear_tracks_assigments(self):
		# for all normal tracks, clear assignments
		for i in range(NUM_TRACKS):
			strip = self._mixer.channel_strip(i)
			if (strip!=None):
				self.clear_track_assignment(strip)

		# for all return tracks, clear assignments
		for i in range(2):
			return_strip = self._mixer.return_strip(i)
			if (return_strip!=None):
				self.clear_return_track_assignment(return_strip)

	def selected_track_changed(self):
		# if on mixer mode update display
		if (self._operation_mode_selector.mode_index==OP1_MODE_MIXER):
			self.update_display_mixer_mode()

		# clear track assignments
		self.clear_tracks_assigments()

		# getting selected strip
		self._channel_strip = self._mixer.selected_strip()

		# perform track assignments 
		self._channel_strip.set_volume_control(EncoderElement(MIDI_CC_TYPE, CHANNEL, OP1_ENCODER_1, Live.MidiMap.MapMode.relative_two_compliment))
		self._channel_strip.set_pan_control(EncoderElement(MIDI_CC_TYPE, CHANNEL, OP1_ENCODER_2, Live.MidiMap.MapMode.relative_two_compliment))

		# setting a tuple of encoders to control sends
		send_controls = EncoderElement(MIDI_CC_TYPE, CHANNEL, OP1_ENCODER_3, Live.MidiMap.MapMode.relative_two_compliment), EncoderElement(MIDI_CC_TYPE, CHANNEL, OP1_ENCODER_4, Live.MidiMap.MapMode.relative_two_compliment),

		# setting send encoders
		self._channel_strip.set_send_controls(tuple(send_controls))

		# setting solo button
		self._channel_strip.set_solo_button(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_SS6_BUTTON))

		# if track can be armed, set arm button
		if (self._channel_strip._track.can_be_armed):
			self._channel_strip.set_arm_button(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_SS7_BUTTON))

		# if track is no master, set mute button
		if (self._channel_strip._track!=self.song().master_track):
			self._channel_strip.set_mute_button(ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_SS5_BUTTON))


	def browser_toggle_button_callback(self, value):
		if (value==127):
			if (self.session_visible):
				if (self.session_browser_visible==True):
					self.session_browser_visible=False
					self.app.view.hide_view("Browser")
				else:
					self.session_browser_visible=True
					self.app.view.show_view("Browser")

			if (self.arrange_visible):
				if (self.arrange_browser_visible==True):
					self.arrange_browser_visible=False
					self.app.view.hide_view("Browser")
				else:
					self.arrange_browser_visible=True
					self.app.view.show_view("Browser")

	def back_to_arranger_button_callback(self, value):
		if (value==127):
			self.song().back_to_arranger = False

	def mainview_toggle_button_callback(self, value):
		if (value==127):
			if (self.session_visible==True):
				self.session_visible=False
				self.arrange_visible=True
				self.app.view.show_view("Arranger")
				self.arrange_browser_visible = self.app.view.is_view_visible("Browser");
			else:
				self.session_visible=True
				self.arrange_visible=False
				self.app.view.show_view("Session")
				self.session_browser_visible = self.app.view.is_view_visible("Browser");

	def detailview_toggle_button_callback(self, value):
		if (value==127):
			if (self.detail_visible==True):
				self.detail_visible=False
				self.app.view.hide_view("Detail")
			else:
				self.detail_visible=True
				self.app.view.show_view("Detail")

	def write_text(self, msg):
		text_list = []
		sequence = ()
		
		text_list.append(len(msg.strip()))
		
		for i in msg.strip():
   			text_list.append(ord(i))
   		
   		sequence = self.text_start_sequence + tuple(text_list) + self.text_end_sequence
		
		self._send_midi(sequence)

	def suggest_input_port(self):
		return "OP-1 Midi Device"

	def suggest_output_port(self):
		return "OP-1 Midi Device"

	def update_display_perform_mode(self):
		self.write_text("perform\rmode")

	def reset_display_clips(self):
		count = 0
		colors = []
		length = []
		sequence = ()
		
		for i in range (NUM_TRACKS):
			count+=1

			colors.append(0x00)
			colors.append(0x00)
			colors.append(0x00)

		length.append(count)
		sequence = self.text_color_start_sequence + tuple(length) + tuple(colors) + self.text_end_sequence
		self._send_midi(sequence)

	def update_display_clips(self):
		#self.log("UPDATING DISPLAY CLIPS")
		count = 0
		colors = []
		length = []
		sequence = ()
		
		tracks_len = len(self.song().tracks)-self._session._track_offset

		if (tracks_len>NUM_TRACKS):
			tracks_len = NUM_TRACKS

		for i in range (tracks_len):
			count+=1

			clip_slot = self._session.scene(0).clip_slot(i)
			
			if (clip_slot!=None):
				if (clip_slot.has_clip()!=False):
					clip_color = clip_slot._clip_slot.clip.color
					colors.append(((clip_color>>16)&0x000000ff)>>1)
					colors.append(((clip_color>>8)&0x000000ff)>>1)
					colors.append((clip_color&0x000000ff)>>1)
				else:
					colors.append(0x00)
					colors.append(0x00)
					colors.append(0x00)
			else:
				colors.append(0x00)
				colors.append(0x00)
				colors.append(0x00)

		length.append(count)
		sequence = self.text_color_start_sequence + tuple(length) + tuple(colors) + self.text_end_sequence
		self._send_midi(sequence)

	def update_display_clip_mode(self):
		self.write_text("sel. scene\r" + str(self.song().view.selected_scene.name.lower().strip()))

	def update_display_transport_mode(self):
		song_time = str(self.song().get_current_beats_song_time())
		self.write_text("song pos.\r" + song_time[:len(song_time)-4])

	def update_display_mixer_mode(self):
		self.write_text("sel. track\r" + str(self.song().view.selected_track.name.lower()))

	def update_display(self):
		if not(self.device_connected):
			if (self.retries_count<5):
				self.log("TRYING OP-1 CONNECTION")
				self.retries_count+=1
				self._send_midi(self.id_sequence)
				time.sleep(1)

		# if in transport mode, update display with song position
		if (self._operation_mode_selector.mode_index==OP1_MODE_TRANSPORT):
			self.update_display_transport_mode()

		# checking if app current view is session
		if (self.app.view.is_view_visible("Session")):
			# checking if session browser state is diferent from the internal
			if (self.session_browser_visible != self.app.view.is_view_visible("Browser")):
				self.session_browser_visible = self.app.view.is_view_visible("Browser")

		# checking if app current view is arrange
		if (self.app.view.is_view_visible("Arranger")):
			# checking if arrange browser state is diferent from the internal
			if (self.arrange_browser_visible != self.app.view.is_view_visible("Browser")):
				self.arrange_browser_visible = self.app.view.is_view_visible("Browser")

		# checking if app current view is detail
		if (self.app.view.is_view_visible("Detail")):
			# checking if detail state is diferent from the internal
			if (self.detail_visible != self.app.view.is_view_visible("Detail")):
				self.detail_visible = self.app.view.is_view_visible("Detail")

	def refresh_state(self):
		self.log("REFRESH STATE")
		self.retries_count = 0
		self.device_connected = False

	def build_midi_map(self, midi_map_handle):
		#self.log("BUILD MIDI MAP")

		assert (self._suppress_requests_counter == 0)
		self._in_build_midi_map = True
		self._midi_map_handle = midi_map_handle
		self._forwarding_registry = {}
		for control in self.controls:
			if isinstance(control, InputControlElement):
				control.install_connections()
		self._midi_map_handle = None
		self._in_build_midi_map = False
		if (self._pad_translations != None):
			self._c_instance.set_pad_translation(self._pad_translations)

		# remove clip listeners
		self.rem_clip_slot_listeners()
		
		# add clip listeners
		self.add_clip_slot_listeners()
		
		# update display
		self.update_display_clips()
		
	def log(self, msg):
		self.c_instance.log_message("[TE OP-1] " + msg)

	def disconnect(self):
		# removing clip slots listeners
		self.rem_clip_slot_listeners()

		# removing value listener for track changed
		self.song().view.remove_selected_track_listener(self.selected_track_changed)

		# removing value listener for scene changed
		self.song().view.remove_selected_scene_listener(self.selected_scene_changed)

		# removing value listener for operation mode index
		self._operation_mode_selector.remove_mode_index_listener(self.mode_index_changed)

		# removing global transport assignments
		self._transport.set_punch_buttons(None, None)
		self._transport.set_loop_button(None)
		self._transport.set_overdub_button(None)
		self._transport.set_record_button(None)
		self._transport.set_play_button(None)
		self._transport.set_stop_button(None)  
		self._transport.set_metronome_button(None)  
		self._transport.set_tap_tempo_button(None)

		# removing global session assignments
		self._session.set_scene_bank_buttons(None, None)
		
		# removing misc listeners
		self.browser_toggle_button.remove_value_listener(self.browser_toggle_button_callback)
		self.mainview_toggle_button.remove_value_listener(self.mainview_toggle_button_callback)
		self.detailview_toggle_button.remove_value_listener(self.detailview_toggle_button_callback)
		self.clear_track_button.remove_value_listener(self.clear_track_button_callback)
		self.back_to_arranger_button.remove_value_listener(self.back_to_arranger_button_callback)
		
		# sending special ableton mode disable sequence
		self._send_midi(self.disable_sequence)
		
		# disconnecting control surface
		ControlSurface.disconnect(self)
		
		self.log("DISCONNECTED")


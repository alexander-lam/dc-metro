import time

import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrix import Matrix

from config import config


class TrainBoard:
	"""
		get_new_data is a function that is expected to return an array of dictionaries like this:

		[
			{
				'line_color': 0xFFFFFF,
				'destination': 'Dest Str',
				'arrival': '5'
			}
		]
	"""
	def __init__(self, get_new_data):
		self.get_new_data = get_new_data
		
		self.display = Matrix().display

		self.parent_group = displayio.Group()
		# An empty group we swap in to blank the screen for the "off" setting,
		# without tearing down parent_group's labels/state.
		self.blank_group = displayio.Group()

		self.heading_label = Label(config['font'], anchor_point=(0,0), anchored_position=(0,0))
		self.heading_label.color = config['heading_color']
		self.heading_label.text=config['heading_text']
		self.parent_group.append(self.heading_label)

		self.trains = []
		for i in range(config['num_trains']):
			self.trains.append(Train(self.parent_group, i))

		self.is_on = True
		self.display.root_group = self.parent_group

	def refresh(self) -> bool:
		if not self.is_on:
			return

		print('Refreshing train information...')
		train_data = self.get_new_data()
		
		if train_data is not None:
			print('Reply received.')
			for i in range(config['num_trains']):
				if i < len(train_data):
					train = train_data[i]
					self._update_train(i, train['line_color'], train['destination'], train['arrival'])
				else:
					self._hide_train(i)
			
			print('Successfully updated.')
		else:
			print('No data received. Clearing display.')

			for i in range(config['num_trains']):
				self._hide_train(i)

	def turn_off(self):
		"""Blanks the matrix. Cheap and reversible - state underneath is untouched."""
		self.is_on = False
		self.display.root_group = self.blank_group

	def turn_on(self):
		"""Shows the train board again (e.g. after turn_off() or show_message())."""
		self.is_on = True
		self.display.root_group = self.parent_group

	def show_message(self, text: str, duration: float = None):
		"""Blocks for `duration` seconds showing a centered message, wrapped
		onto multiple lines if it's too wide for the matrix, then leaves the
		display on that message - call turn_on()/turn_off() afterwards to
		move on to the real content."""
		if duration is None:
			duration = config['switch_message_duration']

		lines = self._wrap_text(text)

		message_group = displayio.Group()

		line_height = config['character_height'] + config['text_padding']
		total_height = line_height * len(lines)
		# Center point of the first line, so the whole block is vertically centered.
		first_line_y = (self.display.height - total_height) // 2 + line_height // 2

		for i, line in enumerate(lines):
			label = Label(
				config['font'],
				anchor_point=(0.5, 0.5),
				anchored_position=(self.display.width // 2, first_line_y + i * line_height),
			)
			label.color = config['text_color']
			label.text = line
			message_group.append(label)

		self.display.root_group = message_group
		time.sleep(duration)

	def _wrap_text(self, text: str) -> [str]:
		"""Word-wraps text into lines that fit the matrix width, based on the
		fixed-width bitmap font's character width."""
		max_chars = max(1, config['matrix_width'] // config['character_width'])

		if len(text) <= max_chars:
			return [text]

		lines = []
		current_line = ''

		for word in text.split(' '):
			candidate = word if not current_line else current_line + ' ' + word

			if len(candidate) <= max_chars:
				current_line = candidate
				continue

			if current_line:
				lines.append(current_line)
				current_line = ''

			# A single word longer than the whole line still needs a hard split.
			while len(word) > max_chars:
				lines.append(word[:max_chars])
				word = word[max_chars:]
			current_line = word

		if current_line:
			lines.append(current_line)

		return lines

	def _hide_train(self, index: int):
		self.trains[index].hide()

	def _update_train(self, index: int, line_color: int, destination: str, minutes: str):
		self.trains[index].update(line_color, destination, minutes)

class Train:
	def __init__(self, parent_group, index):
		y = (int)(config['character_height'] + config['text_padding']) * (index + 1)

		self.line_rect = Rect(0, y, config['train_line_width'], config['train_line_height'], fill=config['loading_line_color'])
		
		self.destination_label = Label(config['font'], anchor_point=(0,0))
		self.destination_label.anchored_position = (config['train_line_width'] + 2, y)
		self.destination_label.color = config['text_color']
		self.destination_label.text = config['loading_destination_text'][:config['destination_max_characters']]

		self.min_label = Label(config['font'], anchor_point=(0,0))
		self.min_label.anchored_position = (config['matrix_width'] - (config['min_label_characters'] * config['character_width']) + 1, y)
		self.min_label.color = config['text_color']
		self.min_label.text = config['loading_min_text']

		self.group = displayio.Group()
		self.group.append(self.line_rect)
		self.group.append(self.destination_label)
		self.group.append(self.min_label)

		parent_group.append(self.group)

	def show(self):
		self.group.hidden = False

	def hide(self):
		self.group.hidden = True

	def set_line_color(self, line_color: int):
		self.line_rect.fill = line_color

	def set_destination(self, destination: str):
		self.destination_label.text = destination[:config['destination_max_characters']]

	def set_arrival_time(self, minutes: str):
		# Ensuring we have a string
		minutes = str(minutes)
		minutes_len = len(minutes)

		# Left-padding the minutes label
		minutes = ' ' * (config['min_label_characters'] - minutes_len) + minutes

		self.min_label.text = minutes

	def update(self, line_color: int, destination: str, minutes: str):
		self.show()
		self.set_line_color(line_color)
		self.set_destination(destination)
		self.set_arrival_time(minutes)

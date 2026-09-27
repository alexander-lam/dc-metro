# DC Metro Board
import time

import board
import digitalio

from config import config
from train_board import TrainBoard
from metro_api import MetroApi, MetroApiOnFireException

STATIONS = config['stations']
REFRESH_INTERVAL = config['refresh_interval']
BUTTON_POLL_INTERVAL = config['button_poll_interval']

# One extra virtual state past the last station means "screen off".
OFF_INDEX = len(STATIONS)
NUM_STATES = len(STATIONS) + 1

current_index = 0

button_up = digitalio.DigitalInOut(board.BUTTON_UP)
button_up.switch_to_input(pull=digitalio.Pull.UP)

button_down = digitalio.DigitalInOut(board.BUTTON_DOWN)
button_down.switch_to_input(pull=digitalio.Pull.UP)

prev_up_pressed = False
prev_down_pressed = False


def is_screen_off() -> bool:
	return current_index == OFF_INDEX


def refresh_trains() -> [dict]:
	station = STATIONS[current_index]
	try:
		return MetroApi.fetch_train_predictions(station['metro_station_code'], station['train_group'])
	except MetroApiOnFireException:
		print('WMATA Api is currently on fire. Trying again later ...')
		return None


def check_buttons() -> bool:
	"""Polls the up/down buttons and advances current_index on a press.
	Returns True if the selection changed since the last check."""
	global current_index, prev_up_pressed, prev_down_pressed

	# Matrix Portal buttons pull the pin low when pressed (pull-up idle high).
	up_pressed = not button_up.value
	down_pressed = not button_down.value

	changed = False

	if up_pressed and not prev_up_pressed:
		current_index = (current_index - 1) % NUM_STATES
		changed = True

	if down_pressed and not prev_down_pressed:
		current_index = (current_index + 1) % NUM_STATES
		changed = True

	prev_up_pressed = up_pressed
	prev_down_pressed = down_pressed

	return changed


train_board = TrainBoard(refresh_trains)

# Negative so the very first loop iteration triggers an immediate refresh.
last_refresh = -REFRESH_INTERVAL

while True:
	if check_buttons():
		if is_screen_off():
			print('Turning screen off.')
			train_board.show_message(config['off_message_text'])
			train_board.turn_off()
		else:
			station = STATIONS[current_index]
			print('Switched to station: {}'.format(station['name']))
			train_board.show_message(station['name'])
			train_board.turn_on()
			train_board.refresh()
		last_refresh = time.monotonic()
	elif not is_screen_off() and time.monotonic() - last_refresh >= REFRESH_INTERVAL:
		train_board.refresh()
		last_refresh = time.monotonic()

	time.sleep(BUTTON_POLL_INTERVAL)

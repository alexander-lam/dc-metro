import os

from adafruit_bitmap_font import bitmap_font

config = {
	#########################
	# Metro Configuration   #
	#########################

	# List of stations you can cycle through with the up/down buttons.
	# Pressing "down" past the last one turns the screen off; pressing
	# "up" from the first one wraps back to "off" too.
	# 'name' is shown in the popup when you switch to that station, and in
	# the serial console log.
	'stations': [
		{
			'name': 'McPherson Square West',
			'metro_station_code': 'C02',
			'train_group': '2',
		},
		{
			'name': 'McPherson Square East',
			'metro_station_code': 'C02',
			'train_group': '1',
		},
		{
			'name': 'Mt Vernon Square South',
			'metro_station_code': 'E01',
			'train_group': '2',
		},
		{
			'name': 'Mt Vernon Square North',
			'metro_station_code': 'E01',
			'train_group': '1',
		},
		{
			'name': 'Metro Center Red Line West',
			'metro_station_code': 'A01',
			'train_group': '2',
		},
		{
			'name': 'Metro Center Red Line East',
			'metro_station_code': 'A01',
			'train_group': '1',
		},
	],

	# API Key for WMATA
	'metro_api_key': os.getenv('METRO_API_KEY'),

	#########################
	# Other Values You      #
	# Probably Shouldn't    #
	# Touch                 #
	#########################
	'metro_api_url': 'https://api.wmata.com/StationPrediction.svc/json/GetPrediction/',
	'metro_api_retries': 2,
	'refresh_interval': 5, # 5 seconds is a good middle ground for updates, as the processor takes its sweet ol time
	'button_poll_interval': 0.05, # how often (in seconds) to check the up/down buttons
	'switch_message_duration': 1.0, # how long (in seconds) the "switching to..." popup stays up
	'off_message_text': 'Off',

	# Display Settings
	'matrix_width': 64,
	'num_trains': 3,
	'font': bitmap_font.load_font('lib/5x7.bdf'),

	'character_width': 5,
	'character_height': 7,
	'text_padding': 1,
	'text_color': 0xFF7500,

	'loading_destination_text': 'Loading',
	'loading_min_text': '---',
	'loading_line_color': 0xFF00FF, # Something something Purple Line joke

	'heading_text': 'LN DEST   MIN',
	'heading_color': 0xFF0000,

	'train_line_height': 6,
	'train_line_width': 2,

	'min_label_characters': 3,
	'destination_max_characters': 9,
}

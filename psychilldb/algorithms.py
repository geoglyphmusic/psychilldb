KeyCycle = {'C Major': 1, 'A Minor': 1, 'G Major': 2, 'E Minor': 2, 'D Major': 3, 'B Minor': 3,
					'A Major': 4, 'F#/Gb Minor': 4, 'E Major': 5, 'C#/Db Minor': 5,
					'B Major': 6, 'G#/Ab Minor': 6, 'F#/Gb Major': 7, 'D#/Eb Minor': 7,
					'C#/Db Major': 8, 'A#/Bb Minor': 8, 'G#/Ab Major': 9, 'F Minor': 9,
					'D#/Eb Major': 10, 'C Minor': 10, 'A#/Bb Major': 11, 'G Minor': 11,
					'F Major': 12, 'D Minor': 12}

def similarity(self_energy, self_key, other_energy, other_key):
	energy_difference = abs(self_energy - other_energy)
	self_key_index = KeyCycle[self_key]
	other_key_index = KeyCycle[other_key]
	key_difference = abs(self_key_index - other_key_index)
	if key_difference > 6:
		key_difference = 12 - key_difference
	similarity = energy_difference + key_difference
	return similarity
	

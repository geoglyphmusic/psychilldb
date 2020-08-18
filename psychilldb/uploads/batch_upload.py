import sqlalchemy
from pyexcel_ods3 import get_data
from psychilldb import db, Track

Data = get_data("batch_upload.ods", start_row=1, start_column=0)
ActiveData = Data['Sheet1']

for item in ActiveData:
	item_exists = Track.query.filter_by(artist=item[0], album=item[1], title=item[2]).first()
	if item_exists:
		print(item[0] + ' - ' + item[2] + ' - is already in the database.')
	else:
		track = Track(artist=item[0], album=item[1], title=item[2],	year=item[3], tempo=item[4], key=item[5], energy=item[6])
		if track.tempo >= 130:
			track.tempo = track.tempo/2
		db.session.add(track)
		db.session.commit()
		print(item[0] + ' - ' + item[2] + ' - uploaded.')

	
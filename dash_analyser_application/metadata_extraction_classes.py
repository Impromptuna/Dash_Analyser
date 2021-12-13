from os import system, remove
from csv import writer, reader
from abc import ABC, abstractmethod

class MetadataExtractor(ABC):
	"""An abstract class defining classes which have a metadata extraction method"""
	def __init__(self, video: str, temp_directory: str):
		self.video = video
		self.temp_directory = temp_directory

	@abstractmethod
	def extract_metadata(self, input_directory:str):
		#An abstract method representing a method to extract metadata using exiftool
		pass

class GPSMetadataExtractor(MetadataExtractor):

	"""Handles the gps metadata for a video"""
	
	def extract_metadata(self, input_directory:str):
		system(f'exiftool  -ee -csv -p "$GPSSpeed, $GPSSpeedRef, $GPSLatitude, $GPSLongitude" -r -n {input_directory}\\{self.video} >> {self.temp_directory}\\{self.video[0:-4]}_gpsdata.csv')
		print(f"gps data done for {self.video}")
		self.trim_data()

	def trim_data(self):
		#removes rows in the exiftool csv output for gpsdata which can cause errors later in the code
		with open(f"{self.temp_directory}\\{self.video[0:-4]}_gpsdata.csv", "r") as csvfile_read, open(f"{self.temp_directory}\\{self.video[0:-4]}_gpsdata_converted.csv", "w", newline="") as csvfile_write:
			cvs_writer=writer(csvfile_write)
			for row in reader(csvfile_read):
				if set(row).intersection(["SourceFile"]):
					continue
				else:
					cvs_writer.writerow(row)
		remove(f"{self.temp_directory}\\{self.video[0:-4]}_gpsdata.csv")


class FileInfoMetadataExtractor(MetadataExtractor):

	"""Handles the file information metadata for a video"""

	def extract_metadata(self, input_directory:str):
		system(f'exiftool -ee -FileType -filesize -MIMEType -d %d-%m-%Y" "%H:%M:%S -createDate -Duration -csv  {input_directory}\\{self.video} >> {self.temp_directory}\\{self.video[0:-4]}_fileinfo.csv')
		print(f"file info done for {self.video}")

class TimeMetadataExtractor(MetadataExtractor):

	"""Handles the temporal metadata for a video"""

	def extract_metadata(self, input_directory:str):
		system(f'exiftool -ee -d %d-%m-%Y" "%H:%M:%S -gpsdatetime -s -s -s {input_directory}\\{self.video} >> {self.temp_directory}\\{self.video[0:-4]}_timedata.csv')
		print(f"time data done for {self.video}")
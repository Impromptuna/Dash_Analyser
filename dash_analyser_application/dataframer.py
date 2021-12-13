from pandas import read_csv, to_datetime, concat, DataFrame
from os import listdir
from geopy import distance
from folium.plugins import BeautifyIcon, MeasureControl, Draw
from datetime import timedelta, datetime
from dash_analyser_application.mapper_functions import ExclusionZone


class MetaDataFrames:

	"""
	Manages GPS, temporal, and file information for a video file
	Takes in a list of metadata output files containing one of each of the following file types:
	- A GPS data file
	- A temporal data file
	- A file containing information about the original video file
	Also takes in a list of ExclusionZone objects, and a temp directory for output files
	"""

	def __init__(self, video_metadata_csvs: list, exclusion_zones: list, temp_dir: str):
		self.file_info_df = read_csv(f"{temp_dir}\\{video_metadata_csvs[0]}")
		file_path = self.file_info_df["SourceFile"].iloc[0]
		self.video_name = file_path[file_path.rfind("/")+1:]
		gps_df = read_csv(f"{temp_dir}\\{video_metadata_csvs[1]}", names=["Speed", "Speed Reference", "GPS Latitude", "GPS Longitude"])
		time_df = read_csv(f"{temp_dir}\\{video_metadata_csvs[2]}", names=["DateTime"])
		
		self.gps_df=gps_df.join(time_df)

		self.exclusion_zones = exclusion_zones

	def process_gps_and_time_dataframe(self):

		"""Processes the combined GPS and temporal dataframe to remove excess rows, create a combined (latitude, longitude) column, and convert the datetime column to a datetime object"""

		self.trim_dataframes()
		self.combine_lat_long_columns()
		self.convert_to_datetime()

	def process_file_info_dataframe(self):

		"""Processes the file info dataframe to add average speed, maximum speed, and speed reference columns"""

		self.add_average_speed()
		self.add_max_speed()
		self.add_speed_reference()

	def trim_dataframes(self):
		#Removes rows from merged dataframe which contain impossible coordinates
		indexes=self.gps_df[self.gps_df["GPS Latitude"]==-180].index
		self.gps_df.drop(indexes, inplace=True)
		self.gps_df.reset_index(drop=True, inplace=True) #resets row numbering - if this isn't done the row numbers will have gaps if data is removed

	def combine_lat_long_columns(self):
		#Combine the latitude and longitude columns into one column
		self.gps_df["Latitude, Longitude"]=list(self.gps_df[["GPS Latitude", "GPS Longitude"]].to_records(index=False))

	def convert_to_datetime(self):
		#converts the date and time columns in the dataframe to datetime objects, allowing them to be used for other functions
		self.gps_df["DateTime"]=to_datetime(arg = self.gps_df["DateTime"], format = "%d-%m-%Y %H:%M:%S")
		self.file_info_df["CreateDate"]=to_datetime(arg = self.file_info_df["CreateDate"], format = "%d-%m-%Y %H:%M:%S")

	def add_label_for_speed_chart(self):
		#Adds a column to the dataframe to identify the source of the data. This is done to make a legend for the speed chart.
		self.gps_df["DataSource"] = len(self.gps_df.index) * ["Extracted metadata using exiftool"]

	def add_average_speed(self):
		#Calculates the average speed for the video and adds it to the file info dataframe
		self.file_info_df["AverageSpeed"] = round(self.gps_df["Speed"].mean(), 2)

	def add_max_speed(self):
		#Calculates the max speed for the video and adds it to the file info dataframe
		self.file_info_df["MaxSpeed"] = round(self.gps_df["Speed"].max(), 2)

	def add_speed_reference(self):
		#Gets the speed reference for the video
		speed_ref = self.gps_df.at[0, "Speed Reference"]
		if speed_ref == " K":
			self.file_info_df["SpeedRef"] = "kmph"
		else:
			self.file_info_df["SpeedRef"] = "mph"

def make_video_csv_list(metadata_extraction_directory: str) -> list:
	#Returns a list containing lists of three files. Each set of three files combined contains the metadata for one video being analysed.
	files = listdir(metadata_extraction_directory)
	video_csv_list = [files[x:x+3] for x in range(0, len(files), 3)]
	return video_csv_list

def make_video_metadata_handlers(video_metadata_csv_list: list, exclusion_zones: list, temp_dir: str) -> list:
	"""
	Takes in a list of strings which represents the output csv files from the metadata extraction, a list of ExclusionZone instances, 
	and a temporary output directory.
	Makes and returns a list of MetaDataFrames instances to handle the data, and calls the functions necessary to populate the dataframes.
	"""
	video_metadata_handler_list = [MetaDataFrames(video_metadata_csvs, exclusion_zones, temp_dir) for video_metadata_csvs in video_metadata_csv_list]
	for video_metadata_handler in video_metadata_handler_list:
		video_metadata_handler.process_gps_and_time_dataframe()
		video_metadata_handler.process_file_info_dataframe()
		video_metadata_handler.add_label_for_speed_chart()
	return video_metadata_handler_list

def make_speed_dataframe(video_list: list) -> DataFrame:
	"""Takes in a list of video data handlers - either ocr or metadata, and returns a dataframe containing the speeds and datetimes in the list"""
	speed_data = concat([video.gps_df[["Speed", "DateTime", "DataSource"]] for video in video_list])
	return speed_data

def find_final_point_in_route(video_list: list) -> tuple:
	"""Takes in a list of video data handlers - either ocr or metadata, and returns the final available coordinate"""
	final_point = video_list[-1].gps_df["Latitude, Longitude"].iloc[-1]
	return final_point
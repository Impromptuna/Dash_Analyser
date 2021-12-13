from pandas import DataFrame

class TimelineBar:
	"""
	Represents the data for a single video on the timeline chart
	Takes in two dataframes containing geospatial and file information
	"""
	def __init__(self, gps_df:DataFrame, file_info_df:DataFrame):

		self.video_start = gps_df["DateTime"].iloc[0] 
		self.video_end = gps_df["DateTime"].iloc[-1]

		if type(file_info_df["Present in Exclusion Zones"].iloc[0]) == list:
			self.exclusion_zones = [exclusion_zone for exclusion_zone in file_info_df["Present in Exclusion Zones"].iloc[0]]
		else:
			self.exclusion_zones = file_info_df["Present in Exclusion Zones"].iloc[0]
		
		self.date = self.video_start.date()
		self.filepath = file_info_df["SourceFile"].iloc[0]
		self.average_speed = f'{file_info_df["AverageSpeed"].iloc[0]} {file_info_df["SpeedRef"].iloc[0]}'
		self.max_speed = f'{file_info_df["MaxSpeed"].iloc[0]} {file_info_df["SpeedRef"].iloc[0]}'
		self.filetype = file_info_df["FileType"].iloc[0]
		self.filesize = file_info_df["FileSize"].iloc[0]

	def make_dictionary_for_bar(self):
		"""
		Uses the data from the input dataframes to generate a dictionary representing a bar in a plotly.express timeline
		"""
		self.bar_data = dict(
			FilePath = self.filepath,
			Date = self.date.strftime("%d/%m/%Y"), 
			Start = self.video_start.strftime("%Y-%m-%d %H:%M:%S"), 
			End = self.video_end.strftime("%Y-%m-%d %H:%M:%S"), 
			ExclusionZones = self.exclusion_zones,
			AverageSpeed = self.average_speed,
			MaxSpeed = self.max_speed,
			FileType = self.filetype,
			FileSize = self.filesize
			)





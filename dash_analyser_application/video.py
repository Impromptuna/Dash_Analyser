from cv2 import VideoCapture, imwrite, CAP_PROP_POS_MSEC, imread, cvtColor, COLOR_BGR2GRAY
from pytesseract import pytesseract, image_to_string
from os import system, listdir
from pandas import DataFrame, to_datetime, to_numeric
from datetime import datetime
from shutil import rmtree
from pickle import dump, load
from abc import ABC, abstractmethod
from dash_analyser_application.convert_coord_to_decimal import dms2dec

pytesseract.tesseract_cmd = 'Tesseract-OCR\\tesseract'

class Video(ABC):

	"""	
	A class which forms the base for classes which can process videos from various kinds of dashcams.
	"""
	
	def __init__(self, video_name:str, temp_directory:str, video_directory:str):
		self.video_name=video_name
		self.output_folder=f"{temp_directory}\\{video_name}"
		self.video_file=f"{video_directory}\\{video_name}"

	@abstractmethod
	def get_image_crop_indices(self):
		pass

	def extract_frames(self):
		#Goes through the video frame by frame using cv2, extracting one frame per second and saving that frame as a .jpg
		system(f"mkdir {self.output_folder}")
		vidcap = VideoCapture(self.video_file)
		success,image = vidcap.read()
		count = 0
		while success:
			vidcap.set(CAP_PROP_POS_MSEC, (count*1000))
			#the below if condition causes files with a single digit count to be saved with a double digit number. This keeps the extracted frames in order.
			if count < 10:
				frame_name = f"{self.video_name[0:-4]}_frame00{count}.jpg"
			elif count <100: 
				frame_name = f"{self.video_name[0:-4]}_frame0{count}.jpg"
			else:
				frame_name = f"{self.video_name[0:-4]}_frame{count}.jpg"


			print(frame_name)

			imwrite(f"{self.output_folder}\\{frame_name}", cvtColor(image[self.y_lower:self.y_upper, self.x_lower:self.x_upper], COLOR_BGR2GRAY))

			success,image = vidcap.read()
			count += 1

	@abstractmethod
	def make_start_string(self):
		pass

	def trim_watermark_output(self):
		"""
		Calls make_start_string and uses the output to clear any junk data from the watermark
		"""
		self.make_start_string()
		for i, watermark in enumerate(self.watermarks):
			start_index = watermark.find(self.start_string)
			trimmed_watermark = watermark[start_index+len(self.start_string):-2]
			if trimmed_watermark[0] == " ":
				trimmed_watermark = trimmed_watermark[1:]
			self.watermarks[i] = trimmed_watermark

	def read_watermarks(self):
		#Goes through the saved frames of the video one by one and uses pytesseract to read the watermarks
		self.frames=listdir(self.output_folder)
		self.watermarks=[]
		for frame in self.frames:
			image = imread(f'{self.output_folder}\\{frame}')
			custom_config = r'--oem 3 --psm 6'
			tesseract_output = pytesseract.image_to_string(image, config=custom_config)
			print(f"Read {frame}")
			self.watermarks.append(tesseract_output)

	def split_watermark_output(self):
		#Splits the string output from the pytesseract read into individual strings separated by spaces.
		for i, watermark in enumerate(self.watermarks):
			self.watermarks[i] = watermark.split(" ")

	@abstractmethod
	def process_watermarks(self):
		"""
		This method will be called to call multiple other methods. 
		The end result should be that the watermarks are in a format which can be placed in a DataFrame.
		"""
		pass

	@abstractmethod
	def combine_date_and_time(self):
		#Combines the date and time fields read from the dashcam video watermark
		pass

	def remove_misreads_and_missing_coords(self):
		#Sometimes, the OCR data picks up erroneous data in the middle of the watermark.
		#If this occurs, the data will have a different number of entries than the expected number.
		#As well as this, sometimes the watermark has no speed or coordinates due to a loss of satellite connection.
		#Thus, any rows of data which are not 5 entries long are removed, as this is the expected number after the preceeding processing.
		self.watermarks = [watermark for watermark in self.watermarks if len(watermark) == 5]

	def make_watermark_df(self):
		#Makes a dataframe containing the datetime and GPS data extracted from the watermarks
		self.gps_df = DataFrame(
			data = self.watermarks, 
			columns = [
				"DateTime", 
			   	"Latitude", 
			   	"Longitude", 
			   	"Speed", 
			   	"Speed Ref"
			   	]
			   	)

	def convert_df(self):
		#ensures each column of the dataframe is the expected type
		self.gps_df["DateTime"] = to_datetime(self.gps_df["DateTime"], errors = "coerce")
		self.gps_df["Latitude"] = to_numeric(self.gps_df["Latitude"], errors = "coerce")
		self.gps_df["Longitude"] = to_numeric(self.gps_df["Longitude"], errors = "coerce")
		self.gps_df["Speed"] = to_numeric(self.gps_df["Speed"], errors = "coerce")

	def remove_nans(self):
		#Removes any rows from the dataframe which could not be properly converted by convert_df()
		self.gps_df.dropna(inplace=True)

	def add_dataframe_source_label(self):
		#When making a speed chart in altair with multiple lines, in order to make a legend the dataframe needs a column to identify it by
		self.gps_df["DataSource"] = len(self.gps_df.index) * ["Read metadata from watermarks using pytesseract"]

	def make_points(self):
		self.gps_df["Latitude, Longitude"] = list(self.gps_df[["Latitude", "Longitude"]].to_records(index=False))

	def make_file_info_df(self):
		#Make a dataframe containing file information fields that are the same as for the file information extracted using ExifTool.
		#This allows this object to later be passed directly into the timeline making function
		file_info_dictionary = dict(
			SourceFile = self.video_file, 
			FileType = self.video_file[-4:], 
			FileSize = "Unknown - this data was extracted using OCR", 
			MIMEType = "Unknown - this data was extracted using OCR", 
			CreateDate = str(self.gps_df["DateTime"].iloc[0]), 
			Duration = str(self.gps_df["DateTime"].iloc[-1] - self.gps_df["DateTime"].iloc[0]),
			MaxSpeed = round(self.gps_df["Speed"].max(), 2),
			AverageSpeed = round(self.gps_df["Speed"].mean(), 2),
			SpeedRef = self.gps_df["Speed Ref"].iloc[0]
			)
		self.file_info_df = DataFrame(data = [file_info_dictionary])




class GARMINVideo(Video):
	"""
		This class is used to process a video from a Garmin dashcam
	"""
	def get_image_crop_indices(self):
		self.y_lower=685
		self.y_upper=710
		self.x_lower=0
		self.x_upper=1000

	def make_start_string(self):
		#generate the string which indicates the start of useful data in the watermark
		self.start_string = "GARMIN"

	def trim_watermark_output(self):
		#Only include data after GARMIN and before the line break character used by pystesseract.
		for i,watermark in enumerate(self.watermarks):
			start_index = watermark.find("GARMIN")
			trimmed_watermark = watermark[start_index+7:-2].strip()
			self.watermarks[i] = trimmed_watermark

	def convert_Os_to_0s(self):
		#Converts Os to 0s after the OCR read in the speed column. This was a common bug for this model of dashcam.
		for watermark in self.watermarks:
			try:
				if watermark[-2] == "O":
					watermark[-2] = "0"
			except:
				continue

	def combine_date_and_time(self):
		#Converts the date and time read by pytesseract from the watermark to a datetime
		for watermark in self.watermarks:
			watermark[0] = watermark[0] + watermark[1] + watermark[2]
			try:
				watermark[0] = datetime.strptime(watermark[0], "%d/%m/%Y%I:%M:%S%p")
			except:
				self.watermarks.remove(watermark) # If the watermark will not convert to a datetime, it has likely been misread by the OCR, so is discarded
			watermark.remove(watermark[1])
			watermark.remove(watermark[1])

	def process_watermarks(self):
		self.combine_date_and_time()

class Nextbase312Video(Video):

	def get_image_crop_indices(self):
		self.y_lower=670
		self.y_upper=705
		self.x_lower=1
		self.x_upper=1240

	def make_start_string(self):
		#generate the string which indicates the start of useful data in the watermark
		self.start_string = "NBDVR312GW"

	def convert_tude_to_decimal(self, tude):
		tude_list = list(tude)
		if tude[0] in ["W", "S"]:
			tude_list[0] = "-"
		else:
			tude_list[0] = ""
		return "".join(tude_list)

	def combine_date_and_time(self, watermark):
		#Converts the date and time read by pytesseract from the watermark to a datetime
		watermark[0] = watermark[0] + watermark[1]
		try:
			watermark[0] = datetime.strptime(watermark[0], "%I:%M:%S%d/%m/%Y")
		except:
			self.watermarks.remove(watermark) # If the watermark will not convert to a datetime, it has likely been misread by the OCR, so is discarded
		watermark.remove(watermark[1])

	def process_watermarks(self):
		for i, watermark in enumerate(self.watermarks):
			watermark.pop(2) #This removes a junk string that gets read in the centre of the watermark for this model of dashcam
			watermark[-1] = self.convert_tude_to_decimal(watermark[-1])
			watermark[-2] = self.convert_tude_to_decimal(watermark[-2])

			#Split the speed from the speed ref
			watermark.insert(3, watermark[2][watermark[2].find("K"):])
			watermark[2] = watermark[2][0:watermark[2].find("K")]

			self.combine_date_and_time(watermark)

			order = [0, 3, 4, 1, 2]
			self.watermarks[i] = [watermark[index] for index in order] #reshuffle order of watermark data to be in the predefined format: datetime, lat, long, speed, speed ref

class MiVueVideo(Video):

	def get_image_crop_indices(self):
		self.y_lower=995
		self.y_upper=1045
		self.x_lower=1570
		self.x_upper=1960

	def make_start_string(self):
		#generate the string which indicates the start of useful data in the watermark
		self.start_string = ""

	def split_watermark_output(self):
		#Splits the string output from the pytesseract read into individual strings separated by newlines and spaces.
		for i, watermark in enumerate(self.watermarks):
			self.watermarks[i] = watermark.split("\n")

		for i, watermark in enumerate(self.watermarks):
			watermark[0] = watermark[0].split(" ")
			watermark[0].append(watermark[-1][2:13] + watermark[-1][0])
			watermark[0].append(watermark[-1][15:] + watermark[-1][14])
			watermark.remove(watermark[-1])
			self.watermarks[i] = watermark[0]

	def process_watermarks(self):
		for i, watermark in enumerate(self.watermarks):
			try:
				watermark[-2] = dms2dec(watermark[-2])
				watermark[-1] = dms2dec(watermark[-1])
			except:
				self.watermarks.remove(watermark)
				print("removed watermark")
			self.combine_date_and_time(watermark)

		for i, watermark in enumerate(self.watermarks):
			try:
				order = [0, 3, 4, 1, 2]
				self.watermarks[i] = [watermark[index] for index in order] #reshuffle order of watermark data to be in the predefined format: datetime, lat, long, speed, speed ref
			except:
				self.watermarks.remove(self.watermarks[i])


	def combine_date_and_time(self, watermark:str):
		#Converts the date and time read by pytesseract from the watermark to a datetime
		watermark[0] = watermark[0] + watermark[1]
		try:
			watermark[0] = datetime.strptime(watermark[0], "%Y/%m/%d%H:%M:%S")
		except:
			self.watermarks.remove(watermark) # If the watermark will not convert to a datetime, it has likely been misread by the OCR, so is discarded
		watermark.remove(watermark[1])


class Nextbase422Video(Video):

	def get_image_crop_indices(self):
		self.y_lower=1350
		self.y_upper=1500
		self.x_lower=1050
		self.x_upper=1980

	def make_start_string(self):
		#generate the string which indicates the start of useful data in the watermark
		self.start_string = ""

	def split_watermark_output(self):
		#Splits the string output from the pytesseract read into individual strings separated by newlines and spaces.
		for i, watermark in enumerate(self.watermarks):
			self.watermarks[i] = watermark.split(" ")

		for watermark in self.watermarks:
			watermark[2]=watermark[2].split("M")
			watermark[2][1] = "K" + watermark[2][1]
			watermark.insert(2, watermark[2][0])
			watermark.insert(3, watermark[3][1])
			watermark.remove(watermark[4])
			if watermark[2]=="O":
				watermark[2]=0
			try:
				watermark[2] = float(watermark[2]) * 1.60934
			except:
				self.watermarks.remove(watermark)

	def process_watermarks(self):
		for i, watermark in enumerate(self.watermarks):
			try:
				watermark[0] = self.get_lat_long_sign(watermark[0])
				watermark[1] = self.get_lat_long_sign(watermark[1])
			except:
				self.watermarks.remove(watermark)
				print("removed watermark")
			self.combine_date_and_time(watermark)

		for i, watermark in enumerate(self.watermarks):
			try:
				order = [4, 0, 1, 2, 3]
				self.watermarks[i] = [watermark[index] for index in order] #reshuffle order of watermark data to be in the predefined format: datetime, lat, long, speed, speed ref
			except:
				self.watermarks.remove(self.watermarks[i])

	def get_lat_long_sign(self, lat_or_long):
		if lat_or_long[0] in ["S", "W"]:
			return "-" + lat_or_long[1:]
		else:
			return lat_or_long[1:]

	def combine_date_and_time(self, watermark):
		#Converts the date and time read by pytesseract from the watermark to a datetime
		watermark[-2] = watermark[-2] + watermark[-1]
		try:
			watermark[-2] = datetime.strptime(watermark[-2], "%H:%M:%S%d/%m/%Y")
		except:
			print("removed watermark at datetime conversion")
			self.watermarks.remove(watermark) # If the watermark will not convert to a datetime, it has likely been misread by the OCR, so is discarded
		watermark.remove(watermark[-1])

def make_video(video_name:str, temp_directory:str, input_dir:str, dashcam_type:str) -> Video:
	"""
	Uses the dashcam type string to determine what Video type to initiate, and returns that video type
	"""
	if dashcam_type == "GARMIN":
		return GARMINVideo(video_name, temp_directory, input_dir)
	elif dashcam_type=="Nextbase 312GW":
		return Nextbase312Video(video_name, temp_directory, input_dir)
	elif dashcam_type=="MiVue":
		return MiVueVideo(video_name, temp_directory, input_dir)
	elif dashcam_type=="Nextbase 422GW":
		return Nextbase422Video(video_name, temp_directory, input_dir)
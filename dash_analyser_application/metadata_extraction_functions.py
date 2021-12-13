from os import listdir, system, remove
from shutil import rmtree
import csv
from abc import ABC, abstractmethod
from dash_analyser_application.metadata_extraction_classes import GPSMetadataExtractor, TimeMetadataExtractor, FileInfoMetadataExtractor

def get_file_list(input_directory: str) -> list:
	"""
	Takes in the input directory containing the subject dashcam videos.
	Lists the directory.
	Returns the list of video files in the directory.
	"""
	video_name_list=[]
	for file in listdir(input_directory):
		if file.endswith(".MP4") or file.endswith(".MOV"):
			video_name_list.append(file)
	return video_name_list

def make_handlers(video_name_list: list, temp_directory: str) -> list:
	#Takes in a list of video names and temp directory, and makes a list of 3 metadata handlers for each video name.
	#Returns the list of metadata handlers
	metadata_handler_list=[]
	for video in video_name_list:
		metadata_handler_list.append(GPSMetadataExtractor(video = video, temp_directory=temp_directory))
		metadata_handler_list.append(TimeMetadataExtractor(video = video, temp_directory=temp_directory))
		metadata_handler_list.append(FileInfoMetadataExtractor(video = video, temp_directory=temp_directory))
	return metadata_handler_list

def extract_metadata_loop(metadata_handler_list: list, input_directory: str):
	#Takes in a list of metadata handlers and calls their extract_metadata() methods
	for metadata_handler in metadata_handler_list:
		metadata_handler.extract_metadata(input_directory)
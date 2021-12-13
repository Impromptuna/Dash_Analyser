from pickle import dump, load
from dash_analyser_application.video import Video


def make_ocr_video_list(video_name_list: list, temp_ocr_directory: str, input_dir: str) -> list:
	"""
	Returns a list of Video instances using a list of video names
	"""
	ocr_video_list = []
	for video_name in video_name_list:
		video = Video(video_name, temp_ocr_directory, input_dir)
		ocr_video_list.append(video)
	return ocr_video_list

def extract_frames(ocr_video_list: list):
	"""
	Calls the extract_frames method for each Video in the list.
	This takes frames out of the video at set intervals and stores them in a temp directory
	"""
	print("Extracting frames...")
	for video in ocr_video_list:
		video.extract_frames()

def read_watermarks(ocr_video_list: list):
	"""
	Reads frames extracted using extract_frames
	"""
	for video in ocr_video_list:
		video.read_watermarks()

def process_watermark_data(ocr_video_list: list):
	"""Calls the necessary methods to process the watermark data for each Video"""
	for video in ocr_video_list:
		video.trim_watermark_output()
		video.split_watermark_output()
		video.convert_to_datetime()
		video.convert_Os_to_0s()
		video.remove_misreads_and_missing_coords()
		video.make_watermark_df()
		video.convert_df()
		video.remove_nans()
		video.make_points()
		video.add_dataframe_source_label()
		video.make_file_info_df()
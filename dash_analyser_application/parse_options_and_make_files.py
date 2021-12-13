from dash_analyser_application.dataframer import make_video_csv_list, make_video_metadata_handlers, make_speed_dataframe, find_final_point_in_route
from dash_analyser_application.metadata_extraction_functions import make_handlers
from dash_analyser_application.video import Video, make_video
import dash_analyser_application.mapper_functions as mapper
import dash_analyser_application.timeline_functions as tl
from os import system, listdir, getcwd
from shutil import rmtree
from pandas import concat
from folium import FeatureGroup, Map
from plotly.express import timeline
from branca.colormap import linear

def remove_temp_directory(temp_directory):
	"""Removes the temp directory"""
	try:
		rmtree(temp_directory)
		print("deleted temp")
	except:
		print("no temp folder to delete")

def make_directories(temp_metadata_directory:str, temp_ocr_directory:str):
	"""Makes temp directories for the tool to use"""
	system(f"mkdir {temp_metadata_directory}")
	system(f"mkdir {temp_ocr_directory}")

def extract_metadata(video_name_list:list, temp_metadata_directory:str, input_directory:str):
	"""
	Takes in a list of video names (list of strings), a temp output directory, and an input directory
	Uses the list of video names and temporary output directory to call a function which initialises a list of metadata extraction classes
	Calls the extract_metadata() method for each metadata extraction class using the input directory
	"""
	metadata_handler_list = make_handlers(video_name_list = video_name_list, temp_directory = temp_metadata_directory)
	for metadata_handler in metadata_handler_list:
		metadata_handler.extract_metadata(input_directory)

def make_metadata_dataframes(temp_metadata_directory:str, exclusion_zones:list) -> list:
	"""
	Takes in the name of a temp output directory (string), and a list of ExclusionZone (mapper_classes.py) instances
	Returns a list of MetaDataFrames (found in dataframer.py) instances
	"""
	video_csv_list = make_video_csv_list(temp_metadata_directory)
	video_metadata_handler_list = make_video_metadata_handlers(video_csv_list, exclusion_zones, temp_metadata_directory)
	return video_metadata_handler_list

def add_data_to_map(video_list: list, routelines: FeatureGroup, start_markers: FeatureGroup, speed_lines: FeatureGroup, routeline_colour: str, colour_map: linear):
	"""
	Takes in either a list of Video (video.py) or MetaDataFrames (dataframer.py) instances, three folium FeatureGroups, and a linear branca colour map.
	Makes a RouteLineMaker (mapper_classes.py) instance for each video in the video list, and uses these instances to add routelines, start markers, and speed lines to a folium Map
	"""
	for video in video_list:
		routeliner = mapper.add_routeline_to_map(
			gps_df = video.gps_df,
			routeline_group = routelines,
			start_marker_group = start_markers,
			colour_line_group = speed_lines)
		routeliner.make_routeline(routeline_colour)
		mapper.add_start_marker_to_map(video.file_info_df, routeliner)
		mapper.add_speedline_to_map(routeliner, colour_map)

def generate_timeline(video_metadata_handler_list: list, timeline_title: str) -> timeline:
	"""
	Takes in either a list of Video (video.py) or MetaDataFrames (dataframer.py) instances and a timeline title; either OCR or extracted metadata
	Returns a plotly.express timeline figure
	"""
	timeline_bar_list = tl.make_timeline_bars(video_metadata_handler_list)
	timeline_dataframe = tl.make_timeline_dataframe(timeline_bar_list)
	timeline_figure = tl.make_timeline_figure(timeline_dataframe, timeline_title)
	tl.configure_timeline_yaxis(timeline_figure)
	return timeline_figure

def add_timeline_to_map(timeline_figure: timeline, average_point: tuple, map_feature_group: FeatureGroup):
	"""
	Takes in a plotly.express timeline figure,  the average coordinate of all videos in the intake, and a folium FeatureGroup
	Uses the average coordinate of all videos in the intake to add the timeline figure to the folium FeatureGroup
	"""
	timeline_html = tl.convert_timeline_to_html(timeline_figure)
	popup=mapper.make_folium_popup_for_timeline(timeline_html)
	timeline_marker = mapper.make_timeline_marker(average_point, popup)
	timeline_marker.add_to(map_feature_group)

def make_exclusion_zones(exclusion_zone_list: list) -> list:
	"""
	Takes in a list of dictionaries representing exclusion zones defined by the user
	Returns a list of ExclusionZone (mapper_classes.py) instances
	"""
	if exclusion_zone_list != []:
		exclusion_zones = 	[mapper.make_exclusion_zone(
			location = exclusion_dictionary["Location"], 
			radius = exclusion_dictionary["Radius"]) 
		   	for exclusion_dictionary in exclusion_zone_list if exclusion_zone_list]
	else:
		exclusion_zones =  []

	return exclusion_zones

def extract_metadata_and_make_dataframers(video_name_list:list, temp_metadata_directory:str, input_directory:str, exclusion_zones:list) -> list:
	"""
	Takes in a list of video names (list of strings), a temp output directory, an input directory, and a list of ExclusionZone (mapper_classes.py) instances
	Calls the extract metadata function to extract metadata from the videos in video_name_list
	Makes MetaDataFrames (dataframer.py) instances for each video, calls methods to populate the dataframes managed by these instances
	Returns a list of the MetaDataFrames instances
	"""
	extract_metadata(video_name_list, temp_metadata_directory, input_directory)# make list of metadata handlers, which then extract metadata
	video_metadata_handler_list = make_metadata_dataframes(temp_metadata_directory, exclusion_zones)
	for video_metadata_handler in video_metadata_handler_list:
		video_metadata_handler.gps_df = mapper.test_exclusion_zones(video_metadata_handler.gps_df, exclusion_zones)
		video_metadata_handler.file_info_df = mapper.add_exclusion_zones_to_file_info(video_metadata_handler.gps_df, video_metadata_handler.file_info_df, exclusion_zones)
	return video_metadata_handler_list

def ocr_option_process(video_name_list:list, temp_ocr_directory:str, input_dir:str, dashcam_type:str) -> list:
	"""
	Takes in a list of video names (list of strings), a temp output directory, an input directory, and a dashcam type
	Uses these to make a Video (video.py) instance for each video in the input directory.
	Calls all the methods for the Video instances, reading the watermarks in each frame.
	Returns a list of the Video instances, which now each store gps and file information dataframes.
	"""
	ocr_video_list = [make_video(video_name, temp_ocr_directory, input_dir, dashcam_type) for video_name in video_name_list]
	for video in ocr_video_list:
		print("\n---------------------------------------------------------------------------------------\n")
		video.get_image_crop_indices()
		print(f"Performing OCR on {video.video_name}")
		video.extract_frames()
		print(f"DONE EXTRACTING FRAMES FOR {video.video_name}")
		video.read_watermarks()
		print(f"DONE READING WATERMARKS FOR {video.video_name}")
		video.trim_watermark_output()
		video.split_watermark_output()
		video.process_watermarks()
		video.remove_misreads_and_missing_coords()
		video.make_watermark_df()
		video.convert_df()
		video.remove_nans()
		video.add_dataframe_source_label()
		video.make_points()
		video.make_file_info_df()
		print(f"DONE PROCESSING WATERMARKS FOR {video.video_name}")
		rmtree(video.output_folder)
	return ocr_video_list



def parse_options(input_dir:str, output_dir:str, options_list:list, exclusion_zones:list, dashcam_type:str):
	"""
	This function is the "main" under-the-hood function for the application.
	Takes in an input directory, output directory, list of options input by the user, list of dictionaries representing exclusion zones, and a dashcam type.
	Parses the list of options, and calls the necessary functions to carry out the user's wishes.
	Once it is finished, the user's desired output files will be in the specified output directory.
	"""
	for option, value in options_list.items():
		options_list[option]=bool(value)
	print(options_list)

	temp_directory = f"{getcwd()}\\temp"
	temp_metadata_directory = f"{temp_directory}\\metadata"
	temp_ocr_directory = f"{temp_directory}\\ocr"

	video_name_list = listdir(input_dir) # make a list of input videos
	remove_temp_directory(temp_directory)
	make_directories(temp_metadata_directory, temp_ocr_directory)

	if options_list["ExtractMetadata"]:
		video_metadata_handler_list = extract_metadata_and_make_dataframers(video_name_list, temp_metadata_directory, input_dir, exclusion_zones)
		print(video_metadata_handler_list)
		speed_data = make_speed_dataframe(video_metadata_handler_list)
		final_point = find_final_point_in_route(video_metadata_handler_list)
		large_points_df = concat([video_metadata_handler.gps_df[["GPS Latitude", "GPS Longitude"]] for video_metadata_handler in video_metadata_handler_list])
		mean_point = (large_points_df["GPS Latitude"].mean(), large_points_df["GPS Longitude"].mean())
		median_point = (large_points_df["GPS Latitude"].mean(), large_points_df["GPS Longitude"].mean())

	if options_list["OCR"]:
		ocr_video_list = ocr_option_process(video_name_list, temp_ocr_directory, input_dir, dashcam_type)
		system(f"mkdir {output_dir}\\ocr")
		for video in ocr_video_list:
			video.gps_df = mapper.test_exclusion_zones(video.gps_df, exclusion_zones)
			video.file_info_df = mapper.add_exclusion_zones_to_file_info(video.gps_df, video.file_info_df, exclusion_zones)
			print("Done with just OCR")
		ocr_speed_data = make_speed_dataframe(ocr_video_list)
		ocr_final_point = find_final_point_in_route(ocr_video_list)
		ocr_large_points_df = concat([video.gps_df[["Latitude", "Longitude"]] for video_metadata_handler in ocr_video_list])
		ocr_mean_point = (ocr_large_points_df["Latitude"].mean(), ocr_large_points_df["Longitude"].mean())
		ocr_median_point = (ocr_large_points_df["Latitude"].mean(), ocr_large_points_df["Longitude"].mean())

	if options_list["Map"]:
		try:
			mappy = mapper.initialise_map(mean_point)
		except UnboundLocalError:
			mappy = mapper.initialise_map(ocr_mean_point)
		try:
			colour_map = mapper.generate_speed_colour_map(speed_data)
		except UnboundLocalError:
			colour_map = mapper.generate_speed_colour_map(ocr_speed_data)

		mappy.canvas.add_child(colour_map)
		mapper.add_exclusion_zones_to_map(mappy.exclusion_zone_feature_group, exclusion_zones)


	if options_list["Map"] and options_list["ExtractMetadata"]:
		add_data_to_map(video_metadata_handler_list, mappy.routelines, mappy.start_markers, mappy.speed_lines, "blue", colour_map)
		mappy.canvas.save(f"{output_dir}\\mappy.html")

	if options_list["SpeedChart"] and options_list["ExtractMetadata"]:
		speed_chart = mapper.make_speed_chart(speed_data = speed_data)
		speed_chart.save(f"{output_dir}\\speed_chart.html")
		print("Speed chart saved")

	if options_list["Timeline"] and options_list["ExtractMetadata"]:
		metadata_timeline_figure = generate_timeline(video_metadata_handler_list, "Timeline Generated With Metadata Extracted Using ExifTool")
		tl.save_timeline_to_file(metadata_timeline_figure, f"{output_dir}\\timeline_from_metadata.html")
		print("Done with just timeline")

	if options_list["OCR"] and options_list["Map"]:
		for video in ocr_video_list:
			routeliner = mapper.add_routeline_to_map(video.gps_df, mappy.ocr_routelines, mappy.ocr_start_markers, mappy.ocr_speed_lines)
			routeliner.make_routeline("purple")
			mapper.add_start_marker_to_map(video.file_info_df, routeliner)
			mapper.add_speedline_to_map(routeliner, colour_map)
			mappy.canvas.save(f"{output_dir}\\mappy.html")
		print("Done with OCR + Map")

	if options_list["OCR"] and options_list["Timeline"]:
		for video in ocr_video_list:
			video.file_info_df = mapper.add_exclusion_zones_to_file_info(video.gps_df, video.file_info_df, exclusion_zones)
		ocr_timeline_figure = generate_timeline(ocr_video_list, "Timeline Generated Using Watermark Data")
		tl.save_timeline_to_file(ocr_timeline_figure, f"{output_dir}\\timeline_from_ocr.html")
		print("Done with OCR + timeline")

	if options_list["OCR"] and options_list["Map"] and options_list["Timeline"]:
		try:
			add_timeline_to_map(ocr_timeline_figure, median_point, mappy.ocr_timeline_marker)
		except UnboundLocalError:
			add_timeline_to_map(ocr_timeline_figure, ocr_median_point, mappy.ocr_timeline_marker)

		mappy.canvas.save(f"{output_dir}\\mappy.html")
		print("Done with OCR + map + timeline")

	if options_list["SpeedChart"] and options_list["OCR"]:
		ocr_speed_data = make_speed_dataframe(ocr_video_list)
		ocr_speed_chart = mapper.make_speed_chart(ocr_speed_data)
		try:
			speed_chart = speed_chart + ocr_speed_chart
		except UnboundLocalError:
			speed_chart = ocr_speed_chart
		speed_chart.save(f"{output_dir}\\speed_chart.html")
		print("Done with speed chart + ocr")

	if options_list["Map"] and options_list["SpeedChart"]:
		try:
			mapper.add_speed_chart_to_map(speed_chart, final_point, mappy.speed_chart_marker)
		except UnboundLocalError:
			mapper.add_speed_chart_to_map(speed_chart, ocr_final_point, mappy.speed_chart_marker)

		mappy.canvas.save(f"{output_dir}\\mappy.html")
		print("Done with map + speed chart")

	if options_list["Timeline"] and options_list["Map"] and options_list["ExtractMetadata"]:
		add_timeline_to_map(metadata_timeline_figure, mean_point, mappy.timeline_marker)
		mappy.canvas.save(f"{output_dir}\\mappy.html")
		print("Done with timeline + map")

	if options_list["SaveMetadata"]:

		system(f"mkdir {output_dir}\\extracted_metadata")

		if options_list["ExtractMetadata"]:
			for video_metadata_handler in video_metadata_handler_list:
				video_metadata_handler.gps_df.to_csv(
	path_or_buf = f"{output_dir}\\extracted_metadata\\{video_metadata_handler.video_name}_extracted_gps_metadata.csv", 
 	sep = ","
 	)
				video_metadata_handler.file_info_df.to_csv(
	path_or_buf = f"{output_dir}\\extracted_metadata\\{video_metadata_handler.video_name}_extracted_file_info.csv", 
   	sep = ","
   	)
		if options_list["OCR"]:
			for video in ocr_video_list:
				video.gps_df.to_csv(
	path_or_buf = f"{output_dir}\\ocr\\{video.video_name}_ocr_output.csv", 
	sep = ","
	)
		print("Saved metadata")
	remove_temp_directory(temp_directory)
	print("Deleted temp")
	print(f"DONE - go to {output_dir} to see your files")
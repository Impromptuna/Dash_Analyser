from plotly.io import to_html
from pandas import DataFrame
from plotly.express import timeline
from dash_analyser_application.timeline_classes import TimelineBar

def make_timeline_bars(video_data_handler_list:list) -> list:
	"""
	Takes in a list of either Video (video.py) or MetaDataFrames (dataframer.py) instances
	Uses these instances to return a list of TimelineBar instances
	"""
	timeline_bar_list = [TimelineBar(video_data_handler.gps_df, video_data_handler.file_info_df) for video_data_handler in video_data_handler_list]
	for bar in timeline_bar_list:
		bar.make_dictionary_for_bar()
	return timeline_bar_list

def make_timeline_dataframe(timeline_bar_list:list) -> DataFrame:
	"""
	Takes in a list of TimelineBar objects and returns a DataFrame containing the information required to 
	make a plotly.express timeline
	"""
	df = DataFrame([bar.bar_data for bar in timeline_bar_list])
	return df

def make_timeline_figure(df:DataFrame, title:str) -> timeline:
	"""
	Uses the input DataFrame and the given title to return a plotly.express timeline figure
	"""
	fig = timeline(
		df, 
		x_start="Start", 
		x_end="End", 
		y="Date", 
		color="ExclusionZones", 
		hover_data=[
			"FilePath",
			"Date", 
			"Start", 
			"End", 
			"ExclusionZones", 
			"AverageSpeed", 
			"MaxSpeed", 
			"FileType", 
			"FileSize"
			],
		title=title
		)
	return fig

def configure_timeline_yaxis(timeline:timeline):
	"""
	Causes the different rows in the timeline figure to descend chronologically rather than ascend
	"""
	timeline.update_yaxes(autorange="reversed")

def convert_timeline_to_html(timeline:timeline) -> "html timeline":
	"""
	Converts the timeline to an html representation of itself and returns the html
	"""
	timeline = to_html(timeline)
	return timeline

def save_timeline_to_file(timeline:"html timeline", timeline_file_name: str):
	"""
	Saves the HTML timeline to a .html file
	"""
	timeline.write_html(timeline_file_name)
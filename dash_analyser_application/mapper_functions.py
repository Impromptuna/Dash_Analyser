from branca.colormap import linear
from dash_analyser_application.mapper_classes import ExclusionZone, Mappy, StartMarkerPopup, RouteLineMaker
from folium import Popup, Html, IFrame, Marker, Icon, FeatureGroup
from altair import Chart, data_transformers
from folium.features import VegaLite
from pandas import DataFrame
from geopy import distance
from plotly.express import timeline


def make_exclusion_zone(location:tuple, radius:float) -> ExclusionZone:
	#Makes an instance of the ExclusionZone class with the given location and radius
	exclusion_zone=ExclusionZone(location=location, radius=radius)
	return exclusion_zone

def initialise_map(video_metadata:DataFrame) -> Mappy:
	#Initialises an instance of the Mappy class, which manages a folium map
	mappy = Mappy(video_metadata)
	mappy.add_tilelayers()
	mappy.add_draw_options()
	mappy.generate_feature_groups()
	mappy.add_layer_control()
	mappy.add_measure_control()
	return mappy

def add_exclusion_zones_to_map(exclusion_group:FeatureGroup, exclusion_zones:list):
	#Calls the add_to_map() method for each ExclusionZone instance stored in the exclusion_zones list
	for zone in exclusion_zones:
		zone.add_to_map(exclusion_group)

def generate_speed_colour_map(speed:DataFrame) -> linear:
	#Takes in a dataframe containing a large list of speed, and uses this to generate a branca linear colour map.
	colour_map=linear.Set1_09.scale(speed["Speed"].min(), speed["Speed"].max())
	colour_map.caption="Speed colour scale: "
	return colour_map

def make_speed_chart(speed_data:DataFrame) -> Chart:
	#Takes in a dataframe of speed and datetime data, and returns an altair Chart of that data
	data_transformers.disable_max_rows()
	speed_chart=Chart(speed_data
					).mark_line(
						point=False
					).encode(
						x="DateTime", 
						y="Speed",
						color="DataSource"
					).properties(
						height=500, 
						width=600
					).interactive()
	return speed_chart

def add_routeline_to_map(gps_df:DataFrame, routeline_group:FeatureGroup, start_marker_group:FeatureGroup, colour_line_group:FeatureGroup)->RouteLineMaker:
	"""	
	Takes in a dataframe containing GPS and temporal data, as well as featuregroups for a routeline, start marker, and speed line.
	Uses this data to generate an instance of the RouteLineMaker class, and returns the instance
	"""
	routeliner = RouteLineMaker(gps_df, routeline_group, start_marker_group, colour_line_group)
	return routeliner

def add_start_marker_to_map(file_info_df:DataFrame, routeliner:RouteLineMaker):
	"""	
	Takes in a dataframe containing file information for a video and an instance of the RouteLineMaker class associated with that file.
	Uses the file information dataframe to make a popup for a start marker. Calls the make_start_marker() method for the RouteLineMaker instance to add
	the popup to a start marker
	"""
	marker_popup = StartMarkerPopup(file_info_df).start_marker_popup_html()
	routeliner.make_start_marker(marker_popup)

def add_speedline_to_map(routeliner:RouteLineMaker, colour_map:linear):
	"""
	Takes in an instance of the RouteLineMaker class and a linear branca colormap.
	Calls a method for the RouteLineMaker instance which uses the colour map to add a speed line to the map.
	"""
	routeliner.make_routeline_with_speed_colouring(colour_map)


def make_folium_popup_for_timeline(timeline:timeline) -> Popup:
	"""
	Takes in a timeline figure plotted using plotly.express, and adds it to a folium Popup.
	The Popup is then returned to be added to a marker.
	"""
	popup = Popup(Html(IFrame(timeline, width=1000, height=400).render(), script=True), max_width=2650)
	return popup

def make_timeline_marker(location:tuple, popup:Popup) -> Marker:
	"""
	Takes in a location, which will be the median coordinate of all GPS data for the dashcam, and a folium Popup.
	Adds the Popup to a Marker at the given location, and returns the Marker, which will now contain a timeline figure.
	"""
	timeline_marker = Marker(location = location, popup = popup, icon=Icon(icon="hourglass-start", prefix="fa", color="purple"))
	return timeline_marker

def add_speed_chart_to_map(speed_chart:Chart, final_point:tuple, map_feature_group:FeatureGroup):
	"""
	Takes in an altair chart which will be a speed chart, the final point represented in the dashcam footage, and the speed chart marker FeatureGroup
	Converts the speed chart to a folium Popup using VegaLite
	Adds the speed chart Popup to the speed chart marker, which is then added to the FeatureGroup
	"""
	speed_chart_popup=Popup()
	VegaLite(speed_chart, height="100%", width="100%").add_to(speed_chart_popup)
	marker = Marker(location=final_point, popup=speed_chart_popup, icon=Icon(icon="road" ,color="red")).add_to(map_feature_group)

def test_exclusion_zones(gps_df:DataFrame, exclusion_zones: list) -> DataFrame:
	"""
	Takes in a dataframe containing GPS data and a list of ExclusionZone instances
	Checks every coordinate in the dataframe for whether it is present in any ExclusionZone
	If a coordinate is in an ExclusionZone, it is noted in a new column in the dataframe
	The dataframe is returned
	"""
	for i, exclusion_zone in enumerate(exclusion_zones):
		for test_point in gps_df["Latitude, Longitude"]:
			dis = distance.distance(exclusion_zone.location, test_point).km
			if dis <= exclusion_zone.radius_km:
				gps_df[f"In Exclusion Zone {i+1}"] = True
			else:
				gps_df[f"In Exclusion Zone {i+1}"] = False

	return gps_df

def add_exclusion_zones_to_file_info(gps_df:DataFrame, file_info_df:DataFrame, exclusion_zones:list) -> DataFrame:
	"""
	Takes in a GPS dataframe, a file info dataframe, and a list of ExclusionZones. Checks whether any coordinates are in any of the ExclusionZones,
	and if they are it is noted in the file info dataframe. The ammended file info dataframe is then returned.
	"""
	exclusion_zone_list=[exclusion_zone.timeline_label for i, exclusion_zone in enumerate(exclusion_zones) if gps_df[f"In Exclusion Zone {i+1}"].any()]
	if exclusion_zone_list == []:
		file_info_df["Present in Exclusion Zones"] = "Not in exclusion zones"
	else:
		file_info_df["Present in Exclusion Zones"] = ",<br><br>".join(exclusion_zone_list)
	return file_info_df
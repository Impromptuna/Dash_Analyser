from folium import TileLayer, Map, Marker, Icon, LayerControl, ColorLine, Popup, IFrame, Circle, FeatureGroup
from folium.vector_layers import PolyLine
from folium.plugins import MeasureControl, Draw
from pandas import DataFrame

class RouteLineMaker:

	"""
	Takes in a dataframe containing coordinates and speeds from a single dashcam video.
	Plots a single-coloured routeline on a folium map using those coordinates.
	Plots a routeline which is coloured based on the speed of the vehicle.
	Adds a marker to the start of the routeline with a popup containing information about the video file that is being plotted.
	"""

	def __init__(self, gps_df: DataFrame, routeline_group: FeatureGroup, start_marker_group: FeatureGroup, colour_line_group: FeatureGroup):

		self.points = gps_df["Latitude, Longitude"].to_list()
		self.speed = gps_df["Speed"].to_list()
		self.routeline_group = routeline_group
		self.start_marker_group = start_marker_group
		self.colour_line_group = colour_line_group

	def make_routeline(self, routeline_colour: str):
		"""		
		Take in a routeline colour (either blue for extracted metadata or purple for watermark data), 
		and plot the coordinates stored by the class instance on the map
		"""
		PolyLine(locations=self.points, color = routeline_colour).add_to(self.routeline_group)

	def make_routeline_with_speed_colouring(self, colour_map: "branca linear colormap"):
		"""		
		Take in a branca linear color map, and use this to plot an additional routeline which uses the speeds stored by the class instance
		as a colour scale
		"""
		ColorLine(positions=self.points, colors=self.speed, colormap=colour_map, weight=4.5).add_to(self.colour_line_group)

	def make_start_marker(self, popup: Popup):
		"""		
		Take in a popup for a start marker, which contains an HTML table of file details, and add it to a start marker for the routelines.
		"""
		Marker(location=self.points[0], tooltip=f"Start of route line. Click to see file details.", popup=popup, icon=Icon(icon="plus-circle", prefix="fa")).add_to(self.start_marker_group)

class StartMarkerPopup:
	"""
	Parses the file information dataframe for a single video file into its separate components
	Generates the popup used by the RouteLineMaker class for its start marker using the parsed file information.
	"""
	def __init__(self, file_info_df):
		self.file_name = file_info_df["SourceFile"].iloc[0]
		self.file_type = file_info_df["FileType"].iloc[0]
		self.file_size = file_info_df["FileSize"].iloc[0]
		self.MIMEType = file_info_df["MIMEType"].iloc[0]
		self.duration = file_info_df["Duration"].iloc[0]
		self.average_speed = f'{file_info_df["AverageSpeed"].iloc[0]} {file_info_df["SpeedRef"].iloc[0]}'
		self.max_speed = f'{file_info_df["MaxSpeed"].iloc[0]} {file_info_df["SpeedRef"].iloc[0]}'
		self.file_create_date = file_info_df["CreateDate"].iloc[0]
	
	def start_marker_popup_html(self) -> Popup:
		#Defines the HTML file details table
		self.popup_html = """<html  lang="en">
			<head>
			<meta  charset="UTF-8">
	<style> 
	table {
		font-family:  arial,  sans-serif; 
		border-collapse:  collapse; 
		width:  100%;
	}

	td,  th  {
		border:  1px  solid  #dddddd; 
		text-align:  left;  
		padding:  8px;
	}
	 


	tr:nth-child(even) { 
		background-color:  #dddddd;
	}
	</style>
	 
			</head>
			<body>
			 

			<h1>File Information</h1>
			<table style ="width:100%">
				<tr>	
					<th> File  Attribute(s)</th>
					<th> Value(s)</th>
				</tr>	
				<tr>	
					<td>	Name:  </td>
					<td> """ + self.file_name + """ </td>
				</tr>	
				<tr>	
					<td>	File Type  </td>
					<td> """ + self.file_type + """	 </td>
				</tr>	
				<tr>	
					<td>	File Size  </td>
					<td>	""" + self.file_size + """  </td>
				</tr>	
				<tr>	
					<td>	MIME Type  </td>
					<td>	""" + self.MIMEType + """   </td>
				</tr>	
				<tr>	
					<td>	Video Length  </td>
					<td>	"""+ self.duration + """  </td>
				</tr>
				</tr>	
				<tr>	
					<td>	Average  Speed:	</td>
					<td>	""" + str(self.average_speed) + """  </td>
				</tr>	
				<tr>	
					<td>	Highest  Speed:	</td>
					<td>	""" + str(self.max_speed) + """  </td>
				</tr>
				<tr>		 
					<td>  File Create Date and Time:	</td>
					<td>  """ + str(self.file_create_date) + """  </td>
				</tr>
			</tr>
		
		</table>


		</body>
		</html>  
		
		"""
		iframe=IFrame(html=self.popup_html, width=500, height=300)
		popup=Popup(iframe, max_width=2650)

		return popup

class ExclusionZone:

	"""
	This class stores information about an exclusion zone and adds graphical elements to a folium map representing the exclusion zone.
	The information stored is the central point of the zone, and the radius of the zone in meters and kilometers
	"""

	def __init__(self, location, radius):

		self.radius_km = radius
		self.location = location
		self.radius_metres = radius * 1000
		self.timeline_label = f"Present in zone:<br>-Radius {self.radius_km}km<br>-At {self.location}"

	def add_to_map(self, group:FeatureGroup):
		"""
		Sets the group of the exclusion zone to the provided feature group for the folium map
		Calls functions to make the table for the exclusion zone popup and add a circle of the given radius 
		and centred at the given coordinates, which is then placed on a map.
		"""
		self.group = group
		self.make_exclusion_zone_popup()
		self.make_exclusion_zone_radius()

	def make_exclusion_zone_popup(self):
		#Makes a popup containing the exclusion zone's information. This popup is added to the marker element at the ceentre of the zone.
		html= """<html lang="en">
		<html  lang="en">
		<head>
		<style> table {
			font-family:  arial, sans-serif; 
			border-collapse:  collapse; 
			width:  100%;
		}

		td,  th  {
			border:  1px  solid  #dddddd; 
			text-align:  left;  
			padding:  8px;
		}

		tr:nth-child(even) { 
			background-color:  #dddddd;
		}
		</style>
		</head>
		<body>
			<p>Center of Exclusion Zone</p>
			<table  style  ="width:100%">
		 	<tr>
				<th>  Zone  Details:</th>
				<th>  Value(s)</th>
			</tr>
			<tr>
				<td>Coordinates:  </td>
				<td>"""  +  str(self.location)  +  """  </td>
			</tr>
			<tr>
				<td>Radius  (Kilometers):  </td>
				<td>""" + str(self.radius_km) + """ </td>
			</tr>
		</table>


	</body>
	</html>
	"""
		self.iframe=IFrame(html=html, width=500, height=200)

	def make_exclusion_zone_radius(self):
		#Adds a circle object to the map
		Circle(radius=self.radius_metres, location=self.location, tooltip="Exclusion Zone", color="red", fill=True, fill_colour="red", popup=Popup(self.iframe)).add_to(self.group)


class Mappy:

	"""Class which stores the folium map canvas, adds tilelayers, adds draw options, and adds featuregroups"""

	def __init__(self, average_point):

		self.canvas = Map(location=average_point, 
						  zoom_start=12)

	def add_tilelayers(self):
		#Adds different map styles which can bee freely switched between by the user
		TileLayer('OpenStreet Map').add_to(self.canvas)
		TileLayer("Stamen Terrain").add_to(self.canvas)
		TileLayer("Stamen Toner").add_to(self.canvas)

	def add_draw_options(self):
		#Adds draw options for the user
		Draw(export=True, 
			 filename="my_data.geojson", 
			 position="topleft", 
			 draw_options={"polyline":{"allowIntersection": False}}, 
			 edit_options={"poly":{"allowIntersection": False}}
			 ).add_to(self.canvas)

	def generate_feature_groups(self):
		"""
		Makes the required feature groups. These groups represent display layers, and will contain features displayed on the map.
		Each feature group can be toggled on and off by the user from the interactive map file, with elements toggled on displayed on the map, and those toggled off removed.
		"""
		self.routelines=FeatureGroup(name="Route line", show=True).add_to(self.canvas)
		self.speed_lines=FeatureGroup(name="Route line coloured by speed", show=False).add_to(self.canvas)
		self.start_markers=FeatureGroup(name="Start markers for each video", show=True).add_to(self.canvas)
		self.speed_chart_marker=FeatureGroup(name="Speed chart marker", show=True).add_to(self.canvas)
		self.timeline_marker=FeatureGroup(name="Timeline marker", show=True).add_to(self.canvas)
		self.exclusion_zone_feature_group=FeatureGroup(name="Exclusion zone group", show=True).add_to(self.canvas)
		self.ocr_routelines=FeatureGroup(name="Show routelines read from watermarks", show=False).add_to(self.canvas)
		self.ocr_start_markers=FeatureGroup(name="Show file information markers read from watermarks", show=False).add_to(self.canvas)
		self.ocr_speed_lines=FeatureGroup(name="Show speed lines read from watermarks", show=False).add_to(self.canvas)
		self.ocr_timeline_marker=FeatureGroup(name="Show timeline generated from OCR data", show=False).add_to(self.canvas)

	def add_layer_control(self):
		LayerControl().add_to(self.canvas) #adds the ability to hide and show featuregroups/tilelayers
		
	def add_measure_control(self):
		MeasureControl(position="bottomleft").add_to(self.canvas) #adds the ability to measure the distance between two points

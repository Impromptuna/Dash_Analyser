from tkinter import Frame, font, Tk, IntVar
from dash_analyser_application.GUIScreen1 import SetupScreen
from dash_analyser_application.GUIScreen2 import ExclusionZonesScreen
from dash_analyser_application.Screen1ButtonFunctions import select_and_display_directory, select_directory, display_directory
from dash_analyser_application.parse_options_and_make_files import parse_options, make_exclusion_zones


class GUIController(Tk):

    """
    This creates the window and frame that will contain the screens for the application. 
    It also stores the variables associated with the options for the application, and calls the function which parses the options.
    Essentially, it forms the underlying controller for the option-setting application.
    Adapted from https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
    """

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.make_GUI()

    def set_fonts(self):
        #Defining font styles
        self.label_font=font.Font(family="Helvetica", size=12)
        self.directory_display_font=font.Font(family="Helvetica", size=8, weight="bold", slant="italic")
        self.button_font=font.Font(family="Helvetica", size=10)
        self.title_font=font.Font(family="Helvetica", size=14, weight="bold")   

    def make_container(self):
        #The container will be where the individual screens of the GUI are stacked. 
        #These screens can be switched between by moving them further up or down the stack
        self.container=Frame(master=self)
        self.container.pack(side="top", fill="both", expand=True)

    def configure_container(self):
        #This will make the rows and columns of the container's grid expand with the window
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def options(self):
        #Define the output file options
        self.extract_metadata_option=IntVar(value = 0)
        self.map_option=IntVar(value = 0)
        self.timeline_option=IntVar(value = 0)
        self.ocr_option=IntVar(value = 0)
        self.speed_chart_option=IntVar(value = 0)
        self.save_extracted_metadata_option=IntVar(value = 0)
        self.exclusion_zones_option=IntVar(value = 0)
        self.dashcam_type=""

    def make_exclusion_zones(self):
        #Initialise the list of exclusion zones. This is appended to by the second GUI screen.
        self.exclusion_zone_list=[]

    def make_frames(self):
        #Make a list of frames which will each act as a new screen for the application
        self.frames={}
        #Initialise and place the Setup and Graphical Options screens with this class as the controller
        #and the container as the master
        self.frames["Setup Screen"]=SetupScreen(master=self.container, controller=self)
        self.frames["Setup Screen"].grid(row=0, column=0, sticky="nsew")
        self.frames["Exclusion Zone Input"]=ExclusionZonesScreen(master=self.container, controller=self)
        self.frames["Exclusion Zone Input"].grid(row=0, column=0, sticky="nsew")

        #Show the Setup Screen when the application is run
        self.show_frame("Setup Screen")

    def show_frame(self, page_name):
        #Display the specified screen
        #Removes any currently displayed frames, then displays the frame for the given frame name
        for frame in self.frames.values():
            frame.grid_remove()
        frame = self.frames[page_name]
        frame.grid()
        self.title(f"DashAnalyser: {page_name}")

    def input_directory_select(self, display_directory_label):
        #takes a directory display label and calls the select_and_display_directory function.
        #this command is triggered when the user presses the select input directory button.
        self.input_directory=select_and_display_directory(display_directory_label)
        self.input_directory = self.input_directory.replace("/", "\\")

    def output_directory_select(self, display_directory_label):
        #this command is triggered when the user presses the select output directory button.
        self.output_directory=select_and_display_directory(display_directory_label)
        self.output_directory = self.output_directory.replace("/", "\\")

    def make_GUI(self):
        #Calls the functions required for the GUI to work
        self.set_fonts()
        self.make_container()
        self.configure_container()
        self.options()
        self.make_exclusion_zones()
        self.make_frames()

    def get_options_list(self):
        #Get the options set by the user and place them in a dictionary to be used by the parse_options() function
        self.options_list = dict(   
            ExtractMetadata = self.extract_metadata_option.get(),
            Map = self.map_option.get(), 
            Timeline = self.timeline_option.get(), 
            OCR = self.ocr_option.get(), 
            SpeedChart = self.speed_chart_option.get(), 
            SaveMetadata = self.save_extracted_metadata_option.get()
            )

    def visualise(self):
        #Begin the process of visualising the data
        print("VISUALISING")
        self.get_options_list()
        exclusion_zones = make_exclusion_zones(self.exclusion_zone_list)
        parse_options(self.input_directory, self.output_directory, self.options_list, exclusion_zones, self.dashcam_type)
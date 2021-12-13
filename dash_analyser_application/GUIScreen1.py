from tkinter import Label,  Frame, font, SUNKEN, Entry, messagebox, Text
from tkinter.ttk import Button, Checkbutton, Combobox
from ttkwidgets import tooltips


class SetupScreen(Frame):

    """
    Defines the widgets and functions for the setup screen of the GUI for Dash Analyser
    """

    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller=controller
        self.grid()
        self.make_screen()

    def make_dashcam_type_dropdown(self):
        #Makes and places the elements for a drop down menu that allows the user to select the type of dashcam being used.
        self.dashcam_type_frame=Frame(master=self, relief=SUNKEN, borderwidth=5, width = 40)
        self.dashcam_type_drop_down = Combobox( 
            master = self.dashcam_type_frame,
            values = ["GARMIN", "Nextbase 312GW", "MiVue", "Transcend", "Nextbase 422GW", "Other"],
            state = "readonly",
            tooltip="Select the dashcam type from which the input videos were taken.")
        Label(master = self.dashcam_type_frame, text="Choose dashcam type: ").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.dashcam_type_drop_down.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.dashcam_type_frame.grid(row=0, padx=10, pady=10, sticky="nsew")

    def directory_frame(self):
        #Defines and places the frame for the directory input and output selection section of the GUI
        self.directory_selection_frame=Frame(master=self, relief=SUNKEN, borderwidth=5, width = 40)
        self.directory_selection_frame.grid(row=1, padx=10, pady=10, sticky="nsew")
        self.directory_selection_frame_title = Label(master = self.directory_selection_frame, text="Directory Selection:", font=self.controller.title_font)
        self.directory_selection_frame_title.grid(row = 0, padx=5, pady=15, sticky = "w")

    def make_input_directory_button(self):
        # Defines the elements required for input directory selection
        self.select_input_label=Label(master=self.directory_selection_frame, text="Input directory", font=self.controller.label_font)
        self.display_input_directory=Label(master=self.directory_selection_frame, text="Directory Path", font=self.controller.directory_display_font)
        self.select_input_button=Button(
            master=self.directory_selection_frame,
            text="Select",
            command=lambda: self.controller.input_directory_select(self.display_input_directory),
            tooltip = "Select the directory containing the dashcam videos to be analysed."
            )

    def place_input_directory_button(self):
        # Places the elements required for input directory selection in the directory selection frame
        self.select_input_label.grid(row = 1, padx=5, pady=15, sticky = "w")
        self.select_input_button.grid(row=1, column=1, padx=5, pady=5, sticky="e")
        self.display_input_directory.grid(row=2, padx=5, pady=5)

    def make_output_directory_button(self):
        # Defines the elements required for output directory selection
        self.select_output_label=Label(master=self.directory_selection_frame, text="Output directory", font=self.controller.label_font)
        self.display_output_directory=Label(master=self.directory_selection_frame, text="Directory Path", font=self.controller.directory_display_font)
        self.select_output_button=Button(
            master=self.directory_selection_frame,
            text="Select",
            command=lambda: self.controller.output_directory_select(self.display_output_directory),
            tooltip = "Select the directory to which you would like to save the selected output files."
            )


    def place_output_directory_button(self):
        # Places the elements required for input directory selection in the directory selection frame
        self.select_output_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.select_output_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.display_output_directory.grid(row=4, padx=5, pady=5)

    def data_extraction_menu_frame(self):
        #Defined the frame for the data extraction options
        self.data_extraction_options_frame=Frame(master=self, relief=SUNKEN, borderwidth=5, width = 40)
        self.data_extraction_options_frame.grid(row=2, padx=10, pady=10, sticky="nsew")
        self.data_extraction_options_frame.bind("<Enter>", self.check_dashcam_type)

    def make_data_extraction_menu(self):
        self.data_extraction_options_title = Label(master = self.data_extraction_options_frame, text="Select Data Extraction Methods:", font=self.controller.title_font)
        self.data_extraction_options_title.grid(row=0, padx=5, pady=5, sticky="w")
        self.extract_metadata_select=Checkbutton(
            master=self.data_extraction_options_frame, 
            text="Extract embedded metadata", 
            variable=self.controller.extract_metadata_option,
            tooltip = "Extract embedded metadata using exiftool.")
        self.ocr_option_select=Checkbutton( 
            master=self.data_extraction_options_frame,
            text="Read watermarks",
            variable=self.controller.ocr_option,
            tooltip = "Read the watermarks displayed in the videos.")
        self.extract_metadata_select.grid(row=1, padx=5, pady=5, sticky="w")
        self.ocr_option_select.grid(row=2, padx=5, pady=5, sticky="w")

    def output_menu_frame(self):
        # Defines the frame containing the elements required to set the date and time ranges for the data
        self.output_options_frame=Frame(master=self, relief=SUNKEN, borderwidth=5, width=25)
        self.output_options_frame.grid(row=3, padx=10, pady=10, sticky="nsew")
        self.output_options_frame.bind("<Enter>", self.check_dashcam_type)


    def make_output_file_menu(self):
        #Defines the options for the output file menu
        self.output_options_frame_title = Label(master = self.output_options_frame, text="Select Output Options:", font=self.controller.title_font)
        self.output_options_frame_title.grid(row = 0, padx=5, pady=15, sticky = "w")


        self.map_option_select=Checkbutton( 
            master=self.output_options_frame, 
            text="Generate map", 
            variable=self.controller.map_option,
            tooltip = "Output a map showing routelines and file details.")

        self.timeline_option_select=Checkbutton(
            master=self.output_options_frame, 
            text="Generate timeline", 
            variable=self.controller.timeline_option,
            tooltip = "Output a timeline of the activity taking place in the dashcam. If you also select the map option, the timeline will be placed on the map in a marker.")

        self.speed_chart_option_select=Checkbutton( 
            master=self.output_options_frame, 
            text="Generate speed chart", 
            variable=self.controller.speed_chart_option,
            tooltip = 'Generate a chart of speed against time using extracted metadata. If the "Read watermarks" options has also been selected, a second line will be plotted on the same axes using this data.')

        self.save_extracted_metadata_option_select=Checkbutton( 
            master=self.output_options_frame, 
            text="Save extracted metadata", 
            variable=self.controller.save_extracted_metadata_option,
            tooltip = "Output the metadata extracted from the dashcam videos to .json files in the output directory.")

        self.exclusion_zones_option_select=Checkbutton( 
            master=self.output_options_frame, 
            text="Define exclusion zone/s", 
            variable=self.controller.exclusion_zones_option, 
            tooltip= "If this option is selected, you will be asked to define some exclusion zones. If the map option is selected, these exclusion zones will be graphically represented on the map as circles. If the timeline option is selected, any videos in which the dashcam has enetered one of the zones will be coloured to indicate this.")

    def check_dashcam_type(self, combobox):
        if self.dashcam_type_drop_down.get()=="MiVue":
            self.extract_metadata_select.state(["disabled"])
            self.ocr_option_select.state(["!disabled"])
        elif self.dashcam_type_drop_down.get()=="GARMIN":
            self.extract_metadata_select.state(["!disabled"])
            self.ocr_option_select.state(["!disabled"])
        elif self.dashcam_type_drop_down.get()=="Nextbase 312GW":
            self.extract_metadata_select.state(["!disabled"])
            self.ocr_option_select.state(["!disabled"])
        elif self.dashcam_type_drop_down.get()=="Transcend":
            self.extract_metadata_select.state(["!disabled"])
            self.ocr_option_select.state(["disabled"])
        elif self.dashcam_type_drop_down.get()=="Nextbase 422GW":
            self.extract_metadata_select.state(["!disabled"])
            self.ocr_option_select.state(["!disabled"])
        elif self.dashcam_type_drop_down.get()=="Other":
            self.extract_metadata_select.state(["!disabled"])
            self.ocr_option_select.state(["disabled"])

    def place_output_file_menu(self):
        #Places the output file menu options within the output file menu frame
        self.map_option_select.grid(row=2, padx=5, pady=5, sticky="w")
        self.timeline_option_select.grid(row=3, padx=5, pady=5, sticky="w")
        self.speed_chart_option_select.grid(row=4, padx=5, pady=5, sticky="w")
        self.save_extracted_metadata_option_select.grid(row=6, padx=5, pady=5, sticky="w")
        self.exclusion_zones_option_select.grid(row=7, padx=5, pady=5, sticky="w")

    def make_continue_button(self):
        #Defines and places 
        continue_button=Button(
            master=self,
            text="Continue",
            command=self.on_continue_press,
            tooltip='If the "Define exclusion zone/s" option has been selected, you will be taken to a screen in which you can define your exclusion zones. Otherwise, the data extraction and visualisation processes will begin.'
            )
        continue_button.grid(row=4, padx=10, pady=10, sticky="nsew")

    def on_continue_press(self):
        try:
            str(self.controller.input_directory)
            str(self.controller.output_directory)
            self.controller.dashcam_type = self.dashcam_type_drop_down.get()
        except:
            messagebox.showerror("Error", "Please ensure that you have selected input and output directories, and a dashcam type.")
        else:
            if self.controller.ocr_option.get() == 1:
                if self.dashcam_type_drop_down.get() == "":
                    messagebox.showerror("Error", "You must select a dashcam type if you wish to read the watermarks")
                else:
                    self.continue_checks()
            else:
                self.continue_checks()

    def continue_checks(self):
        if (self.controller.exclusion_zones_option.get() == 1):
            self.controller.show_frame("Exclusion Zone Input")
        else:
            self.controller.visualise()

    def make_screen(self):
        #Calls all functions necessary to make the screen
        self.directory_frame()
        self.make_input_directory_button()
        self.place_input_directory_button()
        self.make_output_directory_button()
        self.place_output_directory_button()
        self.make_dashcam_type_dropdown()
        self.data_extraction_menu_frame()
        self.make_data_extraction_menu()
        self.output_menu_frame()
        self.make_output_file_menu()
        self.place_output_file_menu()
        self.make_continue_button()
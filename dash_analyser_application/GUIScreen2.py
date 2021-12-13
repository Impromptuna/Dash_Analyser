from tkinter import Label, Frame, Button, font, SUNKEN, Entry, Scrollbar, Canvas, messagebox
from tkinter.messagebox import askyesno
from tkinter.ttk import Button
from geopy import Nominatim, exc

class ExclusionZonesScreen(Frame):

    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller=controller
        self.grid()
        self.make_screen()

    def row_and_column_configure(self):
        self.rowconfigure(index=1, weight=2)

    def make_exclusion_zone_form_frame(self):
        #Define and place the frame for exclusion zone forms. This frame will contain a canvas and a scrollbar.
        self.exclusion_zone_form_frame=Frame(master=self, relief=SUNKEN, borderwidth=5)
        self.exclusion_zone_form_frame.grid(row=1, padx=10, pady=10, sticky="nsew")

    def make_exclusion_zone_form_canvas(self):
        #Defines a canvas for the exclusion zone form frame to go in. This allows a scrollbar to be added to the frame.
        self.exclusion_zone_form_canvas=Canvas(master=self.exclusion_zone_form_frame)
        self.exclusion_zone_form_canvas.pack(side="left", fill="both")

    def make_exclusion_zone_form_frame_scrollbar(self):
        #Makes a scrollbar for the exclusion zone form frame.
        self.exclusion_scrollbar=Scrollbar(master=self.exclusion_zone_form_frame, orient="vertical", command=self.exclusion_zone_form_canvas.yview)
        self.exclusion_scrollbar.pack(side="right", fill="y")

    def make_scrollable_exclusion_zone_form_frame(self):
        #Defines the frame which will contain exclusion forms. This frame sits inside the canvas made above, and will be scrollable.
        self.scrollable_exclusion_zone_form_frame=Frame(master=self.exclusion_zone_form_canvas, borderwidth=5)
        self.form_count = 1 #used as a counter when adding exclusion zone forms

        self.exclusion_forms = []
        self.exclusion_form_entry_fields=[]

        self.exclusion_zone_title=Label(master=self.scrollable_exclusion_zone_form_frame, text="Set Exclusion Zones", font=self.controller.title_font)
        self.exclusion_zone_title.grid(row=0, padx=7, pady=7, sticky="w")

    def configure_exclusion_zone_scrollbar(self):
        #Configures the scrollbar to show the correct section of the GUI when it is used.
        self.scrollable_exclusion_zone_form_frame.bind("<Configure>",lambda e: self.exclusion_zone_form_canvas.configure(scrollregion=self.exclusion_zone_form_canvas.bbox("all")))
        self.exclusion_zone_form_canvas.create_window((0,0), window=self.scrollable_exclusion_zone_form_frame, anchor="nw")
        self.exclusion_zone_form_canvas.configure(yscrollcommand=self.exclusion_scrollbar.set)

    def make_exclusion_button_frame(self):
        #Define a frame for the add and remove exclusion zone form buttons
        self.exclusion_button_frame=Frame(master=self.scrollable_exclusion_zone_form_frame)
        self.exclusion_button_frame.grid(row=2)

    def make_add_form_button(self):
        #Adds a button to add new exclusion zone forms
        self.add_form_button = Button(master=self.exclusion_button_frame, text='Add exclusion zone', command=self.add_form_button_press)
        self.add_form_button.grid(row=0, column=0)

    def make_remove_previous_form_button(self):
        #Adds a button which can remove the most recently added exclusion zone form
        self.remove_form_button = Button(master=self.exclusion_button_frame, text='Remove exclusion zone', command=self.remove_exclusion_form)
        self.remove_form_button.grid(row=0, column=1)

    def add_form_button_press(self):

        """
        When the user clicks "Add exclusion form", this function calls others to validate the user's input, and then calls another to add the new exclusion form.
        """

        if self.exclusion_form_entry_fields != []:
            self.check_radius_entry()
            self.make_exclusion_form()
        else:
            self.make_exclusion_form()

    def check_radius_entry(self):
        #Ensure that the radius provided by the user is a valid number
        try:
            radius = float(self.exclusion_form_entry_fields[-1]["Radius Entry"].get())
        except:
            messagebox.showerror("Error", "Please enter a valid radius. Must be a number.")
            return ValueError
        else:
            location_coordinates = self.check_location_entry()
            self.controller.exclusion_zone_list.append(dict(Location=location_coordinates, Radius=radius))

    def check_location_entry(self):

        """
        Used for input validation from the GUI - the first if statement checks whether a postcode has been provided, and if it has
        it checks whether the postcode can be geocoded into a longitude and latitude. If a longitude and latitude have been provided,
        it checks whether they are valid numbers.
        """

        if self.exclusion_form_entry_fields[-1]["Postcode Entry"].get() != "":
            try:
                geolocator = Nominatim(user_agent="dashanalyser")
                location = geolocator.geocode(self.exclusion_form_entry_fields[-1]["Postcode Entry"].get())
                location_coordinates = (location.latitude, location.longitude)
            except AttributeError:
                messagebox.showerror("Error", "Please enter a valid postcode.")
                return ValueError
            except exc.GeocoderServiceError:
                messagebox.showerror("Error", "Sorry, geocoding postcodes is unavailable at this time - likely due to a network issue. Please use the latitude and longitude entry fields instead.")
                return ValueError
            else:
                return location_coordinates

        elif self.exclusion_form_entry_fields[-1]["Latitude Entry"] != "" or self.exclusion_form_entry_fields[-1]["Latitude Entry"] != "":
            try:
                latitude_coord = float(self.exclusion_form_entry_fields[-1]["Latitude Entry"].get())
                longitude_coord = float(self.exclusion_form_entry_fields[-1]["Longitude Entry"].get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid postcode or latitude and longitude.")
            else:
                location_coordinates = (latitude_coord, longitude_coord)
                return location_coordinates

    def make_exclusion_form(self):

        #Defines the exlusion zone form frame and fields, and places each field within the frame. A new frame and form is made
        #every time a user clicks the "Add exclusion zone" button

        exclusion_form=Frame(master=self.scrollable_exclusion_zone_form_frame, relief=SUNKEN)
        exclusion_form_dict={}

        postcode_entry_frame=Frame(master=exclusion_form)
        postcode_entry_label=Label(master=postcode_entry_frame, text="Postcode:", font=self.controller.label_font)
        postcode_entry=Entry(master=postcode_entry_frame, width=20)
        exclusion_form_dict["Postcode Entry"] = postcode_entry
        postcode_entry_label.grid(row=0, column=0, sticky="w")
        postcode_entry.grid(row=0, column=1, sticky="w", padx=5)
        postcode_entry_frame.grid(row=0, column=0, sticky="ew")

        or_label = Label(master=exclusion_form, text="OR", font = self.controller.label_font)
        or_label.grid(row=1, column=0, sticky="w")

        latitude_longitude_entry_frame=Frame(master=exclusion_form)

        latitude_entry_frame=Frame(master=latitude_longitude_entry_frame)
        latitude_entry_label=Label(master=latitude_entry_frame, text="Latitude:", font=self.controller.label_font)
        latitude_entry=Entry(master=latitude_entry_frame, width=13)
        exclusion_form_dict["Latitude Entry"] = latitude_entry
        latitude_entry_label.grid(row=1, column=0, sticky="w")
        latitude_entry.grid(row=1, column=1, sticky="w")
        latitude_entry_frame.grid(row=0, column=0, padx=5, sticky="w")

        longitude_entry_frame=Frame(master=latitude_longitude_entry_frame)
        longitude_entry_label=Label(master=longitude_entry_frame, text="Longitude:", font=self.controller.label_font)
        longitude_entry=Entry(master=longitude_entry_frame, width=13)
        exclusion_form_dict["Longitude Entry"] = longitude_entry
        longitude_entry_label.grid(row=1, column=2, sticky="w")
        longitude_entry.grid(row=1, column=3, sticky="w")
        longitude_entry_frame.grid(row=0, column=1, padx=5, sticky="w")
        
        latitude_longitude_entry_frame.grid(row=2, column=0, sticky="ew")


        radius_entry_frame=Frame(master=exclusion_form)
        radius_entry_label=Label(master=radius_entry_frame, text="Radius (kilometers):", font=self.controller.label_font)
        radius_entry=Entry(master=radius_entry_frame, width=13)
        exclusion_form_dict["Radius Entry"] = radius_entry
        radius_entry_label.grid(row=0, column=0, sticky="w")
        radius_entry.grid(row=0, column=1, sticky="e", padx=13)
        radius_entry_frame.grid(row=3, column=0, pady= 10, sticky="ew")

        exclusion_form.grid(row=self.form_count+1, padx=7, pady=7)

        self.exclusion_form_entry_fields.append(exclusion_form_dict)

        self.exclusion_button_frame.grid(row=self.form_count+2)
        self.exclusion_forms.append(exclusion_form)
        self.form_count+=1

    def remove_exclusion_form(self):
        #removes most recent exclusion zone form from the GUI
        self.exclusion_forms[-1].grid_remove()
        self.exclusion_forms.pop()
        self.exclusion_form_entry_fields.pop()

    def make_back_button(self):
        #Defines and places a button the user can use to go back to the setup page
        back_button=Button(master=self, text="Back to Setup Screen", command=lambda: self.controller.show_frame("Setup Screen"), tooltip = "Will take you back to the Setup Screen if you wish to change your mind about your options.")
        back_button.grid(row=3, padx=10, pady=10, sticky="nsew")

    def make_generate_button(self):
        #Defines and places the generate button. Once pressed this button generates the output files using the options specified by the user.
        generate_button=Button(master=self, text="Generate", command=self.generate)
        generate_button.grid(row=4, padx=10, pady=10, sticky="nsew")

    def generate(self):
        #Performed when the generate button is pressed
        self.check_radius_entry()
        self.controller.get_options_list()
        if all(value == 0 for value in self.controller.options_list.values()):
            answer = askyesno(title = "Confirmation", message = "You have not selected any visualisation or metadata extraction options - are you sure you want to proceed?")
            if answer:
                self.controller.visualise()
        else:
            self.controller.visualise()


    def make_screen(self):
        #Calls all functions necessary to display the screen
        self.row_and_column_configure()
        self.make_exclusion_zone_form_frame()
        self.make_exclusion_zone_form_canvas()
        self.make_exclusion_zone_form_frame_scrollbar()
        self.make_scrollable_exclusion_zone_form_frame()
        self.configure_exclusion_zone_scrollbar()
        self.make_exclusion_button_frame()
        self.make_add_form_button()
        self.make_remove_previous_form_button()
        self.make_back_button()
        self.make_generate_button()
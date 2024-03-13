# Python program to create a basic form
# GUI application using the customtkinter module
from turtle import fd

import customtkinter as ctk
import tkinter as tk

import os
from tkinter import font

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import excel_handler
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import XL2
import threading
import re
import tkinter.font as tkFont

import speed_radar
import spinbox
from datetime import datetime

from measurements import Measurements

# Sets the appearance of the window
# Supported modes : Light, Dark, System
# "System" sets the appearance mode to
# the appearance mode of the system
ctk.set_appearance_mode("System")
# Sets the color of the widgets in the window
# Supported themes : green, dark-blue, blue
ctk.set_default_color_theme("green")

# Dimensions of the window
appWidth, appHeight = 800, 700

# Set style for graph
plt.style.use('fivethirtyeight')

# name of Excel file that is used/created
path_name = ""

# name of text file with measurment details
file_name_measurement_details = ""

# canvas for plotting laf
fig = Figure()
ax = fig.add_subplot(111)
ax.set_title('LAF')
ax.set_xlabel('sample')
ax.set_ylabel('dB')
ax.set_xlim(0, 100)
ax.set_ylim(20, 100)
lines = ax.plot([], [])[0]

# canvas for plotting the speed
fig_speed = Figure()
ax_speed = fig_speed.add_subplot(111)
ax_speed.set_title('Speed')
ax_speed.set_xlabel('sample')
ax_speed.set_ylabel('km/h')
ax_speed.set_xlim(0, 100)
ax_speed.set_ylim(0, 100)
lines_speed = ax_speed.plot([], [])[0]

laf_data = np.array([])
speed_data = np.array([])
measurements_list = []
forking_enabled = False
measurement_start = False
air_temp = 0
road_temp = 0
wind_speed = 0


# create a new Excel file
def create_new_file(project_name_entry, location_name_entry, section_name_entry):
    global path_name
    global file_name_measurement_details
    path_name = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                             filetypes=(("excel file", "*.xlsx"), ("All Files", "*.*")))
    if path_name == "":
        tk.messagebox.showinfo(title=None, message="File not created")
    else:
        excel_handler.create_file(path_name)

        last_slash_index = path_name.rindex("/")
        file_name_measurement_details = path_name[:last_slash_index] + '/measurment details.txt'

        print(file_name_measurement_details)
        file = open(file_name_measurement_details, 'w')
        name = project_name_entry.get()
        file.write("Project name:" + name + "\n")
        location_name = location_name_entry.get()
        file.write("Location name:" + location_name + "\n")
        section_name = location_name_entry.get()
        file.write("Section name:" + section_name + "\n")

        file.close()
        tk.messagebox.showinfo(title=None, message="File created successfully")
        print(path_name)


# load an already existing Excel file
def browseFiles():
    global filename
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=(("Excel files",
                                                                                             "*.xlsx*"),
                                                                                            ("all files",
                                                                                             "*.*")))
    if filename == "":
        tk.messagebox.showinfo(title=None, message="No file selected")
    else:
        tk.messagebox.showinfo(title=None, message="File loaded successfully")
    print(filename)


def get_measurement_details(road_surface_entry, speed_entry, back_board_entry, length_entry, width_entry,
                            optional_microphone_entry):
    # Save the text to a text file
    global file_name_measurement_details
    if os.path.exists(file_name_measurement_details):
        print("File exists.")
        textfile = open(file_name_measurement_details, 'a')
        road_surface = road_surface_entry.get()
        textfile.write("Road surface:" + road_surface + "\n")
        speed = speed_entry.get()
        textfile.write("Speed limit:" + speed + "\n")
        back_board = back_board_entry.get()
        textfile.write("Backboard was used:" + back_board + "\n")
        length = length_entry.get()
        textfile.write("Length:" + length + "\n")
        width = width_entry.get()
        textfile.write("Width:" + width + "\n")
        optional_microphone = optional_microphone_entry.get()
        textfile.write("Optional microphone was used:" + optional_microphone + "\n")
        textfile.close()
    else:
        tk.messagebox.showinfo(title=None, message="Create a new file first at project info")


# updating the graphs
def update(canvas_laf, canvas_speed, textbox, listbox_measurements):
    # get the LAF value
    global speed_data
    global laf_data
    global measurement_start

    if measurement_start:
        LAF = XL2.measure_Laf()
        LAF = LAF.decode('utf-8')
        LAF = re.findall(r'\d+', LAF)
        LAF = LAF[0]

        # get the speed value
        speed = speed_radar.measure_speed()
        if speed.isspace():
            speed = "0"

        # only keep 100 samples to display
        if len(speed_data) < 100:
            speed_data = np.append(speed_data, float(speed[0:4]))
            laf_data = np.append(laf_data, float(LAF[0:4]))
        else:
            speed_data[0:99] = speed_data[1:100]
            speed_data[99] = float(speed[0:4])
            laf_data[0:99] = laf_data[1:100]
            laf_data[99] = float(LAF[0:4])

        # lines for laf
        lines.set_xdata(np.arange(0, len(laf_data)))
        lines.set_ydata(laf_data)
        canvas_laf.draw()

        # line for speed
        lines_speed.set_xdata(np.arange(0, len(speed_data)))
        lines_speed.set_ydata(speed_data)
        canvas_speed.draw()

        # display the speed in numbers
        textbox.delete("0.0", "end")
        string_speed = str(speed)
        textbox.insert("0.0", string_speed)

        if not len(measurements_list) == 0:
            for m in measurements_list:
                m = str(m)
                if m not in (listbox_measurements.get(0, tk.END)):
                    listbox_measurements.insert(tk.END, m)

    # run this function every 10ms
    threading.Timer(0.01, update, [canvas_laf, canvas_speed, textbox, listbox_measurements]).start()


def get_Environmental_conditions(entry1, entry2, entry3):
    global air_temp, road_temp, wind_speed
    air_temp = entry1.get()
    road_temp = entry2.get()
    wind_speed = entry3.get()


def start_measurement():
    global measurement_start
    XL2.start_measurement()
    measurement_start = True


def stop_measurement():
    global measurement_start
    global path_name

    if path_name != "":
        excel_handler.save_measurement(path_name, measurements_list)
        XL2.stop_measurement()
        measurement_start = False
        tk.messagebox.showinfo(title=None, message="Measurements saved to excel file")

    else:
        tk.messagebox.showinfo(title=None, message="Error measurements not save, no excel file found")


def delete_measurement(listbox):
    selected_indeces = listbox.curselection()
    for index in selected_indeces[::-1]:
        listbox.delete(index)
        print(measurements_list[index])
        print(index)
        del measurements_list[index]


def take_measurement(vehicle_type_listbox):
    now = datetime.now()
    max_index = np.argmax(laf_data)
    speed = speed_data[max_index]
    octave = XL2.measure_RTA()
    selected_vehicle_type = vehicle_type_listbox.get(tk.ACTIVE)
    if selected_vehicle_type:
        print(f'{selected_vehicle_type}')
    else:
        tk.messagebox.showerror("No Vehicle Selected", "No vehicle selected, set to default type car")
        selected_vehicle_type = "car"
    measurement = Measurements()
    measurement.date = now.strftime("%d/%m/%Y")
    measurement.time = now.strftime("%H:%M:%S")
    measurement.la_max = np.max(laf_data)
    measurement.wind_speed = wind_speed
    measurement.road_temp = road_temp
    measurement.air_temp = air_temp
    measurement.category = selected_vehicle_type
    measurement.octave = octave
    measurement.speed = speed

    measurements_list.append(measurement)


def calibration():
    global add_calibration
    LAF = XL2.measure_Laf()
    LAF = LAF.decode('utf-8')
    LAF = re.findall(r'\d+', LAF)
    LAF = LAF[0]
    add_calibration = 90 - int(LAF)
    tk.messagebox.showinfo(title=None, message="XL2 calibrated")


def fork_mode():
    global forking_enabled
    if not forking_enabled:
        speed_radar.forking_mode_on()
        forking_enabled = True
        tk.messagebox.showinfo(title=None, message="forking mode enabled")
    else:
        forking_enabled = False
        speed_radar.forking_mode_off()
        tk.messagebox.showinfo(title=None, message="forking mode disabled")


def create_vehicle_type(vehicle_type_entry, vehicle_type_listbox):
    new_vehicle_type = vehicle_type_entry.get()
    vehicle_type_listbox.insert(tk.END, new_vehicle_type)
    vehicle_type_entry.delete(0, tk.END)


class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create tabs
        self.add("Project info")
        self.add("Measurement details")
        self.add("Calibration")
        self.add("Passby measurements")
        self.add("Environmental conditions")

        ################################################
        # ------- Tab Project info ------- #
        ################################################
        # project name entry field
        project_name_label = ctk.CTkLabel(master=self.tab("Project info"), text="Project name",
                                          font=('Helvetica bold', 26))
        project_name_label.place(relheigh=0.07, relwidt=0.15, relx=0.1, rely=0.05, anchor=tk.W)

        project_name_entry = ctk.CTkEntry(master=self.tab("Project info"),
                                          placeholder_text="Project name",
                                          corner_radius=10)
        project_name_entry.place(relheigh=0.07, relwidt=0.15, relx=0.1, rely=0.1, anchor=tk.W)

        # location entry field
        project_location_label = ctk.CTkLabel(master=self.tab("Project info"), text="Location name",
                                              font=('Helvetica bold', 26))
        project_location_label.place(relheigh=0.07, relwidt=0.15, relx=0.3, rely=0.05, anchor=tk.W)

        project_location_entry = ctk.CTkEntry(master=self.tab("Project info"),
                                              placeholder_text="location name",
                                              corner_radius=10)
        project_location_entry.place(relheigh=0.07, relwidt=0.15, relx=0.3, rely=0.1, anchor=tk.W)

        # Section name entry field
        section_name_label = ctk.CTkLabel(master=self.tab("Project info"), text="Section name",
                                          font=('Helvetica bold', 26))
        section_name_label.place(relheigh=0.07, relwidt=0.15, relx=0.5, rely=0.05, anchor=tk.W)

        section_name_entry = ctk.CTkEntry(master=self.tab("Project info"),
                                          placeholder_text="section name",
                                          corner_radius=10)
        section_name_entry.place(relheigh=0.07, relwidt=0.15, relx=0.5, rely=0.1, anchor=tk.W)

        # open button
        open_button = ctk.CTkButton(master=self.tab("Project info"), text="Open", command=browseFiles,
                                    font=('Helvetica bold', 26))
        open_button.place(anchor=tk.W, relheight=0.07, relwidth=0.15, relx=0.1, rely=0.9)

        # close button
        close_button = ctk.CTkButton(master=self.tab("Project info"), text="New",
                                     command=lambda: create_new_file(project_name_entry, project_location_entry,
                                                                     section_name_entry),
                                     font=('Helvetica bold', 26))
        close_button.place(anchor=tk.W, relheight=0.07, relwidth=0.15, relx=0.3, rely=0.9)

        ################################################
        # ------- Tab measurement details ------- #
        ################################################

        #  road surface type entry field
        road_surface_label = ctk.CTkLabel(master=self.tab("Measurement details"), text="Type of road surface",
                                          font=('Helvetica bold', 26))
        road_surface_label.place(relheigh=0.07, relwidt=0.15, relx=0.1, rely=0.05, anchor=tk.W)

        road_surface_entry = ctk.CTkEntry(master=self.tab("Measurement details"),
                                          placeholder_text="Dense asphalt surface",
                                          corner_radius=10)
        road_surface_entry.place(relheigh=0.07, relwidt=0.15, relx=0.1, rely=0.1, anchor=tk.W)

        # speed limit entry field
        speed_limit_label = ctk.CTkLabel(master=self.tab("Measurement details"), text="Speed limit",
                                         font=('Helvetica bold', 26))
        speed_limit_label.place(relheigh=0.07, relwidt=0.15, relx=0.45, rely=0.05, anchor=tk.W)

        speed_entry = ctk.CTkEntry(master=self.tab("Measurement details"),
                                   placeholder_text="km/h",
                                   corner_radius=10)
        speed_entry.place(relheigh=0.07, relwidt=0.15, relx=0.45, rely=0.1, anchor=tk.W)

        # back board entry field
        back_board_label = ctk.CTkLabel(master=self.tab("Measurement details"), text="Backing board used?",
                                        font=('Helvetica bold', 26))
        back_board_label.place(relheigh=0.07, relwidt=0.15, relx=0.8, rely=0.05, anchor=tk.W)

        back_board_entry = ctk.CTkEntry(master=self.tab("Measurement details", ),
                                        placeholder_text="Yes/No",
                                        corner_radius=10)
        back_board_entry.place(relheigh=0.07, relwidt=0.15, relx=0.8, rely=0.1, anchor=tk.W)

        # length entry field
        length_label = ctk.CTkLabel(master=self.tab("Measurement details"), text="length", font=('Helvetica bold', 26))
        length_label.place(relheigh=0.07, relwidt=0.15, relx=0.1, rely=0.3, anchor=tk.W)

        length_entry = ctk.CTkEntry(master=self.tab("Measurement details"),
                                    placeholder_text="m",
                                    corner_radius=10)
        length_entry.place(relheigh=0.07, relwidt=0.15, relx=0.1, rely=0.35, anchor=tk.W)

        # width entry field
        width_label = ctk.CTkLabel(master=self.tab("Measurement details"), text="width", font=('Helvetica bold', 26))
        width_label.place(relheigh=0.07, relwidt=0.15, relx=0.45, rely=0.3, anchor=tk.W)

        width_entry = ctk.CTkEntry(master=self.tab("Measurement details"),
                                   placeholder_text="m",
                                   corner_radius=10)
        width_entry.place(relheigh=0.07, relwidt=0.15, relx=0.45, rely=0.35, anchor=tk.W)

        # optional microphone used entry fiefd
        optional_microphone_label = ctk.CTkLabel(master=self.tab("Measurement details"), text="Optional microphone",
                                                 font=('Helvetica bold', 26))
        optional_microphone_label.place(relheigh=0.07, relwidt=0.15, relx=0.8, rely=0.3, anchor=tk.W)

        optional_microphone_entry = ctk.CTkEntry(master=self.tab("Measurement details"),
                                                 placeholder_text="Yes/No",
                                                 corner_radius=10)
        optional_microphone_entry.place(relheigh=0.07, relwidt=0.15, relx=0.8, rely=0.35, anchor=tk.W)

        # Enter button
        enter = ctk.CTkButton(master=self.tab("Measurement details"), text="Submit",
                              command=lambda: get_measurement_details(road_surface_entry, speed_entry,
                                                                      back_board_entry, length_entry, width_entry,
                                                                      optional_microphone_entry),
                              font=('Helvetica bold', 26))
        enter.place(anchor=tk.W, relheight=0.07, relwidth=0.15, relx=0.1, rely=0.45)

        entry_vehicle_label = ctk.CTkLabel(master=self.tab("Measurement details"), text="vehicle type",
                                           font=('Helvetica bold', 26))
        entry_vehicle_label.place(anchor=tk.W, relheigh=0.07, relwidth=0.15, relx=0.1, rely=0.7)

        vehicle_type_entry = ctk.CTkEntry(master=self.tab("Measurement details"))
        vehicle_type_entry.place(anchor=tk.W, relheigh=0.07, relwidth=0.15, relx=0.1, rely=0.85)

        add_button = ctk.CTkButton(master=self.tab("Measurement details"), text="Add Vehicle Type", command=lambda: create_vehicle_type(vehicle_type_entry, vehicle_type_selection_listbox))
        add_button.place(anchor=tk.W, relheigh=0.07, relwidth=0.15, relx=0.1, rely=0.95)

        ################################################
        # ------- Tab Calibration ------- #
        ################################################

        # calibrate XL2 button
        calibrate_button = ctk.CTkButton(master=self.tab("Calibration"), text="calibrate", command=calibration,
                                         font=('Helvetica bold', 26))
        calibrate_button.place(anchor=tk.N, relheight=0.07, relwidth=0.15, relx=0.2, rely=0.1)

        # Forking mode on/off
        fork_button = ctk.CTkButton(master=self.tab("Calibration"), text="fork mode On/Off", command=fork_mode,
                                    font=('Helvetica bold', 26))
        fork_button.place(anchor=tk.N, relheight=0.07, relwidth=0.15, relx=0.2, rely=0.2)

        ################################################
        # ------- Tab Environmental conditions ------- #
        ################################################

        # Create a label for the first input field
        label1 = ctk.CTkLabel(master=self.tab("Environmental conditions"), text="Air Temperature:",
                              font=('Helvetica bold', 26))
        label1.place(anchor=tk.N, relheight=0.07, relwidth=0.15, relx=0.4, rely=0.2)

        # Create the first input field
        entry1 = ctk.CTkEntry(master=self.tab("Environmental conditions"))
        entry1.place(anchor=tk.N, relheight=0.07, relwidth=0.15, relx=0.55, rely=0.2)

        # Create a label for the second input field
        label2 = ctk.CTkLabel(master=self.tab("Environmental conditions"), text="Road Temperature:",
                              font=('Helvetica bold', 26))
        label2.place(anchor=tk.N, relheight=0.07, relwidth=0.15, relx=0.4, rely=0.4)

        # Create the second input field
        entry2 = ctk.CTkEntry(master=self.tab("Environmental conditions"))
        entry2.place(anchor=tk.N, relheight=0.07, relwidth=0.15, relx=0.55, rely=0.4)

        # Create a label for the third input field
        label3 = ctk.CTkLabel(master=self.tab("Environmental conditions"), text="Wind speed:",
                              font=('Helvetica bold', 26))
        label3.place(anchor=tk.N, relheight=0.07, relwidth=0.15, relx=0.4, rely=0.6)

        # Create the third input field
        entry3 = ctk.CTkEntry(master=self.tab("Environmental conditions"))
        entry3.place(anchor=tk.N, relheight=0.07, relwidth=0.15, relx=0.55, rely=0.6)

        button = ctk.CTkButton(master=self.tab("Environmental conditions"), text="Submit",
                               command=lambda: get_Environmental_conditions(entry1, entry2, entry3),
                               font=('Helvetica bold', 26))
        button.place(anchor=tk.N, relheight=0.07, relwidth=0.15, relx=0.5, rely=0.8)

        ################################################
        # ------- Tab passby measurements ------- #
        ################################################

        # ------create Plot object on GUI-----------
        # add figure canvas for laf
        canvas_laf = FigureCanvasTkAgg(fig, master=self.tab("Passby measurements"))
        canvas_laf.get_tk_widget().place(anchor=tk.E, relheight=0.5, relwidth=0.5, relx=0.5, rely=0.3)
        canvas_laf.draw()

        # add figure canvas for speed
        canvas_speed = FigureCanvasTkAgg(fig_speed, master=self.tab("Passby measurements"))
        canvas_speed.get_tk_widget().place(anchor=tk.E, relheight=0.5, relwidth=0.5, relx=1, rely=0.3)
        canvas_speed.draw()

        # Textbox displaying the speed
        textbox = ctk.CTkTextbox(master=self.tab("Passby measurements"))
        textbox.place(anchor=tk.E, relheight=0.05, relwidth=0.05, relx=0.7, rely=0.65)

        # start button
        start_button = ctk.CTkButton(master=self.tab("Passby measurements"), text="Start measurement",
                                     command=start_measurement, font=('Helvetica bold', 26))
        start_button.place(anchor=tk.W, relheight=0.1, relwidth=0.2, relx=0.05, rely=0.75)

        # stop button
        stop_button = ctk.CTkButton(master=self.tab("Passby measurements"), text="Stop measurement",
                                    command=stop_measurement, font=('Helvetica bold', 26))
        stop_button.place(anchor=tk.W, relheight=0.1, relwidth=0.2, relx=0.05, rely=0.9)

        custom_font = font.Font(size=18)
        vehicle_type_selection_listbox = tk.Listbox(master=self.tab("Passby measurements"), font= custom_font)
        vehicle_type_selection_listbox.place(anchor=tk.W, relheight=0.2, relwidth=0.2, relx=0.45, rely=0.75)

        take_measurement_button = ctk.CTkButton(master=self.tab("Passby measurements"), text="Take measurement",
                                                command=lambda: take_measurement(vehicle_type_selection_listbox),
                                                font=('Helvetica bold', 26))

        take_measurement_button.place(anchor=tk.W, relheight=0.05, relwidth=0.2, relx=0.45, rely=0.95)

        # Overview measurements

        listbox_measurements = tk.Listbox(master=self.tab("Passby measurements"), selectmode=tk.MULTIPLE,
                                          font=custom_font)
        listbox_measurements.place(anchor=tk.W, relheight=0.2, relwidth=0.2, relx=0.75, rely=0.75)

        if not len(measurements_list) == 0:
            for measurement in measurements_list:
                listbox_measurements.insert(tk.END, measurement)

        # delete button
        delete_button = ctk.CTkButton(master=self.tab("Passby measurements"), text="delete",
                                      command=lambda: delete_measurement(listbox_measurements),
                                      font=('Helvetica bold', 26))

        delete_button.place(anchor=tk.W, relheight=0.05, relwidth=0.1, relx=0.75, rely=0.95)

        update(canvas_laf, canvas_speed, textbox, listbox_measurements)


# App Class
class App(ctk.CTk):
    # The layout of the window will be written
    # in the init function itself
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sets the title of the window to "App"
        self.title("SPB measurements")
        # Sets the dimensions of the window to 600x700
        self.geometry(f"{appWidth}x{appHeight}")
        self.resizable(True, True)
        self.tab_view = MyTabView(master=self)
        self.tab_view.pack(expand=True, fill="both")


if __name__ == "__main__":
    XL2.init()
    app = App()
    speed_radar.init()
    # Used to run the application
    app.mainloop()

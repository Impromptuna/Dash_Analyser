from tkinter.filedialog import askdirectory

def select_directory():
	#Displays a file directory selection screen. Adds each file in the directory to a list.
	directory=askdirectory()
	return directory

def display_directory(directory:str, directory_label:str):
	"""Changes the directory display label to show the user-selected directory"""
	directory_label["text"]=directory

def select_and_display_directory(directory_label:str) -> str:
	"""Calls the other two functions in this file to allow a user to select a directory"""
	directory=select_directory()
	display_directory(directory, directory_label)
	return directory

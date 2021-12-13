from dash_analyser_application.GUIController import GUIController

"""Called by the entrypoint file outside the main directory. Calls the GUI controller file and displays the window to the user."""

def main():
    app=GUIController()
    app.resizable(False, True)
    app.mainloop()
import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import QThread, pyqtSignal

from lts_controller import LTSController

# To-Do: find a way to move the two in parallel, right now that means finding a way to know if the devices are still moving or not

# Note: this version of code is setup so that a second lts isn't required for testing purposes. Change line 165 from False to True to enable the use of the 2nd device.

# If needed in the future, it would be simple to add the ability to request a custom position in the user interface.

# This class controlls the user interface setup
class MainWindow(QWidget):
    # dictionary of locations ( these are random numbers for testing)
    LOCATIONS = {
    1: (8.0, 8.0),
    2: (10.0, 10.0),
    3: (12.0, 12.0),
    4: (14.0, 14.0),
    5: (16.0, 16.0),
    6: (20.0, 10.0),
    }

    def __init__(self, connect_y=True):
        super().__init__()

        # REMEMBER to change to correct serial number
        self.lts_x = LTSController("45863008")  # horizontal (NOTE: this is technically the serial # for the vertical device I just used it for testing)
        self.lts_x.connect()

        self.lts_y = None
        if connect_y:
            # REMEMBER to change to correct serial number
            self.lts_y = LTSController("11111111")  # vertical
            self.lts_y.connect()

        
        # Setting the visual appearance and titles of the gui
        self.setWindowTitle("LTS Control")
        self.resize(400, 300)
        self.buttons = []

        layout = QVBoxLayout()
        title = QLabel("Select a position:")
        title.setStyleSheet("font: 16pt 'Arial'; color: white;")
        layout.addWidget(title)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Generating the 6 buttons
        for i in range(6):
            coords = self.LOCATIONS[i + 1]
            button = QPushButton(f"Position {i+1}: ({coords[0]}, {coords[1]})")
            button.setCheckable(True)
            button.clicked.connect(lambda checked, n=i+1: self.on_click(n))
            layout.addWidget(button)
            self.buttons.append(button)
        self.setLayout(layout)

    # determining what happens when a button is clicked
    def on_click(self,n):
        print(f"Button {n} pressed")
        button = self.sender()
        
        # this disables the buttons until movement is finished
        for b in self.buttons:
            b.setEnabled(False)

        button.setChecked(True)  # Turn button green when clicked

        # this is the position of the button that was pressed
        x_target, y_target = self.LOCATIONS[n]

        # this runs the code to interact with the lts devices
        self.worker = Worker(self.lts_x, self.lts_y, x_target, y_target, n)
        self.worker.finished.connect(self.on_motion_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    # this re-enables the buttons after moving the devices and sets the buttons to green
    def on_motion_finished(self, n):
        print(f"Motion finished for button {n}")

        # this renables the buttons once the devices have stopped moving
        for b in self.buttons:
            b.setEnabled(True)

        # Turn the pressed button back to red when done moving
        self.buttons[n - 1].setChecked(False)

    # this makes sure that the devices are properly disconnected when the gui window is closed
    def closeEvent(self, event):
        self.lts_x.disconnect()
        if self.lts_y:
            self.lts_y.disconnect()
        event.accept()

    def on_error(self, msg):
        print("Error:", msg)
        for b in self.buttons:
            b.setEnabled(True)

# This class interacts with the LTS devices using the lts_controller.py file
class Worker(QThread):
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
    
    #defining the variables for the devices and positions
    def __init__(self, controller_x, controller_y, x_pos, y_pos, button_id):
        super().__init__()
        self.controller_x = controller_x
        self.controller_y = controller_y
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.button_id = button_id

    # telling the devices to move
    def run(self):
        try:
            self.controller_x.move_to(self.x_pos)

            if self.controller_y:
                self.controller_y.move_to(self.y_pos)

            # attempt to make the devices move at the same time, working on this next
            """
            while self.controller_x.is_moving() or self.controller_y.is_moving():
                time.sleep(0.05)
            """

            self.finished.emit(self.button_id)

        except Exception as e:
            self.error.emit(str(e))

        # testing functionality
        """
        print(f"Starting movement for button {self.button_id}")
        import time
        time.sleep(3)  # simulate device motion
        print(f"Finished movement for button {self.button_id}")
        self.finished.emit(self.button_id)"""
    

app = QApplication(sys.argv)

# This controls the appearance of the gui
app.setStyleSheet("""
    QPushButton {
        background-color: #8f1f1f; 
        color: white; 
        border-radius: 10px;
        padding: 8px;
    }
    
    QPushButton:checked {
        background-color: #4CAF50; 
        color: white;
    }
""")

# Make sure to change this line to True if using both devices instead of just one
window = MainWindow(connect_y=False)
window.show()
sys.exit(app.exec())



                                                    
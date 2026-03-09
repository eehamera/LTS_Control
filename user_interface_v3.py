import sys
import time
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,QHBoxLayout, QGridLayout, QGroupBox, QLineEdit)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont


USE_MOCK = False
ENABLE_MANUAL_POSITION = True
# --------------------------------
# Mock controller (no hardware required)
# --------------------------------
class MockLTSController:
    def __init__(self, serial_number):
        self.serial = serial_number
        self._moving = False

    def connect(self):
        print(f"[MOCK] Connected to device {self.serial}")

    def disconnect(self):
        print(f"[MOCK] Disconnected device {self.serial}")

    def move_to(self, position):
        print(f"[MOCK] Device {self.serial} moving to {position}")
        self._moving = True
        time.sleep(1)  # simulate movement
        self._moving = False
        print(f"[MOCK] Device {self.serial} finished moving")

    def is_moving(self):
        return self._moving

# --------------------------------
# Use real or mock controller
# --------------------------------
if not USE_MOCK:
    from lts_controller import LTSController
else:
    LTSController = MockLTSController

# --------------------------------
# GUI
# --------------------------------
class MainWindow(QWidget):

    LOCATIONS = {
        1: (8.0, 70.0),
        2: (10.0, 30.0),
        3: (12.0, 12.0),
        4: (14.0, 14.0),
        5: (16.0, 16.0),
        6: (20.0, 10.0),
        7: (12.0, 12.0),
        8: (14.0, 14.0),
        9: (16.0, 16.0),
       10: (0.0, 0.0),
       11: (0.0, 0.0)
    }

    def __init__(self, connect_y=True):
        super().__init__()

        # Initialize controllers
        self.lts_x = LTSController("45863391")
        self.lts_x.connect()

        self.lts_y = None
        if connect_y:
            self.lts_y = LTSController("45863008")
            self.lts_y.connect()

        self.setWindowTitle("LTS Control")
        self.resize(900, 400)
        self.buttons = []

        self.active_button_index = None  # track which button is currently active

        self.status_label = QLabel("Current position: None")
        self.status_label.setStyleSheet("color: white; font: 14pt 'Arial';")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: black;
            font: 14pt 'Arial';
            background-color: #D3D3D3;   /* dark gray background */
            border: 2px solid black;     /* white outline */
            border-radius: 10px;         /* rounded corners */
            padding: 8px;                /* spacing inside the box */
        """)

        self.reset_button = QPushButton("RESET")
        self.reset_button.setMinimumHeight(70)
        self.reset_button.setStyleSheet("""
            QPushButton {
                color: black;
                font: 18pt 'Arial';
                background-color: #FFBE30;
                border: 2px solid black;
                border-radius: 10px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #C0C0C0;
            }

            QPushButton:pressed {
                background-color: #AAAAAA;
            }
        """)

        self.reset_button.clicked.connect(lambda: self.on_click(11))
        
        # Main layout
        main_layout = QVBoxLayout()
        #title = QLabel("Select a position:")
        #title.setStyleSheet("font: 28pt 'Arial'; color: black; font-weight: bold;")
        #main_layout.addWidget(title)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Horizontal layout for two columns
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(40)  # space between left and right group

        # -----------------------
        # LEFT GROUP: 2x3 grid
        # -----------------------
        left_group = QGroupBox("Large Sample Holder")
        left_group.setFont(QFont("Arial", 24))  # 24pt font size
        left_group.setStyleSheet("""
            QGroupBox {
                border: 3px solid black;
                border-radius: 10px;
                margin-top: 20px;    /*reduce top margin */
                padding: 10px;
                color: white;
            }

            QGroupBox::title {
                subcontrol-origin: margin;          /* measure from outside */
                subcontrol-position: top center;    /* above the border */
                padding: 0 10px;                     /*extra horizontal padding */
                background-color: #FFFFFF;          /* matches window bg to “lift” title */
                font-size: 60pt;
                font-weight: bold;
                color: black;
            }
        """)
        left_grid = QGridLayout()
        left_grid.setContentsMargins(20, 1, 20, 1)
        left_grid.setSpacing(20)
        left_group.setLayout(left_grid)
        left_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for i in range(6):
            coords = self.LOCATIONS[i + 1]
            button = QPushButton(f"{i+1}")
            #button = QPushButton(f"{i+1}: ({coords[0]}, {coords[1]})")
            button.setCheckable(True)
            button.setMinimumHeight(120)
            #button.setMaximumWidth(140)
            button.setStyleSheet("font: 20pt 'Arial';")
            button.clicked.connect(lambda checked, n=i+1: self.on_click(n))

            row = i // 3  # 2 rows
            col = i % 3   # 3 columns
            left_grid.addWidget(button, row, col)
            self.buttons.append(button)
        #for r in range(2):
        #   left_grid.setRowStretch(r, 1)

        for c in range(3):
            left_grid.setColumnStretch(c, 1)

        # -----------------------
        # RIGHT GROUP: 2x2 grid
        # -----------------------
        right_group = QGroupBox("Small Sample Holder")
        right_group.setFont(QFont("Arial", 24))  # 24pt font size
        right_group.setStyleSheet("""
            QGroupBox {
                border: 3px solid black;
                border-radius: 10px;
                margin-top: 20px;   /* reduce top margin */
                padding: 10px;
                color: black;
            }

            QGroupBox::title {
                subcontrol-origin: margin;          /* measure from outside */
                subcontrol-position: top center;    /* above the border */
                padding: 0 10px;                    /* extra horizontal padding */
                background-color: #FFFFFF;          /* matches window bg to “lift” title */
                font-size: 60pt;
                font-weight: bold;
                color: black;
            }                     
        """)
        right_grid = QGridLayout()
        #right_grid.setContentsMargins(10, 2, 10, 10)
        #right_grid.setVerticalSpacing(2)
        #right_grid.setHorizontalSpacing(20)
        right_group.setLayout(right_grid)
        right_grid.setSpacing(20)
        right_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        positions = [7, 8, 9, 10]
        button_names = [1, 2, 3, 4]

        for idx, pos in enumerate(positions):
            coords = self.LOCATIONS[pos]
            button = QPushButton(f"{button_names[idx]}")
            #button = QPushButton(f"{button_names[idx]}: ({coords[0]}, {coords[1]})")
            button.setCheckable(True)
            button.setMinimumHeight(120)
            button.setMinimumWidth(120)
            button.setStyleSheet("font: 20pt 'Arial';")
            button.clicked.connect(lambda checked, n=pos: self.on_click(n))

            row = idx // 2
            col = idx % 2
            right_grid.addWidget(button, row, col)
            self.buttons.append(button)
        #for r in range(2):
        #    right_grid.setRowStretch(r, 1)

        #for c in range(2):
        #    right_grid.setColumnStretch(c, 1)

        main_layout.addWidget(self.status_label)
        main_layout.addSpacing(10)  # optional spacing

        # Add groups to columns layout
        columns_layout.addWidget(left_group)
        columns_layout.addWidget(right_group)
        main_layout.addStretch()

        main_layout.addLayout(columns_layout)

        main_layout.addSpacing(20)
        main_layout.addWidget(self.reset_button)

        if ENABLE_MANUAL_POSITION:

            manual_layout = QHBoxLayout()

            self.x_input = QLineEdit()
            self.x_input.setPlaceholderText("X position")
            self.x_input.setMaximumWidth(150)

            self.y_input = QLineEdit()
            self.y_input.setPlaceholderText("Y position")
            self.y_input.setMaximumWidth(150)

            self.manual_move_button = QPushButton("Enter")
            self.manual_move_button.setMaximumHeight(40)
            self.manual_move_button.setMaximumWidth(80)
            self.manual_move_button.setStyleSheet("font-size: 12pt; padding: 4px;")
            self.manual_move_button.clicked.connect(self.manual_move)

            manual_layout.addWidget(self.x_input)
            manual_layout.addWidget(self.y_input)
            manual_layout.addWidget(self.manual_move_button)
            self.x_input.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    color: black;
                    border: 2px solid black;
                    padding: 4px;
                    font-size: 12pt;
                }
            """)

            self.y_input.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    color: black;
                    border: 2px solid black;
                    padding: 4px;
                    font-size: 12pt;
                }
            """)

            main_layout.addSpacing(10)
            manual_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addLayout(manual_layout)
            
        
        self.setLayout(main_layout)
        main_layout.addStretch()

    # -----------------------
    # Button logic
    # -----------------------
    def on_click(self, n):
        print(f"Button {n} pressed")

        for b in self.buttons:
            b.setEnabled(False)
        if n<=10:
            if self.active_button_index is not None:
                self.buttons[self.active_button_index].setChecked(False)

            # Check the new active button
            self.buttons[n - 1].setChecked(True)
            self.active_button_index = n - 1  # store new active button

        if n <=6:
            self.status_label.setText(f"Moving to position: {n}")
        elif n <= 10:
            self.status_label.setText(f"Moving to position: {n-6}")
        else:
            self.status_label.setText("Resetting position")

        self.status_label.setStyleSheet("""
            color: black;
            font: 14pt 'Arial';
            background-color: #FFBE30;   /* yellow */
            border: 2px solid black;
            border-radius: 10px;
            padding: 8px;
        """)

        x_target, y_target = self.LOCATIONS[n]
        self.worker = Worker(self.lts_x, self.lts_y, x_target, y_target, n)
        self.worker.finished.connect(self.on_motion_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_motion_finished(self, n):
        print(f"Motion finished for button {n}")
        for b in self.buttons:
            b.setEnabled(True)
        if n == 11:
            for b in self.buttons:
                b.setChecked(False)
            self.active_button_index = None

        # Update label with the reached position
        if n <=6:
            self.status_label.setText(f"Current position: {n}")
        elif n <= 10:
            self.status_label.setText(f"Current position: {n-6}")
        elif n == 12:
            self.status_label.setText("Manual Position set")
        else:
            self.status_label.setText("Position reset")
        self.status_label.setStyleSheet("""
            color: black;
            font: 14pt 'Arial';
            background-color: #4CAF50;   /* green */
            border: 2px solid black;
            border-radius: 10px;
            padding: 8px;
        """)
        if ENABLE_MANUAL_POSITION:
            self.manual_move_button.setEnabled(True)
        self.reset_button.setEnabled(True)

    def manual_move(self):
        try:
            x_target = float(self.x_input.text())
            y_target = float(self.y_input.text())

            print(f"Manual move to {x_target}, {y_target}")

            for b in self.buttons:
                b.setEnabled(False)

            self.reset_button.setEnabled(False)
            self.manual_move_button.setEnabled(False)

            self.status_label.setText("Moving to manual position")

            self.worker = Worker(self.lts_x, self.lts_y, x_target, y_target, 12)
            self.worker.finished.connect(self.on_motion_finished)
            self.worker.error.connect(self.on_error)
            self.worker.start()

        except ValueError:
            self.status_label.setText("Invalid manual position")

    def closeEvent(self, event):
        self.lts_x.disconnect()
        if self.lts_y:
            self.lts_y.disconnect()
        event.accept()

    def on_error(self, msg):
        print("Error:", msg)
        for b in self.buttons:
            b.setEnabled(True)

# -----------------------
# Worker thread
# -----------------------
class Worker(QThread):
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, controller_x, controller_y, x_pos, y_pos, button_id):
        super().__init__()
        self.controller_x = controller_x
        self.controller_y = controller_y
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.button_id = button_id

    def run(self):
        try:
            self.controller_x.move_to(self.x_pos)
            if self.controller_y:
                self.controller_y.move_to(self.y_pos)
            self.finished.emit(self.button_id)
        except Exception as e:
            self.error.emit(str(e))

# -----------------------
# Run app
# -----------------------
app = QApplication(sys.argv)

app.setStyleSheet("""
    QWidget {
        background-color: #FFFFFF;
    }

    QPushButton {
        background-color: #8f1f1f;
        color: white;
        border-radius: 12px;
        padding: 12px;
        font-size: 60pt;
        font-weight: bold;
    }

    QPushButton:checked {
        background-color: #4CAF50;
        color: white;
    }

    QPushButton:hover {
        background-color: #a32929;
    }
""")

window = MainWindow(connect_y=True)
window.show()
sys.exit(app.exec())
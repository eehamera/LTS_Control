import sys
import time
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,QHBoxLayout, QGridLayout, QGroupBox, QLineEdit, QTabWidget)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont


USE_MOCK = True
ENABLE_MANUAL_POSITION = True
xg1 = 0.0
yg1 = 0.0
xg2 = 0.0
yg2 = 0.0
# --------------------------------
# Mock controller (don't need connection to LTS devices to run)
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
        time.sleep(1) 
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
    # ADJUST THE LOCATIONS THE BUTTONS CORRESPOND TO HERE
    LOCATIONS = {
        # 96 SAMPLE HOLDER
        1: (130.0, 182.0),
        2: (95.0, 182.0),
        3: (58.0, 182.0),
        4: (130.0, 147.0),
        5: (95.0, 147.0),
        6: (58.0, 147.0),
        # 6 SAMPLE HOLDER (renamed 1-4 in gui)
        7: (138.0, 167.0),
        8: (111.0, 167.0),
        9: (138.0, 140.0),
       10: (111.0, 140.0),
       #RESET (if you press this button before closing the application its much quicker to start up again)
       11: (0.0, 0.0),
       # 24 SAMPLE HOLDER
       12: (129.0 + xg1, 187.0 + yg1),
       13: (91.0 + xg1, 187.0 + yg1),
       14: (53.0 + xg1, 187.0 + yg1),
       15: (129.0 + xg1, 149.0 + yg1),
       16: (91.0 + xg1, 149.0 + yg1),
       17: (53.0 + xg1, 149.0 + yg1),
       # 12 SAMPLE HOLDER
       18: (138.0 + xg2, 167.0 + yg2), 
       19: (111.0 + xg2, 167.0 + yg2),
       20: (84.0 + xg2, 167.0 + yg2),
       21: (57.0 + xg2, 167.0 + yg2),
       22: (30.0 + xg2, 167.0 + yg2),
       23: (3.0 + xg2, 167.0 + yg2),
       24: (138.0 + xg2, 140.0 + yg2),
       25: (111.0 + xg2, 140.0 + yg2),
       26: (84.0 + xg2, 140.0 + yg2),
       27: (57.0 + xg2, 140.0 + yg2),
       28: (30.0 + xg2, 140.0 + yg2),
       29: (3.0 + xg2, 140.0 + yg2),
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
        self.button_map = {}

        self.active_button_index = None 


        # Creating a status label
        #-------------------------------------------------------------
        self.status_group = QGroupBox("Status")
        self.status_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid black;
                border-radius: 10px;
                margin-top: 12px;
                font: bold 14pt 'Arial';
            }

            QGroupBox::title {
                color: black;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                background-color: #FFFFFF;
            }
        """)

        self.status_label = QLabel("Current position: None")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_label.setStyleSheet("""
            color: black;
            font: 14pt 'Arial';
            background-color: #D3D3D3;
            border-radius: 6px;
            padding: 8px;
        """)

        status_layout = QVBoxLayout()
        status_layout.addWidget(self.status_label)

        self.status_group.setLayout(status_layout)
        #-------------------------------------------------------------

        # Creating a reset button
        #-------------------------------------------------------------
        self.reset_button = QPushButton("RESET")
        self.reset_button.setMinimumHeight(70)
        self.reset_button.setStyleSheet("""
                                                                    
            QPushButton {
                color: black;
                font: 18pt 'Arial';
                background-color: #89CFF0;
                border: 2px solid black;
                border-radius: 10px;
                padding: 8px;
            }


            QPushButton:pressed {
                background-color: #AAAAAA;
            }
        """)

        self.reset_button.clicked.connect(lambda: self.on_click(11))
        #-------------------------------------------------------------
        
        # Main layout
        #-------------------------------------------------------------
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #89CFF0;
                color: black;
                font-size: 18pt;
                padding: 10px 20px;
                min-width: 200px;
                height: 50px;

                border: 2px solid black;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }

            QTabBar::tab:selected {
                background: #4CAF50;
                color: black;
            }

            /* hovered NON-selected tabs */
            QTabBar::tab:hover:!selected {
                background: #6FB7E9;
                color: white;               
            }

            /* hovered selected tab stays green */
            QTabBar::tab:selected:hover {
                background: #4CAF50;
                color: white;
            }

            QTabWidget::pane {
                border: 2px solid black;
                top: -1px;
            }
        """)
        

        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)


        #-------------------------------------------------------------
        # 96 Sample Holder
        #-------------------------------------------------------------
        g96 = QGroupBox("96 Sample Holder")
        g96.setFont(QFont("Arial", 18)) 
        
        grid96 = QGridLayout()
        g96.setLayout(grid96)
        grid96.setSpacing(20)
        grid96.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for i in range(6):
            button = QPushButton(f"{i+1}")
            button.setCheckable(True)
            button.setMinimumHeight(140)
            button.setMinimumWidth(140)
            button.setStyleSheet("font: 20pt 'Arial';")
            button.clicked.connect(lambda checked, n=i+1: self.on_click(n))

            row = i // 3  
            col = i % 3   
            grid96.addWidget(button, row, col)
            self.buttons.append(button)
            self.button_map[i + 1] = button

        page96 = QWidget()
        page_layout96 = QVBoxLayout()
        page_layout96.addWidget(g96)
        page96.setLayout(page_layout96)

        self.tabs.addTab(page96, "96 Sample Holder")

        #-------------------------------------------------------------
        # 6 Sample Holder
        #-------------------------------------------------------------
        g6 = QGroupBox("6 Sample Holder")
        g6.setFont(QFont("Arial", 18))

        grid6 = QGridLayout()
        g6.setLayout(grid6)
        grid6.setSpacing(20)
        grid6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        positions = [7, 8, 9, 10]
        button_names = [1, 2, 3, 4]

        for idx, pos in enumerate(positions):
            button = QPushButton(f"{button_names[idx]}")
            button.setCheckable(True)
            button.setMinimumHeight(140)
            button.setMinimumWidth(140)
            button.setStyleSheet("font: 20pt 'Arial';")
            button.clicked.connect(lambda checked, n=pos: self.on_click(n))

            row = idx // 2
            col = idx % 2
            grid6.addWidget(button, row, col)
            self.buttons.append(button)
            self.button_map[pos] = button
        
        page6 = QWidget()
        page_layout6 = QVBoxLayout()
        page_layout6.addWidget(g6)
        page6.setLayout(page_layout6)
        #self.tabs.addTab(page6, "6 Sample Holder")

        #-------------------------------------------------------------
        # 24 sample holder
        #-------------------------------------------------------------
        g24 = QGroupBox("24 Sample Holder")
        g24.setFont(QFont("Arial", 18))

        grid24 = QGridLayout()
        g24.setLayout(grid24)
        grid24.setSpacing(20)
        grid24.setAlignment(Qt.AlignmentFlag.AlignCenter)

        positions = [12, 13, 14, 15, 16, 17]
        button_names = [1, 2, 3, 4, 5, 6]

        for idx, pos in enumerate(positions):
            button = QPushButton(f"{button_names[idx]}")
            button.setCheckable(True)
            button.setMinimumHeight(140)
            button.setMinimumWidth(140)
            button.setStyleSheet("font: 20pt 'Arial';")
            button.clicked.connect(lambda checked, n=pos: self.on_click(n))

            row = idx // 3
            col = idx % 3
            grid24.addWidget(button, row, col)
            self.buttons.append(button)
            self.button_map[pos] = button

        page24 = QWidget()
        page_layout24 = QVBoxLayout()
        page_layout24.addWidget(g24)
        page24.setLayout(page_layout24)

        self.tabs.addTab(page24, "24 Sample Holder")

        #-------------------------------------------------------------
        # 12 sample holder 
        #-------------------------------------------------------------
        g12 = QGroupBox("12 Sample Holder")
        g12.setFont(QFont("Arial", 18))
        grid12 = QGridLayout()
        g12.setLayout(grid12)
        grid12.setSpacing(20)
        grid12.setAlignment(Qt.AlignmentFlag.AlignCenter)

        positions = [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
        button_names = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        for idx, pos in enumerate(positions):
            button = QPushButton(f"{button_names[idx]}")
            button.setCheckable(True)
            button.setMinimumHeight(120)
            button.setMinimumWidth(120)
            button.setStyleSheet("font: 20pt 'Arial';")
            button.clicked.connect(lambda checked, n=pos: self.on_click(n))

            row = idx // 6
            col = idx % 6
            grid12.addWidget(button, row, col)
            self.buttons.append(button)
            self.button_map[pos] = button

        page12 = QWidget()
        page_layout12 = QVBoxLayout()
        page_layout12.addWidget(g12)
        page12.setLayout(page_layout12)

        #self.tabs.addTab(page12, "12 Sample Holder")


        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.status_group)
        main_layout.addSpacing(10) 


        main_layout.addStretch()

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

    # -----------------------
    # Button logic
    # -----------------------
    # Controls what happens when a button is pressed
    def on_click(self, n):
        print(f"Button {n} pressed")

        for b in self.buttons:
            b.setEnabled(False)
        self.reset_button.setEnabled(False)

        if n != 11:
            if self.active_button_index is not None:
                self.button_map[self.active_button_index].setChecked(False)

            # Check the new active button
            self.button_map[n].setChecked(True)
            self.active_button_index = n  # store new active button
        if n <=6:
            self.status_label.setText(f"Moving to position: {n}")
        elif n <= 10:
            self.status_label.setText(f"Moving to position: {n-6}")
        elif n >= 12:
            self.status_label.setText(f"Moving to position: {n-11}")
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
    # controls what happens when the device is done moving
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
        elif 12 <= n <= 17:
            self.status_label.setText(f"Current position: {n-11}")
        elif n == 99:
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
        
        self.manual_move_button.setEnabled(True)
        self.reset_button.setEnabled(True)
    # adds ability to move to user defined positions
    def manual_move(self):
        try:
            x_target = float(self.x_input.text())
            y_target = float(self.y_input.text())

            print(f"Manual move to {x_target}, {y_target}")

            if self.active_button_index is not None:
                self.button_map[self.active_button_index].setChecked(False)
                self.active_button_index = None

            for b in self.buttons:
                b.setEnabled(False)

            self.reset_button.setEnabled(False)
            self.manual_move_button.setEnabled(False)

            self.status_label.setText("Moving to manual position")
            self.status_label.setStyleSheet("""
                color: black;
                font: 14pt 'Arial';
                background-color: #FFBE30;   /* yellow */
                border: 2px solid black;
                border-radius: 10px;
                padding: 8px;
            """)
            self.worker = Worker(self.lts_x, self.lts_y, x_target, y_target, 99)
            self.worker.finished.connect(self.on_motion_finished)
            self.worker.error.connect(self.on_error)
            self.worker.start()

        except ValueError:
            self.status_label.setText("Invalid manual position")
    # disconnects the lts devices when the window is closed
    def closeEvent(self, event):
        self.lts_x.disconnect()
        if self.lts_y:
            self.lts_y.disconnect()
        event.accept()

    def on_error(self, msg):
        print("Error:", msg)
        for b in self.buttons:
            b.setEnabled(True)

        self.reset_button.setEnabled(True)
        self.manual_move_button.setEnabled(True)

# -----------------------
# Worker thread, this is what talks to the lts devices through lts_controller.py and moves them
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

    
""")

window = MainWindow(connect_y=False)
window.show()
sys.exit(app.exec())
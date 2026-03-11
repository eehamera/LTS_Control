import time
import clr
from System import Decimal

#if these files don't rely on any others maybe I can create a folder with everything needed to run this application
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.IntegratedStepperMotorsCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *

# IF THE DEVICES ARE NOT CONNECTING, MAKE THE DELAYS LONGER IN THIS CODE (this is because the usb cables are so long)


class LTSController:
    #setting serial number of device
    def __init__(self, serial_no):
        self.serial_no = serial_no
        self.device = None

    # this contains all the setup/initialization parameters
    def connect(self):
        DeviceManagerCLI.BuildDeviceList()

        self.device = LongTravelStage.CreateLongTravelStage(self.serial_no)
        self.device.Connect(self.serial_no)

        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(20000)
            assert self.device.IsSettingsInitialized() is True

        if self.device.IsSettingsInitialized():
            self.device.StartPolling(250)
            time.sleep(0.5)
            self.device.EnableDevice()
            time.sleep(0.5)

            motor_config = self.device.LoadMotorConfiguration(self.serial_no)

            # Get parameters related to homing/zeroing/other
            home_params = self.device.GetHomingParams()
            #print(f'Homing velocity: {home_params.Velocity}\n,'
            #    f'Homing Direction: {home_params.Direction}')
            #ISSUE: I can't seem to be able to change the homing velocity
            home_params.MinVelocity = Decimal(30.0)  # real units, mm/s
            # Set homing params (if changed)
            self.device.SetHomingParams(home_params)

            try:
                #use this to control the veloctity of the devices
                vel_params = self.device.GetVelocityParams()
                vel_params.MaxVelocity = Decimal(30.0) 
                self.device.SetVelocityParams(vel_params)
            except Exception as e:
                print(f"Warning: could not set velocity params for {self.serial_no}: {e}")

            #home device 
            # NOTE: Currently trying to eliminate the time in the parentheses since its taking too long UPDATE: doesn't work so Im just leaving this as a very large time delay.
            
            self.device.Home(100000)
            print("Device connected")

        else:
            print(f"Device {self.serial_no} failed to initialize.")
                      
    # this isn't currently used in the application but can be used to send the device back to zero
    #IMPORTANT: This needs to be done at the beginning to make sure the position is accurate
    #def home(self):
    #    self.device.Home(60000)

    # this is used to move the devices to specified positions
    def move_to(self, position_mm):
        pos = Decimal(position_mm)
        self.device.MoveTo(pos, 60000)

    def disconnect(self):
        self.device.StopPolling()
        self.device.Disconnect()
    

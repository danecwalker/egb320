import time
import math
from DFRobot_DC_Motor_IIC import DFRobot_DC_Motor_IIC  # Ensure this is the correct library for your motor driver
from board import Board  # Ensure to import the Board class from your library

# Constants
GEAR_RATIO = 43  # Adjust this based on your motor's specifications
PWM_FREQUENCY = 1000  # Frequency in Hz
MAX_SPEED = 95  # Maximum duty ratio (0-100)
ENCODER_CPR = 12  # Counts per revolution of the encoder
WHEEL_DIAMETER = 0.065  # Diameter of the wheel in meters
WHEEL_CIRCUMFERENCE = math.pi * WHEEL_DIAMETER  # Circumference in meters
TRACK_WIDTH = 0.1  # Distance between the two wheels in meters (adjust as necessary)

# Initialize the board
board = Board(1, 0x10)  # Adjust I2C address as necessary

# Step 1: Enable the Encoder
board.set_encoder_enable([board.M1, board.M2])  # Enable encoders for both motors

# Step 2: Set the motor reduction ratio
board.set_encoder_reduction_ratio(board.M1, GEAR_RATIO)
board.set_encoder_reduction_ratio(board.M2, GEAR_RATIO)

# Step 3: Set the PWM frequency
board.set_moter_pwm_frequency(PWM_FREQUENCY)

def move_motors(distance, angle):
    # Calculate the number of encoder ticks needed for the movement
    distance_ticks = (distance / WHEEL_CIRCUMFERENCE) * ENCODER_CPR * GEAR_RATIO  # ticks to move forward
    angle_ticks = (angle / 360) * (TRACK_WIDTH * math.pi) * (ENCODER_CPR / GEAR_RATIO)  # ticks for rotation

    # Moving straight
    if distance != 0:
        board.motor_movement(board.M1, board.CW, MAX_SPEED)
        board.motor_movement(board.M2, board.CW, MAX_SPEED)
        
        # Reset encoder counts
        board.set_encoder_value(board.M1, 0)
        board.set_encoder_value(board.M2, 0)

        while True:
            count_m1 = board.get_encoder_value(board.M1)
            count_m2 = board.get_encoder_value(board.M2)
            print(f"Moving: M1 Count: {count_m1}, M2 Count: {count_m2}")

            if count_m1 >= distance_ticks and count_m2 >= distance_ticks:
                break
            time.sleep(0.1)  # Read encoder values every 100ms

        board.motor_movement(board.M1, board.STOP)
        board.motor_movement(board.M2, board.STOP)
        print("Reached desired distance.")

    # Rotating
    if angle != 0:
        if angle > 0:  # Clockwise rotation
            board.motor_movement(board.M1, board.CCW, MAX_SPEED)
            board.motor_movement(board.M2, board.CW, MAX_SPEED)
        else:  # Counter-clockwise rotation
            board.motor_movement(board.M1, board.CW, MAX_SPEED)
            board.motor_movement(board.M2, board.CCW, MAX_SPEED)

        # Reset encoder counts
        board.set_encoder_value(board.M1, 0)
        board.set_encoder_value(board.M2, 0)

        while True:
            count_m1 = board.get_encoder_value(board.M1)
            count_m2 = board.get_encoder_value(board.M2)
            print(f"Rotating: M1 Count: {count_m1}, M2 Count: {count_m2}")

            if abs(count_m1) >= angle_ticks and abs(count_m2) >= angle_ticks:
                break
            time.sleep(0.1)  # Read encoder values every 100ms

        board.motor_movement(board.M1, board.STOP)
        board.motor_movement(board.M2, board.STOP)
        print("Reached desired angle.")

def handle_user_commands(command):
    # Example command handling; you may want to use more robust parsing logic
    parts = command.split()
    if len(parts) == 3 and parts[0].lower() == 'move':
        distance = int(parts[1])  # Distance in mm
        angle = int(parts[2])  # Angle in degrees
        move_motors(distance / 1000, angle)  # Convert distance to meters

if __name__ == "__main__":
    while True:
        user_command = input("Enter command (e.g., 'move 20 0'): ")
        handle_user_commands(user_command)
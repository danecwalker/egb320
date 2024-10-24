#!/usr/bin/python

import time
from modules.vision import take_picture, check_for_yellow, check_for_circle
from modules.motors import move_motors

target_lane = 3

class State:
	def __init__(self, robot):
		self.robot = robot

	def advance(self):
		pass

	def process(self):
		pass

class MovingForward(State):
	def __init__(self, robot):
		print("Moving forward")
		self.robot = robot
		self.next_state = None

	def advance(self):
		self.robot.state = self.next_state

	def process(self):
		move_motors(2, 0)
		self.next_state = Discovering(self.robot)

class Aligning(State):
	def __init__(self, robot):
		print("Aligning")
		self.robot = robot
		self.next_state = None

	def advance(self):
		self.robot.state = self.next_state

	def process(self):
		# check for circle marker
		frame = take_picture()
		_, _, offset = check_for_circle(frame)
		if abs(offset) < 5:
			self.next_state = MovingForward(self.robot)
		elif offset < 0:
			move_motors(0, 90)
			move_motors(2, 0)
			move_motors(0, -90)
		else:
			move_motors(0, -90)
			move_motors(2, 0)
			move_motors(0, 90)
		self.next_state = Aligning(self.robot)

class FindMarker(State):
	def __init__(self, robot):
		print("Finding marker")
		self.robot = robot
		self.next_state = None

	def advance(self):
		self.robot.state = self.next_state

	def process(self):
		# turn 90 degrees to the right
		move_motors(0, -90)
		# check for circle marker
		frame = take_picture()
		circles, _, _ = check_for_circle(frame)
		# if circle detected, self.next_state = Aligning(self.robot)
		if circles == target_lane:
			self.next_state = Aligning(self.robot)
		else:
			move_motors(0, 90)
			move_motors(10, 0)
			self.next_state = FindMarker(self.robot)

class Discovering(State):
	def __init__(self, robot):
		print("Discovering location")
		self.robot = robot
		self.next_state = None


	def advance(self):
		self.robot.state = self.next_state

	def process(self):
		# turn 10 degrees
		move_motors(0, 5)
		# check for yellow
		frame = take_picture()
		yellow = check_for_yellow(frame)
		if yellow:
			self.next_state = FindMarker(self.robot)
		else:
			self.next_state = Discovering(self.robot)
		

class Idle(State):
	def __init__(self, robot):
		print("Idle state")
		self.robot = robot

	def advance(self):
		self.robot.state = Discovering(self.robot)

class Robot:
	def __init__(self):
		self.state = Idle(self)

	def advance(self):
		print("Advancing")
		self.state.advance()

	def process(self):
		if self.state is not None:
			self.state.process()
		else:
			print("No state")
			exit()

def main():
	robot = Robot()

	while True:
		robot.advance()
		robot.process()

if __name__ == "__main__":
	main()
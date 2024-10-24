from picamera2 import Picamera2
import numpy as np
import cv2

# Known diameter of the object in mm (e.g., a coin)
known_diameter_mm = 10  # Example: a 50 mm diameter object
focal_length = 30  # Example: calibrated focal length in pixels (you need to adjust this based on your setup)


picam2 = Picamera2()
picam2.start()

def take_picture():
  frame = picam2.capture_array()
  return frame

def check_for_yellow(frame):
# Convert the image to HSV color space YELLOW
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

  # Define lower and upper bounds for the color you want to segment
  # For example, let's segment the color blue
  lower_yellow = np.array([20, 100, 100])
  upper_yellow = np.array([30, 255, 255])

  # Create a mask using the defined bounds
  mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

  # Find contours in the masked image
  contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  if len(contours) == 0:
      return False
      

  # Draw contours on the original image
  for contour in contours:
      # Calculate the center of the contour
      M = cv2.moments(contour)
      if M['m00'] != 0:
          cx = int(M['m10']/M['m00'])
          cy = int(M['m01']/M['m00'])
          # Draw the center point
          print(f"Center of yellow: ({cx}, {cy})")

  return True

def check_for_circle(frame):
  # Convert the frame to grayscale
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  
  # Apply Gaussian blur to reduce noise and improve circle detection
  gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2)
  
  # Detect circles in the frame using HoughCircles
  circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                          param1=100, param2=60, minRadius=20, maxRadius=100)
  
  # If circles are detected
  if circles is not None:
      # Convert the circle parameters a, b and r to integers
      circles = np.round(circles[0, :]).astype("int")
      circle_count = len(circles)
      # Loop over the detected circles
      for (x, y, r) in circles:
          # Draw the circle in the output frame
          cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
          cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
          
          # Calculate diameter in pixels
          detected_diameter_pixels = 2 * r
          
          # Calculate distance to the object
          distance_mm = (known_diameter_mm * focal_length) / detected_diameter_pixels

          # determine the offset to the center of the frame
          offset = x - frame.shape[1] / 2
          
  else:
      circle_count = 0

  return circle_count, distance_mm, offset
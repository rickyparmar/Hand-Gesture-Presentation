import tkinter as tk
import cv2
import aspose.slides as slides
import aspose.pydrawing as drawing
from tkinter import filedialog
from cvzone.HandTrackingModule import HandDetector
import os
import numpy as np
from tkinter import ttk
import mediapipe as mp
from tkinter import messagebox
import pyautogui

import glob

def delete_images_in_data_folder():
    folder_path = "data"
    if os.path.exists(folder_path):
        files = glob.glob(os.path.join(folder_path, "*.png"))  # Adjust the file extension as needed
        for file in files:
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Error deleting file {file}: {e}")

new=None
camera_source = 0

def set_builtin_camera():
    global camera_source
    camera_source = 0
    processs()

def set_external_camera():
    global camera_source
    camera_source = 1
    processs()

# Create the main application window
root = tk.Tk()
root.title("Hand Gesture Presentation")
root.config(bg='PeachPuff2')
root.iconbitmap("favicon.ico")  # Replace with the actual path to your icon file (ICO format)

logo_image = tk.PhotoImage(file="logo1.png")
logo_label = tk.Label(root, image=logo_image)
logo_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")


title_label = tk.Label(root, text="Hand Gesture Presentation", font=("Helvetica", 25))
title_label.grid(row=0, column=1, padx=10, pady=10, sticky="n")
#borderwidth=2,
style = ttk.Style()
style.configure("Graphical.TButton",
                font=("Arial", 14),
                foreground="black",
                background="DodgerBlue2",
                relief="raised",
                padx=30,
                pady=10)



class CameraError(Exception):
    pass

def start_presentation():
    global new

    new = tk.Tk()
    new.title("Hand Gesture Presentation")
    new.config(bg='PeachPuff2')


    builtin_camera_button = ttk.Button(new, text="Built-in Camera (0)", style="Graphical.TButton",command=set_builtin_camera)
    external_camera_button = ttk.Button(new, text="External Webcam (1)", style="Graphical.TButton",command=set_external_camera)

    builtin_camera_button.grid(row=2, column=0, padx=10, pady=10)
    external_camera_button.grid(row=2, column=2, padx=10, pady=10)
    new.geometry("500x500")
    # frame size of window




def processs():
    global new
    new.destroy()
    width, height = 1280, 720
    gestureThreshold = 300
    folderPath = "data"

    screen_width = 1920
    screen_height = 1200
    # Camera access
    cap = cv2.VideoCapture(camera_source)

    cap.set(3, width)
    cap.set(4, height)

    # Hand Detector
    detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

    # Variables
    imgNumber = 0
    delay = 10
    buttonPressed = False
    counter = 0
    annotations = [[]]
    annotationNumber = -1
    annotationStart = False

    hs, ws = int(120 * 1), int(213 * 1)  # width and height of small image

    # Get list of presentation images
    pathImages = sorted(os.listdir(folderPath), key=len)
    print(pathImages)

    while True:

        # Run the Tkinter main loop

        success, img = cap.read()
        img = cv2.flip(img, 1)
        pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
        imgCurrent = cv2.imread(pathFullImage)
        image_back = cv2.imread('373f51.png')

        # Find the hand and its landmarks
        hands=None
        try:
            hands, img = detectorHand.findHands(img)
        except Exception as e:
            print("Camera Not Found!")
            messagebox.showerror("Error", "External Camera not found.")
            break

        cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

        if hands and buttonPressed is False:  # If hand is detected

            hand = hands[0]
            cx, cy = hand["center"]
            lmList = hand["lmList"]  # List of 21 Landmark points
            fingers = detectorHand.fingersUp(hand)  # List of which fingers are up

            # Constrain values for easier drawing
            xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
            yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
            indexFinger = xVal, yVal

            if cy <= gestureThreshold:  # If hand is at the height of the face
                if fingers == [1, 0, 0, 0, 0]:
                    print("Left")
                    buttonPressed = True
                    if imgNumber > 0:
                        imgNumber -= 1
                        annotations = [[]]
                        annotationNumber = -1
                        annotationStart = False
                if fingers == [1, 1, 0, 0, 0]:
                    print("Right")
                    buttonPressed = True
                    if imgNumber < len(pathImages) - 1:
                        imgNumber += 1
                        annotations = [[]]
                        annotationNumber = -1
                        annotationStart = False

            if fingers == [0, 1, 1, 0, 0]:
                cv2.circle(imgCurrent, indexFinger, 3, (0, 0, 255), cv2.FILLED)

            if fingers == [0, 1, 0, 0, 0]:
                if annotationStart is False:
                    annotationStart = True
                    annotationNumber += 1
                    annotations.append([])
                print(annotationNumber)
                annotations[annotationNumber].append(indexFinger)
                cv2.circle(imgCurrent, indexFinger, 1, (0, 0, 255), cv2.FILLED)

            else:
                annotationStart = False

            if fingers == [0, 1, 1, 1, 0]:
                if annotations:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True

        else:
            annotationStart = False

        if buttonPressed:
            counter += 1
            if counter > delay:
                counter = 0
                buttonPressed = False

        for i, annotation in enumerate(annotations):
            for j in range(len(annotation)):
                if j != 0:
                    cv2.line(imgCurrent, annotation[j - 1], annotation[j], (0, 0, 200), 12)

        imgSmall = cv2.resize(img, (ws, hs))
        h, w, _ = imgCurrent.shape
        imgCurrent[0:hs, w - ws: w] = imgSmall

        imgCurrent = cv2.resize(imgCurrent, (screen_width, screen_height))

        cv2.imshow("Slides", imgCurrent)
        # cv2.imshow("Image", img)

        key = cv2.waitKey(1)
        if key == ord('q'):
            cv2.destroyAllWindows()

            break








def virtual_keys():
    caps_lock_enabled = False
    FRAME_WIDTH = 1920
    FRAME_HEIGHT = 1200

    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_TIP = 12
    Z_THRESHOLD_PRESS = 20
    VK = {
        '1': {'x': 100 + 0, 'y': 0 + 70, 'w': 100, 'h': 100},
        '2': {'x': 200 + 10, 'y': 0 + 70, 'w': 100, 'h': 100},
        '3': {'x': 300 + 20, 'y': 0 + 70, 'w': 100, 'h': 100},
        '4': {'x': 400 + 30, 'y': 0 + 70, 'w': 100, 'h': 100},
        '5': {'x': 500 + 40, 'y': 0 + 70, 'w': 100, 'h': 100},
        '6': {'x': 600 + 50, 'y': 0 + 70, 'w': 100, 'h': 100},
        '7': {'x': 700 + 60, 'y': 0 + 70, 'w': 100, 'h': 100},
        '8': {'x': 800 + 70, 'y': 0 + 70, 'w': 100, 'h': 100},
        '9': {'x': 900 + 80, 'y': 0 + 70, 'w': 100, 'h': 100},
        '0': {'x': 1000 + 90, 'y': 0 + 70, 'w': 100, 'h': 100},
        'Q': {'x': 100 + 0, 'y': 100 + 90, 'w': 100, 'h': 100},
        'W': {'x': 200 + 10, 'y': 100 + 90, 'w': 100, 'h': 100},
        'E': {'x': 300 + 20, 'y': 100 + 90, 'w': 100, 'h': 100},
        'R': {'x': 400 + 30, 'y': 100 + 90, 'w': 100, 'h': 100},
        'T': {'x': 500 + 40, 'y': 100 + 90, 'w': 100, 'h': 100},
        'Y': {'x': 600 + 50, 'y': 100 + 90, 'w': 100, 'h': 100},
        'U': {'x': 700 + 60, 'y': 100 + 90, 'w': 100, 'h': 100},
        'I': {'x': 800 + 70, 'y': 100 + 90, 'w': 100, 'h': 100},
        'O': {'x': 900 + 80, 'y': 100 + 90, 'w': 100, 'h': 100},
        'P': {'x': 1000 + 90, 'y': 100 + 90, 'w': 100, 'h': 100},
        'A': {'x': 150 + 0, 'y': 200 + 110, 'w': 100, 'h': 100},
        'S': {'x': 250 + 10, 'y': 200 + 110, 'w': 100, 'h': 100},
        'D': {'x': 350 + 20, 'y': 200 + 110, 'w': 100, 'h': 100},
        'F': {'x': 450 + 30, 'y': 200 + 110, 'w': 100, 'h': 100},
        'G': {'x': 550 + 40, 'y': 200 + 110, 'w': 100, 'h': 100},
        'H': {'x': 650 + 50, 'y': 200 + 110, 'w': 100, 'h': 100},
        'J': {'x': 750 + 60, 'y': 200 + 110, 'w': 100, 'h': 100},
        'K': {'x': 850 + 70, 'y': 200 + 110, 'w': 100, 'h': 100},
        'L': {'x': 950 + 80, 'y': 200 + 110, 'w': 100, 'h': 100},
        'Z': {'x': 200 + 0, 'y': 300 + 130, 'w': 100, 'h': 100},
        'X': {'x': 300 + 10, 'y': 300 + 130, 'w': 100, 'h': 100},
        'C': {'x': 400 + 20, 'y': 300 + 130, 'w': 100, 'h': 100},
        'V': {'x': 500 + 30, 'y': 300 + 130, 'w': 100, 'h': 100},
        'B': {'x': 600 + 40, 'y': 300 + 130, 'w': 100, 'h': 100},
        'N': {'x': 700 + 50, 'y': 300 + 130, 'w': 100, 'h': 100},
        'M': {'x': 800 + 60, 'y': 300 + 130, 'w': 100, 'h': 100},
        'Backspace': {'x': 800 + 60, 'y': 400 + 150, 'w': 400, 'h': 100},
        'Space': {'x': 400 + 110, 'y': 400 + 150, 'w': 400, 'h': 100},
        'Caps Lock': {'x': 100 + 0, 'y': 400 + 150, 'w': 400, 'h': 100}
    }

    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils



    # def toggle_caps_lock():
    #     global caps_lock_enabled
    #     caps_lock_enabled = not caps_lock_enabled

    def draw_keys(img, x, y, z):
        for k in VK:
            if VK[k]['x'] < x < VK[k]['x'] + VK[k]['w'] and VK[k]['y'] < y < VK[k]['y'] + VK[k][
                'h'] and z <= Z_THRESHOLD_PRESS:
                if k == 'Caps Lock':
                    cv2.rectangle(img, (VK[k]['x'], VK[k]['y']), (VK[k]['x'] + VK[k]['w'], VK[k]['y'] + VK[k]['h']),
                                  (0, 255, 0) if caps_lock_enabled else (0, 0, 255), -1)
                else:
                    cv2.rectangle(img, (VK[k]['x'], VK[k]['y']), (VK[k]['x'] + VK[k]['w'], VK[k]['y'] + VK[k]['h']),
                                  (0, 0, 255), -1)
                cv2.putText(img, f"{k}", (VK[k]['x'] + 30, VK[k]['y'] + 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 5,
                            cv2.LINE_AA)
            else:
                cv2.rectangle(img, (VK[k]['x'], VK[k]['y']), (VK[k]['x'] + VK[k]['w'], VK[k]['y'] + VK[k]['h']),
                              (0, 255, 0) if k == 'Caps Lock' else (0, 255, 0), 1)
                cv2.putText(img, f"{k}", (VK[k]['x'] + 30, VK[k]['y'] + 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0),
                            5, cv2.LINE_AA)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        x = [0, 0]  # Initialize the x and y coordinates for both fingers
        y = [0, 0]
        z = [0, 0]
        key_to_type = None

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

                index_finger_tip = handLms.landmark[INDEX_FINGER_TIP]
                middle_finger_tip = handLms.landmark[MIDDLE_FINGER_TIP]

                x[0] = int(index_finger_tip.x * FRAME_WIDTH)
                y[0] = int(index_finger_tip.y * FRAME_HEIGHT)
                z[0] = int(index_finger_tip.z * FRAME_WIDTH)

                x[1] = int(middle_finger_tip.x * FRAME_WIDTH)
                y[1] = int(middle_finger_tip.y * FRAME_HEIGHT)
                z[1] = int(middle_finger_tip.z * FRAME_WIDTH)

                for key, params in VK.items():
                    if (params['x'] < x[0] < params['x'] + params['w'] and
                            params['y'] < y[0] < params['y'] + params['h'] and
                            params['x'] < x[1] < params['x'] + params['w'] and
                            params['y'] < y[1] < params['y'] + params['h'] and
                            z[0] <= Z_THRESHOLD_PRESS and z[1] <= Z_THRESHOLD_PRESS):
                        if key == 'Caps Lock':
                            caps_lock_enabled = not caps_lock_enabled
                        else:
                            key_to_type = key
                        break

        if key_to_type:
            if caps_lock_enabled:
                pyautogui.press(key_to_type)
                # pyautogui.sleep(0.5)

            else:
                pyautogui.press(key_to_type.lower())
                # pyautogui.sleep(0.5)


        draw_keys(img, x[0], y[0], z[0])
        draw_keys(img, x[1], y[1], z[1])

        cv2.imshow("Virtual Keyboard", img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

def browse_for_image():
    delete_images_in_data_folder()
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.pptx *.ppt *.pdf *.docx")])
    for file_path in file_paths:
        print("Selected:", file_path)
        pres = slides.Presentation(file_path)
        output_directory = "data"
        os.makedirs(output_directory, exist_ok=True)
        for sld in pres.slides:
            bmp = sld.get_thumbnail(1, 1)

            filename = os.path.join(output_directory, f"Slide_{sld.slide_number}.png")

            bmp.save(filename, drawing.imaging.ImageFormat.png)

browse_button = ttk.Button(root, text="Browse PPTs", style="Graphical.TButton" ,command=browse_for_image)
browse_button.grid(row=1, column=1,  padx=10, pady=10)

vk_button = ttk.Button(root, text="Virtual keyboard", style="Graphical.TButton" ,command=virtual_keys)
vk_button.grid(row=1, column=0,  padx=10, pady=10)

start_button = ttk.Button(root, text="Start Presentation", style="Graphical.TButton" , command=start_presentation)
start_button.grid(row=2, column=1,  padx=10, pady=10)


image_paths = ["images1.png", "images2.png"]
image_label = tk.Label(root)
image_label.grid(row=3, column=1, padx=10, pady=10)
# Create buttons to navigate through the images
def show_next_image():
    global current_image_index
    current_image_index = (current_image_index + 1) % len(image_paths)
    show_image()

def show_previous_image():
    global current_image_index
    current_image_index = (current_image_index - 1) % len(image_paths)
    show_image()

prev_button = ttk.Button(root, text="Previous",style="Graphical.TButton" , command=show_previous_image)
next_button = ttk.Button(root, text="Next",style="Graphical.TButton", command=show_next_image)
prev_button.grid(row=3, column=0, padx=10, pady=10)
next_button.grid(row=3, column=2, padx=10, pady=10)

# Initialize the current image index
current_image_index = 0

def show_image():
    image_path = image_paths[current_image_index]
    photo = tk.PhotoImage(file=image_path)
    image_label.config(image=photo)
    image_label.image = photo

# Show the first image initially
show_image()

# root.state('zoomed')

root.mainloop()
import cv2 # pyre-ignore
import threading
import tkinter as tk
from tkinter import Label, Frame, filedialog
from PIL import Image, ImageTk # pyre-ignore
from ultralytics import YOLO # pyre-ignore
import pyttsx3 # pyre-ignore
import datetime
import time
import re

# ==========================
# LOAD YOLO MODEL
# ==========================
model = YOLO("best.pt")  # your trained YOLO model

# ==========================
# ROAD SIGN DICTIONARY
# ==========================
road_signs = {
    "APR-09": "Car, Motorcycle, Van speed limit",
    "APR-10": "Speed limit during 5.00 am - 9.00 pm",
    "APR-11": "Bus and Truck speed limit",
    "APR-12": "Three-wheeler and Tractor speed limit",
    "APR-14": "No left turn",
    "DWS-01":"Curve to the left",
    "DWS-02":"Curve to the right",
    "DWS-03":"Double curve, first to the left",
    "DWS-04":"Double curve, first to the right",
    "DWS-09":"Road narrows",
    "DWS-10":"Road narrows on the left",
    "DWS-11":"Road narrows on the right",
    "DWS-12":"Crossroads",
    "DWS-13":"Staggered junctions",
    "DWS-14":"Staggered junctions",
    "DWS-15": "T junction",
    "DWS-16": "Y junction",
    "DWS-17": "Merging traffic from the left",
    "DWS-18": "Joining a side road at right angles to the left",
    "DWS-19": "Merging traffic from the right",
    "DWS-20": "Joining a side road at right angles to the right",
    "DWS-21": "Narrow bridge",
    "DWS-25": "Roundabout ahead",
    "DWS-26": "Traffic lights ahead",
    "DWS-27": "Steep descent",
    "DWS-28": "Steep ascent",
    "DWS-29": "Slippery road",
    "DWS-32": "Pedestrian crossing ahead",
    "DWS-33": "Children",
    "DWS-35": "Roadworks",
    "DWS-36": "Level crossing with barriers ahead",
    "DWS-40": "Cyclists",
    "DWS-41": "Domestic animals",
    "DWS-42": "Quayside or riverbank",
    "DWS-44": "Bump ahead",
    "DWS-46": "Dip",
    "MNS-01": "Turn left",
    "MNS-02": "Turn right",
    "MNS-03": "Proceed straight", 
    "MNS-04": "Turn left ahead", 
    "MNS-05": "Turn right ahead", 
    "MNS-06": "Pass onto left", 
    "MNS-07": "Pass onto right",
    "MNS-09": "Roundabout",
    "OSD-01": "Pedestrian crossing",
    "OSD-02": "One-way street",
    "OSD-03": "Hospital",
    "OSD-04": "Parking",
    "OSD-06": "Bus Stop",
    "OSD-07": "Bus Lane",
    "OSD-16": "Motorway",
    "OSD-17": "End of motorway",
    "OSD-26": "Exit ramp",
    "PHS-01": "No entry",
    "PHS-02": "No left turn",
    "PHS-03": "No right turn",
    "PHS-04": "No U-turn",
    "PHS-05": "No horns",
    "PHS-23": "No parking",
    "PHS-24": "No parking and standing",
    "PRS-01": "STOP",
    "PRS-02": "Give way",
    "SLS-100": "Maximum speed limit 100km/h",
    "SLS-15": "Maximum speed limit 15km/h",
    "SLS-40": "Maximum speed limit 40km/h",
    "SLS-50": "Maximum speed limit 50km/h",
    "SLS-60": "Maximum speed limit 60km/h",
    "SLS-70": "Maximum speed limit 70km/h",
    "SLS-80": "Maximum speed limit 80km/h",
    "TLS-C": "Red & yellow traffic light",
    "TLS-G": "Green traffic light",
    "TLS-R": "Red traffic light",
    "TLS-Y": "Yellow traffic light"
}

# ==========================
# TEXT-TO-SPEECH WARNING
# ==========================

# Initialize Pyttsx3 globally on the main thread so Windows COM doesn't crash
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "zira" in voice.name.lower() or "female" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 140)
engine.setProperty('volume', 1.0)

last_spoken_sign = None
last_spoken_time = 0

def play_warning(text):
    """Play warning audio safely."""
    try:
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', str(text))
        engine.say(clean_text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

# ==========================
# TKINTER GUI
# ==========================
window = tk.Tk()
window.title("🚦 Advanced Driver Assistance System (ADAS) - HUD")
window.geometry("1450x850")
try:
    window.state('zoomed') # Maximizes window on launch
except:
    pass
window.configure(bg="#0f172a")

header_frame = Frame(window, bg="#0f172a")
header_frame.pack(fill="x", pady=(20, 10))
Label(header_frame, text="🚦 Smart HUD Road Sign Detection", font=("Segoe UI", 28, "bold"), fg="#38bdf8", bg="#0f172a").pack()
Label(header_frame, text="Real-time Context-Aware & Predictive Hazard System", font=("Segoe UI", 12), fg="#94a3b8", bg="#0f172a").pack()

# Bottom status bar (Needs to be packed before main_frame expand grabs everything)
status = Label(window, text="Status: Idle", font=("Segoe UI", 11), fg="#94a3b8", bg="#0f172a", anchor="w", padx=20, pady=5)
status.pack(side="bottom", fill="x")

main_frame = Frame(window, bg="#0f172a")
main_frame.pack(fill="both", expand=True, padx=30, pady=10)

# LEFT — Video Frame
video_wrapper = Frame(main_frame, bg="#1e293b", highlightbackground="#334155", highlightthickness=1)
video_wrapper.pack(side="left", fill="both", expand=True, padx=(0, 20))
video_wrapper.pack_propagate(False)

Label(video_wrapper, text="LIVE VIDEO FEED", font=("Segoe UI", 14, "bold"), fg="#94a3b8", bg="#1e293b").pack(pady=(15, 5))
video_label = Label(video_wrapper, bg="black")
video_label.pack(fill="both", expand=True, padx=15, pady=(0, 15))

# RIGHT — Control Panel
control_panel = Frame(main_frame, bg="#0f172a", width=500)
control_panel.pack(side="right", fill="y", padx=(20, 0))
control_panel.pack_propagate(False)

# Card 1: Alert Dashboard (VITAL FOR DRIVER)
alert_card = Frame(control_panel, bg="#1e293b", highlightbackground="#0ea5e9", highlightthickness=2)
alert_card.pack(fill="x", pady=(0, 25))
Label(alert_card, text="⚠️ DRIVER ALERT STATUS", font=("Segoe UI", 16, "bold"), fg="#0ea5e9", bg="#1e293b").pack(pady=(20, 10))

alert_label = Label(alert_card, text="No sign detected", fg="#f8fafc", bg="#334155", font=("Segoe UI", 26, "bold"), height=3, wraplength=450, justify="center")
alert_label.pack(fill="x", padx=20, pady=(0, 15))

desc_label = Label(alert_card, text="System ready...", fg="#94a3b8", bg="#1e293b", font=("Segoe UI", 15, "bold"))
desc_label.pack(pady=(0, 25))

# Card 2: Telemetry
telemetry_card = Frame(control_panel, bg="#1e293b", highlightbackground="#334155", highlightthickness=1)
telemetry_card.pack(fill="x", pady=(0, 20))
Label(telemetry_card, text="VEHICLE TELEMETRY", font=("Segoe UI", 12, "bold"), fg="#94a3b8", bg="#1e293b").pack(pady=(15, 5), anchor="w", padx=20)

speed_slider = tk.Scale(telemetry_card, from_=0, to=120, orient="horizontal", label="Vehicle Speed (km/h)", bg="#1e293b", fg="#f8fafc", length=420, highlightthickness=0, troughcolor="#334155", activebackground="#38bdf8", sliderrelief="flat", font=("Segoe UI", 11, "bold"))
speed_slider.set(60)
speed_slider.pack(pady=(0, 20))

# Video Control Logic
is_streaming = False
cap = cv2.VideoCapture(0)

def use_webcam():
    global cap, is_streaming
    if cap.isOpened():
        cap.release()
    cap = cv2.VideoCapture(0)
    is_streaming = True
    status.config(text="Status: Active (Source: Webcam)", fg="#10b981")

def open_video_file():
    global cap, is_streaming
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
    if file_path:
        if cap.isOpened():
            cap.release()
        cap = cv2.VideoCapture(file_path)
        is_streaming = True
        status.config(text=f"Status: Active (Source: {file_path.split('/')[-1]})", fg="#10b981")

def stop_stream():
    global is_streaming, cap
    is_streaming = False
    if 'cap' in globals() and cap.isOpened():
        cap.release()
    status.config(text="Status: Stream stopped", fg="#ef4444")
    alert_label.config(text="No sign detected", bg="#334155", fg="#f8fafc")
    desc_label.config(text="System ready...", fg="#94a3b8")
    
    # Clear the video label frame
    black_img = Image.new('RGB', (1024, 576), color='black')
    img = ImageTk.PhotoImage(black_img)
    video_label.imgtk = img # type: ignore
    video_label.config(image=img)

# Card 3: Video Input Controls
video_card = Frame(control_panel, bg="#1e293b", highlightbackground="#334155", highlightthickness=1)
video_card.pack(fill="x")
Label(video_card, text="VIDEO SOURCE", font=("Segoe UI", 12, "bold"), fg="#94a3b8", bg="#1e293b").pack(pady=(15, 5), anchor="w", padx=20)

tk.Button(video_card, text="Use Webcam", bg="#0ea5e9", activebackground="#0284c7", command=use_webcam, font=("Segoe UI", 12, "bold"), fg="white", width=25, relief="flat", pady=8).pack(pady=(0, 10))
tk.Button(video_card, text="Open Video File", bg="#10b981", activebackground="#059669", command=open_video_file, font=("Segoe UI", 12, "bold"), fg="white", width=25, relief="flat", pady=8).pack(pady=(0, 20))

tk.Button(video_card, text="🛑 STOP STREAM", bg="#ef4444", activebackground="#b91c1c", command=stop_stream, font=("Segoe UI", 16, "bold"), fg="white", width=20, relief="flat", pady=15).pack(pady=(10, 25))

# ==========================
# Update Video Frame
# ==========================
def update_frame():
    if not is_streaming:
        window.after(50, update_frame) # type: ignore
        return

    ret, frame = cap.read() # type: ignore
    if not ret:
        status.config(text="⚠ No video source!", fg="red")
        window.after(30, update_frame) # type: ignore
        return

    detected_sign_name = None
    current_speed = speed_slider.get()

    # Draw Modern HUD Overlay (Background)
    overlay = frame.copy()
    cv2.rectangle(overlay, (20, 20), (380, 140), (15, 23, 42), -1)  # dark slate
    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
    # Accent line
    cv2.rectangle(frame, (20, 20), (380, 25), (14, 165, 233), -1) # Sky blue accent

    current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, f"Time:  {current_time_str}", (35, 55), cv2.FONT_HERSHEY_DUPLEX, 0.6, (248, 250, 252), 1)
    cv2.putText(frame, f"Speed: {current_speed} km/h", (35, 90), cv2.FONT_HERSHEY_DUPLEX, 0.6, (56, 189, 248), 1)
    cv2.putText(frame, f"GPS:   6.9271 N, 79.8612 E", (35, 125), cv2.FONT_HERSHEY_DUPLEX, 0.6, (248, 250, 252), 1)

    results = model(frame, verbose=False) # type: ignore
    for r in results: # type: ignore
        for box in r.boxes: # type: ignore
            class_id = int(box.cls[0]) # type: ignore
            class_name = model.names[class_id]
            conf = float(box.conf[0])

            base_sign_name = road_signs.get(class_name, class_name)
            detected_sign_name = base_sign_name
            
            box_color = (0, 0, 255) # Red default
            hud_warning = None
            hud_color = (0, 0, 255)
            threat_level = "HIGH"

            # 1. Sign Degradation Detection
            if conf < 0.60:
                box_color = (0, 165, 255) # Orange
                hud_warning = f"Degraded Sign: {base_sign_name}"
                threat_level = "MODERATE - Poor Visibility"

            # 2. Context-Aware Detection (School Zone/Crossing)
            if class_name in ["DWS-33"]: # DWS-33 is Children / school zone 
                current_hour = datetime.datetime.now().hour
                if 7 <= current_hour <= 16:
                    if current_speed > 30:
                        hud_warning = "School Zone Active - Reduce Speed!"
                        threat_level = "CRITICAL"
                        if int(time.time() * 5) % 2 == 0:
                            box_color = (0, 0, 255) # Red flashing
                        else:
                            box_color = (255, 255, 255) # White flashing
                    else:
                        hud_warning = "School Zone Active - Speed OK"
                        threat_level = "SAFE"
                        box_color = (0, 255, 0)
                else:
                    # Inactive hours -> Show school closed message, no threat
                    hud_warning = "School Zone Inactive (Closed)"
                    box_color = (148, 163, 184) # Slate color for inactive
                    threat_level = "SAFE"

            # 3. Predictive Hazard Alerts (Speeding)
            if class_name.startswith("SLS-"):
                try:
                    limit = int(class_name.split("-")[1])
                    if current_speed > limit:
                        hud_warning = "Over Speeding - Slow Down!"
                        threat_level = "CRITICAL"
                        if int(time.time() * 5) % 2 == 0:
                            box_color = (0, 0, 255)
                        else:
                            box_color = (255, 255, 255)
                except:
                    pass

            # 4. STOP Sign Ignored
            if class_name == "PRS-01":
                if current_speed > 5:
                    hud_warning = "STOP Sign Ignored - Danger!"
                    threat_level = "CRITICAL"
                    if int(time.time() * 5) % 2 == 0:
                        box_color = (0, 0, 255)
                    else:
                        box_color = (255, 255, 255)
                else:
                    hud_warning = "Vehicle Stopped Correctly"
                    box_color = (0, 255, 0) # Green
                    threat_level = "SAFE"

            display_name = str(hud_warning if hud_warning else detected_sign_name)

            # Draw box
            x1, y1, x2, y2 = map(int, box.xyxy[0]) # type: ignore
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            # Add background for text
            (w, h), _ = cv2.getTextSize(display_name, cv2.FONT_HERSHEY_DUPLEX, 0.7, 1) # type: ignore
            cv2.rectangle(frame, (x1, y1 - 35), (x1 + w + 10, y1), box_color, -1)
            cv2.putText(frame, display_name, (x1 + 5, y1 - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

            # Update GUI colors based on threat
            if threat_level in ["HIGH", "CRITICAL"]:
                bg_color = "#dc2626" # Stronger red
                fg_color = "#ffffff"
            elif threat_level in ["MODERATE - Poor Visibility", "LOW - Out of hours"]:
                bg_color = "#f59e0b" # amber
                fg_color = "#ffffff"
            elif threat_level == "SAFE":
                bg_color = "#059669" # Stronger green
                fg_color = "#ffffff"
            else:
                bg_color = "#334155" # grey
                fg_color = "#f8fafc"
                
            alert_label.config(text=display_name, bg=bg_color, fg=fg_color)
            desc_label.config(text=f"Threat Level: {threat_level}", fg=bg_color)

            # Speak road sign without spamming
            global last_spoken_sign, last_spoken_time
            current_time = time.time()
            if display_name != last_spoken_sign or (current_time - last_spoken_time) > 4:
                last_spoken_sign = display_name
                last_spoken_time = current_time
                # Use a daemon thread to prevent Tkinter from freezing while the TTS engine speaks
                threading.Thread(target=play_warning, args=(display_name,), daemon=True).start()

    if detected_sign_name is None:
        alert_label.config(text="No sign detected", bg="#334155", fg="#f8fafc")
        desc_label.config(text="System ready...", fg="#94a3b8")

    # Resize video for larger display
    frame = cv2.resize(frame, (1024, 576))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = ImageTk.PhotoImage(Image.fromarray(rgb))
    video_label.imgtk = img # type: ignore
    video_label.config(image=img)

    window.after(10, update_frame) # type: ignore

# Start the Tkinter loop
update_frame()
window.mainloop()

cap.release()
cv2.destroyAllWindows()

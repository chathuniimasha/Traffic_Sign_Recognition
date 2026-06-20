import cv2 
import threading
import tkinter as tk
from tkinter import Label, Frame, filedialog, Canvas
from PIL import Image, ImageTk 
from ultralytics import YOLO
import pyttsx3 
import datetime
import time
import re
import math


# LOAD YOLO MODEL

model = YOLO("best.pt")  # your trained YOLO model


# ROAD SIGN DICTIONARY

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


# TEXT-TO-SPEECH WARNING

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "zira" in voice.name.lower() or "female" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 140)
engine.setProperty('volume', 1.0)

def play_warning(text):
    """Play warning audio safely."""
    try:
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', str(text))
        engine.say(clean_text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")


# TKINTER GUI - MAIN APP


class StartupScreen:
    """Modern startup screen with animations"""
    def __init__(self, parent_window):
        self.window = parent_window
        self.frame = Frame(self.window, bg="#0f172a")
        self.frame.pack(fill="both", expand=True)
        
        self.create_startup_ui()
        self.animate_logo()
    
    def create_startup_ui(self):
        # Center container
        center_frame = Frame(self.frame, bg="#0f172a")
        center_frame.pack(fill="both", expand=True)
        
        # Animated logo canvas
        canvas = Canvas(center_frame, bg="#0f172a", highlightthickness=0, width=200, height=200)
        canvas.pack(pady=(80, 40))
        self.logo_canvas = canvas
        self.logo_id = canvas.create_oval(60, 60, 140, 140, fill="#38bdf8", outline="#0ea5e9", width=3)
        self.logo_text = canvas.create_text(100, 100, text="⚡", font=("Segoe UI", 60, "bold"), fill="#0f172a")
        
        # Title
        Label(center_frame, text="Smart ADAS HUD System", font=("Segoe UI", 42, "bold"), 
              fg="#38bdf8", bg="#0f172a").pack(pady=(20, 10))
        
        
        
        # Buttons frame
        button_frame = Frame(center_frame, bg="#0f172a")
        button_frame.pack(pady=40)
        
        # Start button
        tk.Button(button_frame, text="START SYSTEM", bg="#0ea5e9", activebackground="#0284c7",
                 font=("Segoe UI", 14, "bold"), fg="white", width=30, relief="flat", pady=12,
                 command=self.start_system).pack(pady=10)
        
        # Open video button
        tk.Button(button_frame, text="OPEN VIDEO FILE", bg="#38bdf8", activebackground="#22d3ee",
                 font=("Segoe UI", 14, "bold"), fg="#0f172a", width=30, relief="flat", pady=12,
                 command=self.open_video_file).pack(pady=10)
        
        # Exit button
        tk.Button(button_frame, text="EXIT", bg="#64748b", activebackground="#475569",
                 font=("Segoe UI", 14, "bold"), fg="white", width=30, relief="flat", pady=12,
                 command=self.window.quit).pack(pady=10)
        
        # Loading indicator
        self.loading_frame = Frame(center_frame, bg="#0f172a")
        self.loading_frame.pack(pady=(60, 0))
        self.loading_label = Label(self.loading_frame, text="", font=("Segoe UI", 11), 
                                   fg="#38bdf8", bg="#0f172a")
        self.loading_label.pack()
        self.loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_index = 0
    
    def animate_logo(self):
        """Animate the logo with pulsing effect"""
        scale = 1.0 + 0.2 * math.sin(time.time() * 3)
        self.logo_canvas.itemconfig(self.logo_id, width=int(3 * scale))
        self.loading_index = (self.loading_index + 1) % len(self.loading_chars)
        self.loading_label.config(text=f"{self.loading_chars[self.loading_index]} Initializing AI Model...")
        self.window.after(100, self.animate_logo)
    
    def start_system(self):
        """Start with webcam"""
        self.frame.destroy()
        global cap, is_streaming
        cap = cv2.VideoCapture(0)
        is_streaming = True
        dashboard = MainDashboard(self.window)
        dashboard.update_frame()
    
    def open_video_file(self):
        """Open video file"""
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if file_path:
            self.frame.destroy()
            global cap, is_streaming
            cap = cv2.VideoCapture(file_path)
            is_streaming = True
            dashboard = MainDashboard(self.window)
            dashboard.update_frame()


class MainDashboard:
    """Main ADAS dashboard with real-time detection"""
    def __init__(self, parent_window):
        self.window = parent_window
        self.window.title("🚦 Smart ADAS HUD System - Main Dashboard")
        self.window.geometry("1600x950")
        try:
            self.window.state('zoomed')
        except:
            pass
        self.window.configure(bg="#0f172a")
        
        # Performance tracking
        self.fps = 0
        self.frame_count = 0
        self.last_time = time.time()
        self.last_spoken_sign = None
        self.last_spoken_time = 0
        
        self.create_main_ui()
    
    def create_main_ui(self):
        """Create the main dashboard UI"""
        # Header
        header = Frame(self.window, bg="#0f172a", height=80)
        header.pack(fill="x", padx=20, pady=(15, 10))
        header.pack_propagate(False)
        
        title = Label(header, text="🚦 SMART ADAS HUD SYSTEM", font=("Segoe UI", 32, "bold"), 
                     fg="#38bdf8", bg="#0f172a")
        title.pack(side="left", padx=20)
        
     
        
        # Status indicator
        status_frame = Frame(header, bg="#0f172a")
        status_frame.pack(side="right", padx=20)
        self.status_dot = Canvas(status_frame, width=12, height=12, bg="#0f172a", 
                                highlightthickness=0)
        self.status_dot.create_oval(2, 2, 10, 10, fill="#10b981", outline="#059669", width=2)
        self.status_dot.pack(side="left", padx=5)
        self.status_text = Label(status_frame, text="System Active", font=("Segoe UI", 11, "bold"), 
                                fg="#10b981", bg="#0f172a")
        self.status_text.pack(side="left")
        
        # Main content
        main_frame = Frame(self.window, bg="#0f172a")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # LEFT: Video feed
        self.create_video_panel(main_frame)
        
        # RIGHT: Control panels
        self.create_control_panels(main_frame)
    
    def create_video_panel(self, parent):
        """Create video feed with HUD overlay"""
        video_frame = Frame(parent, bg="#1e293b", highlightbackground="#38bdf8", highlightthickness=2)
        video_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        # Video label
        self.video_label = Label(video_frame, bg="black")
        self.video_label.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Create initial black frame
        black_img = Image.new('RGB', (1024, 576), color='black')
        img = ImageTk.PhotoImage(black_img)
        self.video_label.imgtk = img
        self.video_label.config(image=img)
    
    def create_control_panels(self, parent):
        """Create all right-side control panels"""
        control_frame = Frame(parent, bg="#0f172a", width=500)
        control_frame.pack(side="right", fill="both", padx=(20, 0))
        control_frame.pack_propagate(False)
        
        # Panel 1: Alert Status
        self.create_alert_panel(control_frame)
        
        # Panel 2: Telemetry
        self.create_telemetry_panel(control_frame)
    
    def create_alert_panel(self, parent):
        """Driver alert card with threat indicator"""
        card = Frame(parent, bg="#1e293b", highlightbackground="#0ea5e9", highlightthickness=2)
        card.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        Label(card, text="⚠️  DRIVER ALERT STATUS", font=("Segoe UI", 14, "bold"), 
             fg="#0ea5e9", bg="#1e293b").pack(pady=(12, 10), anchor="w", padx=15)
        
        self.alert_label = Label(card, text="No sign detected", fg="#f8fafc", bg="#334155", 
                                font=("Segoe UI", 24, "bold"), height=3, wraplength=430, justify="center")
        self.alert_label.pack(fill="both", expand=True, padx=12, pady=10)
        
        self.desc_label = Label(card, text="System ready...", fg="#94a3b8", bg="#1e293b", 
                               font=("Segoe UI", 11, "bold"))
        self.desc_label.pack(pady=(0, 12), padx=15)
    
    
    def create_telemetry_panel(self, parent):
        """Vehicle telemetry panel"""
        card = Frame(parent, bg="#1e293b", highlightbackground="#334155", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        Label(card, text="🚗 VEHICLE TELEMETRY", font=("Segoe UI", 12, "bold"), 
             fg="#94a3b8", bg="#1e293b").pack(pady=(12, 10), anchor="w", padx=15)
        
        # Speed slider with modern styling
        self.speed_slider = tk.Scale(card, from_=0, to=120, orient="horizontal", 
                                    label="Vehicle Speed (km/h)", bg="#1e293b", fg="#f8fafc", 
                                    length=400, highlightthickness=0, troughcolor="#334155", 
                                    activebackground="#38bdf8", sliderrelief="flat", 
                                    font=("Segoe UI", 10, "bold"))
        self.speed_slider.set(60)
        self.speed_slider.pack(padx=15, pady=(0, 10))
        
        # Info labels
        info_frame = Frame(card, bg="#1e293b")
        info_frame.pack(padx=15, pady=(0, 12), fill="x")
        
        Label(info_frame, text="⏰ Time:", font=("Segoe UI", 10), fg="#94a3b8", bg="#1e293b").pack(anchor="w")
        self.time_label = Label(info_frame, text="--:--:--", font=("Segoe UI", 10, "bold"), 
                               fg="#38bdf8", bg="#1e293b")
        self.time_label.pack(anchor="w", pady=(0, 5))
        
        Label(info_frame, text="📍 GPS:", font=("Segoe UI", 10), fg="#94a3b8", bg="#1e293b").pack(anchor="w")
        self.gps_label = Label(info_frame, text="6.9271 N, 79.8612 E", font=("Segoe UI", 10, "bold"), 
                              fg="#38bdf8", bg="#1e293b")
        self.gps_label.pack(anchor="w")
    
    def update_frame(self):
        """Main video update loop with detection"""
        global is_streaming, cap
        
        if not is_streaming:
            self.window.after(50, self.update_frame)
            return
        
        ret, frame = cap.read()
        if not ret:
            self.window.after(30, self.update_frame)
            return
        
        # Update time
        self.time_label.config(text=datetime.datetime.now().strftime("%H:%M:%S"))
        
        # FPS calculation
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_time >= 1:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_time = current_time
        
        detected_sign_name = None
        current_speed = self.speed_slider.get()
        
        # Draw HUD overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (20, 20), (380, 160), (15, 23, 42), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        cv2.rectangle(frame, (20, 20), (380, 26), (14, 165, 233), -1)
        
        current_time_str = datetime.datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, f"Time:  {current_time_str}", (35, 55), cv2.FONT_HERSHEY_DUPLEX, 0.6, (248, 250, 252), 1)
        cv2.putText(frame, f"Speed: {current_speed} km/h", (35, 90), cv2.FONT_HERSHEY_DUPLEX, 0.6, (56, 189, 248), 1)
        cv2.putText(frame, f"GPS:   6.9271 N, 79.8612 E", (35, 125), cv2.FONT_HERSHEY_DUPLEX, 0.6, (248, 250, 252), 1)
        cv2.putText(frame, f"FPS:   {self.fps}", (35, 160), cv2.FONT_HERSHEY_DUPLEX, 0.6, (56, 189, 248), 1)
        
        # YOLO Detection
        results = model(frame, verbose=False)
        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                conf = float(box.conf[0])
                
                base_sign_name = road_signs.get(class_name, class_name)
                detected_sign_name = base_sign_name
                
                box_color = (0, 0, 255)
                hud_warning = None
                threat_level = "HIGH"
                
                # Sign degradation
                if conf < 0.60:
                    box_color = (0, 165, 255)
                    hud_warning = f"Degraded: {base_sign_name}"
                    threat_level = "MODERATE - Poor Visibility"
                
                # School zone context
                if class_name in ["DWS-33"]:
                    current_hour = datetime.datetime.now().hour
                    if 7 <= current_hour <= 16:
                        if current_speed > 30:
                            hud_warning = "School Zone - Reduce Speed!"
                            threat_level = "CRITICAL"
                            if int(time.time() * 5) % 2 == 0:
                                box_color = (0, 0, 255)
                            else:
                                box_color = (255, 255, 255)
                        else:
                            hud_warning = "School Zone - Speed OK"
                            threat_level = "SAFE"
                            box_color = (0, 255, 0)
                    else:
                        hud_warning = "School Zone Inactive"
                        box_color = (148, 163, 184)
                        threat_level = "SAFE"
                
                # Speed limit violation
                if class_name.startswith("SLS-"):
                    try:
                        limit = int(class_name.split("-")[1])
                        if current_speed > limit:
                            hud_warning = "Over Speeding!"
                            threat_level = "CRITICAL"
                            if int(time.time() * 5) % 2 == 0:
                                box_color = (0, 0, 255)
                            else:
                                box_color = (255, 255, 255)
                    except:
                        pass
                
                # STOP sign ignored
                if class_name == "PRS-01":
                    if current_speed > 5:
                        hud_warning = "STOP Sign Ignored!"
                        threat_level = "CRITICAL"
                        if int(time.time() * 5) % 2 == 0:
                            box_color = (0, 0, 255)
                        else:
                            box_color = (255, 255, 255)
                    else:
                        hud_warning = "Vehicle Stopped"
                        box_color = (0, 255, 0)
                        threat_level = "SAFE"
                
                display_name = str(hud_warning if hud_warning else detected_sign_name)
                
                # Draw detection box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                (w, h), _ = cv2.getTextSize(display_name, cv2.FONT_HERSHEY_DUPLEX, 0.7, 1)
                cv2.rectangle(frame, (x1, y1 - 35), (x1 + w + 10, y1), box_color, -1)
                cv2.putText(frame, display_name, (x1 + 5, y1 - 10),
                           cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
                
                # Update GUI colors
                if threat_level in ["HIGH", "CRITICAL"]:
                    bg_color = "#dc2626"
                    fg_color = "#ffffff"
                elif threat_level in ["MODERATE - Poor Visibility"]:
                    bg_color = "#f59e0b"
                    fg_color = "#ffffff"
                elif threat_level == "SAFE":
                    bg_color = "#059669"
                    fg_color = "#ffffff"
                else:
                    
                    bg_color = "#334155"
                    fg_color = "#f8fafc"
                
                self.alert_label.config(text=display_name, bg=bg_color, fg=fg_color)
                self.desc_label.config(text="Sign detected", fg=bg_color)
                
                # TTS warning with throttling
                current_time = time.time()
                if display_name != self.last_spoken_sign or (current_time - self.last_spoken_time) > 4:
                    self.last_spoken_sign = display_name
                    self.last_spoken_time = current_time
                    threading.Thread(target=play_warning, args=(display_name,), daemon=True).start()
        
        if detected_sign_name is None:
            self.alert_label.config(text="No sign detected", bg="#334155", fg="#f8fafc")
            self.desc_label.config(text="System ready...", fg="#94a3b8")
        
        # Resize and display
        frame = cv2.resize(frame, (1024, 576))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(rgb))
        self.video_label.imgtk = img
        self.video_label.config(image=img)
        
        self.window.after(10, self.update_frame)


# ==========================
# INITIALIZE AND LAUNCH
# ==========================
window = tk.Tk()
window.title("🚦 Smart ADAS HUD System")
window.geometry("1600x950")
try:
    window.state('zoomed')
except:
    pass
window.configure(bg="#0f172a")

# Global video capture
cap = None
is_streaming = False

# Show startup screen
startup = StartupScreen(window)

# Start the Tkinter loop
window.mainloop()

# Cleanup
if cap is not None and cap.isOpened():
    cap.release()
cv2.destroyAllWindows()


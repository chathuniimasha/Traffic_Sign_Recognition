 🚗 Traffic Sign Recognition System (Sri Lanka)

 📌 Overview
An intelligent real-time traffic sign detection and driver assistance system designed for Sri Lankan roads. The system uses YOLOv8 deep learning to detect traffic signs from a dashboard camera and provides smart alerts to improve driving safety.



 🎯 Key Features

 🔍 Smart Detection
- Real-time traffic sign detection from webcam/video feed
- Supports major Sri Lankan sign categories:
  - Danger Warning Signs (DWS)
  - Prohibition Signs (PHS)
  - Mandatory Signs (MNS)
  - Speed Limit Signs (SLS)
  - Traffic Light Signs (TLS)
  - Other Direction Signs (OSD)

 🧠 Context-Aware Alerts
- Speed limit violation detection
- School zone warnings based on time (07:00–16:00)
- STOP sign compliance alerts
- Detection of damaged or low-confidence signs

 🖥️ Driver Interface
- Heads-Up Display (HUD) with speed, GPS, and timestamp
- Color-coded alerts (Red / Yellow / Green)
- Voice alerts using Text-to-Speech (TTS)
- Interactive speed control and video input selection



 🛠️ Tech Stack
- Python
- YOLOv8 (Ultralytics)
- OpenCV
- Tkinter (GUI)
- pyttsx3 (Text-to-Speech)
- Google Colab (Training)
- Roboflow Dataset



 📊 Model Details
- Model: YOLOv8s
- Image Size: 640×640
- Epochs: 50
- Optimizer: AdamW
- Evaluation: Precision, Recall, mAP@50, mAP@50-95



 🚀 Installation

```bash
git clone https://github.com/yourusername/traffic-sign-recognition.git
cd traffic-sign-recognition
pip install -r requirements.txt

▶️ Run Project
python app.py


📁 Project Structure
traffic-sign-recognition/
├── app.py
├── sign.ipynb
├── best.pt
├── requirements.txt
└── assets/
````



📈 Results
Real-time detection (30–60 FPS)
High accuracy in normal lighting conditions
Robust multi-class traffic sign recognition



🔮 Future Improvements
GPS-based location alerts
Mobile app version (Android/iOS)
Night-time detection improvement
Embedded deployment (Raspberry Pi / Jetson Nano)

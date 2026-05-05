import cv2
import mediapipe as mp
import time
from model_handler import ModelHandler

# Inițializări globale
mp_face_detection = mp.solutions.face_detection
# Am setat model_selection=1 pentru detecție la distanță (0 e pentru distanțe scurte < 2m)
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
model = ModelHandler('best.pt')

sleep_start_time = None

def set_camera_resolution(cap):
    """
    Cheamă această funcție imediat după cap = cv2.VideoCapture(0)
    pentru a îmbunătăți vederea la distanță.
    """
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("Rezoluție setată la 1280x720 pentru detecție la distanță.")

def proceseaza_ai(frame):
    global sleep_start_time
    
    # Pasul 1: Detecție față cu MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_mp = face_detection.process(rgb_frame)
    
    label = "Activ"
    prob = 0
    currently_sleeping = False

    if results_mp.detections:
        for detection in results_mp.detections:
            bbox = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            
            # Calculăm coordonatele
            x, y, w, h = int(bbox.xmin * iw), int(bbox.ymin * ih), int(bbox.width * iw), int(bbox.height * ih)
            
            # Adăugăm o marjă (padding) mai inteligentă pentru a prinde și pleoapele clar
            padding = 40 
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(iw, x + w + padding)
            y2 = min(ih, y + h + padding)
            
            face_crop = frame[y1:y2, x1:x2]
            
            if face_crop.size > 0:
                # YOLO va primi acum un crop de rezoluție mai mare
                results_yolo = model.predict_face(face_crop)
                for r in results_yolo:
                    if r.probs is not None:
                        idx = r.probs.top1
                        prob = r.probs.top1conf.item() * 100
                        label = model.names[idx]
                        
                        if idx == 1 and prob > 65:
                            currently_sleeping = True

            # Desenăm pe cadru
            color = (0, 0, 255) if currently_sleeping else (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, f"{label} {prob:.1f}%", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Gestionare cronometru
    if currently_sleeping:
        if sleep_start_time is None:
            sleep_start_time = time.time()
        durata = time.time() - sleep_start_time
    else:
        sleep_start_time = None
        durata = 0

    return frame, currently_sleeping, durata
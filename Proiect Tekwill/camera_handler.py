import cv2

class CameraHandler:
    def __init__(self, source=0):
        # Inițializăm camera web
        self.cap = cv2.VideoCapture(source)
        
        # Setăm rezoluția HD (1280x720) pentru a te putea vedea clar de la distanță
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def get_frame(self):
        # Citim imaginea de la cameră
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def show_frame(self, frame, label, prob, timer_text=""):
        """
        Această funcție desenează interfața pe care o va vedea juriul la Tekwill.
        """
        # Alegem culoarea în funcție de stare
        # Roșu dacă e Fatigue/Alarmă, Verde dacă e Active
        if "!!!" in label or "Oboseala" in label:
            color = (0, 0, 255) # Roșu (Format BGR)
        else:
            color = (0, 255, 0) # Verde

        # 1. Desenăm un chenar negru în partea de sus pentru text (ca un dashboard)
        cv2.rectangle(frame, (0, 0), (1280, 80), (30, 30, 30), -1)

        # 2. Scriem statusul principal (Active / Fatigue)
        status_display = f"STATUS: {label}"
        cv2.putText(frame, status_display, (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        # 3. Scriem probabilitatea (cât de sigur e AI-ul)
        prob_display = f"Confid: {prob:.1f}%"
        cv2.putText(frame, prob_display, (950, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # 4. Afișăm fereastra finală
        cv2.imshow("TEKWILL AI - Driver Safety System", frame)

    def release(self):
        # Închidem camera și ferestrele când oprim programul
        self.cap.release()
        cv2.destroyAllWindows()
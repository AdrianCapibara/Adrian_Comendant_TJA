import time
import pygame

class SafeDriveEngine:
    def __init__(self, model_handler):
        self.model = model_handler
        self.sleep_start_time = None
        self.alarm_threshold = 5.0
        pygame.mixer.init()

    def proceseaza_cadru(self, frame, translations, lang):
        results = self.model.predict_face(frame)
        sleeping = False
        
        for r in results:
            if r.probs is not None:
                # 1 = Fatigue/Ochi închiși
                if r.probs.top1 == 1 and r.probs.top1conf.item() > 0.70:
                    sleeping = True

        status_text = "OK"
        color = "#2ECC71"

        if sleeping:
            if self.sleep_start_time is None:
                self.sleep_start_time = time.time()
            
            elapsed = time.time() - self.sleep_start_time
            status_text = f"{elapsed:.1f}s"
            color = "#E67E22"
            
            if elapsed >= self.alarm_threshold:
                status_text = translations[lang]["alert"]
                color = "#E74C3C"
                if not pygame.mixer.music.get_busy():
                    try:
                        pygame.mixer.music.load("alarm.mp3")
                        pygame.mixer.music.play(-1)
                    except:
                        pass
        else:
            self.sleep_start_time = None
            pygame.mixer.music.stop()

        return status_text, color
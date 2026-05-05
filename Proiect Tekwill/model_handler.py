from ultralytics import YOLO

class ModelHandler:
    def __init__(self, model_path='best.pt'):
        self.model = YOLO(model_path)
        self.names = self.model.names 

    def predict_face(self, face_image):
        # conf=0.5 e pragul de siguranță
        results = self.model.predict(face_image, conf=0.5, verbose=False)
        return results
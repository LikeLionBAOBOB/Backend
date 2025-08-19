from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # YOLOv8 모델 불러오기
model.export(format="onnx")  # yolov8n.onnx 파일 생성
import cv2
from ultralytics import YOLO
from pathlib import Path

model_path = "yolov8n.onnx"

def detect_objects(img_path, conf=0.3):
    model = YOLO(model_path)
    wanted = {"person", "laptop"}
    class_ids = []
    for cid, name in model.names.items():
        if name in wanted:
            class_ids.append(cid)

    # 추론 수행
    results = model.predict(
        source=img_path,
        conf=conf,
        classes=class_ids,
        save=False,
        verbose=False
    )

    boxes = []
    r = results[0]
    if r.boxes is not None:
        for b in r.boxes:
            # 클래스 이름
            cls_idx = int(b.cls.item())
            name = r.names[cls_idx]
            score = float(b.conf.item())
            # 바운딩 박스 좌표 구하기
            xyxy = b.xyxy[0].tolist()
            x1 = int(xyxy[0])
            y1 = int(xyxy[1])
            x2 = int(xyxy[2])
            y2 = int(xyxy[3])
            # 중심 좌표 구하기
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            boxes.append({
                "name": name,
                "bbox": [x1, y1, x2, y2],
                "confidence": score,
                "center": [cx, cy]
            })
    return boxes
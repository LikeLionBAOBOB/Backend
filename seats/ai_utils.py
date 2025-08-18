import os, json, cv2, re
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO

# 기본 설정
PROJECT_ROOT = Path(__file__).parent.parent  # BACKEND 폴더
IMAGES = PROJECT_ROOT / "media/images"  # BACKEND/media/images 폴더
ROIS = PROJECT_ROOT / "seats/rois"  # BACKEND/seats/rois 폴더
OUT = PROJECT_ROOT / "seats/outputs"  # BACKEND/seats/outputs 폴더

model_path = "yolov8n.pt"
CONF = 0.3  # 신뢰도 임계값

# 파일명 오름차순 정렬 (숫자순으로)
def natural_key(name):
    # 숫자 나오는 부분마다 자르기 ("file23test9.txt" → ['file', '23', 'test', '9', '.txt', '']))
    parts = re.split(r'(\d+)', str(name))
    result = []
    for s in parts:
        if s.isdigit():
            result.append(int(s))  # 숫자면 int형으로 변경
        else:
            result.append(s)  # 문자열은 그대로
    return result

# images/<library_code>/ 폴더 안의 jpg 파일 목록
def list_images(lib_code:int):
    folder = IMAGES / str(lib_code)
    if not folder.exists():
        return []
    files = []
    for p in folder.iterdir():
        if p.is_file():
            ext = p.suffix.lower()
            if ext == ".jpg" or ext == ".jpeg" or ext == ".png":
                files.append(p)
    files.sort(key=natural_key)
    return files

# rois/<lib_code>.json 불러오기 (없으면 기본 구조 반환)
def load_rois(lib_code:int):
    roi_file = ROIS / f"{lib_code}.json"
    if not roi_file.exists():
        return {"lib_code": lib_code, "images": {}}
    with open(roi_file, "r", encoding="utf-8") as f:
        return json.load(f)

# 좌표가 주어진 사각형 안에 점이 있는지 확인
def point_in_rect(cx: float, cy: float, rect: dict):
    if cx < rect["x"]:
        return False
    if cy < rect["y"]:
        return False
    if cx > rect["x"] + rect["w"]:
        return False
    if cy > rect["y"] + rect["h"]:
        return False
    return True

# 결과를 저장할 출력 폴더를 생성하고 경로 반환
def make_output_dir(lib_code: int, run_id: str):
    d = OUT / str(lib_code) / run_id
    d.mkdir(parents=True, exist_ok=True)
    return d

# 좌석 ROI 사각형과 좌석 ID를 그려줌 (디버깅용)
def draw_seat_rectangles(img, seats):
    for s in seats:
        x = int(s["x"])
        y = int(s["y"])
        w = int(s["w"])
        h = int(s["h"])
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, str(s.get("seat_id", "")), (x + 3, y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

# 메인 함수
def analyze(lib_code:int, conf:float=CONF, save_vis:bool=True):
    lib_code = int(lib_code)

    # 이미지 목록 불러오기
    images = list_images(lib_code)
    if len(images) == 0:
        print("이미지가 없습니다:", lib_code)
        return

    # 모델 로드, 원하는 클래스 id(person, laptop) 추출
    model = YOLO(model_path)
    wanted = {"person", "laptop"}
    class_ids = []
    for cid, name in model.names.items():
        if name in wanted:
            class_ids.append(cid)

    # ROI 불러오기
    roi_data = load_rois(lib_code)

    # 실행 결과를 저장할 폴더
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")  # 현재 시간 기반의 고유 ID
    out_dir = make_output_dir(lib_code, run_id)  # 출력 경로 생성

    # 결과를 저장할 리스트
    payload_imgs = []

    # 이미지별로 추론
    for img_path in images:
        # 좌석 정보 불러오기 (없으면 빈 리스트)
        seats_info = []
        # ROI JSON에서 키로 쓰기 위해 파일명 추출
        img_key = img_path.name
        if img_key in roi_data.get("images", {}):
            # 좌석 정보 배열 가져옴
            seats_info = roi_data["images"][img_key].get("seats", [])
        else:
            seats_info = []

        # 추론 수행
        results = model.predict(
            source=str(img_path),  # 현재 이미지 한 장만 입력
            conf=conf,  # 신뢰도 임계값 (이 값 미만은 버림)
            classes=class_ids,  # 감지할 클래스 ID (person, laptop)
            save=False,
            verbose=False
        )
        r = results[0]

        # 감지된 박스들 정리
        detections = []  # (name, cx, cy, (x1,y1,x2,y2))
        if r.boxes is not None:
            for b in r.boxes:
                # 클래스 이름 구하기
                cls_idx = int(b.cls.item())
                name = r.names[cls_idx]
                # 바운딩 박스 좌표 구하기
                xyxy = b.xyxy[0].tolist()
                x1 = int(xyxy[0])
                y1 = int(xyxy[1])
                x2 = int(xyxy[2])
                y2 = int(xyxy[3])
                # 중심 좌표 구하기
                cx = (x1 + x2) / 2.0
                cy = (y1 + y2) / 2.0
                # 중심 좌표와 클래스 이름을 detections에 추가
                detections.append((name, cx, cy, (x1, y1, x2, y2)))

        # 좌석별 카운트
        seat_rows = []
        for s in seats_info:
            person_cnt = 0
            laptop_cnt = 0

            # 좌석 영역 내의 감지 결과 필터링
            for det in detections:
                det_name = det[0]
                det_cx = det[1]
                det_cy = det[2]
                if point_in_rect(det_cx, det_cy, s):
                    if det_name == "person":
                        person_cnt += 1
                    elif det_name == "laptop":
                        laptop_cnt += 1
            # 좌석별 카운트 추가
            seat_rows.append({
                "seat_id": s.get("seat_id", ""),
                "person": person_cnt,
                "laptop": laptop_cnt
            })

        # 전체 카운트
        total_person = 0
        total_laptop = 0
        for det in detections:
            if det[0] == "person":
                total_person += 1
            elif det[0] == "laptop":
                total_laptop += 1

        # 좌석별 카운트와 전체 카운트를 payload에 추가
        payload_imgs.append({
            "image": img_path.name,
            "seats": seat_rows,
            "counts": {
                "person": total_person,
                "laptop": total_laptop
            }
        })

        # 시각화 저장 (감지 결과를 원본 이미지 위에 그려서 파일로 저장)
        if save_vis:
            img = cv2.imread(str(img_path))
            for det in detections:
                name = det[0]
                x1, y1, x2, y2 = det[3]
                # 사람: 노란색 사각형, 노트북: 보라색 사각형
                if name == "person":
                    color = (0, 255, 255) # 노랑
                else:
                    color = (255, 0, 255) # 보라

                # 사각형 그리기
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                # 클래스 이름(person, laptop)을 박스 위쪽 여백에 표시
                cv2.putText(img, name, (x1, max(0, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

            # 좌석 ROI(사각형)와 좌석 ID를 초록색으로 덧그림
            draw_seat_rectangles(img, seats_info)
            # 출력 경로 및 저장
            out_img_path = out_dir / f"{img_path.stem}_det.jpg"  # 출력 이미지 경로
            cv2.imwrite(str(out_img_path), img)  # 이미지 저장

    # 결과 JSON 저장
    payload = {
        "lib_code": lib_code,
        "run_id": run_id,  # 실행 ID
        "model": Path(model_path).name,
        "classes": ["person", "laptop"],  # 감지할 클래스
        "images": payload_imgs,
        "created_at": datetime.now().isoformat()  # 생성 일시
    }

    # 결과 JSON
    result_path = out_dir / "results.json"  # 결과 JSON 파일 경로
    with open(result_path, "w", encoding="utf-8") as f:  # 결과 JSON 파일 열기
        json.dump(payload, f, ensure_ascii=False, indent=2)  # JSON 데이터 쓰기

# 메인 함수
if __name__ == "__main__":
    import argparse  # 명령줄 인자 파싱용
    parser = argparse.ArgumentParser()  # ArgumentParser 객체 생성
    parser.add_argument("lib_code", type=int)  # 라이브러리 코드
    args = parser.parse_args()  # 명령줄 인자 파싱

    # 분석 수행
    analyze(args.lib_code)
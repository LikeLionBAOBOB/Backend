from pathlib import Path
import json, re, os

PROJECT_ROOT = Path(__file__).parent.parent.parent  # BACKEND 폴더
IMAGES = PROJECT_ROOT / "media/images"  # BACKEND/media/images 폴더
ROIS = PROJECT_ROOT / "seats/rois"  # BACKEND/seats/rois 폴더
ROIS.mkdir(parents=True, exist_ok=True)  # BACKEND/seats/rois 폴더 생성

# 파일명 오름차순 정렬 (숫자순으로)
def natural_key(name):
    # 숫자 나오는 부분마다 자르기 ("file23test9.txt" → ['file', '23', 'test', '9', '.txt', '']))
    parts = re.split(r'(\d+)', name)
    result = []
    for s in parts:
        if s.isdigit():
            result.append(int(s))  # 숫자면 int형으로 변경
        else:
            result.append(s)  # 문자열은 그대로
    return result

def main():
    libs = []
    for lib_dir in IMAGES.iterdir():
        # 폴더만 찾고, 폴더 이름은 리스트에 추가
        if lib_dir.is_dir():
            libs.append(lib_dir.name)
    libs.sort(key=natural_key)

    for lib_code in libs:
        lib_dir = IMAGES / lib_code
        img_list = []
        for img_file in lib_dir.iterdir():
            # 확장자가 .jpg인 파일만 찾고, 파일 이름은 리스트에 추가
            if img_file.suffix == ".jpg":
                img_list.append(img_file.name)
        img_list.sort(key=natural_key)

        # JSON 파일의 기본 데이터 구조
        data = {"lib_code": int(lib_code), "images": {}}
        for img_name in img_list:
            data["images"][img_name] = {"seats": []}

        # 파일 저장
        out = ROIS / f"{lib_code}.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
        print("wrote", out)

if __name__ == "__main__":
    main()
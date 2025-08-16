import json, datetime, re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

PROJECT_ROOT = Path(__file__).parent.parent.parent  # BACKEND 폴더
IMAGES = PROJECT_ROOT / "media/images"  # BACKEND/media/images 폴더
ROIS = PROJECT_ROOT / "seats/rois"  # BACKEND/seats/rois 폴더
ROIS.mkdir(parents=True, exist_ok=True)  # BACKEND/seats/rois 폴더 생성

MAX_W, MAX_H = 1280, 800  # 미리보기 최대 크기

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

# 좌석 ID 생성
def next_seat_id(seats:list) -> str:
    nums = []
    for seat in seats:
        seat_id = seat.get("seat_id")
        if isinstance(seat_id, str) and seat_id.isdigit():
            nums.append(int(seat_id))
    n = (max(nums) + 1) if nums else 1
    return str(n)

# 메인 클래스
class RectROILabeler:
    # lib_code를 받아 이미지 폴더의 파일을 읽고 초기 세팅
    def __init__(self, lib_code):
        self.lib_code = str(lib_code)
        img_folder = IMAGES / self.lib_code
        self.img_files = sorted(img_folder.glob("*.jpg"), key=natural_key)

        # json 파일 로드 또는 생성
        self.data = self._load_or_init_json()
        for p in self.img_files:
            if p.name not in self.data["images"]:
                self.data["images"][p.name] = {"seats": []}

        self.idx = 0
        self._init_ui()
        self._load_image()

    # JSON 저장 경로
    def _json_path(self):
        return ROIS / f"{self.lib_code}.json"

    # 기존 JSON 있으면 로드하고, 실패하면 새로 생성
    def _load_or_init_json(self):
        path = self._json_path()
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
            except:
                messagebox.showwarning("경고", "JSON 불러오기 실패. 새로 만듦.")
        return {"lib_code": int(self.lib_code), "images": {}}

    # 현재 데이터 상태를 JSON 파일로 저장
    def _save_json(self):
        path = self._json_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        self.status.config(text="saved")

    # UI
    def _init_ui(self):
        self.root = tk.Tk()
        self.root.title(f"ROI Rect Labeler - {self.lib_code}")

        top = tk.Frame(self.root)
        top.pack(fill="x")
        self.lbl = tk.Label(top, text="")
        self.lbl.pack(side="left", padx=8, pady=6)

        tk.Button(top, text="Prev (←)", command=self.prev_img).pack(side="left", padx=4)
        tk.Button(top, text="Next (→)", command=self.next_img).pack(side="left", padx=4)
        tk.Button(top, text="Save (S)", command=self._save_json).pack(side="left", padx=8)
        tk.Button(top, text="Delete Last (Del)", command=self.delete_last).pack(side="left", padx=8)

        self.status = tk.Label(top, text="", fg="gray")
        self.status.pack(side="right", padx=8)

        self.canvas = tk.Canvas(self.root, width=MAX_W, height=MAX_H, bg="black", cursor="tcross")
        self.canvas.pack(fill="both", expand=True)

        # 키 바인딩
        self.root.bind("<Left>",  lambda e: self.prev_img())
        self.root.bind("<Right>", lambda e: self.next_img())
        self.root.bind("<Key-s>", lambda e: self._save_json())
        self.root.bind("<Delete>", lambda e: self.delete_last())

        # 마우스 이벤트(사각형 전용)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    # 이미지 로드 및 갱신
    def _load_image(self):
        img_path = self.img_files[self.idx]
        self.cur_name = img_path.name
        self.img = Image.open(img_path).convert("RGB")
        self.w, self.h = self.img.size
        self.scale = min(MAX_W / self.w, MAX_H / self.h, 1.0)

        disp = self.img.resize((int(self.w * self.scale), int(self.h * self.scale)))
        self.tkimg = ImageTk.PhotoImage(disp)

        self.canvas.delete("all")
        self.canvas.config(width=int(self.w * self.scale), height=int(self.h * self.scale))
        self.canvas.create_image(0, 0, image=self.tkimg, anchor="nw", tags="bg")

        self._draw_existing()
        self._update_label()

    def _update_label(self):
        seats = self.data["images"].get(self.cur_name, {"seats": []})["seats"]
        self.lbl.config(text=f"{self.lib_code} | {self.cur_name} | {self.idx+1}/{len(self.img_files)} | seats: {len(seats)}")

    def _draw_existing(self):
        self.canvas.delete("roi")
        seats = self.data["images"].get(self.cur_name, {"seats": []})["seats"]
        for s in seats:
            x, y, w, h = s["x"], s["y"], s["w"], s["h"]
            X0, Y0 = x * self.scale, y * self.scale
            X1, Y1 = (x + w) * self.scale, (y + h) * self.scale
            self.canvas.create_rectangle(X0, Y0, X1, Y1, outline="lime", width=2, tags="roi")
            self.canvas.create_text(X0 + 3, Y0 + 14, text=s["seat_id"], anchor="w", fill="lime", tags="roi")

    # 마우스 (사각형 드래그)
    def on_press(self, e):
        self.start = (e.x, e.y)
        self.temp = self.canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="yellow", width=1, dash=(3, 2), tags="temp")

    def on_drag(self, e):
        if hasattr(self, "temp"):
            self.canvas.coords(self.temp, self.start[0], self.start[1], e.x, e.y)

    def on_release(self, e):
        if not hasattr(self, "temp"):
            return
        x0, y0 = self.start
        x1, y1 = e.x, e.y
        self.canvas.delete(self.temp)
        del self.start, self.temp

        # 너무 작은 드래그는 무시
        if abs(x1 - x0) < 6 or abs(y1 - y0) < 6:
            return

        # 캔버스 -> 원본 좌표
        rx, ry = min(x0, x1) / self.scale, min(y0, y1) / self.scale
        rw, rh = abs(x1 - x0) / self.scale, abs(y1 - y0) / self.scale

        seats = self.data["images"][self.cur_name]["seats"]
        sid = next_seat_id(seats)
        seats.append({
            "seat_id": sid,
            "x": int(round(rx)), "y": int(round(ry)),
            "w": int(round(rw)), "h": int(round(rh))
        })
        self._draw_existing()
        self._update_label()

    # 조작
    def delete_last(self):
        seats = self.data["images"].get(self.cur_name, {"seats": []})["seats"]
        if seats:
            seats.pop()
            self._draw_existing()
            self._update_label()

    def prev_img(self):
        if self.idx > 0:
            self._save_json()  # 간단 자동저장
            self.idx -= 1
            self._load_image()

    def next_img(self):
        if self.idx < len(self.img_files) - 1:
            self._save_json()  # 간단 자동저장
            self.idx += 1
            self._load_image()

    def run(self):
        self.root.mainloop()

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Rect-only ROI labeler")
    ap.add_argument("--lib", type=int, required=True, help="library code (e.g., 111257)")
    args = ap.parse_args()
    RectROILabeler(args.lib).run()

if __name__ == "__main__":
    main()
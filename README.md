# Backend
멋쟁이사자처럼 13기 중앙해커톤 BAOBOB_백엔드

```
BACKEND/
│
├─ accounts/                # 사용자 인증/관리 앱
│  ├─ admin.py              # 관리자 페이지 설정
│  ├─ forms.py              # (폼 정의, 회원가입/로그인 등)
│  ├─ models.py             # User 모델 정의
│  ├─ serializers.py        # DRF용 직렬화 클래스
│  ├─ urls.py               # accounts 하위 라우팅
│  └─ views.py              # API 엔드포인트/비즈니스 로직
│
├─ adminpanel/              # 운영자(관리자) 기능 전용 앱
│  ├─ admin.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ urls.py
│  └─ views.py
│
├─ libraries/               # 도서관 관련 데이터/로직
│  ├─ data/
│  │  └─ library_info.json  # 도서관 정보 메타데이터(JSON)
│  ├─ management/
│  │  └─ commands/
│  │     └─ seed_libraries.py # 커스텀 커맨드(예: 도서관 데이터 초기화)
│  ├─ admin.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ urls.py
│  └─ views.py
│
├─ maps/                    # 지도/위치/지오코딩 관련 기능
│  ├─ utils/
│  │  └─ geocoding.py       # 좌표 변환 등 부가기능
│  ├─ admin.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ services.py           # 지도/위치 서비스 로직
│  ├─ urls.py
│  └─ views.py
│
├─ media/                   # 업로드된 파일 저장 폴더 (이미지 등)
│
├─ seats/                   # 좌석 관리, AI/ROI 관련 기능
│  ├─ roi_tools/            # 좌석 ROI 라벨링/생성 툴
│  │  ├─ init_rois.py       # 초기 ROI json 생성
│  │  └─ roi_rect.py        # Tkinter 기반 사각형 ROI 라벨링툴
│  ├─ rois/                 # 도서관별 좌석 ROI 정보(json)
│  │  ├─ 111051.json
│  │  ├─ ...                # (도서관별 json)
│  ├─ admin.py
│  ├─ ai_utils.py           # AI 분석 보조 함수들
│  ├─ detect_objects.py     # YOLO 등 객체 탐지 메인 로직
│  ├─ models.py
│  ├─ serializers.py
│  ├─ urls.py
│  └─ views.py
│
├─ configs/                 # 전체 프로젝트 환경설정 (settings)
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ settings.py           # 핵심 환경설정
│  ├─ urls.py               # 프로젝트 전체 라우팅
│  └─ wsgi.py
│
├─ .env.example             # .env 예시파일(팀원 공유용)
├─ requirements.txt         # 파이썬 패키지/의존성 목록
│
├─ convert.py               # (단독 실행, onnx 변환 스크립트)
├─ manage.py                # Django 명령어 실행 진입점
│
├─ yolov8n.onnx             # YOLOv8 모델(ONNX 포맷)
└─ yolov8n.pt               # YOLOv8 모델(Pytorch 포맷)

```

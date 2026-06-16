# 저장소 가이드라인

## 프로젝트 구조와 모듈 구성

TOKIMEKI BOARD는 Python 3.12, PyQt6, pynput 기반 데스크톱 앱입니다. 실행 진입점은 `main.py`이며, 주요 애플리케이션 코드는 `src/` 아래에 있습니다.

- `src/core/`: 설정, 이벤트, 모델, 디스플레이 크기 관련 코드.
- `src/mappers/`: 키보드와 스크롤 이벤트 매핑.
- `src/services/`: 에셋 로딩, 입력 처리, 이미지 상태, 업데이트, 커서 추적 로직.
- `src/ui/`: Qt 렌더링, 오버레이 창, 트레이, 플랫폼 권한 처리.
- `assets/`: 런타임과 패키징에 사용하는 아이콘 및 표정 이미지.
- `tests/`: pytest 기반 단위 테스트와 통합 테스트.
- `docs/`: 데모 미디어와 플랫폼별 설치 가이드.
- `scripts/`: macOS와 Windows용 PyInstaller 빌드 스크립트.

## 빌드, 테스트, 개발 명령어

- `uv sync --extra dev`: 런타임 및 테스트 의존성을 포함해 로컬 환경을 생성하거나 갱신합니다.
- `uv run main.py`: 저장소 루트에서 앱을 로컬 실행합니다.
- `uv run pytest`: `pyproject.toml` 설정에 따라 기본 테스트를 실행합니다.
- `uv run pytest tests/ --cov=src --cov-report=term`: 커버리지 결과와 함께 테스트를 실행합니다.
- `./scripts/build_macos.sh`: PyInstaller로 macOS `.app` 번들을 빌드합니다.
- `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`: Windows 실행 파일을 빌드합니다.

## 코딩 스타일과 네이밍 규칙

표준 Python 스타일을 따르고 들여쓰기는 공백 4칸을 사용합니다. 필요한 경우 타입 친화적인 dataclass와 모델을 사용하고, 모듈은 책임 단위로 작게 유지합니다. 소스 파일명은 `cursor_follower.py`처럼 소문자와 밑줄을 사용합니다. 클래스는 `PascalCase`, 함수와 변수 및 테스트명은 `snake_case`, 상수는 `UPPER_SNAKE_CASE`를 사용합니다. 현재 별도 포매터나 린터 설정은 없으므로 주변 코드 스타일과 일관되게 작성합니다.

## 테스트 가이드라인

테스트는 pytest를 사용하며 `tests/` 아래의 `test_*.py` 파일, `Test*` 클래스, `test_*` 함수가 자동 발견됩니다. 공통 fixture는 `tests/conftest.py`에 둡니다. core와 service 로직은 집중된 단위 테스트로 검증하고, 이미지 및 입력 흐름처럼 여러 컴포넌트가 엮이는 동작은 통합 테스트로 확인합니다. 새 기능을 추가할 때는 패키징 전에 관련 테스트를 추가하거나 갱신합니다.

## 커밋과 풀 리퀘스트 가이드라인

최근 커밋 기록은 `feat:`, `bug:`, `docs:`, `actions` 같은 접두어와 짧은 제목을 사용합니다. 가능하면 이 스타일을 따르세요. 예: `feat: add update check interval`. 커밋은 하나의 목적에 집중하고, 플랫폼별 변경이 있으면 제목이나 본문에 명시합니다.

풀 리퀘스트에는 간단한 설명, 관련 이슈 링크, 테스트 결과(`uv run pytest`), UI나 에셋 변경 시 스크린샷 또는 화면 녹화를 포함합니다. macOS 권한, 패키징, 릴리스 워크플로에 영향이 있으면 반드시 적습니다.

## 보안 및 설정 팁

`build/`, `dist/`, 임시 가상환경 같은 생성물은 커밋하지 않습니다. PyInstaller 스크립트가 올바르게 포함할 수 있도록 런타임 에셋은 `assets/` 아래에 유지합니다.

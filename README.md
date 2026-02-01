# Reddit BULDAK Timeline Tracker

Reddit에서 불닭(BULDAK) 관련 언급량을 수집하고 시계열 그래프로 시각화하는 도구입니다.

---

## 어디서 실행할 수 있나요?

### 방법 1: 내 컴퓨터에서 실행 (권장)

1. **Python 설치 확인**
   - 터미널/명령 프롬프트를 열고 `python --version` 입력
   - Python 3.8 이상이 필요합니다
   - 없다면: https://www.python.org/downloads/ 에서 설치

2. **이 프로젝트 다운로드**
   ```bash
   git clone <이 저장소 URL>
   cd BULDAK
   ```

3. **필요한 패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **실행!**
   ```bash
   python run_quarterly.py
   ```

### 방법 2: Google Colab에서 실행 (설치 없이)

1. https://colab.research.google.com 접속
2. 새 노트북 생성
3. 다음 코드를 복사해서 실행:

```python
# 1. 패키지 설치
!pip install praw pandas matplotlib numpy

# 2. 파일 다운로드 (또는 직접 업로드)
!git clone <이 저장소 URL>
%cd BULDAK

# 3. 실행
!python run_quarterly.py
```

### 방법 3: Jupyter Notebook에서 실행

Jupyter가 설치되어 있다면:
```bash
pip install jupyter
jupyter notebook
```
새 노트북에서 위의 코드를 실행하세요.

---

## 빠른 시작: 분기별 언급량 그래프 (2023~현재)

가장 간단한 방법:

```bash
python run_quarterly.py
```

이 명령어 하나로:
- 2023년 1월 ~ 현재까지의 샘플 데이터 생성
- 분기별 언급량 막대 그래프 표시
- `charts/buldak_quarterly.png` 파일로 저장

---

## 상세 사용법

### 1. 샘플 데이터로 시작하기 (API 키 불필요)

```bash
# 분기별 그래프만 보기
python visualize_timeline.py --generate-sample --quarterly

# 모든 그래프 보기
python visualize_timeline.py --generate-sample
```

### 2. 실제 Reddit 데이터 수집

Reddit API 키가 필요합니다.

#### Reddit API 키 발급 방법:
1. https://www.reddit.com/prefs/apps 접속 (로그인 필요)
2. 페이지 하단 "create app" 또는 "create another app" 클릭
3. 이름 입력 (예: buldak_tracker)
4. "script" 선택
5. redirect uri에 `http://localhost:8080` 입력
6. "create app" 클릭
7. client_id (앱 이름 바로 아래 짧은 문자열)와 secret 확인

#### 데이터 수집:

```bash
python reddit_buldak_collector.py \
    --client-id YOUR_CLIENT_ID \
    --client-secret YOUR_CLIENT_SECRET \
    --output buldak_timeline.csv
```

#### 시각화:

```bash
# 분기별 그래프만
python visualize_timeline.py --input buldak_timeline.csv --quarterly

# 모든 그래프
python visualize_timeline.py --input buldak_timeline.csv
```

---

## 출력 파일

| 파일 | 설명 |
|------|------|
| `buldak_timeline.csv` | 일별 집계된 시계열 데이터 |
| `charts/buldak_quarterly.png` | **분기별 언급량 막대 그래프** |
| `charts/buldak_timeline.png` | 일별 시계열 그래프 |
| `charts/buldak_heatmap.png` | 요일별 히트맵 |
| `charts/buldak_monthly.png` | 월별 요약 차트 |

---

## 검색 키워드

다음 키워드로 Reddit을 검색합니다:
- `buldak`, `불닭`
- `fire noodles`, `samyang fire`
- `hot chicken ramen`
- `2x spicy`, `carbonara buldak`

## 검색 대상 서브레딧

- r/spicy, r/ramen, r/instantramen
- r/KoreanFood, r/asianeats
- r/food, r/FoodPorn
- r/snackexchange, r/korea

---

## 명령어 옵션

```bash
# 차트 저장만 (화면 표시 안함) - 서버 환경에서 유용
python visualize_timeline.py --generate-sample --no-show

# 출력 디렉토리 지정
python visualize_timeline.py --output-dir ./my_charts

# 분기별 그래프만 생성
python visualize_timeline.py --quarterly
```

---

## 문제 해결

### "ModuleNotFoundError" 오류
```bash
pip install -r requirements.txt
```

### 그래프가 안 보여요
- `--no-show` 옵션을 제거하세요
- 또는 `charts/` 폴더에서 저장된 PNG 파일을 확인하세요

### 한글이 깨져요
- matplotlib 한글 폰트 설정이 필요할 수 있습니다
- macOS: `pip install koreanize-matplotlib`
- Windows: 기본 폰트로 표시됩니다

---

## 주의사항

- Reddit API는 요청 제한이 있습니다 (분당 100회)
- 스크립트는 자동으로 rate limiting을 적용합니다
- 대량의 히스토리 데이터가 필요한 경우 Pushshift API 사용을 고려하세요

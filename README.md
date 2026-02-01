# Reddit BULDAK Timeline Tracker

Reddit에서 불닭(BULDAK) 관련 언급량을 수집하고 시계열 그래프로 시각화하는 도구입니다.

## 설치

```bash
pip install -r requirements.txt
```

## 사용 방법

### 1. 샘플 데이터로 시작하기 (API 키 불필요)

데모용 샘플 데이터를 생성하고 시각화:

```bash
# 샘플 데이터 생성
python reddit_buldak_collector.py --sample

# 시각화
python visualize_timeline.py
```

또는 한 번에:

```bash
python visualize_timeline.py --generate-sample
```

### 2. 실제 Reddit 데이터 수집

Reddit API 키가 필요합니다.

#### Reddit API 키 발급 방법:
1. https://www.reddit.com/prefs/apps 접속
2. "create app" 또는 "create another app" 클릭
3. 이름 입력, "script" 선택
4. redirect uri에 `http://localhost:8080` 입력
5. "create app" 클릭
6. client_id (앱 이름 아래 문자열)와 secret 확인

#### 데이터 수집:

```bash
python reddit_buldak_collector.py \
    --client-id YOUR_CLIENT_ID \
    --client-secret YOUR_CLIENT_SECRET \
    --output buldak_timeline.csv
```

#### 시각화:

```bash
python visualize_timeline.py --input buldak_timeline.csv
```

## 출력 파일

- `buldak_timeline.csv`: 일별 집계된 시계열 데이터
- `charts/buldak_timeline.png`: 메인 시계열 그래프
- `charts/buldak_heatmap.png`: 요일별 히트맵
- `charts/buldak_monthly.png`: 월별 요약 차트

## 검색 키워드

다음 키워드로 Reddit을 검색합니다:
- buldak, 불닭
- fire noodles, samyang fire
- hot chicken ramen
- 2x spicy, carbonara buldak

## 검색 대상 서브레딧

- r/spicy, r/ramen, r/instantramen
- r/KoreanFood, r/asianeats
- r/food, r/FoodPorn
- r/snackexchange, r/korea

## 시각화 옵션

```bash
# 차트 저장만 (화면 표시 안함)
python visualize_timeline.py --no-show

# 출력 디렉토리 지정
python visualize_timeline.py --output-dir ./my_charts
```

## 주의사항

- Reddit API는 요청 제한이 있습니다 (분당 100회)
- 스크립트는 자동으로 rate limiting을 적용합니다
- 대량의 히스토리 데이터가 필요한 경우 Pushshift API 사용을 고려하세요

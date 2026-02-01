# BULDAK Tracker

불닭(BULDAK) 관련 데이터를 수집하고 시계열 그래프로 시각화하는 도구입니다.

## 지원하는 데이터 소스

| 소스 | 데이터 | API 필요 |
|------|--------|----------|
| **Reddit** | 언급량, 업보트, 댓글 | Reddit API (무료) |
| **Amazon** | 제품 리뷰, 별점 | Rainforest API (무료 100회/월) |

---

## 빠른 시작 (Colab)

### Reddit 분기별 언급량
```python
!pip install praw pandas matplotlib numpy -q
!git clone https://github.com/alskdjfasdfsadf/BULDAK.git
%cd BULDAK

from run_quarterly import main
main()
```

### Amazon 리뷰 분석
```python
from run_amazon import run_amazon_analysis
run_amazon_analysis()  # 샘플 데이터

# 실제 데이터 (API 키 필요)
# run_amazon_analysis(api_key="YOUR_RAINFOREST_API_KEY")
```

---

## Amazon 리뷰 분석

### 샘플 데이터로 시작 (API 키 불필요)

```bash
python run_amazon.py
```

### 실제 Amazon 데이터 수집

**Rainforest API**를 사용합니다 (무료 100 크레딧/월).

#### API 키 발급 방법:
1. https://www.rainforestapi.com/ 접속
2. 무료 계정 생성 (Sign Up)
3. 대시보드에서 API Key 복사

#### 실행:

```bash
# 명령어로 실행
python run_amazon.py --api-key YOUR_API_KEY

# 또는 Colab에서
from run_amazon import run_amazon_analysis
run_amazon_analysis(api_key="YOUR_API_KEY")
```

### 분석 항목

- **분기별 리뷰 수** - 시간에 따른 리뷰 증가 추이
- **평균 평점 추이** - 분기별 평균 별점 변화
- **별점 분포** - 1~5점 비율 파이 차트
- **제품별 비교** - 어떤 불닭이 인기인지

### 포함된 불닭 제품

| 제품 | ASIN |
|------|------|
| 불닭볶음면 오리지널 | B01MUGP5FJ |
| 핵불닭볶음면 (2배) | B01N7Y0D5U |
| 까르보불닭볶음면 | B07B4MKTL3 |
| 치즈불닭볶음면 | B07QHN2LX8 |
| 짜장불닭볶음면 | B08HV7RPRP |
| 불닭볶음면 라이트 | B09XHQJ5BC |

---

## Reddit 언급량 분석

### 샘플 데이터로 시작 (API 키 불필요)

```bash
python run_quarterly.py
```

### 실제 Reddit 데이터 수집

#### Reddit API 키 발급 방법:
1. https://www.reddit.com/prefs/apps 접속
2. "create app" → "script" 선택
3. redirect uri: `http://localhost:8080`
4. client_id와 secret 확인

#### 실행:

```bash
python reddit_buldak_collector.py \
    --client-id YOUR_CLIENT_ID \
    --client-secret YOUR_CLIENT_SECRET

python visualize_timeline.py --quarterly
```

---

## 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install praw pandas matplotlib numpy requests
```

---

## 출력 파일

| 파일 | 설명 |
|------|------|
| `charts/buldak_quarterly.png` | Reddit 분기별 언급량 |
| `charts/amazon_quarterly.png` | Amazon 분기별 리뷰 수 & 평점 |
| `charts/amazon_rating_dist.png` | Amazon 별점 분포 |
| `charts/amazon_products.png` | 제품별 비교 |

---

## 문제 해결

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Colab에서 그래프가 안 보여요
`!python` 대신 함수를 직접 import해서 실행하세요:
```python
from run_amazon import run_amazon_analysis
run_amazon_analysis()
```

### API 오류
- API 키가 올바른지 확인
- 무료 크레딧이 남아있는지 확인 (Rainforest: 100회/월)

#!/usr/bin/env python3
"""
Amazon BULDAK Review Collector
아마존에서 불닭(BULDAK) 제품 리뷰를 수집합니다.

지원하는 데이터 소스:
1. Rainforest API (실제 아마존 데이터) - API 키 필요
2. 샘플 데이터 생성 (데모용)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random
import time

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# 불닭 제품 목록 (실제 아마존 제품 기반)
BULDAK_PRODUCTS = [
    {
        "asin": "B01MUGP5FJ",
        "name": "Samyang Buldak Hot Chicken Ramen (Original)",
        "name_kr": "불닭볶음면 오리지널",
        "shu": 4404,
    },
    {
        "asin": "B01N7Y0D5U",
        "name": "Samyang 2X Spicy Hot Chicken Ramen",
        "name_kr": "핵불닭볶음면 (2배)",
        "shu": 8808,
    },
    {
        "asin": "B07B4MKTL3",
        "name": "Samyang Carbo Hot Chicken Ramen",
        "name_kr": "까르보불닭볶음면",
        "shu": 2600,
    },
    {
        "asin": "B07QHN2LX8",
        "name": "Samyang Cheese Hot Chicken Ramen",
        "name_kr": "치즈불닭볶음면",
        "shu": 2323,
    },
    {
        "asin": "B08HV7RPRP",
        "name": "Samyang Jjajang Hot Chicken Ramen",
        "name_kr": "짜장불닭볶음면",
        "shu": 1920,
    },
    {
        "asin": "B09XHQJ5BC",
        "name": "Samyang Buldak Light",
        "name_kr": "불닭볶음면 라이트",
        "shu": 1863,
    },
]

class RainforestAPICollector:
    """
    Rainforest API를 사용하여 실제 아마존 리뷰를 수집하는 클래스

    API 키 발급: https://www.rainforestapi.com/ (무료 100 크레딧/월)
    """

    BASE_URL = "https://api.rainforestapi.com/request"

    def __init__(self, api_key: str):
        """
        Args:
            api_key: Rainforest API 키
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests 패키지가 필요합니다: pip install requests")

        self.api_key = api_key
        self.collected_reviews = []

    def get_product_reviews(self, asin: str, amazon_domain: str = "amazon.com",
                           max_pages: int = 5) -> list:
        """
        특정 제품의 리뷰를 가져옵니다.

        Args:
            asin: 아마존 제품 ID
            amazon_domain: 아마존 도메인 (amazon.com, amazon.co.uk 등)
            max_pages: 최대 페이지 수 (페이지당 약 10개 리뷰)

        Returns:
            리뷰 리스트
        """
        reviews = []
        product_info = None

        for page in range(1, max_pages + 1):
            params = {
                "api_key": self.api_key,
                "type": "reviews",
                "amazon_domain": amazon_domain,
                "asin": asin,
                "page": page,
            }

            try:
                print(f"  Fetching page {page} for ASIN: {asin}...")
                response = requests.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                # 제품 정보 저장
                if product_info is None and "product" in data:
                    product_info = data["product"]

                # 리뷰 파싱
                if "reviews" in data:
                    for review in data["reviews"]:
                        reviews.append({
                            "review_id": review.get("id", ""),
                            "asin": asin,
                            "product_name": product_info.get("title", "") if product_info else "",
                            "rating": review.get("rating", 0),
                            "review_date": self._parse_date(review.get("date", {}).get("raw", "")),
                            "review_text": review.get("body", ""),
                            "review_title": review.get("title", ""),
                            "helpful_votes": review.get("helpful_votes", 0),
                            "verified_purchase": review.get("verified_purchase", False),
                            "reviewer_name": review.get("profile", {}).get("name", ""),
                        })

                    # 더 이상 리뷰가 없으면 중단
                    if len(data["reviews"]) == 0:
                        break
                else:
                    break

                # Rate limiting
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"  Error fetching reviews: {e}")
                break

        print(f"  -> Collected {len(reviews)} reviews for ASIN: {asin}")
        return reviews

    def _parse_date(self, date_str: str) -> datetime:
        """날짜 문자열 파싱"""
        try:
            # "Reviewed in the United States on January 15, 2024" 형식
            if "on " in date_str:
                date_part = date_str.split("on ")[-1]
                return datetime.strptime(date_part, "%B %d, %Y")
        except:
            pass
        return datetime.now()

    def collect_buldak_reviews(self, max_pages_per_product: int = 3) -> pd.DataFrame:
        """
        모든 불닭 제품의 리뷰를 수집합니다.

        Args:
            max_pages_per_product: 제품당 최대 페이지 수

        Returns:
            리뷰 데이터프레임
        """
        all_reviews = []

        print(f"Collecting reviews for {len(BULDAK_PRODUCTS)} BULDAK products...")

        for product in BULDAK_PRODUCTS:
            reviews = self.get_product_reviews(
                asin=product["asin"],
                max_pages=max_pages_per_product
            )

            # 한국어 이름 추가
            for review in reviews:
                review["product_name_kr"] = product["name_kr"]

            all_reviews.extend(reviews)
            time.sleep(2)  # Rate limiting between products

        df = pd.DataFrame(all_reviews)
        if not df.empty:
            df["review_date"] = pd.to_datetime(df["review_date"])

        self.collected_reviews = df
        print(f"\nTotal reviews collected: {len(df)}")
        return df


# 샘플 리뷰 템플릿
REVIEW_TEMPLATES = {
    5: [
        "Amazing spicy noodles! Perfect heat level.",
        "Best instant ramen I've ever had. So addictive!",
        "Love the flavor and the kick. Will buy again!",
        "My new favorite! The sauce is incredible.",
        "Absolutely delicious. Worth every penny.",
        "Finally found my go-to spicy noodles!",
        "The heat is perfect, not too much, not too little.",
        "Obsessed with these! Already ordered more.",
    ],
    4: [
        "Great taste but a bit too spicy for me.",
        "Really good, just wish the portions were bigger.",
        "Tasty noodles, decent heat level.",
        "Good quality ramen. Fast shipping too.",
        "Nice flavor, would recommend to spicy food lovers.",
        "Pretty good, the sauce makes it special.",
        "Enjoyed it! A little oily but still great.",
    ],
    3: [
        "It's okay. Expected more flavor.",
        "Decent ramen, but too spicy for everyday eating.",
        "Average taste. The hype is a bit overrated.",
        "Not bad, not great. Just okay.",
        "The spice overpowers the flavor a bit.",
        "It's fine. I've had better instant noodles.",
    ],
    2: [
        "Way too spicy. Couldn't finish it.",
        "Disappointed. Not worth the price.",
        "The noodles were mushy after cooking.",
        "Too oily and overwhelming spice.",
        "Expected better quality for the price.",
    ],
    1: [
        "Inedible. Way too hot!",
        "Burned my mouth. Never again.",
        "Terrible experience. Not for me.",
        "Waste of money. Couldn't eat it.",
        "The spice ruined everything.",
    ],
}


def generate_sample_reviews(start_year: int = 2023, reviews_per_month: tuple = (50, 150)):
    """
    샘플 리뷰 데이터 생성

    Args:
        start_year: 시작 연도
        reviews_per_month: 월별 리뷰 수 범위 (min, max)

    Returns:
        리뷰 데이터프레임
    """
    print(f"Generating sample Amazon reviews from {start_year}...")

    np.random.seed(42)
    random.seed(42)

    reviews = []
    start_date = datetime(start_year, 1, 1)
    end_date = datetime.now()

    current_date = start_date
    review_id = 1

    while current_date < end_date:
        # 월별 리뷰 수 (시간이 지날수록 증가하는 트렌드)
        months_passed = (current_date.year - start_year) * 12 + current_date.month
        growth_factor = 1 + (months_passed * 0.02)  # 매월 2% 증가
        base_reviews = random.randint(*reviews_per_month)
        num_reviews = int(base_reviews * growth_factor)

        # 이번 달의 리뷰 생성
        for _ in range(num_reviews):
            # 랜덤 날짜 (해당 월 내)
            day = random.randint(1, 28)
            review_date = current_date.replace(day=day)

            if review_date > end_date:
                break

            # 랜덤 제품 선택
            product = random.choice(BULDAK_PRODUCTS)

            # 별점 분포 (4-5점이 많도록 가중치)
            # 불닭은 인기 제품이라 높은 평점이 많음
            rating_weights = [0.05, 0.08, 0.12, 0.30, 0.45]  # 1~5점 가중치
            rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]

            # 리뷰 텍스트 선택
            review_text = random.choice(REVIEW_TEMPLATES[rating])

            # 도움이 됐어요 수 (높은 평점일수록 더 많은 helpful)
            helpful_votes = int(np.random.exponential(rating * 2))

            reviews.append({
                "review_id": f"R{review_id:08d}",
                "asin": product["asin"],
                "product_name": product["name"],
                "product_name_kr": product["name_kr"],
                "rating": rating,
                "review_date": review_date,
                "review_text": review_text,
                "helpful_votes": helpful_votes,
                "verified_purchase": random.random() > 0.1,  # 90% verified
            })
            review_id += 1

        # 다음 달로
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    df = pd.DataFrame(reviews)
    print(f"Generated {len(df)} sample reviews")
    return df


def aggregate_reviews_by_time(df: pd.DataFrame, freq: str = "ME") -> pd.DataFrame:
    """
    시간별로 리뷰 집계

    Args:
        df: 리뷰 데이터프레임
        freq: 집계 주기 (ME=월별, QE=분기별)

    Returns:
        시계열 집계 데이터
    """
    df_copy = df.copy()
    df_copy["period"] = pd.to_datetime(df_copy["review_date"]).dt.to_period(
        freq.replace("E", "")  # ME -> M, QE -> Q
    )

    # 집계
    timeline = df_copy.groupby("period").agg({
        "review_id": "count",
        "rating": "mean",
        "helpful_votes": "sum",
    }).rename(columns={
        "review_id": "review_count",
        "rating": "avg_rating",
        "helpful_votes": "total_helpful",
    })

    # 별점 분포 계산
    for rating in range(1, 6):
        rating_counts = df_copy[df_copy["rating"] == rating].groupby("period").size()
        timeline[f"rating_{rating}_count"] = rating_counts
        timeline[f"rating_{rating}_count"] = timeline[f"rating_{rating}_count"].fillna(0).astype(int)

    timeline.index = timeline.index.to_timestamp()
    return timeline


def aggregate_by_product(df: pd.DataFrame) -> pd.DataFrame:
    """제품별 집계"""
    product_stats = df.groupby(["asin", "product_name", "product_name_kr"]).agg({
        "review_id": "count",
        "rating": ["mean", "std"],
        "helpful_votes": "sum",
    }).round(2)

    product_stats.columns = ["review_count", "avg_rating", "rating_std", "total_helpful"]
    product_stats = product_stats.reset_index()
    return product_stats.sort_values("review_count", ascending=False)


def save_data(df: pd.DataFrame, filename: str):
    """데이터 저장"""
    df.to_csv(filename, index=True, encoding="utf-8-sig")
    print(f"Data saved to {filename}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Amazon BULDAK Review Collector")
    parser.add_argument("--api-key", help="Rainforest API key for real Amazon data")
    parser.add_argument("--sample", action="store_true", help="Use sample data (no API needed)")
    parser.add_argument("--start-year", type=int, default=2023, help="Start year for sample data")
    parser.add_argument("--max-pages", type=int, default=3, help="Max pages per product (API mode)")
    parser.add_argument("--output", default="amazon_buldak_reviews.csv", help="Output file")

    args = parser.parse_args()

    if args.api_key:
        # 실제 API 사용
        print("=" * 60)
        print("  Amazon BULDAK Review Collector (Rainforest API)")
        print("=" * 60)

        collector = RainforestAPICollector(api_key=args.api_key)
        reviews_df = collector.collect_buldak_reviews(max_pages_per_product=args.max_pages)

        if reviews_df.empty:
            print("No reviews collected. Check your API key.")
            exit(1)

    elif args.sample:
        # 샘플 데이터 생성
        print("=" * 60)
        print("  Amazon BULDAK Review Collector (Sample Data)")
        print("=" * 60)
        reviews_df = generate_sample_reviews(start_year=args.start_year)

    else:
        print("Please provide --api-key for real data or --sample for demo data")
        print()
        print("Usage:")
        print("  Real data:   python amazon_buldak_collector.py --api-key YOUR_API_KEY")
        print("  Sample data: python amazon_buldak_collector.py --sample")
        print()
        print("Get your free API key at: https://www.rainforestapi.com/")
        exit(0)

    # 저장
    reviews_df.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"\nReview data saved to {args.output}")

    # 시계열 데이터도 저장
    timeline = aggregate_reviews_by_time(reviews_df, freq="ME")
    timeline.to_csv("amazon_buldak_timeline.csv", encoding="utf-8-sig")
    print("Timeline data saved to amazon_buldak_timeline.csv")

    # 제품별 통계
    product_stats = aggregate_by_product(reviews_df)
    product_stats.to_csv("amazon_buldak_products.csv", index=False, encoding="utf-8-sig")
    print("Product stats saved to amazon_buldak_products.csv")

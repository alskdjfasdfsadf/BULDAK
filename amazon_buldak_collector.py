#!/usr/bin/env python3
"""
Amazon BULDAK Review Collector
아마존에서 불닭(BULDAK) 제품 리뷰를 수집합니다.

참고: 실제 아마존 스크래핑은 ToS 위반 가능성이 있습니다.
      이 스크립트는 데모용 샘플 데이터 생성 기능을 포함합니다.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random


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
    parser.add_argument("--start-year", type=int, default=2023, help="Start year")
    parser.add_argument("--output", default="amazon_buldak_reviews.csv", help="Output file")

    args = parser.parse_args()

    # 샘플 데이터 생성
    reviews_df = generate_sample_reviews(start_year=args.start_year)

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

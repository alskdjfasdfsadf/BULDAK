#!/usr/bin/env python3
"""
간단 실행 스크립트: 아마존 불닭 리뷰 분석 및 시각화

사용법:
    샘플 데이터: python run_amazon.py
    실제 데이터: python run_amazon.py --api-key YOUR_RAINFOREST_API_KEY

Colab에서 그래프 바로 보기:
    # 샘플 데이터
    from run_amazon import run_amazon_analysis
    run_amazon_analysis()

    # 실제 API 데이터
    from run_amazon import run_amazon_analysis
    run_amazon_analysis(api_key="YOUR_API_KEY")
"""

import os
import sys


def run_amazon_analysis(api_key: str = None):
    """
    아마존 불닭 리뷰 분석 실행

    Args:
        api_key: Rainforest API 키 (없으면 샘플 데이터 사용)
    """
    print("=" * 60)
    print("  Amazon BULDAK Review Analysis")
    print("  아마존 불닭 리뷰 분석")
    if api_key:
        print("  [실제 Amazon 데이터 - Rainforest API]")
    else:
        print("  [샘플 데이터 - Demo Mode]")
    print("=" * 60)
    print()

    # 패키지 확인
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as e:
        print("필요한 패키지가 없습니다:")
        print("  pip install pandas matplotlib numpy requests")
        return None

    # 1. 데이터 수집
    if api_key:
        print("[1/4] 실제 Amazon 리뷰 수집 중 (Rainforest API)...")
        print("      (제품당 약 30개 리뷰, 총 6개 제품)")
        print()
        try:
            from amazon_buldak_collector import RainforestAPICollector
            collector = RainforestAPICollector(api_key=api_key)
            df = collector.collect_buldak_reviews(max_pages_per_product=3)

            if df.empty:
                print("      리뷰를 가져오지 못했습니다. API 키를 확인하세요.")
                return None
        except Exception as e:
            print(f"      API 오류: {e}")
            print("      샘플 데이터로 전환합니다...")
            from amazon_buldak_collector import generate_sample_reviews
            df = generate_sample_reviews(start_year=2023)
    else:
        print("[1/4] 샘플 리뷰 데이터 생성 중...")
        from amazon_buldak_collector import generate_sample_reviews
        df = generate_sample_reviews(start_year=2023)

    # CSV 저장
    df.to_csv("amazon_buldak_reviews.csv", index=False, encoding="utf-8-sig")
    print(f"      -> amazon_buldak_reviews.csv 저장 완료")

    # 2. 통계 출력
    print()
    print("[2/4] 리뷰 통계:")
    print(f"      총 리뷰 수: {len(df):,}개")

    if "review_date" in df.columns:
        df["review_date"] = pd.to_datetime(df["review_date"])
        print(f"      기간: {df['review_date'].min().date()} ~ {df['review_date'].max().date()}")

    print(f"      평균 평점: {df['rating'].mean():.2f} / 5.00")

    print()
    print("      [별점 분포]")
    for rating in range(5, 0, -1):
        count = (df["rating"] == rating).sum()
        pct = count / len(df) * 100
        stars = "★" * rating + "☆" * (5 - rating)
        bar = "█" * int(pct / 5)
        print(f"      {stars}: {bar} {pct:.1f}%")

    # 3. 분기별 집계
    print()
    print("      [분기별 리뷰 수]")
    df_copy = df.copy()
    df_copy["quarter"] = pd.to_datetime(df_copy["review_date"]).dt.to_period("Q")
    quarterly = df_copy.groupby("quarter").size()
    for q, count in quarterly.items():
        print(f"      {q}: {count:,}개")

    # 4. 그래프 생성
    print()
    print("[3/4] 그래프 생성 중...")
    os.makedirs("charts", exist_ok=True)

    from visualize_amazon import (
        plot_quarterly_reviews,
    )

    # 분기별 리뷰 그래프 (메인)
    print()
    print("[4/4] 분기별 리뷰 & 평점 그래프:")
    plot_quarterly_reviews(df, save_path="charts/amazon_quarterly.png", show_plot=True)

    print()
    print("=" * 60)
    print("  완료!")
    print("  그래프가 charts/ 폴더에 저장되었습니다.")
    if not api_key:
        print()
        print("  실제 Amazon 데이터를 보려면:")
        print("    run_amazon_analysis(api_key='YOUR_KEY')")
        print()
        print("  API 키 발급: https://www.rainforestapi.com/")
    print("=" * 60)

    return df


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Amazon BULDAK Review Analysis")
    parser.add_argument("--api-key", help="Rainforest API key for real Amazon data")

    args = parser.parse_args()
    run_amazon_analysis(api_key=args.api_key)


if __name__ == "__main__":
    main()

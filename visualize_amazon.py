#!/usr/bin/env python3
"""
Amazon BULDAK Review Visualizer
아마존 불닭 리뷰의 시각화를 생성합니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# 폰트 설정 (Colab/Linux 호환)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


def load_reviews(filepath: str) -> pd.DataFrame:
    """리뷰 데이터 로드"""
    df = pd.read_csv(filepath, parse_dates=["review_date"])
    return df


def plot_rating_distribution(df: pd.DataFrame, save_path: str = None, show_plot: bool = True):
    """
    별점 분포 파이 차트
    """
    rating_counts = df["rating"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 8))

    colors = ["#ff6b6b", "#ffa06b", "#ffd93d", "#6bcf6b", "#4ecdc4"]
    explode = [0.02] * 5

    wedges, texts, autotexts = ax.pie(
        rating_counts.values,
        labels=[f"{i} Star" for i in rating_counts.index],
        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*sum(rating_counts.values))})',
        colors=colors,
        explode=explode,
        startangle=90,
        textprops={'fontsize': 11},
    )

    # 평균 평점 표시
    avg_rating = df["rating"].mean()
    ax.text(0, 0, f"Avg\n{avg_rating:.2f}", ha='center', va='center',
            fontsize=20, fontweight='bold')

    ax.set_title("Amazon BULDAK Reviews - Rating Distribution",
                 fontsize=16, fontweight='bold', pad=20)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Rating distribution saved to {save_path}")

    if show_plot:
        plt.show()

    return fig


def plot_quarterly_reviews(df: pd.DataFrame, save_path: str = None, show_plot: bool = True):
    """
    분기별 리뷰 수 및 평균 평점 그래프
    """
    df_copy = df.copy()
    df_copy["quarter"] = pd.to_datetime(df_copy["review_date"]).dt.to_period("Q")

    quarterly = df_copy.groupby("quarter").agg({
        "review_id": "count",
        "rating": "mean"
    }).rename(columns={"review_id": "review_count", "rating": "avg_rating"})

    quarterly.index = quarterly.index.astype(str)

    fig, ax1 = plt.subplots(figsize=(14, 7))

    # 막대 그래프 (리뷰 수)
    colors = plt.cm.Blues([0.4 + 0.4 * i / len(quarterly) for i in range(len(quarterly))])
    bars = ax1.bar(range(len(quarterly)), quarterly["review_count"],
                   color=colors, edgecolor='darkblue', linewidth=1.2, alpha=0.8)

    ax1.set_xlabel("Quarter (분기)", fontsize=12)
    ax1.set_ylabel("Review Count (리뷰 수)", fontsize=12, color='darkblue')
    ax1.tick_params(axis='y', labelcolor='darkblue')
    ax1.set_xticks(range(len(quarterly)))
    ax1.set_xticklabels(quarterly.index, rotation=45, ha='right', fontsize=10)

    # 값 레이블
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.annotate(f'{int(height):,}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5), textcoords="offset points",
                     ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 라인 그래프 (평균 평점) - 두 번째 Y축
    ax2 = ax1.twinx()
    line = ax2.plot(range(len(quarterly)), quarterly["avg_rating"],
                    color='#ff6b6b', linewidth=3, marker='o', markersize=8,
                    label='Avg Rating')
    ax2.set_ylabel("Average Rating (평균 평점)", fontsize=12, color='#ff6b6b')
    ax2.tick_params(axis='y', labelcolor='#ff6b6b')
    ax2.set_ylim(3.5, 5.0)

    # 평점 값 레이블
    for i, (x, y) in enumerate(zip(range(len(quarterly)), quarterly["avg_rating"])):
        ax2.annotate(f'{y:.2f}', xy=(x, y), xytext=(0, 10),
                     textcoords="offset points", ha='center', fontsize=9,
                     color='#ff6b6b', fontweight='bold')

    ax1.set_title("Amazon BULDAK Reviews by Quarter\n(Review Count & Average Rating)",
                  fontsize=16, fontweight='bold', pad=20)

    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_axisbelow(True)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Quarterly chart saved to {save_path}")

    if show_plot:
        plt.show()

    return fig


def plot_product_comparison(df: pd.DataFrame, save_path: str = None, show_plot: bool = True):
    """
    제품별 리뷰 수 및 평점 비교
    """
    product_stats = df.groupby("product_name_kr").agg({
        "review_id": "count",
        "rating": "mean"
    }).rename(columns={"review_id": "review_count", "rating": "avg_rating"})

    product_stats = product_stats.sort_values("review_count", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8))

    # 수평 막대 그래프
    colors = plt.cm.Reds([0.3 + 0.5 * product_stats["avg_rating"].values[i] / 5
                          for i in range(len(product_stats))])

    bars = ax.barh(range(len(product_stats)), product_stats["review_count"],
                   color=colors, edgecolor='darkred', linewidth=1)

    ax.set_yticks(range(len(product_stats)))
    ax.set_yticklabels(product_stats.index, fontsize=11)
    ax.set_xlabel("Review Count (리뷰 수)", fontsize=12)
    ax.set_title("BULDAK Products - Review Count by Product",
                 fontsize=16, fontweight='bold', pad=20)

    # 리뷰 수와 평점 레이블
    for i, (count, rating) in enumerate(zip(product_stats["review_count"],
                                             product_stats["avg_rating"])):
        ax.annotate(f'{int(count):,} reviews | ★{rating:.2f}',
                    xy=(count + 20, i),
                    va='center', fontsize=10)

    ax.grid(True, alpha=0.3, axis='x')
    ax.set_axisbelow(True)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Product comparison saved to {save_path}")

    if show_plot:
        plt.show()

    return fig


def plot_rating_trend(df: pd.DataFrame, save_path: str = None, show_plot: bool = True):
    """
    월별 별점 분포 스택 차트
    """
    df_copy = df.copy()
    df_copy["month"] = pd.to_datetime(df_copy["review_date"]).dt.to_period("M")

    # 월별 별점 분포
    rating_by_month = df_copy.groupby(["month", "rating"]).size().unstack(fill_value=0)
    rating_by_month.index = rating_by_month.index.astype(str)

    # 비율로 변환
    rating_pct = rating_by_month.div(rating_by_month.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(16, 8))

    colors = ["#ff6b6b", "#ffa06b", "#ffd93d", "#6bcf6b", "#4ecdc4"]

    rating_pct.plot(kind='bar', stacked=True, ax=ax, color=colors, width=0.8, alpha=0.85)

    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Percentage (%)", fontsize=12)
    ax.set_title("BULDAK Reviews - Rating Distribution Over Time",
                 fontsize=16, fontweight='bold', pad=20)

    ax.legend(title="Rating", labels=["1 Star", "2 Star", "3 Star", "4 Star", "5 Star"],
              bbox_to_anchor=(1.02, 1), loc='upper left')

    # X축 레이블 간소화
    tick_positions = range(0, len(rating_pct), 3)  # 3개월마다
    ax.set_xticks(tick_positions)
    ax.set_xticklabels([rating_pct.index[i] for i in tick_positions], rotation=45, ha='right')

    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Rating trend saved to {save_path}")

    if show_plot:
        plt.show()

    return fig


def print_summary(df: pd.DataFrame):
    """리뷰 요약 통계 출력"""
    print("\n" + "=" * 60)
    print("  Amazon BULDAK Review Summary")
    print("=" * 60)
    print(f"\n  Total Reviews: {len(df):,}")
    print(f"  Period: {df['review_date'].min().date()} ~ {df['review_date'].max().date()}")
    print(f"\n  Average Rating: {df['rating'].mean():.2f} / 5.00")
    print(f"  Verified Purchases: {df['verified_purchase'].sum():,} ({df['verified_purchase'].mean()*100:.1f}%)")

    print("\n  Rating Distribution:")
    for rating in range(5, 0, -1):
        count = (df["rating"] == rating).sum()
        pct = count / len(df) * 100
        bar = "█" * int(pct / 2)
        print(f"    {rating} Star: {bar} {pct:.1f}% ({count:,})")

    print("\n  Top Products by Review Count:")
    top_products = df.groupby("product_name_kr")["review_id"].count().sort_values(ascending=False)
    for i, (product, count) in enumerate(top_products.head(5).items(), 1):
        print(f"    {i}. {product}: {count:,} reviews")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Visualize Amazon BULDAK reviews")
    parser.add_argument("--input", "-i", default="amazon_buldak_reviews.csv", help="Input CSV")
    parser.add_argument("--output-dir", "-o", default="./charts", help="Output directory")
    parser.add_argument("--no-show", action="store_true", help="Don't display charts")
    parser.add_argument("--generate-sample", action="store_true", help="Generate sample data")

    args = parser.parse_args()

    if args.generate_sample:
        from amazon_buldak_collector import generate_sample_reviews
        df = generate_sample_reviews(start_year=2023)
        df.to_csv("amazon_buldak_reviews.csv", index=False, encoding="utf-8-sig")
        input_file = "amazon_buldak_reviews.csv"
    else:
        input_file = args.input

    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        print("Run with --generate-sample to create sample data.")
        exit(1)

    df = load_reviews(input_file)
    show = not args.no_show

    os.makedirs(args.output_dir, exist_ok=True)

    print_summary(df)

    print("Generating charts...")

    plot_rating_distribution(df, os.path.join(args.output_dir, "amazon_rating_dist.png"), show)
    plot_quarterly_reviews(df, os.path.join(args.output_dir, "amazon_quarterly.png"), show)
    plot_product_comparison(df, os.path.join(args.output_dir, "amazon_products.png"), show)
    plot_rating_trend(df, os.path.join(args.output_dir, "amazon_rating_trend.png"), show)

    print(f"\nAll charts saved to {args.output_dir}/")

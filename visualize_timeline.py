#!/usr/bin/env python3
"""
Reddit BULDAK Timeline Visualizer
불닭(BULDAK) 언급량의 시계열 그래프를 생성합니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import argparse
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = ['DejaVu Sans', 'Malgun Gothic', 'AppleGothic', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


def load_timeline_data(filepath: str) -> pd.DataFrame:
    """시계열 데이터 로드"""
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    return df


def plot_mention_timeline(df: pd.DataFrame, save_path: str = None,
                          show_plot: bool = True):
    """
    언급량 시계열 그래프 생성

    Args:
        df: 시계열 데이터프레임
        save_path: 저장 경로 (None이면 저장 안함)
        show_plot: 화면에 표시 여부
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle('Reddit BULDAK (불닭) Mentions Timeline', fontsize=16, fontweight='bold')

    # 1. 일별 언급량
    ax1 = axes[0]
    ax1.fill_between(df.index, df['mention_count'], alpha=0.3, color='#FF6B6B')
    ax1.plot(df.index, df['mention_count'], color='#FF6B6B', linewidth=1.5, label='Daily Mentions')

    # 7일 이동평균
    ma7 = df['mention_count'].rolling(window=7).mean()
    ax1.plot(df.index, ma7, color='#C92A2A', linewidth=2, linestyle='--', label='7-Day Moving Avg')

    ax1.set_ylabel('Mention Count', fontsize=11)
    ax1.set_title('Daily Mention Count', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(bottom=0)

    # 2. 누적 점수 (Engagement)
    ax2 = axes[1]
    ax2.fill_between(df.index, df['total_score'], alpha=0.3, color='#4ECDC4')
    ax2.plot(df.index, df['total_score'], color='#4ECDC4', linewidth=1.5, label='Total Score (Upvotes)')
    ax2.set_ylabel('Total Score', fontsize=11)
    ax2.set_title('Daily Engagement (Upvotes)', fontsize=12)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(bottom=0)

    # 3. 댓글 수
    ax3 = axes[2]
    ax3.fill_between(df.index, df['total_comments'], alpha=0.3, color='#45B7D1')
    ax3.plot(df.index, df['total_comments'], color='#45B7D1', linewidth=1.5, label='Total Comments')
    ax3.set_ylabel('Comment Count', fontsize=11)
    ax3.set_title('Daily Comments', fontsize=12)
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(bottom=0)

    # X축 포맷
    ax3.xaxis.set_major_locator(mdates.MonthLocator())
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Chart saved to {save_path}")

    if show_plot:
        plt.show()

    return fig


def plot_weekly_heatmap(df: pd.DataFrame, save_path: str = None,
                        show_plot: bool = True):
    """
    요일별 언급량 히트맵 생성

    Args:
        df: 시계열 데이터프레임
        save_path: 저장 경로
        show_plot: 화면에 표시 여부
    """
    # 요일과 주차 추출
    df_copy = df.copy()
    df_copy['weekday'] = df_copy.index.dayofweek
    df_copy['week'] = df_copy.index.isocalendar().week

    # 피벗 테이블 생성
    pivot = df_copy.pivot_table(
        values='mention_count',
        index='weekday',
        columns='week',
        aggfunc='mean',
        fill_value=0
    )

    fig, ax = plt.subplots(figsize=(16, 4))

    im = ax.imshow(pivot.values, aspect='auto', cmap='YlOrRd')

    ax.set_yticks(range(7))
    ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    ax.set_xlabel('Week of Year')
    ax.set_title('BULDAK Mentions Heatmap by Day of Week', fontsize=14, fontweight='bold')

    plt.colorbar(im, label='Avg Mentions')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Heatmap saved to {save_path}")

    if show_plot:
        plt.show()

    return fig


def plot_monthly_summary(df: pd.DataFrame, save_path: str = None,
                         show_plot: bool = True):
    """
    월별 요약 차트 생성

    Args:
        df: 시계열 데이터프레임
        save_path: 저장 경로
        show_plot: 화면에 표시 여부
    """
    # 월별 집계
    monthly = df.resample('M').agg({
        'mention_count': 'sum',
        'total_score': 'sum',
        'total_comments': 'sum'
    })

    fig, ax = plt.subplots(figsize=(12, 6))

    x = range(len(monthly))
    width = 0.25

    bars1 = ax.bar([i - width for i in x], monthly['mention_count'],
                   width, label='Mentions', color='#FF6B6B', alpha=0.8)
    bars2 = ax.bar(x, monthly['total_comments'],
                   width, label='Comments', color='#45B7D1', alpha=0.8)

    ax.set_xlabel('Month')
    ax.set_ylabel('Count')
    ax.set_title('Monthly BULDAK Activity Summary', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime('%Y-%m') for d in monthly.index], rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # 값 레이블 추가
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Monthly summary saved to {save_path}")

    if show_plot:
        plt.show()

    return fig


def generate_statistics(df: pd.DataFrame) -> dict:
    """통계 요약 생성"""
    stats = {
        "period": {
            "start": str(df.index.min().date()),
            "end": str(df.index.max().date()),
            "total_days": len(df)
        },
        "mentions": {
            "total": int(df['mention_count'].sum()),
            "daily_avg": round(df['mention_count'].mean(), 2),
            "daily_max": int(df['mention_count'].max()),
            "peak_date": str(df['mention_count'].idxmax().date())
        },
        "engagement": {
            "total_score": int(df['total_score'].sum()),
            "total_comments": int(df['total_comments'].sum()),
            "avg_score_per_mention": round(
                df['total_score'].sum() / max(df['mention_count'].sum(), 1), 2
            )
        }
    }
    return stats


def print_statistics(stats: dict):
    """통계 출력"""
    print("\n" + "=" * 50)
    print("📊 BULDAK Reddit Mention Statistics")
    print("=" * 50)
    print(f"\n📅 Period: {stats['period']['start']} ~ {stats['period']['end']}")
    print(f"   Total Days: {stats['period']['total_days']}")
    print(f"\n📝 Mentions:")
    print(f"   Total: {stats['mentions']['total']:,}")
    print(f"   Daily Average: {stats['mentions']['daily_avg']}")
    print(f"   Peak: {stats['mentions']['daily_max']} ({stats['mentions']['peak_date']})")
    print(f"\n💬 Engagement:")
    print(f"   Total Score: {stats['engagement']['total_score']:,}")
    print(f"   Total Comments: {stats['engagement']['total_comments']:,}")
    print(f"   Avg Score/Mention: {stats['engagement']['avg_score_per_mention']}")
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Visualize BULDAK Reddit timeline data")
    parser.add_argument("--input", "-i", default="buldak_timeline.csv",
                        help="Input CSV file path")
    parser.add_argument("--output-dir", "-o", default="./charts",
                        help="Output directory for charts")
    parser.add_argument("--no-show", action="store_true",
                        help="Don't display charts (just save)")
    parser.add_argument("--generate-sample", action="store_true",
                        help="Generate sample data and visualize")

    args = parser.parse_args()

    # 샘플 데이터 생성 옵션
    if args.generate_sample:
        from reddit_buldak_collector import create_sample_data
        df = create_sample_data()
        input_file = "buldak_timeline.csv"
        df.to_csv(input_file, encoding="utf-8-sig")
        print(f"Sample data saved to {input_file}")
    else:
        input_file = args.input

    # 데이터 로드
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        print("Run with --generate-sample to create sample data first.")
        return

    df = load_timeline_data(input_file)
    print(f"Loaded {len(df)} days of data")

    # 출력 디렉토리 생성
    os.makedirs(args.output_dir, exist_ok=True)

    # 통계 출력
    stats = generate_statistics(df)
    print_statistics(stats)

    # 차트 생성
    show = not args.no_show

    print("Generating charts...")

    # 1. 메인 타임라인
    plot_mention_timeline(
        df,
        save_path=os.path.join(args.output_dir, "buldak_timeline.png"),
        show_plot=show
    )

    # 2. 히트맵
    plot_weekly_heatmap(
        df,
        save_path=os.path.join(args.output_dir, "buldak_heatmap.png"),
        show_plot=show
    )

    # 3. 월별 요약
    plot_monthly_summary(
        df,
        save_path=os.path.join(args.output_dir, "buldak_monthly.png"),
        show_plot=show
    )

    print(f"\nAll charts saved to {args.output_dir}/")


if __name__ == "__main__":
    main()

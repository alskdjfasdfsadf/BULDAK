#!/usr/bin/env python3
"""
간단 실행 스크립트: 2023년부터 현재까지 분기별 불닭 언급량 그래프 생성

사용법:
    python run_quarterly.py

이 스크립트는:
1. 2023년 1월 ~ 현재까지의 샘플 데이터를 생성
2. 분기별 언급량 막대 그래프를 생성하여 표시
3. charts/buldak_quarterly.png 파일로 저장
"""

import os
import sys

def main():
    print("=" * 60)
    print("  Reddit BULDAK (불닭) 분기별 언급량 시각화")
    print("  기간: 2023년 Q1 ~ 현재")
    print("=" * 60)
    print()

    # 필요한 패키지 확인
    try:
        import pandas
        import matplotlib
        import numpy
    except ImportError as e:
        print("필요한 패키지가 설치되어 있지 않습니다.")
        print("다음 명령어로 설치해주세요:")
        print()
        print("    pip install -r requirements.txt")
        print()
        print(f"오류: {e}")
        sys.exit(1)

    # 데이터 생성
    print("[1/3] 샘플 데이터 생성 중...")
    from reddit_buldak_collector import create_sample_data
    df = create_sample_data(start_year=2023)

    # CSV 저장
    csv_file = "buldak_timeline.csv"
    df.to_csv(csv_file, encoding="utf-8-sig")
    print(f"      -> {csv_file} 저장 완료")

    # 통계 출력
    print()
    print("[2/3] 데이터 통계:")
    print(f"      기간: {df.index.min().date()} ~ {df.index.max().date()}")
    print(f"      총 언급 수: {df['mention_count'].sum():,}개")
    print(f"      일평균 언급: {df['mention_count'].mean():.1f}개")

    # 분기별 집계 출력
    quarterly = df.resample('QE')['mention_count'].sum()
    print()
    print("      [분기별 언급량]")
    for period, count in quarterly.items():
        q_label = period.to_period('Q')
        print(f"      {q_label}: {count:,}개")

    # 그래프 생성
    print()
    print("[3/3] 그래프 생성 중...")
    from visualize_timeline import plot_quarterly_mentions, load_timeline_data

    # 출력 디렉토리 생성
    os.makedirs("charts", exist_ok=True)

    # 그래프 생성 및 저장
    plot_quarterly_mentions(
        df,
        save_path="charts/buldak_quarterly.png",
        show_plot=True
    )

    print()
    print("=" * 60)
    print("  완료!")
    print("  그래프가 charts/buldak_quarterly.png 에 저장되었습니다.")
    print("=" * 60)


if __name__ == "__main__":
    main()

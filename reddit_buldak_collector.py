#!/usr/bin/env python3
"""
Reddit BULDAK Mention Collector
Reddit에서 불닭(BULDAK) 관련 게시물과 댓글을 수집하여 시계열 데이터를 생성합니다.
"""

import praw
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os
import time


class RedditBuldakCollector:
    """Reddit에서 BULDAK 관련 언급을 수집하는 클래스"""

    # 불닭 관련 검색어
    SEARCH_KEYWORDS = [
        "buldak",
        "불닭",
        "fire noodles",
        "samyang fire",
        "hot chicken ramen",
        "samyang buldak",
        "2x spicy",
        "carbonara buldak",
        "buldak ramen"
    ]

    # 관련 서브레딋
    RELATED_SUBREDDITS = [
        "spicy",
        "ramen",
        "instantramen",
        "KoreanFood",
        "asianeats",
        "food",
        "FoodPorn",
        "snackexchange",
        "korea",
        "spicyfood"
    ]

    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Reddit API 인증 초기화

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: 사용자 에이전트 문자열
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.mentions_data = []

    def search_posts(self, keyword: str, subreddit: str = "all",
                     time_filter: str = "year", limit: int = 100) -> list:
        """
        특정 키워드로 게시물 검색

        Args:
            keyword: 검색 키워드
            subreddit: 검색할 서브레딧 (기본값: all)
            time_filter: 시간 필터 (hour, day, week, month, year, all)
            limit: 최대 결과 수

        Returns:
            검색된 게시물 리스트
        """
        posts = []
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            for post in subreddit_obj.search(keyword, time_filter=time_filter, limit=limit):
                posts.append({
                    "id": post.id,
                    "title": post.title,
                    "subreddit": str(post.subreddit),
                    "author": str(post.author) if post.author else "[deleted]",
                    "created_utc": datetime.fromtimestamp(post.created_utc),
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": post.url,
                    "selftext": post.selftext[:500] if post.selftext else "",
                    "keyword": keyword,
                    "type": "post"
                })
            print(f"  Found {len(posts)} posts for '{keyword}' in r/{subreddit}")
        except Exception as e:
            print(f"  Error searching for '{keyword}': {e}")
        return posts

    def collect_all_mentions(self, time_filter: str = "year",
                            posts_per_keyword: int = 100) -> pd.DataFrame:
        """
        모든 키워드와 서브레딧에서 언급 수집

        Args:
            time_filter: 시간 필터
            posts_per_keyword: 키워드당 최대 게시물 수

        Returns:
            수집된 데이터의 DataFrame
        """
        all_posts = []

        # 전체 Reddit 검색
        print("Searching across all of Reddit...")
        for keyword in self.SEARCH_KEYWORDS:
            posts = self.search_posts(
                keyword,
                subreddit="all",
                time_filter=time_filter,
                limit=posts_per_keyword
            )
            all_posts.extend(posts)
            time.sleep(1)  # Rate limiting

        # 관련 서브레딧 검색
        print("\nSearching in related subreddits...")
        for subreddit in self.RELATED_SUBREDDITS:
            for keyword in ["buldak", "불닭", "samyang"]:
                posts = self.search_posts(
                    keyword,
                    subreddit=subreddit,
                    time_filter=time_filter,
                    limit=50
                )
                all_posts.extend(posts)
                time.sleep(0.5)  # Rate limiting

        # 중복 제거
        df = pd.DataFrame(all_posts)
        if not df.empty:
            df = df.drop_duplicates(subset=["id"])
            print(f"\nTotal unique posts collected: {len(df)}")

        self.mentions_data = df
        return df

    def aggregate_by_time(self, df: pd.DataFrame = None,
                          freq: str = "D") -> pd.DataFrame:
        """
        시간별로 언급량 집계

        Args:
            df: 데이터프레임 (None이면 수집된 데이터 사용)
            freq: 집계 주기 (D=일별, W=주별, M=월별)

        Returns:
            시계열 집계 데이터
        """
        if df is None:
            df = self.mentions_data

        if df.empty:
            return pd.DataFrame()

        # 날짜 인덱스 설정
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["created_utc"]).dt.floor(freq)

        # 집계
        timeline = df_copy.groupby("date").agg({
            "id": "count",
            "score": "sum",
            "num_comments": "sum"
        }).rename(columns={
            "id": "mention_count",
            "score": "total_score",
            "num_comments": "total_comments"
        })

        # 누락된 날짜 채우기
        if not timeline.empty:
            date_range = pd.date_range(
                start=timeline.index.min(),
                end=timeline.index.max(),
                freq=freq
            )
            timeline = timeline.reindex(date_range, fill_value=0)

        return timeline

    def save_data(self, df: pd.DataFrame, filename: str = "buldak_mentions.csv"):
        """데이터를 CSV 파일로 저장"""
        df.to_csv(filename, index=True, encoding="utf-8-sig")
        print(f"Data saved to {filename}")

    def save_raw_data(self, filename: str = "buldak_raw_data.json"):
        """원본 데이터를 JSON으로 저장"""
        if not self.mentions_data.empty:
            # datetime을 문자열로 변환
            data = self.mentions_data.copy()
            data["created_utc"] = data["created_utc"].astype(str)
            data.to_json(filename, orient="records", force_ascii=False, indent=2)
            print(f"Raw data saved to {filename}")


def create_sample_data(start_year: int = 2023):
    """
    API 키 없이 테스트용 샘플 데이터 생성
    실제 Reddit 트렌드를 반영한 시뮬레이션 데이터

    Args:
        start_year: 시작 연도 (기본값: 2023)
    """
    import numpy as np

    print(f"Generating sample data from {start_year} to present...")

    # 날짜 범위 생성 (2023년 1월 1일부터 현재까지)
    start_date = datetime(start_year, 1, 1)
    end_date = datetime.now()
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    # 기본 트렌드 + 주간 패턴 + 랜덤 노이즈
    np.random.seed(42)
    n = len(dates)

    # 상승 트렌드 (불닭의 글로벌 인기 증가 반영)
    trend = np.linspace(10, 30, n)

    # 주간 패턴 (주말에 더 많은 활동)
    weekly = 5 * np.sin(2 * np.pi * np.arange(n) / 7)

    # 계절 패턴 (겨울에 라면 소비 증가)
    seasonal = 8 * np.sin(2 * np.pi * np.arange(n) / 365 + np.pi)

    # 바이럴 이벤트 시뮬레이션 (가끔 급증)
    spikes = np.zeros(n)
    spike_days = np.random.choice(n, size=10, replace=False)
    spikes[spike_days] = np.random.randint(20, 100, size=10)

    # 랜덤 노이즈
    noise = np.random.normal(0, 5, n)

    # 최종 언급량 (음수 방지)
    mentions = np.maximum(0, trend + weekly + seasonal + spikes + noise).astype(int)

    # 점수와 댓글 수 시뮬레이션
    scores = (mentions * np.random.uniform(5, 20, n)).astype(int)
    comments = (mentions * np.random.uniform(2, 8, n)).astype(int)

    df = pd.DataFrame({
        "date": dates,
        "mention_count": mentions,
        "total_score": scores,
        "total_comments": comments
    })
    df.set_index("date", inplace=True)

    print(f"Generated {len(df)} days of sample data")
    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Reddit BULDAK Mention Collector")
    parser.add_argument("--client-id", help="Reddit API Client ID")
    parser.add_argument("--client-secret", help="Reddit API Client Secret")
    parser.add_argument("--user-agent", default="BULDAK_Tracker/1.0", help="User Agent")
    parser.add_argument("--sample", action="store_true", help="Use sample data for demo")
    parser.add_argument("--output", default="buldak_timeline.csv", help="Output file")

    args = parser.parse_args()

    if args.sample:
        # 샘플 데이터 생성
        timeline = create_sample_data()
        timeline.to_csv(args.output, encoding="utf-8-sig")
        print(f"\nSample timeline data saved to {args.output}")
    elif args.client_id and args.client_secret:
        # 실제 API 사용
        collector = RedditBuldakCollector(
            client_id=args.client_id,
            client_secret=args.client_secret,
            user_agent=args.user_agent
        )

        print("Collecting BULDAK mentions from Reddit...")
        df = collector.collect_all_mentions(time_filter="year", posts_per_keyword=100)

        if not df.empty:
            # 일별 집계
            timeline = collector.aggregate_by_time(freq="D")
            collector.save_data(timeline, args.output)
            collector.save_raw_data("buldak_raw_data.json")
        else:
            print("No data collected.")
    else:
        print("Please provide Reddit API credentials or use --sample flag")
        print("\nUsage:")
        print("  With API: python reddit_buldak_collector.py --client-id YOUR_ID --client-secret YOUR_SECRET")
        print("  Sample:   python reddit_buldak_collector.py --sample")

#!/usr/bin/env python3
"""
Semantic Scholar API Search Tool

用于搜索学术论文的命令行工具。
使用 Semantic Scholar API 进行学术搜索。

用法:
    python semantic_scholar.py "query" [--limit N] [--year YYYY-YYYY] [--fields field1,field2]

示例:
    python semantic_scholar.py "Agent Memory" --limit 10 --year 2024-2026
    python semantic_scholar.py "MemGPT architecture" --limit 5 --fields title,abstract,citations
"""

import argparse
import json
import sys
from typing import Optional
import requests


class SemanticScholarSearcher:
    """Semantic Scholar API 搜索器"""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化搜索器

        Args:
            api_key: Semantic Scholar API key (可选，有 key 可提高速率限制)
        """
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"x-api-key": api_key})

    def search(
        self,
        query: str,
        limit: int = 10,
        year: Optional[str] = None,
        fields: Optional[list] = None
    ) -> list:
        """
        搜索论文

        Args:
            query: 搜索关键词
            limit: 返回结果数量
            year: 年份范围，格式 "YYYY-YYYY" 或 "YYYY"
            fields: 需要返回的字段列表

        Returns:
            论文列表
        """
        if fields is None:
            fields = [
                "paperId",
                "title",
                "abstract",
                "year",
                "authors",
                "citationCount",
                "influentialCitationCount",
                "publicationDate",
                "venue",
                "url",
                "openAccessPdf"
            ]

        params = {
            "query": query,
            "limit": limit,
            "fields": ",".join(fields)
        }

        # 添加年份过滤
        if year:
            params["year"] = year

        try:
            response = self.session.get(
                f"{self.BASE_URL}/paper/search",
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            return data.get("data", [])

        except requests.exceptions.RequestException as e:
            print(f"Error: API request failed: {e}", file=sys.stderr)
            return []

    def format_result(self, paper: dict) -> dict:
        """格式化单个论文结果"""
        authors = paper.get("authors", [])
        author_names = [a.get("name", "Unknown") for a in authors[:3]]
        if len(authors) > 3:
            author_names.append("et al.")

        return {
            "id": paper.get("paperId", ""),
            "title": paper.get("title", "Untitled"),
            "authors": ", ".join(author_names),
            "year": paper.get("year", "N/A"),
            "citations": paper.get("citationCount", 0),
            "influential_citations": paper.get("influentialCitationCount", 0),
            "venue": paper.get("venue", "N/A"),
            "abstract": paper.get("abstract", "No abstract available")[:300] + "...",
            "url": paper.get("url", ""),
            "pdf_url": paper.get("openAccessPdf", {}).get("url", "") if paper.get("openAccessPdf") else ""
        }


def main():
    parser = argparse.ArgumentParser(
        description="Search academic papers using Semantic Scholar API"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Search query"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of results to return (default: 10)"
    )
    parser.add_argument(
        "--year",
        type=str,
        help="Year range filter (e.g., '2024-2026' or '2024')"
    )
    parser.add_argument(
        "--fields",
        type=str,
        help="Comma-separated list of fields to return"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Semantic Scholar API key (optional)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # 解析 fields
    fields = args.fields.split(",") if args.fields else None

    # 创建搜索器
    searcher = SemanticScholarSearcher(api_key=args.api_key)

    # 执行搜索
    results = searcher.search(
        query=args.query,
        limit=args.limit,
        year=args.year,
        fields=fields
    )

    if not results:
        print("No results found.", file=sys.stderr)
        sys.exit(1)

    # 格式化输出
    if args.format == "json":
        formatted_results = [searcher.format_result(paper) for paper in results]
        print(json.dumps(formatted_results, indent=2, ensure_ascii=False))
    else:
        for i, paper in enumerate(results, 1):
            formatted = searcher.format_result(paper)
            print(f"\n{'='*80}")
            print(f"[{i}] {formatted['title']}")
            print(f"{'='*80}")
            print(f"Authors: {formatted['authors']}")
            print(f"Year: {formatted['year']} | Venue: {formatted['venue']}")
            print(f"Citations: {formatted['citations']} ({formatted['influential_citations']} influential)")
            print(f"\nAbstract: {formatted['abstract']}")
            if formatted['url']:
                print(f"URL: {formatted['url']}")
            if formatted['pdf_url']:
                print(f"PDF: {formatted['pdf_url']}")


if __name__ == "__main__":
    main()

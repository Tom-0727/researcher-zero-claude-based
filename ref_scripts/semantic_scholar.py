import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv



load_dotenv()

def _extract_arxiv_link(paper: Dict[str, Any]) -> str | None:
    """从 Semantic Scholar 返回的 externalIds 中提取 arXiv 链接。"""
    external_ids = paper.get("externalIds") or {}
    arxiv_id = external_ids.get("ArXiv")
    if not arxiv_id:
        return None
    arxiv_id = str(arxiv_id).removeprefix("arXiv:")
    return f"https://arxiv.org/abs/{arxiv_id}"


def search_semantic_scholar(
    query: str, 
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Search papers via the Semantic Scholar Graph API.

    IMPORTANT: This tool uses a STRICT keyword-based academic search engine. It does NOT understand natural-language questions. You MUST use a keyword-based query following the rules below BEFORE calling this tool.

    Query generation rules:
    1. Strip stop words such as: "find", "papers about", "research on",
       "what is", "recent", "how do".
    2. Use double quotes for specific technical phrases or paper titles
       (e.g., "Attention Is All You Need", "Zero-shot learning").
    3. Be specific: prefer method names, model names, datasets, or tasks.
    4. Do NOT pass natural language questions as the query.

    Examples:
    - User: How do large language models handle hallucination?
      Query: "Large Language Models" hallucination mitigation

    - User: Find me the original transformer paper
      Query: "Attention Is All You Need"

    - User: Surveys about graph neural networks
      Query: "Graph Neural Networks" survey

    Args:
        query: Keyword-based search string generated using the rules above
        limit: Number of results to return (default 10)

    Returns:
        A list of dictionaries containing paper metadata.
    """
    
    # 1. 基础 Endpoint
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    # 2. 指定返回字段 (Fields)
    # ReAct Agent 需要摘要(abstract)来判断相关性，需要引用数(citationCount)来判断重要性
    fields = ",".join([
        "paperId", 
        "title", 
        "abstract", 
        "year", 
        "citationCount", 
        "externalIds"
    ])
    
    params = {
        "query": query,
        "limit": limit,
        "fields": fields,
    }
    
    api_key = os.getenv("S2_API_KEY")

    headers = {}
    if api_key:
        print(f"Using API key for Semantic Scholar")
        headers["x-api-key"] = api_key
        
    try:
        # 4. 发送请求
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        
        # 5. 错误处理
        if response.status_code == 429:
            print("Semantic Scholar rate limit exceeded (HTTP 429).")
            return []
        
        response.raise_for_status()
        data = response.json()
        
        # 6. 数据清洗
        results = []
        for paper in data.get("data", []):
            results.append({
                # "id": paper.get("paperId") or None,
                "title": paper.get("title") or "No title available",
                "year": paper.get("year") or None,
                "citations": paper.get("citationCount") or 0,
                "abstract": paper.get("abstract") or "No abstract available.",
                # 直接暴露 arXiv 原文地址；没有则返回 None，不回退到 Semantic Scholar 页面
                "link": _extract_arxiv_link(paper)
            })
            
        return results

    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


if __name__ == "__main__":
    # 示例
    papers = search_semantic_scholar.invoke({
        "query": '"Large Language Models" hallucination mitigation',
        "limit": 3
    })

    print(papers)

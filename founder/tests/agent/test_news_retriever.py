from founder.retrieval.news_retriever import NewsRetriever


def test_news_retriever_loads_and_filters_by_ticker():

    retriever = NewsRetriever()

    if not retriever.articles:
        return

    ticker = retriever.tickers[0]

    results = retriever.search(
        "AI",
        ticker=ticker,
        top_k=5,
    )

    assert all(
        article.get("ticker") == ticker
        for article in results
    )

import asyncio

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


async def async_scrape(urls: list[str]) -> str:
    """
    Async function that scrapes multiple URLs and returns combined markdown content.
    """

    md_generator = DefaultMarkdownGenerator(
        options={
            "ignore_links": True,
            "escape_html": False,
        }
    )

    browser_config = BrowserConfig(
        headless=True,
        verbose=False
    )

    run_config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS,
        stream=False
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:

        results = await crawler.arun_many(
            urls=urls,
            config=run_config
        )

        markdown_results = []

        for result in results:
            if result.success:
                markdown_results.append(result.markdown)
            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")

        return "\n\n".join(markdown_results)


def scrape(urls: list[str]) -> str:
    """
    Synchronous wrapper for async_scrape.
    """
    return asyncio.run(async_scrape(urls))


if __name__ == "__main__":
    URLS = [
        "https://www.scrapethissite.com/faq/",
        "https://www.scrapethissite.com/pages/"
    ]

    print(scrape(URLS))
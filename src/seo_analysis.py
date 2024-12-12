import asyncio
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px
import time
import random


class GoogleTrendsSEOAsync:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)

    async def async_retry(self, func, retries=3, delay=5, *args, **kwargs):
        """
        Retry logic for asynchronous calls.

        Args:
            func (coroutine): The asynchronous function to call.
            retries (int): Maximum number of retries.
            delay (int): Time to wait between retries.
            *args, **kwargs: Arguments for the function.

        Returns:
            The result of the successful function call.
        """
        for attempt in range(retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt < retries - 1:
                    sleep_time = delay + random.uniform(0, 2)  # Add random jitter
                    print(f"Retrying in {sleep_time:.2f}s... (Attempt {attempt + 1})")
                    await asyncio.sleep(sleep_time)
                else:
                    print(f"Max retries reached. Last error: {e}")
                    raise

    async def get_interest_over_time(self, keywords, timeframe='today 12-m', geo=''):
        """
        Fetch interest over time with retry logic.
        """
        async def fetch():
            self.pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
            return self.pytrends.interest_over_time()

        return await self.async_retry(fetch)

    async def get_interest_by_region(self, keyword, resolution='COUNTRY', geo=''):
        """
        Fetch interest by region with retry logic.
        """
        async def fetch():
            self.pytrends.build_payload([keyword], geo=geo)
            return self.pytrends.interest_by_region(resolution=resolution)

        return await self.async_retry(fetch)

    async def get_related_queries(self, keyword, geo=''):
        """
        Fetch related queries with retry logic.
        """
        async def fetch():
            self.pytrends.build_payload([keyword], geo=geo)
            return self.pytrends.related_queries()

        return await self.async_retry(fetch)

    def plot_interest_over_time(self, data, title="Interest Over Time"):
        """
        Visualize interest over time for keywords using Plotly.
        """
        data.reset_index(inplace=True)
        fig = px.line(data, x='date', y=data.columns[:-1], title=title)
        fig.update_layout(xaxis_title="Date", yaxis_title="Search Interest")
        fig.show()

    def plot_interest_by_region(self, data, keyword, title="Regional Interest"):
        """
        Visualize regional interest for a keyword using Plotly.
        """
        data.reset_index(inplace=True)
        fig = px.choropleth(
            data,
            locations=data.index,
            locationmode="country names",
            color=keyword,
            title=title,
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig.update_layout(geo=dict(showframe=False, showcoastlines=False))
        fig.show()


async def main():
    trends = GoogleTrendsSEOAsync()

    # Define keywords
    keywords = ['Black Friday Deals', 'Cyber Monday Deals', 'Holiday Sales']

    # Set region and timeframe
    geo = 'US'  # Example for the United States
    timeframe = 'today 12-m'

    # 1. Analyze Trends
    try:
        interest_over_time = await trends.get_interest_over_time(keywords, timeframe, geo)
        if interest_over_time.empty:
            print("No data retrieved for interest over time.")
        else:
            trends.plot_interest_over_time(interest_over_time, "Emerging Trends in the US")
    except Exception as e:
        print(f"Failed to fetch interest over time: {e}")

    # 2. Regional Analysis
    try:
        region_interest = await trends.get_interest_by_region('Holiday Sales', geo=geo)
        if region_interest.empty:
            print("No data retrieved for regional interest.")
        else:
            trends.plot_interest_by_region(region_interest, 'Holiday Sales', "Regional Interest in the US")
    except Exception as e:
        print(f"Failed to fetch regional interest: {e}")


if __name__ == "__main__":
    asyncio.run(main())

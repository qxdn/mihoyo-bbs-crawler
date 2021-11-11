from enum import Enum
from typing import Callable, List
import httpx
import os
import click
import mihoyo
from mihoyo import ForumType, LatestType, RankType
import asyncio
from tqdm import tqdm


def get_headers():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Referer": "https://bbs.mihoyo.com/",
        "Origin": "https://bbs.mihoyo.com/"
    }
    return headers


async def download2folder(folder: str, urls: List[str]):
    '''
    异步下载
    '''
    if not os.path.exists(folder):
        os.mkdir(folder)
    '''
    
    '''
    os.chdir(folder)
    async with httpx.AsyncClient(headers=get_headers()) as client:
        for url in tqdm(urls):
            r = await client.get(url)
            filename = url.split('/')[-1]
            with open(filename, 'wb') as file:
                file.write(r.content)


def run_async(func: Callable[[str, List[str]], None], *args, **kwargs):
    '''
    运行异步函数
    '''
    loop = asyncio.get_event_loop()
    loop.run_until_complete(func(*args, **kwargs))
    loop.close()


def enum2namelists(enumtype: Enum) -> List:
    return list(map(lambda x: x.name, enumtype))


@click.group()
def cli():
    pass


@cli.command(help="get rank image")
@click.option("--forum", "-f", required=True, type=click.Choice(enum2namelists(ForumType), case_sensitive=False), help='set default forum')
@click.option("--type", "-t", required=True, type=click.Choice(enum2namelists(RankType), case_sensitive=False), help="set rank type")
@click.option("--size", "-s", type=int, default=20)
def rank(forum, type, size):
    rank = mihoyo.Rank(ForumType[forum], RankType[type])
    urls = rank.sync_get_urls(size)
    run_async(download2folder, folder=rank.get_game_name(), urls=urls)


@cli.command(help="get hot image")
@click.option("--forum", "-f", required=True, type=click.Choice(enum2namelists(ForumType), case_sensitive=False), help='set default forum')
@click.option("--size", "-s", type=int, default=20)
def hot(forum, size):
    hot = mihoyo.Hot(ForumType[forum])
    urls = hot.sync_get_urls(size)
    run_async(download2folder, hot.get_game_name(), urls)


@cli.command(help="get good image")
@click.option("--forum", "-f", required=True, type=click.Choice(enum2namelists(ForumType), case_sensitive=False), help='set default forum')
@click.option("--size", "-s", type=int, default=20)
def good(forum, size):
    good = mihoyo.Good(ForumType[forum])
    urls = good.sync_get_urls(size)
    run_async(download2folder, good.get_game_name(), urls)


@cli.command(help="get latest image")
@click.option("--forum", "-f", required=True, type=click.Choice(enum2namelists(ForumType), case_sensitive=False), help='set default forum')
@click.option("--type", "-t", type=click.Choice(enum2namelists(LatestType), case_sensitive=False), help='set latest type')
@click.option("--size", "-s", type=int, default=20)
def latest(forum, type, size):
    latest = mihoyo.Latest(
        ForumType[forum], LatestType[type])
    urls = latest.sync_get_urls(size)
    run_async(download2folder, latest.get_game_name(), urls)


if __name__ == '__main__':
    cli()

from enum import Enum, unique
from typing import Dict, List
import httpx
from urllib import parse


class BasicSpider():

    def __init__(self) -> None:
        self.base_url = "https://bbs-api.mihoyo.com/post/wapi/"
        # api 地址
        self.api = None
        # 社区 id
        self.forum_id = None
        # 含义未知 似乎是game_id
        self.gids = None
        # 精品
        self.is_good = False
        # 热门
        self.is_hot = False
        # 游戏名
        self.game_name = None
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "Referer": "https://bbs.mihoyo.com/",
            "Origin": "https://bbs.mihoyo.com/"
        }

    def get_params(self, page_size: int) -> Dict:
        '''
        获取请求参数
        '''
        return None

    def sync_get_urls(self, page_size: int = 20) -> List:
        '''
        以同步的方式获取图片地址 默认20张，就算不传page_size也是20
        '''
        return []

    def sync_get(self, params: dict = None, is_good: bool = False) -> List:
        '''
        以同步的方式获取response
        params: 请求参数
        is_good: 是否为精华
        '''
        r = httpx.get(self.api, params=params, headers=self.headers)
        return self.handle_response(r, is_good=is_good)

    async def async_get_urls(self, page_size: int = 20) -> List:
        '''
        以异步的方式获取图片地址 默认20张，就算不传page_size也是20
        TODO 测试
        '''
        return []

    async def async_get(self, params: dict = None, is_good: bool = False) -> List:
        '''
        以异步的方式获取response
        params: 请求参数
        is_good: 是否为精华
        '''
        async with httpx.AsyncClient() as client:
            r = await client.get(self.api, params=params, headers=self.headers)

        return self.handle_response(r, is_good=is_good)

    def handle_response(self, response, is_good: bool = False) -> List:
        '''
        处理返回的请求
        '''
        urls = []
        if is_good:
            posts = response.json()["data"]["posts"]
        else:
            posts = response.json()["data"]["list"]
        for post in posts:
            images = post["post"]["images"]
            for image in images:
                urls.append(image)
        return urls

    def get_game_name(self) -> str:
        return self.game_name


@unique
class RankType(Enum):
    '''
    排行榜类型
    '''
    # 日榜
    Daily = 1
    # 周榜
    Weekly = 2
    # 月榜
    Monthly = 3


@unique
class LatestType(Enum):
    '''
    最新回复或者是最新发帖
    '''
    # 最新回复
    LatestComment = 1
    # 最新发帖
    LatestPost = 2


@unique
class GameType(Enum):
    '''
    游戏类型
    '''
    # 原神
    Genshin = 2
    # 崩3
    Honkai3rd = 1
    # 大别墅 话说大别墅为啥是DBY
    DBY = 5
    # 星穹铁道
    StarRail = 6
    # 崩2
    Honkai2 = 3
    # 未定 这名字真奇怪
    TearsOfThemis = 4


@unique
class ForumType(Enum):
    '''
    社区类型 要与游戏类型一致
    '''
    # 原神 cos
    GenshinCos = 49
    # 原神 同人图
    GenshinPic = 29
    # 崩3 同人图
    Honkai3rdPic = 4
    # 大别墅 COS
    DBYCOS = 47
    # 大别墅 同人图
    DBYPIC = 39
    # 星穹铁道 同人图
    StarRailPic = 56
    # 崩2 同人图
    Honkai2Pic = 40
    # 未定 同人图
    TearsOfThemisPic = 38


def get_gids(forum: str) -> GameType:
    forum2gid = {
        "GenshinCos": GameType.Genshin,
        "GenshinPic": GameType.Genshin,
        "Honkai3rdPic": GameType.Honkai3rd,
        "DBYCOS": GameType.DBY,
        "DBYPIC": GameType.DBY,
        "StarRailPic": GameType.StarRail,
        "Honkai2Pic": GameType.Honkai2,
        "TearsOfThemisPic": GameType.TearsOfThemis
    }
    return forum2gid[forum]


class Rank(BasicSpider):
    '''
    榜单
    url: https://bbs.mihoyo.com/ys/imgRanking/49
    '''

    def __init__(self, forum_id: ForumType, type: RankType) -> None:
        super().__init__()
        self.api = parse.urljoin(self.base_url, "getImagePostList")
        self.forum_id = forum_id.value
        gametype = get_gids(forum_id.name)
        self.gids = gametype.value
        # 日榜
        self.type = type.value
        self.game_name = gametype.name

    def get_params(self, page_size: int) -> Dict:
        params = {
            "forum_id": self.forum_id,
            "gids": self.gids,
            "page_size": page_size,
            "type": self.type
        }
        return params

    def sync_get_urls(self, page_size: int = 21) -> List:
        return self.sync_get(self.get_params(page_size))

    async def async_get_urls(self, page_size: int = 20) -> List:
        return await self.async_get(self.get_params(page_size))


class Hot(BasicSpider):
    '''
    热门
    url: https://bbs.mihoyo.com/ys/home/49?type=hot
    '''

    def __init__(self, forum_id: ForumType) -> None:
        super().__init__()
        self.api = parse.urljoin(self.base_url, "getForumPostList")
        self.forum_id = forum_id.value
        gametype = get_gids(forum_id.name)
        self.gids = gametype.value
        self.is_hot = True
        self.game_name = gametype.name

    def get_params(self, page_size: int) -> Dict:
        params = {
            "forum_id": self.forum_id,
            "gids": self.gids,
            "is_good": self.is_good,
            "is_hot": self.is_hot,
            "page_size": page_size
        }
        return params

    def sync_get_urls(self, page_size: int = 20) -> List:
        return self.sync_get(self.get_params(page_size))

    async def async_get_urls(self, page_size: int = 20) -> List:
        return await self.async_get(self.get_params(page_size))


class Good(BasicSpider):
    '''
    精华
    url: https://bbs.mihoyo.com/ys/home/49?type=good
    原神COS精华目录目前为空
    '''

    def __init__(self, forum_id: ForumType) -> None:
        super().__init__()
        self.api = parse.urljoin(self.base_url, "forumGoodPostFullList")
        self.forum_id = forum_id.value
        gametype = get_gids(forum_id.name)
        self.gids = gametype.value
        self.game_name = gametype.name

    def get_params(self, page_size: int) -> Dict:
        params = {
            "forum_id": self.forum_id,
            "gids": self.gids,
            "page_size": page_size
        }
        return params

    def sync_get_urls(self, page_size: int = 20) -> List:
        return self.sync_get(self.get_params(page_size), is_good=True)

    async def async_get_urls(self, page_size: int = 20) -> List:
        return await self.async_get(self.get_params(page_size), is_good=True)


class Latest(BasicSpider):
    '''
    最新回复和发帖
    url: https://bbs.mihoyo.com/ys/home/49?type=1
    '''

    def __init__(self, forum_id: ForumType, sort_type: LatestType) -> None:
        super().__init__()
        self.api = parse.urljoin(self.base_url, "getForumPostList")
        self.forum_id = forum_id.value
        gametype = get_gids(forum_id.name)
        self.gids = gametype.value
        # 排序类型
        self.sort_type = sort_type.value
        self.game_name = gametype.name

    def get_params(self, page_size: int) -> Dict:
        params = {
            "forum_id": self.forum_id,
            "gids": self.gids,
            "page_size": page_size,
            "is_good": self.is_good,
            "is_hot": self.is_hot,
            "sort_type": self.sort_type
        }
        return params

    def sync_get_urls(self, page_size: int = 20) -> List:
        return self.sync_get(self.get_params(page_size))

    async def async_get_urls(self, page_size: int = 20) -> List:
        return await self.async_get(self.get_params(page_size))


if __name__ == '__main__':
    gh = Good(ForumType.Honkai2Pic)
    print(gh.get_game_name())
    # urls = gh.sync_get_urls()
    # print(urls)

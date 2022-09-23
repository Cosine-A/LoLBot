import requests
import json
import discord
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError
from datetime import datetime

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

token = 'MTAyMjQwMDk1Mjk2OTQ2MTkwMQ.Gy5Cct.Kfb9I30FA_oJN_A5cf5dJ0cW9B2fg3VFfX-VRA'

main_channel = 1014858948559503481

now = datetime.now()


@bot.event
async def on_ready():
    state_message = discord.Game("!lol help 를 입력해주세요!")
    await bot.change_presence(status=discord.Status.online, activity=state_message)


command_list = ['search', 'latest']


@bot.event
async def on_message(message):
    search = message.content
    global instance
    if search == "!lol help":
        embed = discord.Embed(title="봇 도움말", color=0xCD8A99)

        embed.add_field(name="!lol info [닉네임]", value=f"해당 플레이어의 정보를 검색합니다.", inline=False)
        embed.add_field(name="!lol latest [닉네임]", value=f"해당 플레이어의 최근 전적을 검색합니다.", inline=False)

        now_time = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}"
        embed.set_footer(text=f"명령어 정보 - {now_time}")
        bot_channel = bot.get_channel(main_channel)
        await bot_channel.send(embed=embed)

    if search.startswith("!lol info "):
        name = space_to_html(search[10:])

        try:
            instance = RankInfo(name)
        except ApiError as e:
            code = e.response.status_code
            await bot.get_channel(main_channel).send(f"존재하지 않는 **소환사** 명입니다. [ERROR: {code}]")
            return

        embed = discord.Embed(title="클릭 시 op.gg로 이동합니다",
                              url=f"https://www.op.gg/summoners/kr/{name}",
                              color=0xFF9900)
        embed.set_thumbnail(url=f"{instance.get_profile()}")
        embed.set_author(name=f"{html_to_space(name)} (Lv.{instance.get_level()})", icon_url=f"{instance.get_profile()}")

        solo_rank = instance.get_solo_rank()
        free_rank = instance.get_free_rank()

        if not solo_rank:
            embed.add_field(name="『 솔로 랭크 』", value="Unranked", inline=True)
        else:
            winning_percentage = str((solo_rank[2] / (solo_rank[2] + solo_rank[3]) * 100))[:2]
            embed.add_field(name="『 솔로 랭크 』",
                            value=f"티어: {solo_rank[0]} {solo_rank[1]}\n"
                                  f"점수: {solo_rank[4]}LP\n"
                                  f"승률: {winning_percentage}%\n"
                                  f"승: {solo_rank[2]}\n"
                                  f"패: {solo_rank[3]}\n"
                            , inline=True)

        if not free_rank:
            embed.add_field(name="『 자유 랭크 』", value="Unranked", inline=True)
        else:
            winning_percentage = str((free_rank[2] / (free_rank[2] + free_rank[3]) * 100))[:2]
            embed.add_field(name="『 자유 랭크 』",
                            value=f"티어: {free_rank[0]} {free_rank[1]}\n"
                                  f"점수: {free_rank[4]}LP\n"
                                  f"승률: {winning_percentage}%\n"
                                  f"승: {free_rank[2]}\n"
                                  f"패: {free_rank[3]}\n"
                            , inline=True)

        embed.add_field(name="1위 숙련도 챔피언",
                        value="1", inline=False)
        embed.set_image(url="https://ddragon.leagueoflegends.com/cdn/12.18.1/img/champion/Pyke.png")

        now_time = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}"
        embed.set_footer(text=f"소환사 정보 검색 - {now_time}")

        bot_channel = bot.get_channel(main_channel)
        await bot_channel.send(embed=embed)

    if search.startswith("!lol latest "):
        name = space_to_html(search[12:])

        try:
            instance = RankInfo(name)
        except ApiError as e:
            code = e.response.status_code
            await bot.get_channel(main_channel).send(f"존재하지 않는 **소환사** 명입니다. [ERROR: {code}]")
            return

        latest_list = instance.get_latest_game()

        embed = discord.Embed(title=f"{name}", color=0xCC9900, description=f"Lv.{instance.get_level()}")

        embed.add_field(name="챔피언", value=f"이름: {latest_list[12]}\n레벨: {latest_list[2]}", inline=False)
        embed.add_field(name="라인", value=f"{latest_list[0]}{latest_list[1]}", inline=False)
        embed.add_field(name="CS", value=f"처치: {latest_list[3]}\n분당: {latest_list[4]}", inline=False)
        embed.add_field(name="K/DA", value=f"{latest_list[5]} / {latest_list[6]} / {latest_list[7]}", inline=False)
        embed.add_field(name="챔피언에게 가한 피해량", value=f"{latest_list[8]}", inline=False)
        embed.add_field(name="와드", value=f"제어와드 설치: {latest_list[9]}"
                                         f"\n와드 설치: {latest_list[10]}"
                                         f"\n와드 파괴: {latest_list[11]}", inline=False)

        now_time = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}"
        embed.set_footer(text=f"최근 전적 검색 - {now_time}")
        bot_channel = bot.get_channel(main_channel)
        await bot_channel.send(embed=embed)


region = 'kr'
api = 'RGAPI-f6c302a1-3899-48a7-ad80-59b49ab80363'

watcher = LolWatcher(api)


class RankInfo:

    def __init__(self, target):
        self.target = target
        self.info_name = watcher.summoner.by_name(region, target)
        print(self.info_name)
        print(self.info_name['profileIconId'])
        self.level = self.info_name["summonerLevel"]

    def get_profile(self):
        return f"http://ddragon.leagueoflegends.com/cdn/12.18.1/img/profileicon/{self.info_name['profileIconId']}.png"

    def get_level(self):
        return self.level

    def get_solo_rank(self):
        return self.get_rank("RANKED_SOLO_5x5")

    def get_free_rank(self):
        return self.get_rank("RANKED_FLEX_SR")

    def get_rank(self, rank):
        rank_list = []
        for info in watcher.league.by_summoner(region, self.info_name["id"]):
            if info["queueType"] == rank:
                rank_list.append(tier_to_korean(info["tier"]))
                rank_list.append(info["rank"])
                rank_list.append(info["wins"])
                rank_list.append(info["losses"])
                rank_list.append(info["leaguePoints"])
        return rank_list

    def get_latest_game(self):
        match_list = watcher.match.matchlist_by_puuid(region, self.info_name["puuid"])
        value = watcher.match.by_id(region, match_list[0])

        info_list = []
        for count in range(0, 10):
            summoner = value['info']['participants'][count]
            if self.target == summoner['summonerName']:
                lane = lane_to_korean(summoner['lane'])
                info_list.append(lane)

                if lane == "탑":
                    if summoner['role'] == "SUPPORT":
                        info_list[0] = ""
                        info_list.append("칼바람 나락")
                elif lane == "칼바람 나락":
                    info_list.append("")
                else:
                    info_list.append(role_to_korean(summoner['role']))

                info_list.append(summoner['champLevel'])
                info_list.append(summoner['totalMinionsKilled'])
                info_list.append(round(summoner['totalMinionsKilled'] / (value['info']['gameDuration'] / 60), 1))
                info_list.append(summoner['kills'])
                info_list.append(summoner['deaths'])
                info_list.append(summoner['assists'])
                info_list.append(summoner['totalDamageDealtToChampions'])
                info_list.append(summoner['visionWardsBoughtInGame'])
                info_list.append(summoner['wardsPlaced'])
                info_list.append(summoner['wardsKilled'])
                info_list.append(summoner['championName'])
                break
        return info_list


def space_to_html(message):
    return message.replace(" ", "%20")


def html_to_space(message):
    return message.replace("%20", " ")


def tier_to_korean(target):
    if target == "CHALLENGER":
        return "챌린저"
    if target == "GRANDMASTER":
        return "그랜드마스터"
    if target == "MASTER":
        return "마스터"
    if target == "DIAMOND":
        return "다이아몬드"
    if target == "PLATINUM":
        return "플레티넘"
    if target == "GOLD":
        return "골드"
    if target == "SILVER":
        return "실버"
    if target == "BRONZE":
        return "브론즈"
    if target == "IRON":
        return "아이언"

def lane_to_korean(target):
    if target == "TOP":
        return "탑"
    if target == "JUNGLE":
        return "정글"
    if target == "MIDDLE":
        return "미드"
    if target == "BOTTOM":
        return "바텀"
    if target == "NONE":
        return "칼바람 나락"


def role_to_korean(target):
    if target == "SOLO":
        return ""
    if target == "NONE":
        return ""
    if target == "CARRY":
        return ", 원딜"
    if target == "SUPPORT":
        return ", 서포터"


bot.run(token)

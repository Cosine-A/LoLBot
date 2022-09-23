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
    if message.channel.id != main_channel:
        return
    global instance
    if search == "!lol help":
        embed = discord.Embed(title="봇 도움말", color=0xCD8A99)

        embed.add_field(name="!lol solo [닉네임]", value=f"해당 플레이어의 솔로 랭크 전적을 검색합니다.", inline=False)
        embed.add_field(name="!lol latest [닉네임]", value=f"해당 플레이어의 최근 전적을 검색합니다.", inline=False)

        now_time = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}"
        embed.set_footer(text=f"명령어 정보 - {now_time}")
        bot_channel = bot.get_channel(main_channel)
        await bot_channel.send(embed=embed)

    if search.startswith("!lol solo "):
        name = search[10:]

        try:
            instance = RankInfo(name)
        except ApiError as e:
            code = e.response.status_code
            await bot.get_channel(main_channel).send(f"존재하지 않는 **소환사** 명입니다. [ERROR: {code}]")
            return

        rank_list = instance.get_solo_rank()

        embed = discord.Embed(title=f"{name}", color=0xFF9900, description=f"Lv.{instance.get_level()}")

        embed.add_field(name="솔로 랭크", value=f"티어: {rank_list[0]} {rank_list[1]}\nLP: {rank_list[4]}\n승: {rank_list[2]}\n패: {rank_list[3]}",
                        inline=False)

        now_time = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}"
        embed.set_footer(text=f"솔로 랭크 검색 - {now_time}")
        bot_channel = bot.get_channel(main_channel)
        await bot_channel.send(embed=embed)

    if search.startswith("!lol latest "):
        name = search[12:]

        try:
            instance = RankInfo(name)
        except ApiError as e:
            code = e.response.status_code
            await bot.get_channel(main_channel).send(f"존재하지 않는 **소환사** 명입니다. [ERROR: {code}]")
            return

        latest_list = instance.get_latest_game()

        embed = discord.Embed(title=f"{name}", color=0xFF9900, description=f"Lv.{instance.get_level()}")

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
api = 'RGAPI-b57f5af7-e4f3-4f27-a825-698fa90fae5a'

watcher = LolWatcher(api)


class RankInfo:

    def __init__(self, target):
        self.target = target
        self.info_name = watcher.summoner.by_name(region, target)
        self.level = self.info_name["summonerLevel"]

    def get_level(self):
        return self.level

    def get_solo_rank(self):
        rank_list = []
        for info in watcher.league.by_summoner(region, self.info_name["id"]):
            print(info)
            if info["queueType"] == "RANKED_SOLO_5x5":
                rank_list.append(info["tier"])
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

import requests
import json
import discord
from discord.ext import commands

intents = discord.Intents.all()

client = commands.Bot(command_prefix="!", intents=intents)

token = 'MTAyMjQwMDk1Mjk2OTQ2MTkwMQ.G2YBlo.0aZMKbcQzjKs4ANu7wUAh2fmLivfK7hbb54WSI'
# api = 'RGAPI-b57f5af7-e4f3-4f27-a825-698fa90fae5a'

# main_channel = 1014858948559503481


@client.event
async def on_ready():
    state_message = discord.Game("아무것도 안하는 중")
    await client.change_presence(status=discord.Status.online, activity=state_message)

client.run(token)

# @bot.event
# async def on_message(message):
#     search = message.content
#     if message.channel.id != main_channel:
#         return
#     if search.startswith("!검색 "):
#         name = search[5:]
#         url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}"
#         request = requests.get(url, headers={"X-Riot-Token": api})
#         if request.status_code == 200:
#             load_json = json.loads(request.text)
#             url2 = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{load_json['id']}"
#
#             res = requests.get(url2, headers={"X-Riot-Token": api})
#             rank_info = json.loads(res.text)
#
#             solo_tier = "언랭"
#             solo_rank = ""
#
#             solo_win = 0
#             solo_lose = 0
#
#             free_tier = "언랭"
#             free_rank = ""
#
#             free_win = 0
#             free_lose = 0
#
#             for i in rank_info:
#                 if i["queueType"] == "RANKED_SOLO_5x5":
#                     # 솔랭
#                     solo_tier = i["tier"]
#                     solo_rank = i["rank"]
#                     solo_win = i["wins"]
#                     solo_lose = i["losses"]
#                 else:
#                     # 자랭
#                     free_tier = i["tier"]
#                     free_rank = i["rank"]
#                     free_win = i["wins"]
#                     free_lose = i["losses"]
#
#             print(solo_tier)
#             print(solo_rank)
#             print(solo_win)
#             print(solo_lose)
#             bot_channel = bot.get_channel(main_channel)
#             embed = discord.Embed(title=f"{name}님의 전적", color=0xFF9900)
#             embed.add_field(name="솔로 랭크", value=f"티어: {solo_tier} {solo_rank}\n승: {solo_win}\n패: {solo_lose}",
#                             inline=True)
#             embed.add_field(name="자유 랭크", value=f"티어: {free_tier} {free_rank}\n승: {free_win}\n패: {free_lose}",
#                             inline=True)
#             embed.set_footer(text=f"1")
#             await bot_channel.send(embed=embed)
#         else:
#             await bot.get_channel(main_channel).send(message)

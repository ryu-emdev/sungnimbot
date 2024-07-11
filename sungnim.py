from typing import Optional
import random
from random import randint
import discord
from discord import app_commands

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

        # CoinManager 인스턴스 생성
        self.coin_manager = CoinManager()

    async def on_ready(self):
        print(f'{self.user} (ID: {self.user.id}) 으로 로그인 되었습니다.')
        print('------')

        for server in self.guilds:
            try:
                self.tree.copy_global_to(guild=discord.Object(id=server.id))
                await self.tree.sync(guild=discord.Object(id=server.id))
                print(f'Synced commands for guild: {server.name} (ID: {server.id})')
            except Exception as e:
                print(f'Failed to sync commands for guild: {server.name} (ID: {server.id}). Error: {e}')

class CoinManager:
    def __init__(self):
        self.user_coins = {}

    def get_coins(self, user_id: int) -> int:
        return self.user_coins.get(user_id, 0)

    def add_coins(self, user_id: int, amount: int):
        current_coins = self.user_coins.get(user_id, 0)
        self.user_coins[user_id] = current_coins + amount

    def remove_coins(self, user_id: int, amount: int):
        current_coins = self.user_coins.get(user_id, 0)
        if current_coins >= amount:
            self.user_coins[user_id] = current_coins - amount
        else:
            raise ValueError("코인이 없다!")

    def gamble_coins(self, user_id: int, amount: int) -> int:
        # Define gambling probabilities
        outcome = random.randint(1, 100)

        if outcome <= 49:
            # Win 2x
            winnings = amount * 2
            self.add_coins(user_id, winnings)
            return winnings
        elif outcome == 50:
            # Win 10x
            winnings = amount * 10
            self.add_coins(user_id, winnings)
            return winnings
        else:
            # Lose
            self.remove_coins(user_id, amount)
            return -amount

intents = discord.Intents.default()
client = MyClient(intents=intents)

# 여기부터 응답 커맨드
@client.tree.command(name="안녕하십니까")
async def hello(interaction: discord.Interaction):
    """인사하기 - 봇 형님께 예의를 갖추자!"""
    await interaction.response.send_message(f'{interaction.user.mention} 오냐')

@client.tree.command(name="얼마있습니까")
async def check_balance(interaction: discord.Interaction):
    """잔액 보기 - 가지고있는 성님코인(SC)을 확인해보자!"""
    user_id = interaction.user.id
    coins = client.coin_manager.get_coins(user_id)
    await interaction.response.send_message(f'{interaction.user.mention} 너한테는 성님코인 {coins}SC정도가 있구만.')

@client.tree.command(name="한푼만주십쇼")
async def receive_coins(interaction: discord.Interaction):
    """구걸하기 - 봇 형님께 성님코인(SC)을 구걸해보자!"""
    user_id = interaction.user.id
    amount = randint(100, 300)
    client.coin_manager.add_coins(user_id, amount)
    await interaction.response.send_message(f'{interaction.user.mention} 옛다 {amount}SC.')

@client.tree.command(name="송금")
async def transfer_coins(interaction: discord.Interaction, target: Optional[discord.User] = None, amount: int = 0):
    """송금하기 - 다른 유저에게 성님코인(SC)을 보내보자!"""
    if target is None or amount <= 0:
        await interaction.response.send_message(f'{interaction.user.mention} 누구한테 줄 건데?')
        return
    
    sender_id = interaction.user.id
    receiver_id = target.id

    try:
        client.coin_manager.remove_coins(sender_id, amount)
        client.coin_manager.add_coins(receiver_id, amount)
        await interaction.response.send_message(f'{interaction.user.mention}: 옛다 받아라 {target.mention}! {amount}SC다.')
    except ValueError:
        await interaction.response.send_message(f'{interaction.user.mention} 없는 형편에 뭘 보낼건데?')

@client.tree.command(name="도박한판합시다")
async def gamble_coins(interaction: discord.Interaction, amount: int):
    """도박하기 - 성님코인(SC)으로 도박을 해보자!"""
    user_id = interaction.user.id

    if amount <= 0:
        await interaction.response.send_message(f'{interaction.user.mention} 올바른 금액을 걸어야지!')
        return

    try:
        result = client.coin_manager.gamble_coins(user_id, amount)

        if result > 0:
            await interaction.response.send_message(f'{interaction.user.mention} {result}SC를 따냈구만 축하해!!')
        elif result < 0:
            await interaction.response.send_message(f'{interaction.user.mention} {amount}SC를 잃었네 안타깝구만...')
        else:
            await interaction.response.send_message(f'{interaction.user.mention} 오류가 난것같아 일단 보류하겠어.')
    except ValueError:
        await interaction.response.send_message(f'{interaction.user.mention} 없는 형편에 도박질이냐?')

client.run('토큰 처넣기')

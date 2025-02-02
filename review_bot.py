import os
from enum import Enum
import re

import discord
from discord import app_commands
from discord.ext import commands

new_line = '\n'
MY_CHANNEL_ID = 1335550042643238962

def is_valid_summary(summary: str):
    return len(summary) >= 10 and len(summary) < 1000

def is_valid_mention(user_link):
    pattern = r'<@(\d+)>'
    return bool(re.fullmatch(pattern, user_link))

def is_valid_discord_link(message_link):
    pattern = r"^https://discord\.com/.+$"
    return bool(re.fullmatch(pattern, message_link))


class Review_Channel(Enum):
    film = ':movie_camera:'
    serial = ':tv:'
    gra = ':video_game:'
    muzyka = ':musical_keyboard:'
    książka = ':books:'
    komiks = ':closed_book:'
    anime_manga = ':mango:'
    inne = ':pencil:'


intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    print('Bot is ready!')
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} command(s)")
    except Exception as e:
        print('An error occurred while syncing commands:', e)


@bot.tree.command(name='save_review',
                  description='przenieś wybraną wiadomość na kanał #kącik-recenzenta')
@app_commands.describe(
    podsumowanie='podsumowanie czego dotyczy recenzja',
    użytkownik="nick użytkownika, który napisał recenzję",
    link='bezpośredni link do pierwszej wiadomości zaczynającej recenzję',
    źródło='z jakiego kanału pochodzi recenzja')
async def save_review(interaction: discord.Interaction, podsumowanie: str,
                      użytkownik: str, link: str, źródło: Review_Channel):
    # validation
    if not is_valid_mention(użytkownik):
        await interaction.response.send_message(
            'Nieprawidłowo oznaczony użytkownik. Aby oznaczyć użytkownika, zacznij wpisywanie od `@`.',
            ephemeral=True)
        return
    if not is_valid_discord_link(link):
        await interaction.response.send_message(
            'Nieprawidłowy link. Aby prawidłowo podlinkować wiadomość, wybierz z opcji `kopiuj link z wiadomością`.',
            ephemeral=True)
        return
    if not is_valid_summary(podsumowanie):
        await interaction.response.send_message(
            'Aby podsumowanie było czytelne i użyteczne, nie może być krótsze niż 10 znaków, ani dłuższe niż 1000.',
            ephemeral=True)
        return
    
    review_channel = await bot.fetch_channel(MY_CHANNEL_ID)
    await review_channel.send(
        f'{źródło.value} Recenzja użytkownika {użytkownik}{new_line}***__{podsumowanie}__***: {link}'
    )
    await interaction.response.send_message(
        f'Recenzja zapisana na kanale {review_channel.jump_url}',
        ephemeral=True)


try:
    token = os.getenv("TOKEN") or ""
    if token == "":
        raise Exception("Please add your token to the Secrets pane.")
    bot.run(token)
except discord.HTTPException as e:
    raise e

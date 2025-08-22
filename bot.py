import os
import sqlite3
import datetime
import discord
from discord.ext import commands

# ---- Intents ----
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)  # use "!حضور" etc.

# ---- Ensure DB exists ----
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/database.sqlite")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
""")
conn.commit()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        await bot.change_presence(activity=discord.Game(name="!حضور"))
    except Exception as e:
        print("Presence error:", e)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command(name="حضور")
async def attend(ctx):
    user_id = str(ctx.author.id)
    username = str(ctx.author)
    timestamp = datetime.datetime.utcnow().isoformat(timespec="seconds")
    cur.execute("INSERT INTO attendance (user_id, username, timestamp) VALUES (?, ?, ?)", (user_id, username, timestamp))
    conn.commit()
    await ctx.send(f"📌 تم تسجيل حضورك: {ctx.author.mention} — `{timestamp} UTC`")

@bot.command(name="الحضور")
async def list_attendance(ctx):
    cur.execute("SELECT username, timestamp FROM attendance ORDER BY id DESC LIMIT 20")
    rows = cur.fetchall()
    if not rows:
        await ctx.send("❌ لا يوجد حضور مسجل بعد.")
        return
    lines = [f"• **{u}** — `{t}`" for (u, t) in rows]
    await ctx.send("📋 آخر 20 حضور:\n" + "\n".join(lines))

# ---- Run ----
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise SystemExit("❌ Env var DISCORD_TOKEN is missing.")
bot.run(token)

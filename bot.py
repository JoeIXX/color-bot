import os
import threading
import time
import urllib.request
import discord
from discord import app_commands
from flask import Flask
import webcolors

# ----------------------------------------------------
# 1. 建立輕量網頁伺服器
# ----------------------------------------------------
app = Flask('')


@app.route('/')
def home():
  return "Color Bot is online!"


def run_web():
  app.run(host='0.0.0.0', port=8080)


# ----------------------------------------------------
# 2. 自我喚醒機制（防止 Render 休眠）
# ----------------------------------------------------
def self_ping():
  RENDER_URL = "https://dc-color-bot-id5t.onrender.com"

  while True:
    try:
      time.sleep(240)  # 每 4 分鐘 (240秒) 執行一次
      with urllib.request.urlopen(RENDER_URL) as response:
        print(f"Self-ping successful: {response.status}")
    except Exception as e:
      print(f"Self-ping failed: {e}")


# ----------------------------------------------------
# 3. 常見中文顏色資料庫
# ----------------------------------------------------
COLOR_MAP = {
    "紅色": ("red", "FF0000", 0xFF0000),
    "暗紅": ("darkred", "8B0000", 0x8B0000),
    "綠色": ("green", "008000", 0x008000),
    "萊姆綠": ("lime", "00FF00", 0x00FF00),
    "藍色": ("blue", "0000FF", 0x0000FF),
    "天藍色": ("skyblue", "87CEEB", 0x87CEEB),
    "海軍藍": ("navy", "000080", 0x000080),
    "黃色": ("yellow", "FFFF00", 0xFFFF00),
    "金色": ("gold", "FFD700", 0xFFD700),
    "粉紅色": ("pink", "FFC0CB", 0xFFC0CB),
    "桃紅色": ("deeppink", "FF1493", 0xFF1493),
    "紫色": ("purple", "800080", 0x800080),
    "橘色": ("orange", "FFA500", 0xFFA500),
    "咖啡色": ("brown", "A52A2A", 0xA52A2A),
    "黑色": ("black", "000000", 0x000000),
    "白色": ("white", "FFFFFF", 0xFFFFFF),
    "灰色": ("gray", "808080", 0x808080),
}


# ----------------------------------------------------
# 4. 機器人主體設定（隱身模式）
# ----------------------------------------------------
class ColorBot(discord.Client):

  def __init__(self):
    super().__init__(
        intents=discord.Intents.default(), status=discord.Status.invisible
    )
    self.tree = app_commands.CommandTree(self)

  async def setup_hook(self):
    await self.tree.sync()

  async def on_ready(self):
    await self.change_presence(status=discord.Status.invisible)
    print(f"Logged in as {self.user} (Invisible mode active)")


client = ColorBot()


# 支援中文名稱與任意色碼查詢的指令
@client.tree.command(name="color", description="輸入中文顏色或任意色碼查詢格式")
@app_commands.describe(
    名稱="請輸入中文名稱（如：紅色）或 6 位數色碼（如：FF5733、#FF5733）"
)
async def color(interaction: discord.Interaction, 名稱: str):
  query = 名稱.strip().replace("#", "")

  found_name = None
  found_data = None

  # 1. 先比對我們的中文資料庫
  for name, (eng, hex_val, dec) in COLOR_MAP.items():
    if query in name or query.lower() == eng.lower() or query.lower() == hex_val.lower():
      found_name = name
      found_data = (eng, hex_val, dec)
      break

  # 2. 如果資料庫沒有，直接檢查是不是合法的 6 位數色碼（例如使用者自己打的色碼）
  if not found_data:
    try:
      if len(query) == 6 and all(c in "0123456789abcdefABCDEF" for c in query):
        hex_val = query.upper()
        dec_color = int(hex_val, 16)
        found_name = f"自訂色碼 #{hex_val}"
        found_data = ("custom", hex_val, dec_color)
    except Exception:
      pass

  # 3. 如果還是找不到，嘗試透過 webcolors 檢查是不是英文色名（例如 coral, salmon 等）
  if not found_data:
    try:
      rgb = webcolors.name_to_rgb(query.lower())
      hex_val = f"{rgb.red:02X}{rgb.green:02X}{rgb.blue:02X}"
      dec_color = (rgb.red << 16) + (rgb.green << 8) + rgb.blue
      found_name = f"英文色名：{query.lower()}"
      found_data = (query.lower(), hex_val, dec_color)
    except Exception:
      pass

  # 4. 回傳查詢結果
  if found_data:
    _, hex_code, dec_color = found_data
    embed = discord.Embed(
        title=f"🎨 顏色查詢結果：{found_name}",
        description=(
            f"**Hex 碼：** `#{hex_code}`\n"
            f"**格式標籤：** `<color=#{hex_code}></color>`"
        ),
        color=dec_color,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
  else:
    await interaction.response.send_message(
        f"❌ 找不到你輸入的「{query}」。你可以輸入預設的中文顏色（如：紅色）、英文色名，或是直接輸入 6 位數色碼（例如 FF5733）！",
        ephemeral=True,
    )


# ----------------------------------------------------
# 5. 啟動入口
# ----------------------------------------------------
if __name__ == "__main__":
  # 1. 啟動網頁伺服器
  t_web = threading.Thread(target=run_web)
  t_web.daemon = True
  t_web.start()

  # 2. 啟動自我喚醒
  t_ping = threading.Thread(target=self_ping)
  t_ping.daemon = True
  t_ping.start()

  # 3. 啟動機器人
  TOKEN = os.getenv("DISCORD_TOKEN")
  client.run(TOKEN)
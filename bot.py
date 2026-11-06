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
# 2. 自我喚醒機制（已直接填入你的 Render 網址，防止休眠）
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
# 3. 顏色資料庫
# ----------------------------------------------------
COLOR_MAP = {
    "經典紅": ("red", "FF0000", 0xFF0000),
    "暗紅色": ("darkred", "8B0000", 0x8B0000),
    "鮮綠色": ("green", "008000", 0x008000),
    "萊姆綠": ("lime", "00FF00", 0x00FF00),
    "純藍色": ("blue", "0000FF", 0x0000FF),
    "天藍色": ("skyblue", "87CEEB", 0x87CEEB),
    "海軍藍": ("navy", "000080", 0x000080),
    "正黃色": ("yellow", "FFFF00", 0xFFFF00),
    "金色": ("gold", "FFD700", 0xFFD700),
    "粉紅色": ("pink", "FFC0CB", 0xFFC0CB),
    "熱情粉紅": ("deeppink", "FF1493", 0xFF1493),
    "紫色": ("purple", "800080", 0x800080),
    "蘭花紫": ("orchid", "DA70D6", 0xDA70D6),
    "橘色": ("orange", "FFA500", 0xFFA500),
    "暗橘色": ("darkorange", "FF8C00", 0xFF8C00),
    "咖啡色": ("brown", "A52A2A", 0xA52A2A),
    "巧克力色": ("chocolate", "D2691E", 0xD2691E),
    "黑色": ("black", "000000", 0x000000),
    "白色": ("white", "FFFFFF", 0xFFFFFF),
    "灰色": ("gray", "808080", 0x808080),
}


# ----------------------------------------------------
# 4. Discord UI 選單介面
# ----------------------------------------------------
class ColorSelectView(discord.ui.View):

  def __init__(self):
    super().__init__()

  @discord.ui.select(
      placeholder="請選擇一個顏色...",
      min_values=1,
      max_values=1,
      options=[
          discord.SelectOption(
              label=name, description=f"查詢 {name} 的 16 進位與標籤"
          )
          for name in COLOR_MAP.keys()
      ],
  )
  async def select_callback(
      self, interaction: discord.Interaction, select: discord.ui.Select
  ):
    selected_name = select.values[0]
    eng_name, hex_code, dec_color = COLOR_MAP[selected_name]

    embed = discord.Embed(
        title=f"🎨 顏色查詢結果：{selected_name}",
        description=(
            f"**Hex 碼：** `#{hex_code}`\n"
            f"**格式標籤：** `<color=#{hex_code}></color>`"
        ),
        color=dec_color,
    )
    await interaction.response.edit_message(embed=embed, view=None)


# ----------------------------------------------------
# 5. 機器人主體設定（設為隱身/離線狀態）
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


@client.tree.command(name="color", description="開啟色彩選單查詢 16 進位碼")
async def color_menu(interaction: discord.Interaction):
  view = ColorSelectView()
  embed = discord.Embed(
      title="🎨 色彩查詢選單",
      description="請點擊下方選單選擇你要查詢的顏色：",
      color=0x3498DB,
  )
  await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ----------------------------------------------------
# 6. 啟動入口
# ----------------------------------------------------
if __name__ == "__main__":
  # 1. 在背景啟動 Flask 網頁伺服器
  t_web = threading.Thread(target=run_web)
  t_web.daemon = True
  t_web.start()

  # 2. 在背景啟動自我喚醒執行緒
  t_ping = threading.Thread(target=self_ping)
  t_ping.daemon = True
  t_ping.start()

  # 3. 啟動 Discord 機器人
  TOKEN = os.getenv("DISCORD_TOKEN")
  client.run(TOKEN)
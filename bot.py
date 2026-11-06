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
# 3. 固定顏色資料庫
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
# 4. 下拉選單與按鈕介面 (View)
# ----------------------------------------------------
class ColorSelect(discord.ui.Select):

  def __init__(self):
    options = [
        discord.SelectOption(
            label=name, description=f"查詢 {name} 的 16 進位與標籤"
        )
        for name in COLOR_MAP.keys()
    ]
    super().__init__(
        placeholder="📌 點擊這裡選擇常用顏色...",
        min_values=1,
        max_values=1,
        options=options,
    )

  async def callback(self, interaction: discord.Interaction):
    selected_name = self.values[0]
    _, hex_code, dec_color = COLOR_MAP[selected_name]
    desc_text = (
        f"**Hex 碼：** `#{hex_code}`\n**格式標籤：**"
        f" `<color=#{hex_code}></color>`"
    )

    embed = discord.Embed(
        title=f"🎨 顏色查詢結果：{selected_name}",
        description=desc_text,
        color=dec_color,
    )
    await interaction.response.edit_message(embed=embed, view=self.view)


class CustomButton(discord.ui.Button):

  def __init__(self):
    super().__init__(
        label="✏️ 自訂輸入其他顏色/色碼",
        style=discord.ButtonStyle.secondary,
        row=1,
    )

  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(CustomColorModal())


class ColorQueryView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)
    self.add_item(ColorSelect())
    self.add_item(CustomButton())


# ----------------------------------------------------
# 5. 彈出式自訂輸入視窗 (Modal) - 支援強效中文比對與色碼查詢
# ----------------------------------------------------
class CustomColorModal(discord.ui.Modal, title="自訂顏色查詢"):
  color_input = discord.ui.TextInput(
      label="請輸入中文顏色名稱或 6 位數色碼",
      placeholder="例如：粉紅、FF5733 或 #00FFFF",
      required=True,
      max_length=20,
  )

  async def on_submit(self, interaction: discord.Interaction):
    query = self.color_input.value.strip()
    query_clean = query.replace("#", "")
    found_name = None
    found_data = None

    # 1. 強效中文模糊比對（支援打「粉紅」就能對應「粉紅色」）
    for name, (eng, hex_val, dec) in COLOR_MAP.items():
      if query in name or name in query:
        found_name = name
        found_data = (eng, hex_val, dec)
        break

    # 2. 如果中文沒對應到，比對英文或色碼
    if not found_data:
      for name, (eng, hex_val, dec) in COLOR_MAP.items():
        if (
            query_clean.lower() == eng.lower()
            or query_clean.lower() == hex_val.lower()
        ):
          found_name = name
          found_data = (eng, hex_val, dec)
          break

    # 3. 若不在資料庫，檢查是否為自訂 6 位數色碼
    if not found_data:
      try:
        if len(query_clean) == 6 and all(
            c in "0123456789abcdefABCDEF" for c in query_clean
        ):
          hex_val = query_clean.upper()
          dec_color = int(hex_val, 16)
          found_name = f"自訂色碼 #{hex_val}"
          found_data = ("custom", hex_val, dec_color)
      except Exception:
        pass

    # 4. 嘗試用 webcolors 解析英文名稱
    if not found_data:
      try:
        rgb = webcolors.name_to_rgb(query_clean.lower())
        hex_val = f"{rgb.red:02X}{rgb.green:02X}{rgb.blue:02X}"
        dec_color = (rgb.red << 16) + (rgb.green << 8) + rgb.blue
        found_name = f"英文色名：{query_clean.lower()}"
        found_data = (query_clean.lower(), hex_val, dec_color)
      except Exception:
        pass

    # 5. 回傳查詢結果
    if found_data:
      _, hex_code, dec_color = found_data
      desc_text = (
          f"**Hex 碼：** `#{hex_code}`\n**格式標籤：**"
          f" `<color=#{hex_code}></color>`"
      )
      embed = discord.Embed(
          title=f"🎨 顏色查詢結果：{found_name}",
          description=desc_text,
          color=dec_color,
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
      await interaction.response.send_message(
          f"❌ 找不到你輸入的顏色「{query}」，請確認名稱或輸入正確的 6 位數色碼！",
          ephemeral=True,
      )


# ----------------------------------------------------
# 6. 機器人主體設定（隱身模式）
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


@client.tree.command(
    name="color", description="開啟色彩查詢選單，或點擊按鈕自行輸入顏色"
)
async def color_menu(interaction: discord.Interaction):
  view = ColorQueryView()
  embed = discord.Embed(
      title="🎨 色彩查詢中心",
      description=(
          "請從下方**下拉選單**挑選常用顏色，\n"
          "或點擊 **「自訂輸入」** 按鈕來查詢中文顏色或自訂色碼！"
      ),
      color=0x3498DB,
  )
  await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ----------------------------------------------------
# 7. 啟動入口
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

  # 3. 機器人啟動
  TOKEN = os.getenv("DISCORD_TOKEN")
  client.run(TOKEN)
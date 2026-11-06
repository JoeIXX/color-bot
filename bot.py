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
    eng_name, hex_code, dec_color = COLOR_MAP[selected_name]

    embed = discord.Embed(
        title=f"🎨 顏色查詢結果：{selected_name}",
        description=(
            f"**Hex 碼：** `#{hex_code}`\n"
            f"**格式標籤：** `<color=#{hex_code}></color>`"
        ),
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
# 5. 彈出式自訂輸入視窗 (Modal)
# ----------------------------------------------------
class CustomColorModal(discord.ui.Modal, title="自訂顏色查詢"):
  color_input = discord.ui.TextInput(
      label="請輸入中文顏色名稱或 6 位數色碼",
      placeholder="例如：粉紅色、FF5733 或 #00FFFF",
      required=True,
      max_length=20,
  )

  async def on_submit(self, interaction: discord.Interaction):
    query = self.color_input.value.strip().replace("#", "")
    found_name = None
    found_data = None

    # 1. 先比對固定資料庫
    for name, (eng, hex_val, dec) in COLOR_MAP.items():
      if query in name or query.lower() == eng.lower() or query.lower
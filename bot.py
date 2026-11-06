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
# 3. 動態顏色資料庫（會隨新增顏色自動擴充）
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
# 4. 下拉選單與按鈕動態介面 (View)
# ----------------------------------------------------
class ColorQueryView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)
    self.update_select_options()

  # 根據目前 COLOR_MAP 動態刷新選單內容
  def update_select_options(self):
    self.clear_items()

    # Discord 下拉選單上限為 25 個選項
    options = [
        discord.SelectOption(
            label=name, description=f"查詢 {name} 的 16 進位與標籤"
        )
        for name in list(COLOR_MAP.keys())[:25]
    ]

    select = discord.ui.Select(
        placeholder="📌 點擊這裡選擇顏色...",
        min_values=1,
        max_values=1,
        options=options,
    )
    select.callback = self.select_callback
    self.add_item(select)

    # 重新加入自訂輸入按鈕
    button = discord.ui.Button(
        label="✏️ 自訂輸入其他顏色/色碼",
        style=discord.ButtonStyle.secondary,
        row=1,
    )
    button.callback = self.custom_button_callback
    self.add_item(button)

  async def select_callback(self, interaction: discord.Interaction):
    select = interaction.data["values"][0]
    selected_name = select
    eng_name, hex_code, dec_color = COLOR_MAP[selected_name]

    embed = discord.Embed(
        title=f"🎨 顏色查詢結果：{selected_name}",
        description=(
            f"**Hex 碼：** `#{hex_code}`\n"
            f"**格式標籤：** `<color=#{hex_code}></color>`"
        ),
        color=dec_color,
    )
    await interaction.response.edit_message(embed=embed, view=self)

  async def custom_button_callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(CustomColorModal(parent_view=self))


# ----------------------------------------------------
# 5. 彈出式自訂輸入視窗 (Modal)
# ----------------------------------------------------
class CustomColorModal(discord.ui.Modal, title="自訂顏色查詢"):

  def __init__(self, parent_view: ColorQueryView):
    super().__init__()
    self.parent_view = parent_view

  color_input = discord.ui.TextInput(
      label="請輸入中文顏色名稱或 6 位數色碼",
      placeholder="例如：馬卡龍綠、FF5733 或 #00FFFF",
      required=True,
      max_length=20,
  )

  async def on_submit(self, interaction: discord.Interaction):
    query = self.color_input.value.strip().replace("#", "")
    found_name = None
    found_data = None
    is_new = False

    # 1. 比對現有選單資料庫
    for name, (eng, hex_val, dec) in COLOR_MAP.items():
      if query in name or query.lower() == eng.lower() or query.lower() == hex_val.lower():
        found_name = name
        found_data = (eng, hex_val, dec)
        break

    # 2. 若不在資料庫，檢查是否為自訂 6 位數色碼
    if not found_data:
      try:
        if len(query) == 6 and all(c in "0123456789abcdefABCDEF" for c in query):
          hex_val = query.upper()
          dec_color = int(hex_val, 16)
          found_name = f"自訂色 #{hex_val}"
          found_data = ("custom", hex_val, dec_color)
          is_new = True
      except Exception:
        pass

    # 3. 嘗試用 webcolors 解析英文名稱
    if not found_data:
      try:
        rgb = webcolors.name_to_rgb(query.lower())
        hex_val = f"{rgb.red:02X}{rgb.green:02X}{rgb.blue:02X}"
        dec_color = (rgb.red << 16) + (rgb.green << 8) + rgb.blue
        found_name = query
        found_data = (query.lower(), hex_val, dec_color)
        is_new = True
      except Exception:
        pass

    # 4. 如果是新找到的顏色，自動把顏色加入 COLOR_MAP
    if found_data:
      if is_new or found_name not in COLOR_MAP:
        COLOR_MAP[found_name] = found_data
        # 自動刷新選單視窗，把新顏色加入選單中
        self.parent_view.update_select_options()

      _, hex_code, dec_color = found_data
      embed = discord.Embed(
          title=f"🎨 顏色查詢結果：{found_name}",
          description=(
              f"**Hex 碼：** `#{hex_code}`\n"
              f"**格式標籤：** `<color=#{hex_code}></color>`"
              f"{' *(已自動新增至下拉選單中！)*' if is_new else ''}"
          ),
          color=dec_color,
      )
      # 更新原訊息面板，顯示結果並同步最新的選單
      await interaction.response.edit_message(embed=embed, view=self.parent_view)
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
          "或點擊 **「自訂輸入」** 輸入新顏色（查到的新顏色會**自動加入選單**中喔！）。"
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

  # 3. 啟動機器人
  TOKEN = os.getenv("DISCORD_TOKEN")
  client.run(TOKEN)
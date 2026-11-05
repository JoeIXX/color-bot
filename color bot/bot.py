import discord
from discord import app_commands
import webcolors

# 顏色對照表：(英文代號, 16進位字串（無 0x）, 轉成十進位供 Discord 顯示顏色用)
COLOR_MAP = {
    # 紅色系
    "經典紅": ("red", "FF0000", 0xFF0000),
    "暗紅色": ("darkred", "8B0000", 0x8B0000),
    # 綠色系
    "鮮綠色": ("green", "008000", 0x008000),
    "萊姆綠": ("lime", "00FF00", 0x00FF00),
    # 藍色系
    "純藍色": ("blue", "0000FF", 0x0000FF),
    "天藍色": ("skyblue", "87CEEB", 0x87CEEB),
    "海軍藍": ("navy", "000080", 0x000080),
    # 黃色系
    "正黃色": ("yellow", "FFFF00", 0xFFFF00),
    "金色": ("gold", "FFD700", 0xFFD700),
    # 粉紅色系
    "粉紅色": ("pink", "FFC0CB", 0xFFC0CB),
    "熱情粉紅": ("deeppink", "FF1493", 0xFF1493),
    # 紫色系
    "紫色": ("purple", "800080", 0x800080),
    "蘭花紫": ("orchid", "DA70D6", 0xDA70D6),
    # 橘色系
    "橘色": ("orange", "FFA500", 0xFFA500),
    "暗橘色": ("darkorange", "FF8C00", 0xFF8C00),
    # 棕色系
    "咖啡色": ("brown", "A52A2A", 0xA52A2A),
    "巧克力色": ("chocolate", "D2691E", 0xD2691E),
    # 黑白灰系
    "黑色": ("black", "000000", 0x000000),
    "白色": ("white", "FFFFFF", 0xFFFFFF),
    "灰色": ("gray", "808080", 0x808080),
}


class ColorSelectView(discord.ui.View):

  def __init__(self):
    super().__init__()

  @discord.ui.select(
      placeholder="請點選或選擇一個顏色...",
      min_values=1,
      max_values=1,
      options=[
          discord.SelectOption(label=name, description=f"查詢 {name} 的 16 進位碼")
          for name in COLOR_MAP.keys()
      ],
  )
  async def select_callback(
      self, interaction: discord.Interaction, select: discord.ui.Select
  ):
    selected_name = select.values[0]
    eng_name, hex_code, dec_color = COLOR_MAP[selected_name]

    # 顯示 16 進位碼以及你要求的標籤格式
    embed = discord.Embed(
        title=f"你選擇了：{selected_name}",
        description=(
            f"16 進位碼 (Hex)：`#{hex_code}`\n格式標籤："
            f" `<color=#{hex_code}></color>`"
        ),
        color=dec_color,
    )

    await interaction.response.edit_message(embed=embed, view=None)


class ColorBot(discord.Client):

  def __init__(self):
    super().__init__(intents=discord.Intents.default())
    self.tree = app_commands.CommandTree(self)

  async def setup_hook(self):
    await self.tree.sync()


client = ColorBot()


@client.tree.command(name="color", description="點擊選單來挑選顏色並查詢 16 進位碼")
async def color_menu(interaction: discord.Interaction):
  view = ColorSelectView()
  embed = discord.Embed(
      title="🎨 色彩查詢選單",
      description="請從下方的下拉選單中選擇一個顏色：",
      color=0x3498DB,
  )
  await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ⚠️ 請把雙引號裡面的文字替換成你的機器人 Token
import os

# 從環境變數安全讀取 Token
TOKEN = os.getenv("DISCORD_TOKEN")
client.run(TOKEN)

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
# 3. 顏色資料庫設定
# ----------------------------------------------------
# 1) 下拉選單專用（清爽的 20 個常用色）
DROPDOWN_COLOR_MAP = {
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

# 2) 打字自訂搜尋專用（包含豐富的中文色彩對照）
SEARCH_COLOR_MAP = {
    **DROPDOWN_COLOR_MAP,
    "深灰色": ("darkgray", "404040", 0x404040),
    "昏灰": ("dimgray", "696969", 0x696969),
    "暗灰色": ("darkgray", "A9A9A9", 0xA9A9A9),
    "銀色": ("silver", "C0C0C0", 0xC0C0C0),
    "淺灰色": ("lightgray", "D3D3D3", 0xD3D3D3),
    "庚斯博羅灰": ("gainsboro", "DCDCDC", 0xDCDCDC),
    "白煙色": ("whitesmoke", "F5F5F5", 0xF5F5F5),
    "雪色": ("snow", "FFFAFA", 0xFFFAFA),
    "鐵灰色": ("irongray", "625B57", 0x625B57),
    "沙棕": ("sandbeige", "E6C3C3", 0xE6C3C3),
    "玫瑰褐": ("rosybrown", "BC8F8F", 0xBC8F8F),
    "淺珊瑚紅": ("lightcoral", "F08080", 0xF08080),
    "印度紅": ("indianred", "CD5C5C", 0xCD5C5C),
    "褐色": ("brown", "A52A2A", 0xA52A2A),
    "磚紅色": ("firebrick", "B22222", 0xB22222),
    "栗色": ("maroon", "800000", 0x800000),
    "暗紅": ("darkred", "8B0000", 0x8B0000),
    "鮮紅": ("strongred", "E60000", 0xE60000),
    "紅色": ("red", "FF0000", 0xFF0000),
    "柿子橙": ("persimmon", "FF4D40", 0xFF4D40),
    "霧玫瑰色": ("mistyrose", "FFE4E1", 0xFFE4E1),
    "鮭紅": ("salmon", "FA8072", 0xFA8072),
    "腥紅": ("scarlet", "FF2400", 0xFF2400),
    "蕃茄紅": ("tomato", "FF6347", 0xFF6347),
    "暗鮭紅": ("darksalmon", "E9967A", 0xE9967A),
    "珊瑚紅": ("coral", "FF7F50", 0xFF7F50),
    "橙色": ("orange", "FF6600", 0xFF6600),
    "橙紅": ("orangered", "FF4500", 0xFF4500),
    "淺鮭紅": ("lightsalmon", "FFA07A", 0xFFA07A),
    "朱紅": ("vermilion", "FF4D00", 0xFF4D00),
    "赭黃": ("sienna", "A0522D", 0xA0522D),
    "熱帶橙": ("tropicalorange", "FF8033", 0xFF8033),
    "駝色": ("camel", "A16B47", 0xA16B47),
    "杏黃": ("apricot", "E69966", 0xE69966),
    "椰褐": ("coconutbrown", "4D1F00", 0x4D1F00),
    "海貝色": ("seashell", "FFF5EE", 0xFFF5EE),
    "鞍褐": ("saddlebrown", "8B4513", 0x8B4513),
    "陽橙": ("sunorange", "FF7300", 0xFF7300),
    "沙褐": ("sandbrown", "F4A460", 0xF4A460),
    "銅色": ("bronze", "CD7F32", 0xCD7F32),
    "亞麻色": ("linen", "FAF0E6", 0xFAF0E6),
    "蜜橙": ("honeyorange", "FFB366", 0xFFB366),
    "烏賊墨色": ("sepia", "704214", 0x704214),
    "燃橙": ("burntorange", "CC5500", 0xCC5500),
    "赭色": ("ocher", "CC7722", 0xCC7722),
    "秘魯色": ("peru", "CD853F", 0xCD853F),
    "橘色": ("tangerine", "F28500", 0xF28500),
    "古董白": ("antiquewhite", "FAEBD7", 0xFAEBD7),
    "日曬色": ("tan", "D2B48C", 0xD2B48C),
    "硬木色": ("burlywood", "DEB887", 0xDEB887),
    "粉撲桃色": ("peachpuff", "FFDAB9", 0xFFDAB9),
    "那瓦霍白": ("navajowhite", "FFDEAD", 0xFFDEAD),
    "鹿皮鞋色": ("moccasin", "FFE4B5", 0xFFE4B5),
    "陶坯黃": ("bisque", "FFE4C4", 0xFFE4C4),
    "杏仁白": ("blanchedalmond", "FFEBCD", 0xFFEBCD),
    "蕃木瓜色": ("papayawhip", "FFEFD5", 0xFFEFD5),
    "玉米絲色": ("cornsilk", "FFF8DC", 0xFFF8DC),
    "萬壽菊黃": ("marigold", "FF9900", 0xFF9900),
    "灰土色": ("paleocre", "CCB38C", 0xCCB38C),
    "卡其色": ("khaki", "996B1F", 0x996B1F),
    "舊蕾絲色": ("oldlace", "FDF5E6", 0xFDF5E6),
    "小麥色": ("wheat", "F5DEB3", 0xF5DEB3),
    "桃色": ("peach", "FFE5B4", 0xFFE5B4),
    "花卉白": ("floralwhite", "FFFAF0", 0xFFFAF0),
    "金菊色": ("goldenrod", "DAA520", 0xDAA520),
    "暗金菊色": ("darkgoldenrod", "B8860B", 0xB8860B),
    "茉莉黃": ("jasmine", "E6C35C", 0xE6C35C),
    "琥珀色": ("amber", "FFBF00", 0xFFBF00),
    "鉻黃": ("chromeyellow", "E6B800", 0xE6B800),
    "淺卡其色": ("lightkhaki", "F0E68C", 0xF0E68C),
    "暗卡其色": ("darkkhaki", "BDB76B", 0xBDB76B),
    "含羞草黃": ("mimosa", "E6D933", 0xE6D933),
    "灰金菊色": ("palegoldenrod", "EEE8AA", 0xEEE8AA),
    "米色": ("beige", "F5F5DC", 0xF5F5DC),
    "淺金菊黃": ("lightgoldenrodyellow", "FAFAD2", 0xFAFAD2),
    "檸檬綢色": ("lemonchiffon", "FFFACD", 0xFFFACD),
    "奶油色": ("cream", "FFFDD0", 0xFFFFF0),
    "淺黃色": ("lightyellow", "FFFFE0", 0xFFFFE0),
    "象牙色": ("ivory", "FFFFF0", 0xFFFFF0),
    "香檳黃": ("champagneyellow", "FFFF99", 0xFFFF99),
    "芥末黃": ("mustard", "CCCC4D", 0xCCCC4D),
    "月黃": ("moonyellow", "FFFF4D", 0xFFFF4D),
    "橄欖色": ("olive", "808000", 0x808000),
    "鮮黃": ("canaryyellow", "FFEF00", 0xFFEF00),
    "苔蘚綠": ("mossgreen", "697723", 0x697723),
    "螢光黃": ("electriclime", "CCFF00", 0xCCFF00),
    "橄欖軍服綠": ("olivedrab", "6B8E23", 0x6B8E23),
    "黃綠": ("yellowgreen", "9ACD32", 0x9ACD32),
    "暗橄欖綠": ("darkolivegreen", "556B2F", 0x556B2F),
    "蘋果綠": ("applegreen", "8CE600", 0x8CE600),
    "綠黃": ("greenyellow", "ADFF2F", 0xADFF2F),
    "草綠": ("grassgreen", "99E64D", 0x99E64D),
    "草坪綠": ("lawngreen", "7CFC00", 0x7CFC00),
    "查特酒綠": ("chartreuse", "7FFF00", 0x7FFF00),
    "葉綠": ("foliagegreen", "73B839", 0x73B839),
    "嫩綠": ("freshleaves", "99FF4D", 0x99FF4D),
    "明亮綠": ("brightgreen", "66FF00", 0x66FF00),
    "鈷綠": ("cobaltgreen", "66FF59", 0x66FF59),
    "蜜瓜綠": ("honeydew", "F0FFF0", 0xF0FFF0),
    "暗海綠": ("darkseagreen", "8FBC8F", 0x8FBC8F),
    "淺綠色": ("lightgreen", "90EE90", 0x90EE90),
    "灰綠": ("palegreen", "98FB98", 0x98FB98),
    "常春藤綠": ("ivygreen", "36BF36", 0x36BF36),
    "森林綠": ("forestgreen", "228B22", 0x228B22),
    "檸檬綠": ("limegreen", "32CD32", 0x32CD32),
    "暗綠": ("darkgreen", "006600", 0x006600),
    "巴黎綠": ("parisiangreen", "50C878", 0x50C878),
    "孔雀石綠": ("malachite", "22C32E", 0x22C32E),
    "薄荷綠": ("mint", "16982B", 0x16982B),
    "青瓷綠": ("celadon", "ACE1AF", 0xACE1AF),
    "鉻綠": ("viridian", "127436", 0x127436),
    "蒼色": ("horizonblue", "B8DDC8", 0xB8DDC8),
    "海綠": ("seagreen", "2E8B57", 0x2E8B57),
    "中海綠": ("mediumseagreen", "3CB371", 0x3CB371),
    "綠松石綠": ("turquoisegreen", "4DE680", 0x4DE680),
    "祖母綠": ("emerald", "50C878", 0x50C878),
    "薄荷奶油色": ("mintcream", "F5FFFA", 0xF5FFFA),
    "春綠色": ("springgreen", "00FF80", 0x00FF80),
    "孔雀綠": ("peacockgreen", "00A15C", 0x00A15C),
    "中春綠色": ("mediumspringgreen", "00FA9A", 0x00FA9A),
    "中碧綠色": ("mediumaquamarine", "66CDAA", 0x66CDAA),
    "碧綠色": ("aquamarine", "7FFFD4", 0x7FFFD4),
    "青藍": ("cyanblue", "0DBF8C", 0x0DBF8C),
    "水藍": ("aquablue", "66FFE6", 0x66FFE6),
    "淺水藍": ("lightaquablue", "AFDFE4", 0xAFDFE4),
    "土耳其藍": ("turquoiseblue", "00FFEF", 0x00FFEF),
    "綠松石色": ("turquoise", "40E0D0", 0x40E0D0),
    "淺海綠色": ("lightseagreen", "20B2AA", 0x20B2AA),
    "中綠松石色": ("mediumturquoise", "48D1CC", 0x48D1CC),
    "淺藍": ("babyblue", "89CFF0", 0x89CFF0),
    "灰綠松石色": ("paleturquoise", "AFEEEE", 0xAFEEEE),
    "暗岩灰": ("darkslategray", "2F4F4F", 0x2F4F4F),
    "鴨綠色": ("teal", "008080", 0x008080),
    "暗青": ("darkcyan", "008B8B", 0x008B8B),
    "淺青色": ("lightcyan", "E0FFFF", 0xE0FFFF),
    "淺水色": ("lightaqua", "E0FFFF", 0xE0FFFF),
    "青色": ("cyan", "00FFFF", 0x00FFFF),
    "暗綠松石色": ("darkturquoise", "00CED1", 0x00CED1),
    "軍服藍": ("cadetblue", "5F9EA0", 0x5F9EA0),
    "孔雀藍": ("peacockblue", "00808C", 0x00808C),
    "濃藍": ("strongblue", "006374", 0x006374),
    "淺藍色": ("lightblue", "ADD8E6", 0xADD8E6),
    "粉藍": ("powderblue", "B0E0E6", 0xB0E0E6),
    "灰藍": ("paleblue", "D1EDF2", 0xD1EDF2),
    "愛麗絲藍": ("aliceblue", "F0F8FF", 0xF0F8FF),
    "薩克斯藍": ("saxeblue", "4798B3", 0x4798B3),
    "深天藍": ("deepskyblue", "00BFFF", 0x00BFFF),
    "水手藍": ("marineblue", "00477D", 0x00477D),
    "普魯士藍": ("prussianblue", "003153", 0x003153),
    "道奇藍": ("dodgerblue", "1E90FF", 0x1E90FF),
    "礦藍": ("mineralblue", "004D99", 0x004D99),
    "蔚藍色": ("cerulean", "007BA7", 0x007BA7),
    "韋奇伍德瓷藍": ("wedgwoodblue", "5686BF", 0x5686BF),
    "淺鋼藍色": ("lightlightblue", "B0C4DE", 0xB0C4DE),
    "灰丹寧布色": ("paledenim", "5E86C1", 0x5E86C1),
    "鼠尾草藍": ("salviablue", "4D80E6", 0x4D80E6),
    "暗粉藍": ("darkpowderblue", "003399", 0x003399),
    "鈷藍": ("cobaltblue", "0047AB", 0x0047AB),
    "藍寶石色": ("sapphire", "082567", 0x082567),
    "國際奇連藍": ("internationalkleinblue", "002FA7", 0x002FA7),
    "青天藍": ("ceruleanblue", "2A52BE", 0x2A52BE),
    "品藍": ("royalblue", "4169E1", 0x4169E1),
    "暗礦藍": ("darkmineralblue", "24367D", 0x24367D),
    "群青": ("ultramarine", "0033FF", 0x0033FF),
    "幽靈白": ("ghostwhite", "F8F8FF", 0xF8F8FF),
    "薰衣草霧": ("lavendermist", "E6E6FA", 0xE6E6FA),
    "薰衣草藍": ("lavenderblue", "CCCCFF", 0xCCCCFF),
    "長春花色": ("periwinkle", "C3CDE6", 0xC3CDE6),
    "藏青": ("navyblue", "000080", 0x000080),
    "暗藍": ("darkblue", "00008B", 0x00008B),
    "中藍": ("mediumblue", "0000CD", 0x0000CD),
    "午夜藍": ("midnightblue", "191970", 0x191970),
    "天青石藍": ("lapislazuli", "26619C", 0x26619C),
    "淺灰紫": ("grayishpurple", "8674A1", 0x8674A1),
    "鋼青色": ("steelblue", "4682B4", 0x4682B4),
    "暗岩藍": ("darkslateblue", "483D8B", 0x483D8B),
    "靛色": ("indigo", "4B0080", 0x4B0080),
    "岩藍": ("slateblue", "6A5ACD", 0x6A5ACD),
    "矢車菊藍": ("cornflowerblue", "6495ED", 0x6495ED),
    "中岩藍": ("mediumslateblue", "7B68EE", 0x7B68EE),
    "岩灰": ("slategray", "708090", 0x708090),
    "淺岩灰色": ("lightslategray", "778899", 0x778899),
    "堇紫色": ("violet", "8000FF", 0x8000FF),
    "藍紫": ("blueviolet", "8A2BE2", 0x8A2BE2),
    "暗洋紅": ("darkmagenta", "8B008B", 0x8B008B),
    "梅紅色": ("plum", "8E4585", 0x8E4585),
    "淺天藍": ("lightskyblue", "87CEFA", 0x87CEFA),
    "勃艮第酒紅": ("burgundy", "800020", 0x800020),
    "宗主教紫": ("patriarch", "800080", 0x800080),
    "中紫": ("mediumpurple", "9370DB", 0x9370DB),
    "暗紫": ("darkviolet", "9400D3", 0x9400D3),
    "暗蘭紫": ("darkorchid", "9933CC", 0x9933CC),
    "紫水晶色": ("amethyst", "9966CC", 0x9966CC),
    "中蘭紫": ("mediumorchid", "BA55D3", 0xBA55D3),
    "薰衣草紫": ("lavender", "B57EDC", 0xB57EDC),
    "三色堇紫": ("pansy", "7400A1", 0x7400A1),
    "錦葵紫": ("mallow", "D94DFF", 0xD94DFF),
    "優品紫紅": ("operamauve", "B784A7", 0xB784A7),
    "淡紫丁香色": ("paillilac", "E6CFE6", 0xE6CFE6),
    "礦紫": ("mineralviolet", "A39DAE", 0xA39DAE),
    "淺紫色": ("lightviolet", "B09DB9", 0xB09DB9),
    "紫丁香色": ("lilac", "C8A2C8", 0xC8A2C8),
    "紫藤色": ("wisteria", "C9A0DC", 0xC9A0DC),
    "薰衣草洋紅色": ("lavendermagenta", "EE82EE", 0xEE82EE),
    "纈草紫": ("heliotrope", "DF73FF", 0xDF73FF),
    "木槿紫": ("mauve", "E0B0FF", 0xE0B0FF),
    "薊紫": ("thistle", "D8BFD8", 0xD8BFD8),
    "鐵線蓮紫": ("clematis", "CCA3CC", 0xCCA3CC),
    "洋紅色": ("magenta", "FF00FF", 0xFF00FF),
    "品紅": ("fuchsia", "FF00FF", 0xFF00FF),
    "品紅色": ("fuchsia", "F400A1", 0xF400A1),
    "蘭紫色": ("orchid", "DA70D6", 0xDA70D6),
    "淺珍珠紅": ("pearlpink", "FFB3E6", 0xFFB3E6),
    "陳玫紅": ("oldrose", "C08081", 0xC08081),
    "淺玫瑰紅": ("rosepink", "FF66CC", 0xFF66CC),
    "中青紫紅": ("mediumvioletred", "C71585", 0xC71585),
    "洋玫瑰紅": ("magentarose", "FF0DA6", 0xFF0DA6),
    "玫瑰紅": ("rose", "FF007F", 0xFF007F),
    "紅寶石色": ("ruby", "CC0080", 0xCC0080),
    "山茶紅": ("camellia", "E63995", 0xE63995),
    "火鶴紅": ("flamingo", "E68AB8", 0xE68AB8),
    "淺珊瑚紅": ("coralpink", "FF80BF", 0xFF80BF),
    "暖粉紅": ("hotpink", "FF69B4", 0xFF69B4),
    "尖晶石紅": ("spinelred", "FF73B3", 0xFF73B3),
    "胭脂紅": ("carmine", "E6005C", 0xE6005C),
    "淺粉紅": ("babypink", "FFD9E6", 0xFFD9E6),
    "樞機紅": ("cardinalred", "C41E3A", 0xC41E3A),
    "薰衣草紫紅": ("lavenderblush", "FFF0F5", 0xFFF0F5),
    "灰紫紅": ("palevioletred", "DB7093", 0xDB7093),
    "櫻桃紅": ("cerise", "DE3163", 0xDE3163),
    "淺鮭紅": ("salmonpink", "FF8099", 0xFF8099),
    "緋紅": ("crimson", "DC143C", 0xDC143C),
    "殼黃紅": ("shellpink", "FFB3BF", 0xFFB3BF),
    "茜紅": ("alizarincrimson", "E32636", 0xE32636),
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
        for name in DROPDOWN_COLOR_MAP.keys()
    ]
    super().__init__(
        placeholder="📌 點擊這裡選擇常用顏色...",
        min_values=1,
        max_values=1,
        options=options,
    )

  async def callback(self, interaction: discord.Interaction):
    selected_name = self.values[0]
    _, hex_code, dec_color = DROPDOWN_COLOR_MAP[selected_name]
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
# 5. 彈出式自訂輸入視窗 (Modal)
# ----------------------------------------------------
class CustomColorModal(discord.ui.Modal, title="自訂顏色查詢"):
  color_input = discord.ui.TextInput(
      label="請輸入中文、英文顏色或 6 位數色碼",
      placeholder="例如：鹿皮鞋色、FF5733",
      required=True,
      max_length=20,
  )

  async def on_submit(self, interaction: discord.Interaction):
    query = self.color_input.value.strip()
    query_clean = query.replace("#", "")
    found_name = None
    found_data = None

    # 1. 中文模糊比對
    for name, (eng, hex_val, dec) in SEARCH_COLOR_MAP.items():
      if query in name or name in query:
        found_name = name
        found_data = (eng, hex_val, dec)
        break

    # 2. 英文名稱或色碼比對
    if not found_data:
      for name, (eng, hex_val, dec) in SEARCH_COLOR_MAP.items():
        if (
            query_clean.lower() == eng.lower()
            or query_clean.lower() == hex_val.lower()
        ):
          found_name = name
          found_data = (eng, hex_val, dec)
          break

    # 3. 自訂 6 位數 HEX 色碼解析
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

    # 4. webcolors 解析標準英文名稱
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
          f"❌ 找不到你輸入的顏色「{query}」，請確認名稱或直接輸入 6 位數色碼！",
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
          "或點擊 **「自訂輸入」** 按鈕來查詢任意中文顏色或自訂色碼！"
      ),
      color=0x3498DB,
  )
  await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ----------------------------------------------------
# 7. 啟動入口
# ----------------------------------------------------
if __name__ == "__main__":
  t_web = threading.Thread(target=run_web)
  t_web.daemon = True
  t_web.start()

  t_ping = threading.Thread(target=self_ping)
  t_ping.daemon = True
  t_ping.start()

  TOKEN = os.getenv("DISCORD_TOKEN")
  client.run(TOKEN)
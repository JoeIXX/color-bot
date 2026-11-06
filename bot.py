# ----------------------------------------------------
# 5. 彈出式自訂輸入視窗 (Modal) - 支援中文與色碼查詢
# ----------------------------------------------------
class CustomColorModal(discord.ui.Modal, title="自訂顏色查詢"):
  color_input = discord.ui.TextInput(
      label="請輸入中文顏色名稱或 6 位數色碼",
      placeholder="例如：粉紅色、FF5733 或 #00FFFF",
      required=True,
      max_length=20,
  )

  async def on_submit(self, interaction: discord.Interaction):
    query = self.color_input.value.strip()
    query_clean = query.replace("#", "")
    found_name = None
    found_data = None

    # 1. 優先比對中文名稱（支援直接打中文查詢）
    for name, (eng, hex_val, dec) in COLOR_MAP.items():
      if query == name or query in name:
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
          f"❌ 找不到你輸入的顏色「{query}」，請確認名稱或輸入正確的 6 位數色碼！",
          ephemeral=True,
      )
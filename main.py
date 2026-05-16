import discord
from discord.ext import commands
from discord import ui
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# --- ⚙️ ตั้งค่า ID ระบบแก๊ง (แก้ไขตรงนี้ให้ถูกต้อง) ---
GANG_LOG_CHANNEL_ID = 1499391381829845112  # ID ห้องที่ให้ใบสมัครส่งไป
GANG_ROLE_ID = 1505069800634974228         # ID ยศแก๊งที่จะแจกให้ทันทีเมื่อผ่านเงื่อนไข
PING_ROLE_ID = 1505084104545271839         # ID ยศที่จะแท็กเรียกคนมาตรวจ (เช่น หัวหน้าแก๊ง)
RULE_CHANNEL_ID = 1505068303758917784      # 📢 ใส่ ID ห้องกฎของเซิร์ฟเวอร์ตรงนี้เพื่อให้บอทแท็ก

# ลิงก์รูป GIF ตกแต่งของแก๊ง (เปลี่ยน URL ได้ตามต้องการ)
GANG_GIF = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2oza2pwdXFubW9kZ3R6N3gzdWptY2RxN3Y0bnd5Znd5ZXg0ZXg4ZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0IykG0AM7911MrCM/giphy.gif"

# --- ⚪ [Modals - ใบสมัครเข้าแก๊ง] ---
class GangModal(ui.Modal, title='⚔️ แบบฟอร์มสมัครเข้าแก๊ง'):
    name_ic_oc = ui.TextInput(label='1. ชื่อ IC / OC', placeholder='ตัวอย่าง: หมู / ต้นน้ำ')
    age_ic_oc = ui.TextInput(label='2. อายุ IC / OC', placeholder='ตัวอย่าง: 19 / 19')
    weapons = ui.TextInput(label='3. อาวุธที่มี (ถ้ามีโปรดระบุบวก)', placeholder='ตัวอย่าง: ไม้+1, มีด, มาเซ')
    reason = ui.TextInput(label='4. เหตุผลที่อยากเข้าแก๊ง', style=discord.TextStyle.paragraph, placeholder='ระบุเหตุผลของคุณ...')
    rule_check = ui.TextInput(label='5. อ่านกฎหรือยัง? (พิมคำว่า อ่านแล้ว)', placeholder='ต้องพิมพ์คำว่า "อ่านแล้ว" ถึงจะได้รับยศ')

    async def on_submit(self, i: discord.Interaction):
        # ป้องกันบอท Timeout (Unknown Interaction)
        await i.response.defer(ephemeral=True)
        
        log_channel = i.client.get_channel(GANG_LOG_CHANNEL_ID)
        if not log_channel:
            return await i.followup.send("❌ ไม่พบห้องส่งข้อมูลใบสมัคร กรุณาตรวจสอบ ID ห้อง", ephemeral=True)

        # แปลงข้อความที่ผู้ใช้พิมพ์เป็นพิมพ์เล็กและตัดช่องว่างออก
        user_answer = self.rule_check.value.strip().replace(" ", "")
        
        # เงื่อนไขการรับยศอัตโนมัติ (มีคำว่า "อ่านแล้ว")
        has_read_rules = "อ่านแล้ว" in user_answer
        
        if has_read_rules:
            role_status = "❌ ไม่ได้รับยศอัตโนมัติ (ระบบผิดพลาด)"
            gang_role = i.guild.get_role(GANG_ROLE_ID)
            if gang_role:
                try:
                    await i.user.add_roles(gang_role)
                    role_status = f"✅ ได้รับยศ {gang_role.mention} เรียบร้อยแล้วอัตโนมัติ!"
                except discord.Forbidden:
                    role_status = "⚠️ พิมพ์ถูกแต่บอทไม่มีอำนาจให้ยศ (ยศบอทต้องอยู่สูงกว่ายศที่จะแจก)"
            else:
                role_status = "⚠️ พิมพ์ถูกแต่หาตำแหน่งยศในเซิร์ฟเวอร์ไม่เจอ ตรวจสอบ ID ยศ"
            
            # ข้อความตอบกลับหาคนสมัคร (กรณีพิมพ์ผ่าน)
            reply_msg = f"✅ ส่งใบสมัครเข้าแก๊งสำเร็จ!\n{role_status}"
        else:
            role_status = "❌ ไม่ได้รับยศอัตโนมัติ (พิมพ์คำยืนยันกฎไม่ถูกต้อง)"
            
            # ข้อความตอบกลับหาคนสมัครพร้อมแท็กห้องกฎ (กรณีพิมพ์ไม่ผ่าน)
            reply_msg = f"❌ ส่งใบสมัครสำเร็จ แต่คุณยังไม่ได้รับยศอัตโนมัติเนื่องจากไม่อ่านกฎแก๊ง กรุณาไปอ่านกฎที่ห้องนี้ก่อนครับ ➡️ <#{RULE_CHANNEL_ID}>"

        # จัดฟอร์ม Embed ส่งเข้าห้อง Log แก๊ง
        emb = discord.Embed(title="🔥 มีใบสมัครเข้าแก๊งใหม่เข้ามา! 🔥", color=0xFF0000, timestamp=datetime.now())
        emb.set_thumbnail(url=i.user.display_avatar.url)
        emb.set_image(url=GANG_GIF)
        
        emb.add_field(name="👤 ผู้สมัคร", value=f"{i.user.mention} (ID: {i.user.id})", inline=False)
        emb.add_field(name="📝 ชื่อ IC / OC", value=self.name_ic_oc.value, inline=True)
        emb.add_field(name="🎂 อายุ IC / OC", value=self.age_ic_oc.value, inline=True)
        emb.add_field(name="⚔️ อาวุธที่มีทั้งหมด", value=self.weapons.value, inline=False)
        emb.add_field(name="💡 เหตุผลที่อยากเข้า", value=f"```{self.reason.value}```", inline=False)
        emb.add_field(name="📜 การยืนยันกฎ", value=f"ผู้สมัครพิมพ์ว่า: `{self.rule_check.value}`", inline=True)
        emb.add_field(name="👑 สถานะยศปัจจุบัน", value=role_status, inline=False)

        try:
            # ส่งข้อมูลไปห้องแก๊งพร้อมแท็กหัวหน้าแก๊งมาตรวจ
            await log_channel.send(content=f"<@&{PING_ROLE_ID}> มีคนมาสมัครเข้าแก๊งครับ!", embed=emb)
            
            # ตอบกลับผู้สมัครแบบเห็นคนเดียว
            await i.followup.send(content=reply_msg, ephemeral=True)
            
        except Exception as e:
            await i.followup.send(f"❌ เกิดข้อผิดพลาดในการส่งข้อมูล: {e}", ephemeral=True)

# --- 🔵 [Views - ปุ่มกดสมัคร] ---
class GangView(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="สมัครเข้าแก๊ง ⚔️", style=discord.ButtonStyle.danger, custom_id="persistent_gang_btn")
    async def callback(self, i: discord.Interaction, b): 
        await i.response.send_modal(GangModal())

# --- 🤖 [Bot Core] ---
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # จำเป็นมากสำหรับการแจกยศ
        super().__init__(command_prefix='!', intents=intents, help_command=None)
    
    async def setup_hook(self):
        self.add_view(GangView())

bot = MyBot()

@bot.event
async def on_ready():
    print(f'✅ บอทระบบแก๊งออนไลน์แล้ว: {bot.user}')

@bot.command()
@commands.has_permissions(administrator=True)
async def สร้างปุ่มแก๊ง(ctx):
    emb = discord.Embed(
        title="⚔️ **เปิดรับสมัครสมาชิกเข้าแก๊ง** ⚔️", 
        description="หากคุณพร้อมที่จะร่วมเดินทางไปกับเรา กดปุ่มด้านล่างเพื่อกรอกใบสมัครได้เลย!\n\n*โปรดระบุข้อมูลตามความจริง และอ่านกฎแก๊งให้ครบถ้วน*", 
        color=0x2f3136
    )
    emb.set_image(url=GANG_GIF)
    await ctx.send(embed=emb, view=GangView())

bot.run(TOKEN)

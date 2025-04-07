import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import json
from datetime import datetime

class GuessGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}  # 用於存儲每個伺服器的猜數字遊戲狀態
        self.scores_file = "data/scores.json"  # 用於存儲玩家猜對次數的檔案
        self.scores = self.load_scores()  # 載入玩家猜對次數

    def get_game(self, guild_id, setter_id):
        """取得伺服器中由特定主持人開啟的猜數字遊戲狀態"""
        game_id = f"{guild_id}_{setter_id}"  # 使用伺服器 ID 和主持人 ID 作為唯一識別符號
        if game_id not in self.games:
            self.games[game_id] = {
                "answer": None,
                "setter": setter_id,
                "guessed_players": [],
                "first_guess": True  # 記錄是否為第一次猜測
            }
        return self.games[game_id]

    def load_scores(self):
        """載入玩家猜對次數"""
        try:
            with open(self.scores_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_scores(self):
        """儲存玩家猜對次數"""
        with open(self.scores_file, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=4)

    def update_score(self, user_id, username, increment_guesses=0):
        """更新玩家的猜對次數和總猜測次數"""
        user_id = str(user_id)
        if user_id not in self.scores:
            self.scores[user_id] = {"username": username, "score": 0, "total_guesses": 0}
        self.scores[user_id]["score"] += 1  # 增加猜對次數
        self.scores[user_id]["total_guesses"] += increment_guesses  # 增加總猜測次數
        self.save_scores()

    @app_commands.command(name="start_guess", description="開始猜")
    async def guess(self, interaction: discord.Interaction):
        """主持人使用表單設定答案"""
        guild_id = interaction.guild.id
        game = self.get_game(guild_id, interaction.user.id)

        class SetAnswerModal(Modal, title="設定答案"):
            answer = TextInput(label="請輸入答案", placeholder="例如：42", required=True)

            def __init__(self, game, setter_id, scores, update_score_func):
                super().__init__()
                self.game = game
                self.setter_id = setter_id
                self.scores = scores
                self.update_score = update_score_func

            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    answer = int(self.answer.value)  # 將輸入轉換為整數
                    self.game["answer"] = answer
                    self.game["setter"] = self.setter_id

                    # 發送確認訊息給主持人
                    await modal_interaction.response.send_message(f"✅ 答案已設定（只有你知道答案）。", ephemeral=True)

                    # 開始猜數字遊戲，發送按鈕給所有玩家
                    class GuessButtonView(View):
                        def __init__(self, game, scores, update_score_func, timeout=3600):  # 設定 Timeout 為 1 小時
                            super().__init__(timeout=timeout)
                            self.game = game
                            self.scores = scores
                            self.update_score = update_score_func

                        async def on_timeout(self):
                            """當按鈕超時時執行的邏輯"""
                            for child in self.children:
                                child.disabled = True  # 禁用所有按鈕
                            # 發送訊息通知玩家按鈕已失效
                            channel = self.game.get("channel")
                            if channel:
                                await channel.send("⏳ 時間已到，按鈕已失效！")

                        @discord.ui.button(label="猜", style=discord.ButtonStyle.primary, custom_id="guess_button")
                        async def guess_button(self, button_interaction: discord.Interaction, button: Button):
                            """玩家點擊按鈕後彈出表單"""
                            # 檢查玩家是否是主持人
                            if button_interaction.user.id == self.game["setter"]:
                                await button_interaction.response.send_message("⚠ 主持人無法參與猜測！", ephemeral=True)
                                return

                            # 檢查玩家是否已經猜對過
                            if button_interaction.user.id in self.game["guessed_players"]:
                                await button_interaction.response.send_message("⚠ 你已經猜對過了，無法再次參與！", ephemeral=True)
                                return

                            class GuessModal(Modal, title="猜數字"):
                                def __init__(self, game, update_score):
                                    super().__init__()
                                    self.game = game
                                    self.update_score = update_score

                                guess = TextInput(label="請輸入你的猜測", placeholder="例如：50", required=True)

                                async def on_submit(self, modal_interaction: discord.Interaction):
                                    try:
                                        guess = float(self.guess.value)  # 將玩家的猜測轉換為數字
                                        answer = self.game["answer"]

                                        # 初始化玩家的猜測次數
                                        if "guess_counts" not in self.game:
                                            self.game["guess_counts"] = {}
                                        if modal_interaction.user.id not in self.game["guess_counts"]:
                                            self.game["guess_counts"][modal_interaction.user.id] = 0

                                        # 增加玩家的猜測次數
                                        self.game["guess_counts"][modal_interaction.user.id] += 1
                                        guess_count = self.game["guess_counts"][modal_interaction.user.id]

                                        # 計算答案的 ±5% 範圍
                                        tolerance = answer * 0.05
                                        lower_bound = answer - tolerance
                                        upper_bound = answer + tolerance

                                        # 判斷猜測結果
                                        if guess == answer:
                                            # 更新玩家的猜對次數和總猜測次數
                                            self.update_score(modal_interaction.user.id, modal_interaction.user.name, increment_guesses=guess_count)
                                            # 將玩家加入已猜對列表
                                            self.game["guessed_players"].append(modal_interaction.user.id)
                                            # 公開顯示猜對訊息，包含猜測次數
                                            await modal_interaction.response.send_message(
                                                f"🎉 {modal_interaction.user.mention} 猜對了！你總共猜了 {guess_count} 次。"
                                            )
                                        elif lower_bound <= guess <= upper_bound:
                                            # 僅對玩家自己顯示接近提示
                                            await modal_interaction.response.send_message(f"🤏 接近了！你已經猜了 {guess_count} 次。", ephemeral=True)
                                        else:
                                            # 僅對玩家自己顯示更高或更低的提示
                                            if guess < answer:
                                                await modal_interaction.response.send_message(f"❌ 錯得離譜！提示：更盤！你已經猜了 {guess_count} 次。", ephemeral=True)
                                            elif guess > answer:
                                                await modal_interaction.response.send_message(f"❌ 錯得離譜！提示：更賺！你已經猜了 {guess_count} 次。", ephemeral=True)
                                    except ValueError:
                                        # 回應錯誤訊息，確保互動完成
                                        await modal_interaction.response.send_message("⚠ 請輸入有效的數字！", ephemeral=True)
                                    except Exception as e:
                                        # 回應錯誤訊息，確保互動完成
                                        await modal_interaction.response.send_message(f"⚠ 發生錯誤：{e}", ephemeral=True)

                            # 傳遞 game 和 update_score 給 GuessModal
                            await button_interaction.response.send_modal(GuessModal(self.game, self.update_score))

                        @discord.ui.button(label="公佈解答", style=discord.ButtonStyle.danger, custom_id="reveal_button")
                        async def reveal_button(self, button_interaction: discord.Interaction, button: Button):
                            """主持人點擊按鈕公佈答案"""
                            guild_id = button_interaction.guild.id
                            game = self.game

                            # 檢查是否是主持人
                            if game["setter"] != button_interaction.user.id:
                                await button_interaction.response.send_message("⚠ 只有主持人可以公佈答案！", ephemeral=True)
                                return

                            if game["answer"] is None:
                                await button_interaction.response.send_message("⚠ 尚未設定答案！", ephemeral=True)
                                return

                            # 公佈答案
                            await button_interaction.response.send_message(f"📢 答案是：{game['answer']}！")
                            # 重置遊戲
                            game["answer"] = None
                            game["setter"] = None
                            game["first_guess"] = True  # 重置第一次猜測狀態

                        @discord.ui.button(label="排行榜", style=discord.ButtonStyle.success, custom_id="leaderboard_button")
                        async def leaderboard_button(self, button_interaction: discord.Interaction, button: Button):
                            """顯示排行榜"""
                            sorted_scores = sorted(self.scores.items(), key=lambda x: x[1]["score"], reverse=True)
                            embed = discord.Embed(title="排行榜", color=discord.Color.blue())
                            for i, (user_id, data) in enumerate(sorted_scores[:10], start=1):
                                embed.add_field(
                                    name=f"{i}. {data['username']}",
                                    value=f"猜對次數：{data['score']} 次\n總猜測次數：{data['total_guesses']} 次",
                                    inline=False
                                )
                            embed.set_footer(text=f"更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            await button_interaction.response.send_message(embed=embed)

                    # 發送按鈕訊息到頻道
                    await modal_interaction.channel.send("點擊按鈕猜！", view=GuessButtonView(self.game, self.scores, self.update_score))

                except ValueError:
                    if not modal_interaction.response.is_done():
                        await modal_interaction.response.send_message("⚠ 請輸入有效的數字！", ephemeral=True)
                except Exception as e:
                    if not modal_interaction.response.is_done():
                        await modal_interaction.response.send_message(f"⚠ 發生錯誤：{e}", ephemeral=True)

        await interaction.response.send_modal(SetAnswerModal(game, interaction.user.id, self.scores, self.update_score))

async def setup(bot: commands.Bot):
    await bot.add_cog(GuessGame(bot))
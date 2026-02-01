import tkinter as tk
from tkinter import messagebox
import random
import math
import webbrowser  # URLを開くために必要
import sys         # アプリを終了するために必要

# ▼ここに飛ばしたいYouTubeのURLを入力してください▼
YOUTUBE_URL = "https://youtu.be/cM7uKegVG-E?si=wueKrQjqanQRSZvI" 
# ▲▲▲

class RouletteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Roulette App")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        # カラーパレット
        self.colors = ["#FF9999", "#66B2FF", "#99FF99", "#FFCC99", "#FF99CC", "#FFFF99"]

        # 通常ルーレット用変数
        self.items = []
        self.current_angle = 0
        self.spin_speed = 0
        self.is_spinning = False
        self.friction = 0.985

        # トラップ用変数
        self.trap_window = None
        self.forced_canvas = None
        self.forced_items = [("死亡", 80), ("逃げる", 20)]
        self.forced_angle = 0
        self.forced_speed = 0
        self.is_forced_spinning = False

        self._setup_ui()

    def _setup_ui(self):
        """通常画面のUIセットアップ"""
        left_frame = tk.Frame(self.root, width=300, bg="#f0f0f0", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="項目設定", font=("Meiryo", 12, "bold"), bg="#f0f0f0").pack(pady=5)
        
        self.entry_widgets = []
        header_frame = tk.Frame(left_frame, bg="#f0f0f0")
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="項目名", width=15, bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Label(header_frame, text="確率(%)", width=8, bg="#f0f0f0").pack(side=tk.LEFT)

        for i in range(10):
            row = tk.Frame(left_frame, bg="#f0f0f0")
            row.pack(fill=tk.X, pady=2)
            name_ent = tk.Entry(row, width=15)
            name_ent.pack(side=tk.LEFT, padx=2)
            name_ent.insert(0, f"項目{i+1}")
            prob_ent = tk.Entry(row, width=8)
            prob_ent.pack(side=tk.LEFT, padx=2)
            self.entry_widgets.append((name_ent, prob_ent))

        self.btn_start = tk.Button(left_frame, text="スタート！", command=self.start_spin, 
                                   bg="#FF5722", fg="white", font=("Meiryo", 14, "bold"), height=2)
        self.btn_start.pack(fill=tk.X, pady=20)

        self.lbl_result = tk.Label(left_frame, text="---", font=("Meiryo", 16, "bold"), bg="#f0f0f0", fg="#333")
        self.lbl_result.pack(pady=10)

        right_frame = tk.Frame(self.root, bg="white")
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.canvas = tk.Canvas(right_frame, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.bind("<Configure>", self.draw_roulette)

    def calculate_probabilities(self):
        """確率計算ロジック（変更なし）"""
        active_items = []
        for name_ent, prob_ent in self.entry_widgets:
            name = name_ent.get().strip()
            prob_str = prob_ent.get().strip()
            if not name: continue
            prob = None
            if prob_str:
                try:
                    prob = float(prob_str)
                except ValueError:
                    messagebox.showerror("エラー", f"「{name}」の確率は数値で入力してください。")
                    return None
            active_items.append({"name": name, "prob": prob})

        if not active_items:
            messagebox.showwarning("警告", "項目を少なくとも1つ入力してください。")
            return None
        
        # ▼▼▼ トラップチェック ▼▼▼
        # 項目名に「こはく」が含まれているかチェック
        for item in active_items:
            if "こはく" in item["name"]:
                self.activate_trap()
                return "TRAP_ACTIVATED" # 特殊な値を返す
        # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲

        specified_total = sum(item["prob"] for item in active_items if item["prob"] is not None)
        if specified_total > 100:
            messagebox.showerror("エラー", f"確率の合計が100%を超えています (現在: {specified_total}%)")
            return None

        count_unspecified = sum(1 for item in active_items if item["prob"] is None)
        remaining_prob = 100 - specified_total
        final_items = []
        for item in active_items:
            p = item["prob"]
            if p is None:
                p = remaining_prob / count_unspecified if count_unspecified > 0 else 0
            if p > 0:
                final_items.append((item["name"], p))
        return final_items

    # --- 通常ルーレットの描画とアニメーション ---
    def draw_roulette(self, event=None):
        """通常ルーレットの描画"""
        if not self.items or self.is_forced_spinning: return
        self._draw_wheel_on_canvas(self.canvas, self.items, self.current_angle)

    def start_spin(self):
        """回転開始処理"""
        if self.is_spinning: return
        
        result = self.calculate_probabilities()
        if result == "TRAP_ACTIVATED": return # トラップ発動時はここで終了
        if not result: return
        
        self.items = result
        self.lbl_result.config(text="回転中...", fg="#FF5722")
        self.spin_speed = random.uniform(20, 30) 
        self.is_spinning = True
        self.btn_start.config(state=tk.DISABLED)
        self.animate()

    def animate(self):
        """通常アニメーションループ"""
        if not self.is_spinning: return
        self.current_angle = (self.current_angle + self.spin_speed) % 360
        self.draw_roulette()
        self.spin_speed *= self.friction
        if self.spin_speed < 0.1:
            self.is_spinning = False
            self.spin_speed = 0
            self.show_result()
            self.btn_start.config(state=tk.NORMAL)
        else:
            self.root.after(16, self.animate)

    def show_result(self):
        """通常結果表示"""
        winner_name = self._get_winner(self.items, self.current_angle)
        self.lbl_result.config(text=f"結果: {winner_name}", fg="red")
        messagebox.showinfo("結果発表", f"選ばれたのは...\n\n【 {winner_name} 】です！")

    # --- 共通描画ヘルパー ---
    def _draw_wheel_on_canvas(self, canvas_obj, items_data, angle_offset):
        """指定されたキャンバスにルーレットを描画する共通関数"""
        canvas_obj.delete("all")
        w = canvas_obj.winfo_width()
        h = canvas_obj.winfo_height()
        center_x, center_y = w / 2, h / 2
        radius = min(w, h) / 2 - 40

        start_deg = angle_offset
        for i, (name, prob) in enumerate(items_data):
            extent = (prob / 100) * 360
            # トラップ時は色を固定
            if self.is_forced_spinning:
                color = "#FF0000" if name == "死亡" else "#00FF00"
            else:
                color = self.colors[i % len(self.colors)]
            
            canvas_obj.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_deg, extent=extent,
                fill=color, outline="white", width=2
            )
            # テキスト描画
            mid_angle_rad = math.radians(start_deg + extent / 2)
            text_r = radius * 0.6
            text_x = center_x + text_r * math.cos(mid_angle_rad)
            text_y = center_y - text_r * math.sin(mid_angle_rad)
            canvas_obj.create_text(text_x, text_y, text=name, font=("Meiryo", 14, "bold"), fill="white" if self.is_forced_spinning else "black")
            start_deg += extent

        # 針の描画
        canvas_obj.create_polygon(
            center_x + radius + 10, center_y,
            center_x + radius + 40, center_y - 15,
            center_x + radius + 40, center_y + 15,
            fill="black", outline="red", width=2
        )

    def _get_winner(self, items_data, angle_offset):
        """角度から当選項目を判定する共通関数"""
        target_angle = (360 - angle_offset) % 360
        current_check = 0
        for name, prob in items_data:
            extent = (prob / 100) * 360
            if current_check <= target_angle < current_check + extent:
                return name
            current_check += extent
        return items_data[-1][0] # フォールバック

    # ==========================================
    # ▼▼▼ ここからトラップ用ロジック ▼▼▼
    # ==========================================
    def activate_trap(self):
        """トラップ発動！メイン画面を隠してBAN画面を表示"""
        self.root.withdraw() # メインウィンドウを隠す
        
        trap_win = tk.Toplevel(self.root)
        trap_win.title("警告")
        trap_win.geometry("600x600")
        trap_win.configure(bg="black")
        trap_win.resizable(False, False)
        # ウィンドウを閉じるボタンを無効化
        trap_win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.trap_window = trap_win

        # BANメッセージ
        tk.Label(trap_win, text="あなたは永久BANです", font=("Meiryo", 24, "bold"), 
                 bg="black", fg="red", pady=20).pack()
        
        tk.Label(trap_win, text="最後の審判が始まります...", font=("Meiryo", 14), 
                 bg="black", fg="white").pack()

        # 強制ルーレット用キャンバス
        self.forced_canvas = tk.Canvas(trap_win, bg="black", highlightthickness=0)
        self.forced_canvas.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # キャンバスのサイズが決まったら描画して回転開始
        self.forced_canvas.bind("<Configure>", self._start_forced_sequence)

    def _start_forced_sequence(self, event=None):
        """強制ルーレットの準備と開始"""
        # バインドを解除（一度だけ実行するため）
        self.forced_canvas.unbind("<Configure>")
        self.draw_forced_roulette()
        # 2秒後に回転開始
        self.root.after(2000, self.start_forced_spin)

    def draw_forced_roulette(self):
        """強制ルーレットの描画"""
        if not self.forced_canvas: return
        self._draw_wheel_on_canvas(self.forced_canvas, self.forced_items, self.forced_angle)

    def start_forced_spin(self):
        """強制回転開始"""
        self.is_forced_spinning = True
        # 初速を少し早めに設定
        self.forced_speed = random.uniform(30, 45)
        self.animate_forced()

    def animate_forced(self):
        """強制アニメーションループ"""
        if not self.is_forced_spinning: return

        self.forced_angle = (self.forced_angle + self.forced_speed) % 360
        self.draw_forced_roulette()

        # 摩擦係数を少し強めにして短時間で止める
        self.forced_speed *= 0.98 

        if self.forced_speed < 0.1:
            self.is_forced_spinning = False
            self.forced_speed = 0
            # 少し待ってから結果発表
            self.root.after(1000, self.show_forced_result)
        else:
            self.root.after(16, self.animate_forced)

    def show_forced_result(self):
        """強制結果判定とアクション実行"""
        winner = self._get_winner(self.forced_items, self.forced_angle)
        
        result_label = tk.Label(self.trap_window, text=f"結果: 【 {winner} 】", 
                                font=("Meiryo", 20, "bold"), bg="black", fg="white")
        result_label.pack(pady=10)

        # 結果に応じたアクション（少し待ってから実行）
        if winner == "逃げる":
            result_label.config(fg="green")
            self.root.after(2000, self._force_exit_app)
        else:
            result_label.config(fg="red")
            self.root.after(2000, self._execute_death_penalty)

    def _force_exit_app(self):
        """アプリ強制終了"""
        messagebox.showinfo("運命", "今回は見逃してやろう...", parent=self.trap_window)
        self.root.destroy()
        sys.exit()

    def _execute_death_penalty(self):
        """死亡ペナルティ執行（YouTubeを開いて終了）"""
        messagebox.showerror("運命", "さようなら...", parent=self.trap_window)
        webbrowser.open(YOUTUBE_URL)
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = RouletteApp(root)
    root.mainloop()
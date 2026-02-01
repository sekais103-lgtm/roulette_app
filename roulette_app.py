import streamlit as st
import pandas as pd
import random
import time

# ▼ここに飛ばしたいYouTubeのURL（埋め込み用ID）▼
# 例: https://www.youtube.com/watch?v=dQw4w9WgXcQ なら "dQw4w9WgXcQ"
YOUTUBE_VIDEO_ID = "dQw4w9WgXcQ" 

def main():
    st.set_page_config(page_title="Roulette App", page_icon="🎯")

    # --- トラップ発動中かどうかの状態管理 ---
    if "trap_active" not in st.session_state:
        st.session_state.trap_active = False
    if "trap_phase" not in st.session_state:
        st.session_state.trap_phase = "intro" # intro, spinning, result

    # もしトラップが発動していたら、BAN画面へ
    if st.session_state.trap_active:
        show_ban_screen()
        return

    # --- 通常画面 ---
    st.title("🎯 Python Roulette App")

    # 左サイドバーで設定
    with st.sidebar:
        st.header("項目設定 (最大10個)")
        items_input = []
        for i in range(10):
            col1, col2 = st.columns([2, 1])
            name = col1.text_input(f"項目名 {i+1}", value=f"項目{i+1}", key=f"n{i}")
            prob = col2.number_input(f"確率(%) {i+1}", min_value=0.0, max_value=100.0, step=1.0, key=f"p{i}", value=0.0)
            items_input.append({"name": name, "prob": prob})

        start_btn = st.button("スタート！", type="primary", use_container_width=True)

    # メインエリア
    placeholder = st.empty()

    if start_btn:
        # 1. トラップ判定
        for item in items_input:
            if "こはく" in item["name"]:
                st.session_state.trap_active = True
                st.rerun() # 画面リロードしてBAN画面へ
        
        # 2. 確率計算
        active_items = [item for item in items_input if item["name"].strip() != ""]
        if not active_items:
            st.warning("項目を入力してください")
            return

        specified_total = sum(item["prob"] for item in active_items if item["prob"] > 0)
        if specified_total > 100:
            st.error(f"確率の合計が100%を超えています: {specified_total}%")
            return

        # 確率の割り振り
        count_unspecified = sum(1 for item in active_items if item["prob"] == 0)
        remaining = 100 - specified_total
        
        final_items = []
        for item in active_items:
            p = item["prob"]
            if p == 0:
                p = remaining / count_unspecified if count_unspecified > 0 else 0
            if p > 0:
                final_items.append({"name": item["name"], "value": p})
        
        if not final_items:
            st.error("有効な項目がありません")
            return

        # 3. ルーレット演出（簡易アニメーション）
        df = pd.DataFrame(final_items)
        
        # 結果を先に抽選
        names = [d["name"] for d in final_items]
        weights = [d["value"] for d in final_items]
        winner = random.choices(names, weights=weights, k=1)[0]

        # 回転演出
        with placeholder.container():
            st.info("回転中...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # パラパラと候補を表示する演出
            for i in range(20):
                temp_pick = random.choice(names)
                status_text.markdown(f"### 🎲 {temp_pick} ...")
                progress_bar.progress((i + 1) / 20)
                time.sleep(0.1 + i * 0.01) # 徐々に遅く
            
            status_text.empty()
            progress_bar.empty()
            
            st.success("決定！")
            st.balloons()
            st.markdown(f"# 結果: 【 {winner} 】")
            st.write("選ばれたのは...", winner)

    else:
        # 待機画面：現在の設定でのグラフを表示
        active_items = [item for item in items_input if item["name"].strip() != ""]
        if active_items:
             # 簡易計算でプレビュー表示
            specified_total = sum(item["prob"] for item in active_items if item["prob"] > 0)
            count_unspecified = sum(1 for item in active_items if item["prob"] == 0)
            remaining = max(0, 100 - specified_total)
            
            preview_data = []
            for item in active_items:
                p = item["prob"]
                if p == 0:
                    p = remaining / count_unspecified if count_unspecified > 0 else 0
                if p > 0:
                    preview_data.append({"項目": item["name"], "確率": p})
            
            if preview_data:
                df = pd.DataFrame(preview_data)
                st.write("現在の確率設定:")
                st.bar_chart(df.set_index("項目"))


def show_ban_screen():
    st.markdown("""
    <style>
    .stApp { background-color: black; color: red; }
    h1, h2, h3, p { color: red !important; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("💀 警告 💀")
    st.header("あなたは永久BANです")
    st.write("最後の審判が始まります...")

    if st.button("運命のルーレットを回す", type="primary"):
        # 強制ルーレットロジック
        with st.spinner("審判中..."):
            time.sleep(3)
        
        # 死亡80%, 逃げる20%
        result = random.choices(["死亡", "逃げる"], weights=[80, 20], k=1)[0]
        
        if result == "逃げる":
            st.success("奇跡的に見逃された...")
            st.info("このタブを閉じてください。")
            st.stop()
        else:
            st.error("【 結果：死亡 】")
            st.write("さようなら...")
            time.sleep(1)
            # YouTube動画埋め込み（自動再生）
            st.video(f"https://www.youtube.com/watch?v={YOUTUBE_VIDEO_ID}", autoplay=True)
            st.stop()

if __name__ == "__main__":
    main()
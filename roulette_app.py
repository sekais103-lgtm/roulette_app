import streamlit as st
import json
import time
import streamlit.components.v1 as components

# ▼ここに飛ばしたいYouTubeのURL▼
YOUTUBE_URL = "https://youtu.be/cM7uKegVG-E?si=Gu4sFhziiEWQvVos"

def main():
    st.set_page_config(page_title="Roulette App", page_icon="🎯", layout="wide")

    # --- セッション状態の初期化 ---
    if "trap_triggered" not in st.session_state:
        st.session_state.trap_triggered = False

    # --- サイドバー設定エリア ---
    with st.sidebar:
        st.header("⚙️ 設定")
        st.info("スマホでは左上の「>」ボタンで設定を開閉できます。")
        
        num_items = st.slider("項目の数", min_value=2, max_value=20, value=5)
        
        items_data = []
        st.subheader("項目と確率")
        
        for i in range(num_items):
            col1, col2 = st.columns([0.65, 0.35])
            default_name = f"項目{i+1}"
            
            with col1:
                name = st.text_input(f"名前{i+1}", value=default_name, key=f"name_{i}", label_visibility="collapsed", placeholder=f"名前{i+1}")
            with col2:
                prob = st.number_input(f"確率{i+1}", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key=f"prob_{i}", label_visibility="collapsed")
            
            items_data.append({"name": name, "prob": prob})

    # --- メイン画面 ---
    
    if st.session_state.trap_triggered:
        render_trap_mode()
    else:
        # 通常モード画面
        st.title("🎯 スマホ・ルーレット")
        
        # スタートボタンをPython側に設置（カウントダウン処理のため）
        if st.button("スタート設定完了", type="primary", use_container_width=True):
            # 1. トラップ判定とカウントダウン
            if any("こはく" in item["name"] for item in items_data):
                # 警告とカウントダウン演出
                placeholder = st.empty()
                with placeholder.container():
                    st.error("⚠️ 警告：禁止ワード「こはく」を検知しました ⚠️")
                    st.markdown("### あなたはBAN対象です。")
                    time.sleep(2)
                    
                    st.markdown("## 3")
                    time.sleep(1)
                    st.markdown("## 2")
                    time.sleep(1)
                    st.markdown("## 1")
                    time.sleep(1)
                
                # トラップフラグを立ててリロード
                st.session_state.trap_triggered = True
                st.rerun()
            else:
                # 2. 通常ルーレット表示（エラーチェック後に表示）
                final_items = calculate_probabilities(items_data)
                if isinstance(final_items, str):
                    st.error(final_items)
                else:
                    # Pythonのボタンを消して、JSルーレットを表示
                    st.session_state.show_roulette = True

        # 通常ルーレットの描画エリア
        if not st.session_state.trap_triggered:
            # まだスタートしていない、または通常モードの場合のプレビュー計算
            final_items = calculate_probabilities(items_data)
            if not isinstance(final_items, str):
                 render_roulette(final_items, mode="normal")
            elif isinstance(final_items, str) and "show_roulette" in st.session_state:
                 # 入力エラー時は表示しない
                 pass


def calculate_probabilities(items):
    """確率計算ロジック"""
    active_items = [x for x in items if x["name"].strip() != ""]
    if not active_items:
        return "項目名を入力してください。"

    specified_total = sum(x["prob"] for x in active_items if x["prob"] > 0)
    if specified_total > 100:
        return f"確率の合計が100%を超えています (現在: {specified_total}%)"

    count_unspecified = sum(1 for x in active_items if x["prob"] == 0)
    remaining = 100 - specified_total

    result = []
    for x in active_items:
        p = x["prob"]
        if p == 0:
            p = remaining / count_unspecified if count_unspecified > 0 else 0
        if p > 0:
            result.append({"name": x["name"], "prob": p})
            
    if not result:
        return "有効な項目がありません。"
        
    return result


def render_trap_mode():
    """トラップ発動時の画面"""
    st.markdown("""
    <style>
    .stApp { background-color: black !important; }
    header, footer { visibility: hidden; }
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    h1, h2, h3, p, div, span { color: red !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # 死亡80%、逃げる20%（面積で制御）
    trap_items = [
        {"name": "死亡", "prob": 80, "color": "#8B0000"}, # 暗い赤
        {"name": "逃げる", "prob": 20, "color": "#00FF00"} # 緑
    ]
    
    render_roulette(trap_items, mode="trap")


def render_roulette(items, mode="normal"):
    """HTML5 Canvasルーレット（ストップボタン付き）"""
    
    items_json = json.dumps(items)
    
    bg_color = "black" if mode == "trap" else "white"
    text_color = "red" if mode == "trap" else "#333"
    
    # トラップモードなら最初から回転させるフラグ
    auto_spin = "true" if mode == "trap" else "false"
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background-color: {bg_color};
            color: {text_color};
            text-align: center;
            margin: 0;
            padding: 10px;
            touch-action: manipulation;
        }}
        #canvas-container {{
            position: relative;
            width: 95vw;
            height: 95vw;
            max-width: 600px;
            max-height: 600px;
            margin: 0 auto 20px auto;
        }}
        canvas {{ width: 100%; height: 100%; }}
        
        /* 巨大ボタン */
        #action-btn {{
            display: block;
            width: 90%;
            max-width: 400px;
            margin: 10px auto;
            padding: 25px 20px;
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
            background: linear-gradient(135deg, #FF5722, #FF8A65);
            border: none;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(255, 87, 34, 0.3);
            -webkit-tap-highlight-color: transparent;
        }}
        #action-btn:active {{ transform: scale(0.98); }}
        #action-btn.stop-mode {{
            background: linear-gradient(135deg, #D32F2F, #FF5252) !important;
            box-shadow: 0 4px 10px rgba(211, 47, 47, 0.5);
            animation: pulse 1s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
        }}

        #result {{ font-size: 1.8rem; font-weight: bold; margin: 20px 0; min-height: 2rem; }}
        #trap-message {{ color: red; font-size: 2rem; font-weight: bold; margin-bottom: 20px; display: {'block' if mode == 'trap' else 'none'}; }}
        
        .pointer {{
            position: absolute; top: 50%; right: -15px; transform: translateY(-50%);
            width: 0; height: 0;
            border-top: 20px solid transparent;
            border-bottom: 20px solid transparent;
            border-right: 40px solid #FF3D00;
            filter: drop-shadow(-2px 2px 2px rgba(0,0,0,0.3));
        }}
    </style>
    </head>
    <body>
        <div id="trap-message">あなたは永久BANです<br><span style="font-size:1.2rem">審判を下してください</span></div>
        <div id="canvas-container">
            <canvas id="wheel" width="1000" height="1000"></canvas>
            <div class="pointer"></div>
        </div>
        <div id="result"></div>
        
        <button id="action-btn" onclick="toggleSpin()">スタート！</button>

        <script>
            const canvas = document.getElementById('wheel');
            const ctx = canvas.getContext('2d');
            const items = {items_json};
            const mode = "{mode}";
            const youtubeUrl = "{YOUTUBE_URL}";
            const btn = document.getElementById('action-btn');
            
            let currentAngle = 0;
            let spinSpeed = 0;
            let isSpinning = false;
            let isStopping = false; // ストップボタンが押されたあとかどうか
            let animationId;
            
            const colors = ["#FF9999", "#66B2FF", "#99FF99", "#FFCC99", "#FF99CC", "#FFFF99", "#CC99FF", "#99FFFF"];
            
            function drawWheel() {{
                const w = canvas.width;
                const h = canvas.height;
                const cx = w / 2;
                const cy = h / 2;
                const r = w / 2 - 40;
                
                ctx.clearRect(0, 0, w, h);
                let startDeg = currentAngle;
                
                items.forEach((item, i) => {{
                    const extent = (item.prob / 100) * 360;
                    ctx.beginPath();
                    ctx.moveTo(cx, cy);
                    ctx.arc(cx, cy, r, (Math.PI / 180) * startDeg, (Math.PI / 180) * (startDeg + extent));
                    ctx.closePath();
                    
                    if (mode === "trap") {{
                        ctx.fillStyle = item.color;
                    }} else {{
                        ctx.fillStyle = colors[i % colors.length];
                    }}
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 4;
                    ctx.stroke();
                    
                    // 文字
                    ctx.save();
                    ctx.translate(cx, cy);
                    ctx.rotate((Math.PI / 180) * (startDeg + extent / 2));
                    ctx.textAlign = "right";
                    ctx.fillStyle = (mode === "trap") ? "white" : "black";
                    const fontSize = (mode === "trap") ? w / 15 : w / 22; 
                    ctx.font = `bold ${{fontSize}}px sans-serif`;
                    ctx.fillText(item.name, r - 30, fontSize / 3);
                    ctx.restore();
                    
                    startDeg += extent;
                }});
            }}
            
            function toggleSpin() {{
                if (!isSpinning) {{
                    // スタート処理
                    isSpinning = true;
                    isStopping = false;
                    spinSpeed = 30; // 常に一定の高速回転
                    if (mode === "trap") spinSpeed = 50; 
                    
                    btn.innerText = "ストップ！";
                    btn.classList.add("stop-mode");
                    document.getElementById('result').innerText = mode === "trap" ? "審判中..." : "回転中...";
                    
                    animate();
                }} else if (!isStopping) {{
                    // ストップ処理（ブレーキ開始）
                    isStopping = true;
                    btn.disabled = true;
                    btn.innerText = "停止中...";
                    btn.classList.remove("stop-mode");
                }}
            }}
            
            function animate() {{
                if (isSpinning) {{
                    currentAngle += spinSpeed;
                    if (currentAngle >= 360) currentAngle -= 360;
                    
                    if (isStopping) {{
                        // ブレーキがかかった時の減速処理
                        spinSpeed *= 0.95; // 急ブレーキ
                        if (spinSpeed < 0.1) {{
                            isSpinning = false;
                            spinSpeed = 0;
                            showResult();
                            return; // アニメーション終了
                        }}
                    }} else {{
                        // ストップボタンを押すまでは減速しない（または極わずか）
                        // spinSpeed *= 1.0; 
                    }}
                    
                    drawWheel();
                    requestAnimationFrame(animate);
                }}
            }}
            
            function showResult() {{
                // 結果判定
                let targetAngle = (360 - currentAngle) % 360;
                if (targetAngle < 0) targetAngle += 360;
                
                let currentCheck = 0;
                let winner = "";
                
                for (let item of items) {{
                    let extent = (item.prob / 100) * 360;
                    if (currentCheck <= targetAngle && targetAngle < currentCheck + extent) {{
                        winner = item.name;
                        break;
                    }}
                    currentCheck += extent;
                }}
                
                const resDiv = document.getElementById('result');
                resDiv.innerText = "結果: " + winner;
                
                if (mode === "trap") {{
                    if (winner === "逃げる") {{
                        resDiv.style.color = "#00FF00";
                        resDiv.innerText += "\\n(タブを閉じています...)";
                        setTimeout(() => {{
                            window.opener = null;
                            window.open('', '_self');
                            window.close();
                            alert("おめでとうございます！\\n（ブラウザのタブを手動で閉じてください）");
                        }}, 1500);
                    }} else {{
                        resDiv.style.color = "red";
                        resDiv.innerText += "\\n(さようなら...)";
                        setTimeout(() => {{
                            window.location.href = youtubeUrl;
                        }}, 1500);
                    }}
                }} else {{
                    btn.innerText = "もう一度回す";
                    btn.disabled = false;
                    btn.classList.remove("stop-mode");
                    resDiv.scrollIntoView({{behavior: "smooth", block: "center"}});
                }}
            }}
            
            // 初期描画
            drawWheel();
            
            // トラップモードなら自動で回転開始（ボタンはストップ状態から）
            if ({auto_spin}) {{
                setTimeout(toggleSpin, 500);
            }}
            
        </script>
    </body>
    </html>
    """
    
    height = 850 if mode == "trap" else 800
    components.html(html_code, height=height, scrolling=False)

if __name__ == "__main__":
    main()
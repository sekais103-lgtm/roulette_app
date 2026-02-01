import streamlit as st
import json
import time
import streamlit.components.v1 as components

# ▼ここに飛ばしたいYouTubeのURL▼
YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

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

    # --- トラップ即時判定ロジック ---
    if not st.session_state.trap_triggered:
        if any("こはく" in item["name"] for item in items_data):
            placeholder = st.empty()
            with placeholder.container():
                st.markdown("""
                <style>
                .stApp { background-color: #220000; }
                h1, h2, h3 { color: red !important; text-align: center; }
                .warning-text { font-size: 2rem; font-weight: bold; color: red; text-align: center; margin-top: 50px; }
                .countdown { font-size: 5rem; font-weight: bold; color: white; text-align: center; }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown('<p class="warning-text">⚠️ 警告：禁止ワード「こはく」を検知しました ⚠️</p>', unsafe_allow_html=True)
                st.markdown('<p class="warning-text">あなたはBAN対象です...</p>', unsafe_allow_html=True)
                time.sleep(2)
                
                st.markdown('<p class="countdown">3</p>', unsafe_allow_html=True)
                time.sleep(1)
                st.markdown('<p class="countdown">2</p>', unsafe_allow_html=True)
                time.sleep(1)
                st.markdown('<p class="countdown">1</p>', unsafe_allow_html=True)
                time.sleep(1)
            
            st.session_state.trap_triggered = True
            st.rerun()

    # --- メイン画面描画 ---
    if st.session_state.trap_triggered:
        render_trap_mode()
    else:
        st.title("🎯 スマホ・ルーレット")
        final_items = calculate_probabilities(items_data)
        if isinstance(final_items, str):
            st.error(final_items)
        else:
            render_roulette(final_items, mode="normal")


def calculate_probabilities(items):
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
    st.markdown("""
    <style>
    .stApp { background-color: black !important; }
    header, footer { visibility: hidden; }
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    h1, h2, h3, p, div, span { color: red !important; }
    </style>
    """, unsafe_allow_html=True)
    
    trap_items = [
        {"name": "死亡", "prob": 80, "color": "#8B0000"},
        {"name": "逃げる", "prob": 20, "color": "#00FF00"}
    ]
    
    render_roulette(trap_items, mode="trap")


def render_roulette(items, mode="normal"):
    items_json = json.dumps(items)
    
    bg_color = "black" if mode == "trap" else "white"
    text_color = "red" if mode == "trap" else "#333"
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
        
        /* YouTubeへ強制移動用ボタンのデザイン */
        #action-btn.punish-mode {{
            background: linear-gradient(135deg, #000000, #330000) !important;
            border: 2px solid red;
            color: red;
            box-shadow: 0 0 15px red;
            animation: shake 0.5s infinite;
        }}

        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
        }}
        
        @keyframes shake {{
            0% {{ transform: translate(1px, 1px) rotate(0deg); }}
            10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
            20% {{ transform: translate(-3px, 0px) rotate(1deg); }}
            30% {{ transform: translate(3px, 2px) rotate(0deg); }}
            40% {{ transform: translate(1px, -1px) rotate(1deg); }}
            50% {{ transform: translate(-1px, 2px) rotate(-1deg); }}
            60% {{ transform: translate(-3px, 1px) rotate(0deg); }}
            70% {{ transform: translate(3px, 1px) rotate(-1deg); }}
            80% {{ transform: translate(-1px, -1px) rotate(1deg); }}
            90% {{ transform: translate(1px, 2px) rotate(0deg); }}
            100% {{ transform: translate(1px, -2px) rotate(-1deg); }}
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
            let isStopping = false;
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
                if (btn.classList.contains("punish-mode")) {{
                    // 制裁ボタンモードの場合、クリックでYouTubeへ移動
                    window.open(youtubeUrl, '_blank');
                    return;
                }}
                
                if (!isSpinning) {{
                    isSpinning = true;
                    isStopping = false;
                    spinSpeed = 30;
                    if (mode === "trap") spinSpeed = 50; 
                    btn.innerText = "ストップ！";
                    btn.classList.add("stop-mode");
                    document.getElementById('result').innerText = mode === "trap" ? "審判中..." : "回転中...";
                    animate();
                }} else if (!isStopping) {{
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
                        spinSpeed *= 0.95;
                        if (spinSpeed < 0.1) {{
                            isSpinning = false;
                            spinSpeed = 0;
                            showResult();
                            return;
                        }}
                    }}
                    drawWheel();
                    requestAnimationFrame(animate);
                }}
            }}
            
            function showResult() {{
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
                        
                        // ★修正ポイント：自動移動を試みるが、失敗対策としてボタンを変える
                        setTimeout(() => {{
                            // 1. まずは自動移動をトライ（スマホだとブロックされやすい）
                            const win = window.open(youtubeUrl, '_blank');
                            
                            // 2. ボタンを「制裁ボタン」に変身させて、手動で押せるようにする
                            btn.disabled = false;
                            btn.innerText = "制裁を受ける（タップ）";
                            btn.classList.add("punish-mode");
                            
                            // 3. もし自動移動が成功していればいいが、していなければユーザーがこのボタンを押す
                            if (!win) {{
                                resDiv.innerText += "\\nボタンを押して移動してください";
                            }}
                        }}, 1000);
                    }}
                }} else {{
                    btn.innerText = "もう一度回す";
                    btn.disabled = false;
                    btn.classList.remove("stop-mode");
                    resDiv.scrollIntoView({{behavior: "smooth", block: "center"}});
                }}
            }}
            
            drawWheel();
            
            if ({auto_spin}) {{
                btn.innerText = "ストップ！";
                btn.classList.add("stop-mode");
                setTimeout(toggleSpin, 100); 
            }}
            
        </script>
    </body>
    </html>
    """
    
    height = 850 if mode == "trap" else 800
    components.html(html_code, height=height, scrolling=False)

if __name__ == "__main__":
    main()
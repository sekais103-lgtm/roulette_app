import streamlit as st
import json
import streamlit.components.v1 as components

# ▼ここに飛ばしたいYouTubeのURL▼
YOUTUBE_URL = "https://youtu.be/cM7uKegVG-E?si=wueKrQjqanQRSZvI"

def main():
    # スマホで見やすいようにlayout="centered"に変更し、初期サイドバー状態を閉じる設定にする案もありますが、
    # 設定項目へのアクセスを考えるとデフォルトのまま、中身をレスポンシブにする方が良いと判断しました。
    st.set_page_config(page_title="Roulette App", page_icon="🎯", layout="wide")

    # --- セッション状態の初期化 ---
    if "trap_triggered" not in st.session_state:
        st.session_state.trap_triggered = False

    # --- サイドバー設定エリア ---
    with st.sidebar:
        st.header("⚙️ 設定")
        st.info("スマホでは左上の「>」ボタンで設定を開閉できます。")
        
        # 項目数の変更機能
        num_items = st.slider("項目の数", min_value=2, max_value=20, value=5)
        
        items_data = []
        st.subheader("項目と確率")
        
        # 指定された数だけ入力欄を表示
        for i in range(num_items):
            # スマホの狭い横幅でも見やすいようにカラム比率を調整
            col1, col2 = st.columns([0.65, 0.35])
            default_name = f"項目{i+1}"
            
            with col1:
                name = st.text_input(f"名前{i+1}", value=default_name, key=f"name_{i}", label_visibility="collapsed", placeholder=f"名前{i+1}")
            with col2:
                # スマホで入力しやすいようにステップを1にして+-ボタンを出しやすくする
                prob = st.number_input(f"確率{i+1}", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key=f"prob_{i}", label_visibility="collapsed")
            
            items_data.append({"name": name, "prob": prob})

        # トラップ判定
        if any("こはく" in item["name"] for item in items_data):
            st.session_state.trap_triggered = True
        else:
            st.session_state.trap_triggered = False

    # --- メイン画面 ---
    
    if st.session_state.trap_triggered:
        render_trap_mode()
    else:
        # 通常モード
        st.title("🎯 スマホ・ルーレット")
        
        final_items = calculate_probabilities(items_data)
        
        if isinstance(final_items, str):
            st.error(final_items)
        else:
            render_roulette(final_items, mode="normal")


def calculate_probabilities(items):
    """確率計算ロジック（変更なし）"""
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
    """トラップ発動時の画面（スマホ対応）"""
    st.markdown("""
    <style>
    .stApp { background-color: black; }
    header, footer { visibility: hidden; }
    /* スマホでの表示崩れを防ぐための調整 */
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    </style>
    """, unsafe_allow_html=True)
    
    trap_items = [
        {"name": "死亡", "prob": 80, "color": "#FF0000"},
        {"name": "逃げる", "prob": 20, "color": "#00FF00"}
    ]
    
    render_roulette(trap_items, mode="trap")


def render_roulette(items, mode="normal"):
    """スマホ最適化されたHTML5 Canvasルーレット"""
    
    items_json = json.dumps(items)
    
    bg_color = "black" if mode == "trap" else "white"
    text_color = "red" if mode == "trap" else "#333"
    btn_display = "none" if mode == "trap" else "block"
    auto_start = "true" if mode == "trap" else "false"
    
    # CSSをスマホ向けに大幅調整
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
            touch-action: manipulation; /* スマホでのタップ反応を良くする */
        }}
        /* レスポンシブなコンテナ */
        #canvas-container {{
            position: relative;
            width: 95vw;  /* 画面横幅の95% */
            height: 95vw; /* 正方形を維持 */
            max-width: 600px; /* PCで大きすぎないように制限 */
            max-height: 600px;
            margin: 0 auto 20px auto;
        }}
        canvas {{
            width: 100%;
            height: 100%;
        }}
        /* スマホで押しやすい巨大ボタン */
        #spin-btn {{
            display: {btn_display};
            width: 90%; /* 横幅いっぱい */
            max-width: 400px;
            margin: 10px auto;
            padding: 25px 20px; /* 上下の余白を大きく */
            font-size: 1.5rem; /* 文字サイズを大きく */
            font-weight: bold;
            color: white;
            background: linear-gradient(135deg, #FF5722, #FF8A65);
            border: none;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(255, 87, 34, 0.3);
            transition: transform 0.1s, box-shadow 0.1s;
            -webkit-tap-highlight-color: transparent; /* タップ時の枠線を消す */
        }}
        #spin-btn:active {{ transform: scale(0.98); box-shadow: 0 2px 5px rgba(255, 87, 34, 0.3); }}
        #spin-btn:disabled {{ background: #ccc; box-shadow: none; cursor: not-allowed; }}
        
        #result {{ font-size: 1.8rem; font-weight: bold; margin: 20px 0; min-height: 1.8rem; word-break: break-all; }}
        #trap-message {{ color: red; font-size: 2rem; font-weight: bold; margin-bottom: 20px; display: {'block' if mode == 'trap' else 'none'}; }}
        
        /* 針のデザイン調整 */
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
        <div id="trap-message">あなたは永久BANです<br><span style="font-size:1.2rem">最後の審判...</span></div>
        <div id="canvas-container">
            <canvas id="wheel" width="1000" height="1000"></canvas>
            <div class="pointer"></div>
        </div>
        <div id="result"></div>
        <button id="spin-btn" onclick="startSpin()">スタート！</button>

        <script>
            const canvas = document.getElementById('wheel');
            const ctx = canvas.getContext('2d');
            const items = {items_json};
            const mode = "{mode}";
            const youtubeUrl = "{YOUTUBE_URL}";
            
            let currentAngle = 0;
            let spinSpeed = 0;
            let isSpinning = false;
            let animationId;
            
            const colors = ["#FF9999", "#66B2FF", "#99FF99", "#FFCC99", "#FF99CC", "#FFFF99", "#CC99FF", "#99FFFF"];
            
            function drawWheel() {{
                // キャンバスの内部解像度を使用
                const w = canvas.width; // 1000
                const h = canvas.height; // 1000
                const cx = w / 2;
                const cy = h / 2;
                const r = w / 2 - 40; // 余白調整
                
                ctx.clearRect(0, 0, w, h);
                
                let startDeg = currentAngle;
                
                items.forEach((item, i) => {{
                    const extent = (item.prob / 100) * 360;
                    const endDeg = startDeg + extent;
                    
                    ctx.beginPath();
                    ctx.moveTo(cx, cy);
                    ctx.arc(cx, cy, r, (Math.PI / 180) * startDeg, (Math.PI / 180) * endDeg);
                    ctx.closePath();
                    
                    if (mode === "trap") {{
                        ctx.fillStyle = item.color;
                    }} else {{
                        ctx.fillStyle = colors[i % colors.length];
                    }}
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 4; // 線を少し太く
                    ctx.stroke();
                    
                    // テキスト描画
                    ctx.save();
                    ctx.translate(cx, cy);
                    const midRad = (Math.PI / 180) * (startDeg + extent / 2);
                    ctx.rotate(midRad);
                    ctx.textAlign = "right";
                    ctx.fillStyle = (mode === "trap") ? "white" : "black";
                    // 解像度に合わせてフォントサイズを調整
                    const fontSize = (mode === "trap") ? w / 15 : w / 22; 
                    ctx.font = `bold ${{fontSize}}px sans-serif`;
                    ctx.fillText(item.name, r - 30, fontSize / 3);
                    ctx.restore();
                    
                    startDeg += extent;
                }});
            }}
            
            function startSpin() {{
                if (isSpinning) return;
                
                isSpinning = true;
                spinSpeed = Math.random() * 25 + 25; // 少しスピードアップ
                if (mode === "trap") spinSpeed = 50;
                
                document.getElementById('spin-btn').disabled = true;
                document.getElementById('result').innerText = mode === "trap" ? "審判中..." : "回転中...";
                
                animate();
            }}
            
            function animate() {{
                spinSpeed *= 0.985;
                currentAngle += spinSpeed;
                if (currentAngle >= 360) currentAngle -= 360;
                
                drawWheel();
                
                if (spinSpeed < 0.1) {{
                    isSpinning = false;
                    showResult();
                }} else {{
                    animationId = requestAnimationFrame(animate);
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
                            alert("あなたの勝ちです。ブラウザのタブを閉じてください。");
                        }}, 1500);
                    }} else {{
                        resDiv.style.color = "red";
                        resDiv.innerText += "\\n(さようなら...)";
                        setTimeout(() => {{
                            window.location.href = youtubeUrl;
                        }}, 1500);
                    }}
                }} else {{
                    document.getElementById('spin-btn').disabled = false;
                    // スマホで結果が見えるように少しスクロール
                    resDiv.scrollIntoView({{behavior: "smooth", block: "center"}});
                }}
            }}
            
            drawWheel();
            
            if ({auto_start}) {{
                setTimeout(startSpin, 1000);
            }}
            
        </script>
    </body>
    </html>
    """
    
    # スマホでスクロールが発生しにくい高さに調整
    height = 800 if mode == "trap" else 750
    components.html(html_code, height=height, scrolling=False)

if __name__ == "__main__":
    main()
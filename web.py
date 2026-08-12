from flask import Flask, request, jsonify, render_template_string
from ollama import chat

app = Flask(__name__)

MODEL = "qwen3:8b"

SYSTEM_PROMPT = """
You are JI, a personal AI assistant.

You are friendly, intelligent, natural, curious and helpful.

Speak naturally and casually when appropriate.
Keep simple answers concise.
Explain difficult things clearly.
Never pretend you did something you didn't do.
Never invent facts.

You are running locally through Ollama.
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JI — Local Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>

/* ============ DESIGN TOKENS ============ */
:root{
  --bg:#050505;
  --bg-panel:rgba(10,10,10,.55);
  --bg-elevated:#101010;
  --border:rgba(255,255,255,.08);
  --border-soft:rgba(255,255,255,.05);
  --text:#f5f5f2;
  --text-dim:#9a9a95;
  --text-faint:#555552;
  --glow:rgba(255,255,255,.08);
  --ease:cubic-bezier(.22,1,.36,1);
  --ease-spring:cubic-bezier(.34,1.56,.64,1);
  --radius-lg:22px;
  --radius-md:14px;
  --radius-sm:10px;
}

*{ box-sizing:border-box; margin:0; padding:0; }

html,body{ height:100%; }

body{
  background:var(--bg);
  color:var(--text);
  font-family:'Inter',-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  height:100vh;
  overflow:hidden;
  -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
  opacity:0;
  animation:appear 1.1s var(--ease) forwards;
}

@keyframes appear{ to{ opacity:1; } }

/* ============ AMBIENT KANJI FIELD (B&W, UP & DOWN) ============ */

#kanji-canvas{
  position:fixed;
  inset:0;
  width:100%;
  height:100%;
  z-index:0;
  pointer-events:none;
}

/* soft vertical gradient masks so glyphs fade at top & bottom */
.fade-top{
  position:fixed; top:0; left:0; right:0; height:26vh; z-index:1;
  pointer-events:none;
  background:linear-gradient(to bottom, rgba(5,5,5,1), rgba(5,5,5,0));
}
.fade-bottom{
  position:fixed; bottom:0; left:0; right:0; height:26vh; z-index:1;
  pointer-events:none;
  background:linear-gradient(to top, rgba(5,5,5,1), rgba(5,5,5,0));
}

.noise{
  position:fixed;
  inset:0;
  z-index:1;
  pointer-events:none;
  opacity:.03;
  mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

.vignette{
  position:fixed;
  inset:0;
  z-index:1;
  pointer-events:none;
  background:radial-gradient(ellipse at 50% 38%, transparent 0%, rgba(0,0,0,.6) 100%);
}

/* ============ SHELL ============ */

.shell{
  position:relative;
  z-index:2;
  display:flex;
  height:100vh;
}

/* ---- SIDEBAR ---- */

.sidebar{
  width:272px;
  flex-shrink:0;
  background:linear-gradient(180deg, rgba(12,12,12,.6), rgba(8,8,8,.4));
  backdrop-filter:blur(26px) saturate(150%);
  -webkit-backdrop-filter:blur(26px) saturate(150%);
  border-right:1px solid var(--border-soft);
  padding:32px 24px;
  display:flex;
  flex-direction:column;
  transition:transform .6s var(--ease);
}

.brand{
  display:flex;
  align-items:center;
  gap:14px;
  margin-bottom:44px;
  user-select:none;
}

.brand-mark{
  width:46px; height:46px;
  border-radius:14px;
  display:flex; align-items:center; justify-content:center;
  font-family:'Shippori Mincho',serif;
  font-size:22px;
  color:#f5f5f2;
  background:linear-gradient(150deg,#1a1a1a,#0a0a0a);
  border:1px solid var(--border);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.06), 0 10px 30px -10px rgba(0,0,0,.8);
}

.brand-name{
  font-size:19px;
  font-weight:650;
  letter-spacing:.02em;
  line-height:1.1;
}

.brand-sub{
  font-size:9.5px;
  letter-spacing:.3em;
  text-transform:uppercase;
  color:var(--text-faint);
  font-weight:500;
  margin-top:3px;
}

.new-chat{
  background:linear-gradient(180deg,#161616,#0e0e0e);
  border:1px solid var(--border);
  color:var(--text);
  padding:14px 18px;
  border-radius:var(--radius-md);
  cursor:pointer;
  font-size:13.5px;
  font-weight:500;
  font-family:inherit;
  letter-spacing:.01em;
  display:flex;
  align-items:center;
  gap:10px;
  transition:transform .25s var(--ease-spring), background .3s var(--ease), border-color .3s var(--ease), box-shadow .3s var(--ease);
}

.new-chat:hover{
  background:#1a1a1a;
  border-color:rgba(255,255,255,.16);
  transform:translateY(-1px);
  box-shadow:0 12px 30px -12px rgba(0,0,0,.9), 0 0 0 1px rgba(255,255,255,.02);
}

.new-chat:active{ transform:scale(.97); }
.new-chat svg{ opacity:.7; }

.sidebar-foot{
  margin-top:auto;
  padding-top:22px;
  border-top:1px solid var(--border-soft);
  font-size:11px;
  color:var(--text-faint);
  line-height:1.8;
  letter-spacing:.01em;
}

.sidebar-foot .dot{
  display:inline-block;
  width:7px; height:7px;
  border-radius:50%;
  background:#f5f5f2;
  margin-right:8px;
  box-shadow:0 0 10px rgba(245,245,242,.6);
  animation:pulse 2.6s ease-in-out infinite;
}

@keyframes pulse{
  0%,100%{ opacity:1; transform:scale(1); }
  50%{ opacity:.35; transform:scale(.8); }
}

/* ---- MAIN ---- */

.main{
  flex:1;
  display:flex;
  flex-direction:column;
  height:100vh;
  min-width:0;
}

.topbar{
  height:72px;
  flex-shrink:0;
  border-bottom:1px solid var(--border-soft);
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:0 36px;
  background:rgba(5,5,5,.35);
  backdrop-filter:blur(18px);
  -webkit-backdrop-filter:blur(18px);
}

.topbar-left{ display:flex; align-items:center; gap:14px; }

.topbar-title{
  font-size:14px;
  font-weight:600;
  letter-spacing:.02em;
}

.topbar-model{
  font-size:11px;
  color:var(--text-faint);
  font-weight:400;
  letter-spacing:.01em;
  padding:5px 10px;
  border:1px solid var(--border-soft);
  border-radius:20px;
  background:rgba(255,255,255,.02);
}

.status-pill{
  display:flex; align-items:center; gap:8px;
  font-size:11px;
  color:var(--text-dim);
  letter-spacing:.02em;
}

.status-dot{
  width:8px; height:8px; border-radius:50%;
  background:#9a9a95;
  box-shadow:0 0 10px rgba(255,255,255,.2);
  animation:softblink 3s ease-in-out infinite;
}

@keyframes softblink{
  0%,100%{ opacity:1; }
  50%{ opacity:.4; }
}

/* ---- CHAT ---- */

.chat{
  flex:1;
  overflow-y:auto;
  padding:56px 24px 24px;
  scroll-behavior:smooth;
}

.chat::-webkit-scrollbar{ width:9px; }
.chat::-webkit-scrollbar-thumb{
  background:linear-gradient(180deg,#1e1e1e,#161616);
  border-radius:9px;
  border:2px solid transparent;
  background-clip:padding-box;
}
.chat::-webkit-scrollbar-thumb:hover{ background:#2a2a2a; background-clip:padding-box; }
.chat::-webkit-scrollbar-track{ background:transparent; }

.message{
  max-width:780px;
  margin:0 auto 36px;
  display:flex;
  gap:18px;
  opacity:0;
  transform:translateY(16px) scale(.985);
  animation:rise .6s var(--ease) forwards;
  will-change:transform,opacity;
}

@keyframes rise{
  to{ opacity:1; transform:translateY(0) scale(1); }
}

.avatar{
  width:38px; height:38px;
  border-radius:12px;
  flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-family:'Shippori Mincho',serif;
  font-size:16px;
  border:1px solid var(--border);
  box-shadow:0 8px 20px -8px rgba(0,0,0,.7);
  transition:transform .3s var(--ease-spring);
}

.message:hover .avatar{ transform:scale(1.06) rotate(-2deg); }

.avatar.ai{
  background:linear-gradient(155deg,#1a1a1a,#0a0a0a);
  color:#f0efe9;
}

.avatar.user{
  background:#f5f5f2;
  color:#0a0a0a;
  font-family:'Inter',sans-serif;
  font-weight:650;
  font-size:12px;
}

.msg-body{ min-width:0; padding-top:7px; }

.msg-role{
  font-size:10.5px;
  font-weight:600;
  letter-spacing:.08em;
  text-transform:uppercase;
  color:var(--text-faint);
  margin-bottom:7px;
}

.content{
  line-height:1.8;
  white-space:pre-wrap;
  font-size:15px;
  color:var(--text);
  font-weight:400;
}

.content.thinking{
  color:var(--text-dim);
  display:flex;
  align-items:center;
  gap:6px;
  padding:14px 18px;
  background:rgba(255,255,255,.02);
  border:1px solid var(--border-soft);
  border-radius:var(--radius-md);
  width:fit-content;
}

.tdot{
  width:6px; height:6px;
  border-radius:50%;
  background:var(--text-dim);
  animation:bounce 1.2s ease-in-out infinite;
}
.tdot:nth-child(2){ animation-delay:.15s; }
.tdot:nth-child(3){ animation-delay:.3s; }

@keyframes bounce{
  0%,60%,100%{ transform:translateY(0); opacity:.4; }
  30%{ transform:translateY(-5px); opacity:1; }
}

/* ---- INPUT ---- */

.input-area{
  padding:18px 24px 26px;
  flex-shrink:0;
}

.input-box{
  max-width:780px;
  margin:auto;
  background:rgba(16,16,16,.7);
  backdrop-filter:blur(22px);
  -webkit-backdrop-filter:blur(22px);
  border:1px solid var(--border);
  border-radius:20px;
  display:flex;
  align-items:flex-end;
  padding:8px 8px 8px 20px;
  transition:border-color .35s var(--ease), box-shadow .35s var(--ease), transform .35s var(--ease);
}

.input-box:focus-within{
  border-color:rgba(255,255,255,.18);
  box-shadow:0 0 0 5px rgba(255,255,255,.02), 0 18px 50px -18px rgba(0,0,0,.8);
  transform:translateY(-1px);
}

textarea{
  flex:1;
  background:transparent;
  border:none;
  outline:none;
  color:var(--text);
  resize:none;
  padding:13px 6px;
  font-size:15px;
  font-family:inherit;
  height:26px;
  max-height:160px;
  line-height:1.5;
}

textarea::placeholder{ color:var(--text-faint); }

button.send{
  background:linear-gradient(180deg,#f5f5f2,#e6e6e2);
  color:#0a0a0a;
  border:none;
  border-radius:14px;
  width:44px; height:44px;
  flex-shrink:0;
  cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  transition:transform .28s var(--ease-spring), box-shadow .28s var(--ease), opacity .25s var(--ease);
  box-shadow:0 8px 20px -8px rgba(245,245,242,.35);
}

button.send:hover{ transform:translateY(-2px) scale(1.04); box-shadow:0 14px 28px -10px rgba(245,245,242,.5); }
button.send:active{ transform:scale(.9); }
button.send:disabled{ opacity:.3; cursor:default; transform:none; box-shadow:none; }

.hint{
  text-align:center;
  font-size:10.5px;
  color:var(--text-faint);
  margin-top:14px;
  letter-spacing:.02em;
}

/* ---- SPLASH / LOADER ---- */

.splash{
  position:fixed;
  inset:0;
  z-index:100;
  background:#050505;
  display:flex; align-items:center; justify-content:center;
  flex-direction:column;
  gap:22px;
  transition:opacity .9s var(--ease), visibility .9s var(--ease);
}

.splash.hidden{ opacity:0; visibility:hidden; }

.splash-mark{
  font-family:'Shippori Mincho',serif;
  font-size:52px;
  color:#f5f5f2;
  animation:markin 1.2s var(--ease-spring) both;
  text-shadow:0 0 40px rgba(245,245,242,.25);
}

@keyframes markin{
  from{ opacity:0; transform:scale(.6) rotate(-6deg); }
  to{ opacity:1; transform:scale(1) rotate(0); }
}

.splash-bar{
  width:120px; height:2px;
  background:#1a1a1a;
  border-radius:2px;
  overflow:hidden;
}

.splash-bar i{
  display:block;
  height:100%;
  width:40%;
  background:#f5f5f2;
  border-radius:2px;
  animation:load 1.4s var(--ease) infinite;
}

@keyframes load{
  0%{ transform:translateX(-120%); }
  100%{ transform:translateX(320%); }
}

/* ---- MOBILE ---- */

@media(max-width:760px){
  .sidebar{
    position:fixed;
    left:0; top:0; bottom:0;
    transform:translateX(-100%);
    z-index:10;
    box-shadow:0 0 60px rgba(0,0,0,.8);
  }
  .sidebar.open{ transform:translateX(0); }
  .topbar{ padding:0 18px; }
  .chat{ padding:36px 14px 14px; }
  .input-area{ padding:12px 14px 18px; }
  .status-pill{ display:none; }
}

/* ---- REDUCED MOTION ---- */

@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{ animation-duration:.001ms !important; animation-iteration-count:1 !important; transition-duration:.001ms !important; }
  body{ opacity:1; }
  .message{ animation:none; opacity:1; transform:none; }
}

</style>
</head>
<body>

<div class="splash" id="splash">
  <div class="splash-mark">識</div>
  <div class="splash-bar"><i></i></div>
</div>

<canvas id="kanji-canvas"></canvas>
<div class="fade-top"></div>
<div class="fade-bottom"></div>
<div class="noise"></div>
<div class="vignette"></div>

<div class="shell">

  <div class="sidebar" id="sidebar">
    <div class="brand">
      <div class="brand-mark">識</div>
      <div>
        <div class="brand-name">JI</div>
<div class="brand-sub">JUGGY INTELLIGENCE</div>
      </div>
    </div>

    <button class="new-chat" onclick="newChat()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
      New conversation
    </button>

    <div class="sidebar-foot">
      <div><span class="dot"></span>Running locally via Ollama</div>
      <div style="margin-top:6px;">Model &middot; qwen3:8b</div>
    </div>
  </div>

  <div class="main">

    <div class="topbar">
      <div class="topbar-left">
        <span class="topbar-title">JI</span>
        <span class="topbar-model">qwen3:8b</span>
      </div>
      <div class="status-pill">
        <span class="status-dot"></span>
        <span id="statusText">idle</span>
      </div>
    </div>

    <div class="chat" id="chat">
      <div class="message" style="animation-delay:.15s">
        <div class="avatar ai">識</div>
        <div class="msg-body">
          <div class="msg-role">JI</div>
          <div class="content">Hey. What's up?</div>
        </div>
      </div>
    </div>

    <div class="input-area">
      <div class="input-box">
        <textarea id="input" placeholder="Message JI..." rows="1" onkeydown="handleKey(event)" oninput="autoGrow(this)"></textarea>
        <button class="send" id="sendBtn" onclick="sendMessage()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="6 11 12 5 18 11"/></svg>
        </button>
      </div>
      <div class="hint">JI can make mistakes. Verify anything important.</div>
    </div>

  </div>

</div>

<script>

/* ============ SPLASH ============ */
window.addEventListener('load', () => {
  setTimeout(() => document.getElementById('splash').classList.add('hidden'), 700);
});

/* ============ AMBIENT KANJI FIELD (B&W, UP & DOWN) ============ */

const canvas = document.getElementById('kanji-canvas');
const ctx = canvas.getContext('2d');

const GLYPHS = ['智','心','思','知','静','学','記','憶','夢','語','光','間','道','無','和','識','未','来','対','話','禅','空','森','風','月','日','水','火','土','金'];

let W, H, upStream, downStream;

function resize(){
  W = canvas.width = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);

/* Each particle belongs to a column and moves either up or down. */
function makeParticle(dir){
  return {
    ch: GLYPHS[Math.floor(Math.random()*GLYPHS.length)],
    col: Math.random()*W,
    y: Math.random()*H,
    size: 26 + Math.random()*80,
    speed: .18 + Math.random()*.38,
    drift: (Math.random()-.5)*.12,
    opacity: .02 + Math.random()*.05,
    dir: dir || (Math.random() < .5 ? 1 : -1)
  };
}

function buildStream(){
  const count = Math.max(26, Math.floor((W*H)/52000));
  upStream = Array.from({length:Math.floor(count*.5)}, () => makeParticle(1));
  downStream = Array.from({length:count - Math.floor(count*.5)}, () => makeParticle(-1));
}

resize();
buildStream();

function drawStream(arr){
  const fadeZone = H*0.12;
  for(const p of arr){
    p.y += p.speed * p.dir;
    p.col += p.drift;

    let fade = 1;
    if(p.dir === 1){ // moving down: fade out at bottom
      if(p.y > H - fadeZone) fade = Math.max(0,(H - p.y)/fadeZone);
      if(p.y < fadeZone) fade = Math.min(fade, p.y/fadeZone);
    } else { // moving up: fade out at top
      if(p.y < fadeZone) fade = Math.max(0, p.y/fadeZone);
      if(p.y > H - fadeZone) fade = Math.min(fade, (H - p.y)/fadeZone);
    }

    ctx.font = `500 ${p.size}px 'Shippori Mincho', serif`;
    ctx.fillStyle = `rgba(245,245,242,${p.opacity*fade})`;
    ctx.fillText(p.ch, p.col, p.y);

    // wraparound
    if(p.dir === 1 && p.y > H + 120) p.y = -120;
    if(p.dir === -1 && p.y < -120) p.y = H + 120;
  }
}

function animate(){
  ctx.clearRect(0,0,W,H);
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  drawStream(upStream);
  drawStream(downStream);
  requestAnimationFrame(animate);
}
animate();

/* ============ CHAT LOGIC ============ */

function autoGrow(el){
  el.style.height = '26px';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}

function addMessage(text, isUser, thinking){
  const chat = document.getElementById('chat');

  const message = document.createElement('div');
  message.className = 'message';

  const avatar = document.createElement('div');
  avatar.className = 'avatar ' + (isUser ? 'user' : 'ai');
  avatar.textContent = isUser ? 'YOU' : '識';

  const body = document.createElement('div');
  body.className = 'msg-body';

  const role = document.createElement('div');
  role.className = 'msg-role';
  role.textContent = isUser ? 'You' : 'JI';

  const content = document.createElement('div');
  content.className = 'content' + (thinking ? ' thinking' : '');

  if(thinking){
    content.innerHTML = '<span class="tdot"></span><span class="tdot"></span><span class="tdot"></span>';
  } else {
    content.textContent = text;
  }

  body.appendChild(role);
  body.appendChild(content);
  message.appendChild(avatar);
  message.appendChild(body);
  chat.appendChild(message);

  chat.scrollTop = chat.scrollHeight;

  return content;
}

function setStatus(text){
  const el = document.getElementById('statusText');
  if(el) el.textContent = text;
}

async function sendMessage(){
  const input = document.getElementById('input');
  const btn = document.getElementById('sendBtn');
  const text = input.value.trim();
  if(!text) return;

  addMessage(text, true);
  input.value = '';
  autoGrow(input);
  btn.disabled = true;
  setStatus('thinking');

  const thinkingEl = addMessage('', false, true);

  try{
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });

    const data = await response.json();

    thinkingEl.classList.remove('thinking');
    thinkingEl.textContent = data.reply;
    setStatus('idle');
  } catch(error){
    thinkingEl.classList.remove('thinking');
    thinkingEl.textContent = 'Something went wrong.';
    setStatus('offline');
  } finally {
    btn.disabled = false;
    document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
  }
}

function handleKey(event){
  if(event.key === 'Enter' && !event.shiftKey){
    event.preventDefault();
    sendMessage();
  }
}

async function newChat(){
  try{ await fetch('/reset', { method: 'POST' }); } catch(e){}

  const chat = document.getElementById('chat');
  while(chat.firstChild) chat.removeChild(chat.firstChild);
  addMessage('New conversation started.', false);
}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat_route():
    data = request.get_json()
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "Please say something."})

    messages.append({"role": "user", "content": user_message})

    try:
        response = chat(model=MODEL, messages=messages)
        reply = response.message.content.strip()

        messages.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as error:
        print(error)
        return jsonify({
            "reply": "I can't reach Ollama. Make sure Ollama is running."
        })


@app.route("/reset", methods=["POST"])
def reset_route():
    messages.clear()
    messages.append({"role": "system", "content": SYSTEM_PROMPT})
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print()
    print("================================")
    print("               JI")
    print("================================")
    print()
    print("Open:")
    print("http://127.0.0.1:5000")
    print()

    app.run(host="127.0.0.1", port=5000, debug=False)

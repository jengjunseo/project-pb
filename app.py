import os
import sqlite3
from flask import Flask, g, jsonify, request, render_template_string

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "project_pb.db")


HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Project PB</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&family=Pretendard:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --midnight: #050505;
      --glass: rgba(255, 255, 255, 0.05);
      --glass-soft: rgba(255, 255, 255, 0.03);
      --text-main: rgba(241, 245, 249, 0.96);
      --text-muted: rgba(148, 163, 184, 0.68);
      --cyan: #22d3ee;
      --violet: #8b5cf6;
      --danger: #fda4af;
      --ok: #67e8f9;
      --ease: cubic-bezier(.22, .61, .36, 1);
      --super-ellipse: 34px;
      --panel-w: min(920px, 100%);
    }

    * {
      box-sizing: border-box;
    }

    html, body {
      margin: 0;
      min-height: 100%;
      color: var(--text-main);
      background: var(--midnight);
      overflow: hidden;
      font-family: "Geist Mono", "Pretendard", "SF Pro Text", "Apple SD Gothic Neo", monospace;
      letter-spacing: -0.018em;
    }

    body::before {
      content: "";
      position: fixed;
      inset: -20%;
      z-index: 0;
      pointer-events: none;
      background:
        radial-gradient(42% 38% at 16% 22%, rgba(34, 211, 238, 0.20), transparent 72%),
        radial-gradient(35% 32% at 82% 18%, rgba(139, 92, 246, 0.24), transparent 72%),
        radial-gradient(34% 40% at 70% 82%, rgba(34, 211, 238, 0.14), transparent 74%),
        linear-gradient(150deg, #050505, #0a0a0f 44%, #0b0f17);
      filter: saturate(110%) blur(4px);
      animation: meshFlow 30s linear infinite alternate;
    }

    body::after {
      content: "";
      position: fixed;
      inset: 0;
      z-index: 0;
      pointer-events: none;
      background:
        linear-gradient(to right, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.028) 1px, transparent 1px);
      background-size: 112px 112px;
      opacity: 0.22;
      mask-image: radial-gradient(circle at center, black 54%, transparent 100%);
    }

    .noise {
      position: fixed;
      inset: 0;
      z-index: 1;
      pointer-events: none;
      opacity: 0.08;
      background-image: radial-gradient(rgba(255, 255, 255, 0.8) 0.45px, transparent 0.45px);
      background-size: 2.4px 2.4px;
      mix-blend-mode: soft-light;
    }

    @keyframes meshFlow {
      0% { transform: translate3d(-1.8%, -1.1%, 0) scale(1.02); }
      50% { transform: translate3d(2%, 1.4%, 0) scale(1.06); }
      100% { transform: translate3d(-1.2%, 1.9%, 0) scale(1.04); }
    }

    .app-shell {
      position: relative;
      z-index: 2;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 26px;
    }

    .panel {
      width: var(--panel-w);
      border-radius: var(--super-ellipse);
      border: 1px solid rgba(255, 255, 255, 0.08);
      background:
        linear-gradient(150deg, rgba(255, 255, 255, 0.085), rgba(255, 255, 255, 0.02)),
        var(--glass-soft);
      backdrop-filter: blur(20px) saturate(150%);
      -webkit-backdrop-filter: blur(20px) saturate(150%);
      padding: 30px 30px 24px;
      display: grid;
      gap: 20px;
      filter:
        drop-shadow(0 24px 62px rgba(0, 0, 0, 0.72))
        drop-shadow(0 0 22px rgba(34, 211, 238, 0.10));
      position: relative;
      isolation: isolate;
    }

    .panel::before {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: inherit;
      pointer-events: none;
      border: 1px solid transparent;
      background:
        linear-gradient(120deg, rgba(34, 211, 238, 0.34), transparent 36%, transparent 66%, rgba(139, 92, 246, 0.36)) border-box;
      -webkit-mask:
        linear-gradient(#fff 0 0) padding-box,
        linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      opacity: 0.78;
    }

    .reveal {
      opacity: 0;
      transform: translateY(22px);
      animation: riseIn 720ms var(--ease) forwards;
    }

    .d1 { animation-delay: 100ms; }
    .d2 { animation-delay: 190ms; }
    .d3 { animation-delay: 280ms; }
    .d4 { animation-delay: 360ms; }

    @keyframes riseIn {
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .header {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: baseline;
    }

    .title {
      margin: 0;
      font-size: clamp(1rem, 1.8vw, 1.22rem);
      font-weight: 500;
      letter-spacing: -0.02em;
    }

    .subtitle {
      margin: 0;
      color: var(--text-muted);
      font-size: 0.82rem;
    }

    .slot-wrap {
      display: grid;
      justify-items: center;
      gap: 8px;
      position: relative;
      padding: 4px 0 10px;
    }

    .slot-input {
      width: min(420px, 88%);
      text-align: center;
      font-size: clamp(3rem, 11vw, 7.6rem);
      font-weight: 600;
      line-height: 1;
      color: rgba(236, 253, 255, 0.95);
      background: transparent;
      border: none;
      outline: none;
      padding: 0;
      letter-spacing: -0.06em;
      caret-color: rgba(34, 211, 238, 0.9);
      text-shadow: 0 0 18px rgba(34, 211, 238, 0.17);
    }

    .slot-glow {
      width: min(420px, 88%);
      height: 2px;
      border-radius: 999px;
      background: linear-gradient(90deg, transparent 4%, rgba(34, 211, 238, 0.65) 50%, transparent 96%);
      opacity: 0.17;
      transition: opacity 260ms var(--ease), filter 260ms var(--ease);
      filter: blur(0.6px);
    }

    .slot-input:focus + .slot-glow {
      opacity: 0.98;
      filter: blur(2px) drop-shadow(0 0 14px rgba(34, 211, 238, 0.45));
    }

    .paste-area {
      width: 100%;
      min-height: 43vh;
      resize: vertical;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: calc(var(--super-ellipse) - 10px);
      background: linear-gradient(170deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
      color: rgba(237, 245, 255, 0.93);
      padding: 18px 20px;
      line-height: 1.62;
      font-size: 0.96rem;
      letter-spacing: -0.01em;
      outline: none;
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      filter:
        drop-shadow(0 16px 26px rgba(0, 0, 0, 0.45))
        drop-shadow(0 0 16px rgba(139, 92, 246, 0.08));
      transition: border-color 180ms var(--ease), filter 180ms var(--ease);
      scrollbar-width: thin;
      scrollbar-color: rgba(34, 211, 238, 0.26) transparent;
    }

    .paste-area:focus {
      border-color: rgba(34, 211, 238, 0.34);
      filter:
        drop-shadow(0 20px 28px rgba(0, 0, 0, 0.52))
        drop-shadow(0 0 20px rgba(34, 211, 238, 0.16));
    }

    .paste-area::-webkit-scrollbar {
      width: 6px;
    }

    .paste-area::-webkit-scrollbar-track {
      background: transparent;
    }

    .paste-area::-webkit-scrollbar-thumb {
      background: linear-gradient(180deg, rgba(34, 211, 238, 0.32), rgba(139, 92, 246, 0.28));
      border-radius: 999px;
    }

    .actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }

    .btn {
      border: none;
      color: rgba(236, 248, 255, 0.96);
      background: rgba(255, 255, 255, 0.04);
      border-radius: 999px;
      height: 44px;
      padding: 0 18px;
      cursor: pointer;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-size: 0.74rem;
      font-weight: 600;
      font-family: inherit;
      position: relative;
      overflow: hidden;
      transition: transform 160ms var(--ease), filter 200ms var(--ease), background-color 200ms var(--ease);
      filter:
        drop-shadow(0 10px 16px rgba(0, 0, 0, 0.44))
        drop-shadow(0 0 12px rgba(34, 211, 238, 0.09));
    }

    .btn::before {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: inherit;
      border: 1px solid transparent;
      background: linear-gradient(120deg, rgba(34, 211, 238, 0.52), rgba(139, 92, 246, 0.52)) border-box;
      -webkit-mask:
        linear-gradient(#fff 0 0) padding-box,
        linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      opacity: 0.92;
      pointer-events: none;
    }

    .btn:hover {
      transform: translateY(-1px);
      background: rgba(255, 255, 255, 0.07);
    }

    .btn:active {
      transform: translateY(0) scale(0.987);
    }

    .btn-label {
      display: inline-block;
      transition: transform 240ms var(--ease), opacity 240ms var(--ease), filter 240ms var(--ease);
    }

    .save-burst .btn-label {
      animation: textBurst 520ms var(--ease);
    }

    @keyframes textBurst {
      0% {
        transform: translateY(0) scale(1);
        opacity: 1;
        filter: blur(0);
      }
      32% {
        transform: translateY(-2px) scale(1.03);
        opacity: 0.42;
        filter: blur(1.2px);
      }
      58% {
        transform: translateY(1px) scale(0.98);
        opacity: 0.55;
        filter: blur(0.7px);
      }
      100% {
        transform: translateY(0) scale(1);
        opacity: 1;
        filter: blur(0);
      }
    }

    .footer {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      color: var(--text-muted);
      font-size: 0.78rem;
      letter-spacing: -0.008em;
    }

    .status {
      min-height: 1.3em;
      transition: color 180ms var(--ease), opacity 180ms var(--ease);
    }

    .status.ok { color: var(--ok); }
    .status.err { color: var(--danger); }

    .pulse {
      animation: tapPulse 220ms var(--ease);
    }

    @keyframes tapPulse {
      0% { transform: scale(1); }
      40% { transform: scale(0.986); }
      100% { transform: scale(1); }
    }

    @media (max-width: 760px) {
      html, body { overflow-y: auto; }

      .panel {
        padding: 22px 18px 18px;
        border-radius: 28px;
      }

      .footer {
        flex-direction: column;
        align-items: flex-start;
      }

      .paste-area {
        min-height: 46vh;
      }
    }
  </style>
</head>
<body>
  <div class="noise"></div>
  <main class="app-shell">
    <section class="panel">
      <div class="header reveal d1">
        <h1 class="title">Project PB</h1>
        <p class="subtitle">Personal 2-Digit Pastebin</p>
      </div>

      <div class="slot-wrap reveal d2">
        <input id="slot" class="slot-input" maxlength="2" inputmode="numeric" pattern="[0-9]{2}" placeholder="00" />
        <div class="slot-glow"></div>
      </div>

      <textarea id="content" class="paste-area reveal d3" placeholder="텍스트를 입력하세요..."></textarea>

      <div class="actions reveal d4">
        <button id="loadBtn" class="btn btn-load" type="button"><span class="btn-label">Load</span></button>
        <button id="saveBtn" class="btn btn-save" type="button"><span class="btn-label">Save</span></button>
      </div>

      <div class="footer reveal d4">
        <span>00~99 슬롯 주소 시스템</span>
        <span id="status" class="status">Ready</span>
      </div>
    </section>
  </main>

  <script>
    const slotInput = document.getElementById("slot");
    const contentArea = document.getElementById("content");
    const loadBtn = document.getElementById("loadBtn");
    const saveBtn = document.getElementById("saveBtn");
    const statusEl = document.getElementById("status");

    function normalizeSlot(raw) {
      const digits = (raw || "").replace(/\\D/g, "").slice(0, 2);
      if (digits.length === 0) return "";
      return digits.padStart(2, "0");
    }

    function validSlot(slot) {
      return /^\\d{2}$/.test(slot);
    }

    function setStatus(message, type = "") {
      statusEl.textContent = message;
      statusEl.className = "status " + type;
    }

    function microFeedback(target) {
      target.classList.remove("pulse");
      void target.offsetWidth;
      target.classList.add("pulse");
    }

    async function loadSlot() {
      const slot = normalizeSlot(slotInput.value);
      slotInput.value = slot;

      if (!validSlot(slot)) {
        setStatus("슬롯은 00~99 두 자리 숫자여야 합니다.", "err");
        return;
      }

      microFeedback(loadBtn);
      setStatus("불러오는 중...");

      try {
        const res = await fetch(`/api/paste/${slot}`);
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Load failed");
        contentArea.value = data.content || "";
        setStatus(`슬롯 ${slot} 불러오기 완료`, "ok");
      } catch (err) {
        setStatus(err.message || "불러오기 실패", "err");
      }
    }

    async function saveSlot() {
      const slot = normalizeSlot(slotInput.value);
      slotInput.value = slot;

      if (!validSlot(slot)) {
        setStatus("슬롯은 00~99 두 자리 숫자여야 합니다.", "err");
        return;
      }

      microFeedback(saveBtn);
      saveBtn.classList.remove("save-burst");
      void saveBtn.offsetWidth;
      saveBtn.classList.add("save-burst");
      setTimeout(() => saveBtn.classList.remove("save-burst"), 540);
      setStatus("저장 중...");

      try {
        const res = await fetch(`/api/paste/${slot}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: contentArea.value })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Save failed");
        setStatus(`슬롯 ${slot} 저장 완료`, "ok");
      } catch (err) {
        setStatus(err.message || "저장 실패", "err");
      }
    }

    slotInput.addEventListener("input", () => {
      slotInput.value = normalizeSlot(slotInput.value);
    });

    slotInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        loadSlot();
      }
    });

    loadBtn.addEventListener("click", loadSlot);
    saveBtn.addEventListener("click", saveSlot);
  </script>
</body>
</html>
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def normalize_slot(slot_value: str):
    if slot_value is None:
        return None
    if not slot_value.isdigit():
        return None
    slot_num = int(slot_value)
    if slot_num < 0 or slot_num > 99:
        return None
    return f"{slot_num:02d}"


def init_db():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pastes (
            slot TEXT PRIMARY KEY,
            content TEXT NOT NULL DEFAULT ''
        )
        """
    )
    cursor.executemany(
        "INSERT OR IGNORE INTO pastes (slot, content) VALUES (?, '')",
        [(f"{i:02d}",) for i in range(100)],
    )
    db.commit()
    db.close()


@app.teardown_appcontext
def close_db(_exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.get("/")
def index():
    return render_template_string(HTML)


@app.get("/api/paste/<slot>")
def get_paste(slot):
    normalized = normalize_slot(slot)
    if normalized is None:
        return jsonify({"error": "slot must be 00-99"}), 400

    db = get_db()
    row = db.execute("SELECT content FROM pastes WHERE slot = ?", (normalized,)).fetchone()
    if row is None:
        return jsonify({"error": "slot not found"}), 404

    return jsonify({"slot": normalized, "content": row["content"]})


@app.post("/api/paste/<slot>")
def save_paste(slot):
    normalized = normalize_slot(slot)
    if normalized is None:
        return jsonify({"error": "slot must be 00-99"}), 400

    payload = request.get_json(silent=True) or {}
    content = payload.get("content", "")
    if not isinstance(content, str):
        return jsonify({"error": "content must be string"}), 400

    db = get_db()
    db.execute("UPDATE pastes SET content = ? WHERE slot = ?", (content, normalized))
    db.commit()
    return jsonify({"ok": True, "slot": normalized})


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

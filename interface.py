import gradio as gr
from llm import generate_command
from sandbox import run_in_sandbox

# ===================================================================
# קבועים
# ===================================================================

TEXTS = {
    "HE": {
        "run_safe":    "▶  הרץ — בטוח להרצה",
        "run_warning": "⚠  הרץ — בדוק לפני הרצה",
        "run_danger":  "🔴  מסוכן — אשר כדי להרץ",
        "run_error":   "🚫  חסום — פקודה לא חוקית",
        "run_default": "▶  הרץ ב-Docker Sandbox",
        "checkbox":    "אני מודע לסיכון ומאשר הרצה",
        "blocked_msg": "⛔ הרצה חסומה — הפקודה לא חוקית.",
        "no_cmd":      "⚠️ אין פקודה להרצה.",
        "blocked_exit":"❌  Blocked",
    },
    "EN": {
        "run_safe":    "▶  Run — Safe to execute",
        "run_warning": "⚠  Run — Proceed with caution",
        "run_danger":  "🔴  Dangerous — Confirm to run",
        "run_error":   "🚫  Blocked — Invalid command",
        "run_default": "▶  Run in Docker Sandbox",
        "checkbox":    "I acknowledge the risk and confirm",
        "blocked_msg": "⛔ Blocked — this command is not allowed.",
        "no_cmd":      "⚠️ No command to run.",
        "blocked_exit":"❌  Blocked",
    },
}

LEVEL_VARIANTS = {
    "SAFE":    ("primary",   True),
    "WARNING": ("secondary", True),
    "DANGER":  ("stop",      False),
    "ERROR":   ("stop",      False),
}

LEVEL_COLORS = {
    "SAFE":    "#63ffb4",
    "WARNING": "#ffd580",
    "DANGER":  "#e06c75",
    "ERROR":   "#7a3038",
}

# ===================================================================
# פונקציות עזר
# ===================================================================

def t(lang: str, key: str) -> str:
    """מחזיר טקסט לפי שפה — fallback לאנגלית."""
    return TEXTS.get(lang, TEXTS["EN"]).get(key, TEXTS["EN"][key])


def parse_response(raw: str) -> tuple[str, str, str]:
    """
    מפרסר תשובת GPT מהפורמט LEVEL|LANG: command.
    מחזיר (level, lang, command).
    """
    try:
        prefix, command = raw.split(":", 1)
        level, lang = prefix.strip().split("|")
        return level.strip(), lang.strip(), command.strip()
    except Exception:
        return "SAFE", "EN", raw.strip()


def make_risk_indicator(level: str) -> str:
    """בונה HTML badge של רמת הסיכון."""
    color = LEVEL_COLORS.get(level, "#63ffb4")
    return f"""
    <div style="
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        color: {color};
        border: 1.5px solid {color};
        border-radius: 8px;
        padding: 7px 14px;
        display: inline-block;
        margin-bottom: 6px;
    ">● {level}</div>
    """

# ===================================================================
# handlers
# ===================================================================

def handle_generate(user_input: str):
    """שולחת טקסט ל-GPT, מפרסרת, ומחזירה עדכוני UI."""
    if not user_input.strip():
        return (
            "", "SAFE", "EN",
            gr.update(value=t("EN", "run_default"), variant="secondary", interactive=False),
            gr.update(visible=False, value=False),
            gr.update(value=""),
        )

    level, lang, command = parse_response(generate_command(user_input))
    variant, interactive = LEVEL_VARIANTS.get(level, ("secondary", False))

    return (
        command,
        level,
        lang,
        gr.update(value=t(lang, f"run_{level.lower()}"), variant=variant, interactive=interactive),
        gr.update(visible=(level == "DANGER"), value=False, label=t(lang, "checkbox")),
        gr.update(value=make_risk_indicator(level)),
    )


def handle_checkbox(checked: bool, level: str, lang: str):
    """מפעיל/מכבה כפתור Run לפי מצב ה-checkbox."""
    if level != "DANGER":
        return gr.update()
    return gr.update(
        value=t(lang, "run_danger"),
        variant="stop",
        interactive=checked,
    )


def handle_run(command: str, level: str, lang: str) -> tuple[str, str, str]:
    """מריץ פקודה ב-sandbox ומחזיר תוצאות."""
    if not command.strip():
        return "", t(lang, "no_cmd"), ""
    if level == "ERROR":
        return "", t(lang, "blocked_msg"), t(lang, "blocked_exit")

    result = run_in_sandbox(command)
    exit_display = "✅  0 — Success" if result.exit_code == 0 else f"❌  {result.exit_code} — Failed"
    return result.stdout, result.stderr, exit_display


def handle_clear():
    """מאפס את כל שדות הממשק."""
    return (
        "", "",
        "SAFE", "EN",
        gr.update(value="▶  Run in Docker Sandbox", variant="secondary", interactive=False),
        gr.update(visible=False, value=False),
        gr.update(value=""),
        "", "", "",
    )

# ===================================================================
# CSS
# ===================================================================

CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');

* { box-sizing: border-box; }

body, .gradio-container {
    background: #0a0b0f !important;
    font-family: 'JetBrains Mono', sans-serif !important;
}

/* רשת רקע עדינה */
.gradio-container::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(99,255,180,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,255,180,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

.main-card {
    background: #0f1117;
    border: 1px solid #1e2130;
    border-radius: 16px;
    padding: 36px 40px 40px;
    max-width: 860px;
    margin: 40px auto;
    box-shadow: 0 0 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(99,255,180,0.04);
    position: relative;
    z-index: 1;
}

/* כותרת */
.header-wrap { margin-bottom: 32px; }
.header-wrap h1 {
    font-family: 'JetBrains Mono', sans-serif !important;
    font-weight: 700 !important;
    font-size: 2rem !important;
    color: #f0f4ff !important;
    margin: 0 0 6px !important;
    letter-spacing: -0.5px;
}
.header-wrap p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    color: #4a5568 !important;
    margin: 0 !important;
}
.accent { color: #63ffb4 !important; }

/* תוויות קטנות */
.section-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #3a4455 !important;
    margin-bottom: 8px !important;
}

/* תיבות טקסט */
textarea, input[type="text"] {
    background: #080a0e !important;
    border: 1px solid #1a1f2e !important;
    border-radius: 10px !important;
    color: #c9d1e0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s ease !important;
    resize: none !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: #63ffb4 !important;
    box-shadow: 0 0 0 3px rgba(99,255,180,0.08) !important;
    outline: none !important;
}

/* תיבת פקודה */
#command-box textarea {
    background: #0c1a14 !important;
    border-color: #1a3328 !important;
    color: #63ffb4 !important;
    font-size: 0.95rem !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* תיבות פלט */
#stdout-box textarea { color: #a8c5a0 !important; }
#stderr-box textarea { color: #e06c75 !important; }
#exit-box textarea {
    color: #ffd580 !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
}

/* כפתורים — בסיס */
button.lg {
    font-family: 'JetBrains Mono', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    border-radius: 10px !important;
    padding: 13px 24px !important;
    transition: all 0.22s ease !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
    border: none !important;
}

/* Generate */
#gen-btn {
    background: linear-gradient(135deg, #63ffb4, #00d4aa) !important;
    color: #050708 !important;
    box-shadow: 0 4px 20px rgba(99,255,180,0.25) !important;
}
#gen-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(99,255,180,0.38) !important;
}

/* Run — SAFE */
#run-btn.primary {
    background: transparent !important;
    color: #63ffb4 !important;
    border: 1.5px solid #63ffb4 !important;
    box-shadow: 0 0 18px rgba(99,255,180,0.1) !important;
}
#run-btn.primary:hover:not(:disabled) {
    background: rgba(99,255,180,0.07) !important;
    transform: translateY(-1px) !important;
}

/* Run — WARNING */
#run-btn.secondary {
    background: transparent !important;
    color: #ffd580 !important;
    border: 1.5px solid #ffd580 !important;
    box-shadow: 0 0 18px rgba(255,213,128,0.08) !important;
}
#run-btn.secondary:hover:not(:disabled) {
    background: rgba(255,213,128,0.07) !important;
    transform: translateY(-1px) !important;
}

/* Run — DANGER / ERROR */
#run-btn.stop {
    background: transparent !important;
    color: #e06c75 !important;
    border: 1.5px solid #e06c75 !important;
    box-shadow: 0 0 18px rgba(224,108,117,0.08) !important;
}
#run-btn.stop:hover:not(:disabled) {
    background: rgba(224,108,117,0.07) !important;
    transform: translateY(-1px) !important;
}

/* Disabled */
#run-btn:disabled {
    opacity: 0.32 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* Checkbox */
#confirm-checkbox {
    background: rgba(224,108,117,0.05) !important;
    border: 1.5px solid rgba(224,108,117,0.28) !important;
    border-radius: 10px !important;
    padding: 11px 16px !important;
    margin: 2px 0 !important;
}
#confirm-checkbox label {
    color: #e06c75 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}

/* Clear */
#clear-btn {
    background: transparent !important;
    color: #2d3748 !important;
    border: 1px solid #1a1f2e !important;
}
#clear-btn:hover {
    color: #e06c75 !important;
    border-color: rgba(224,108,117,0.35) !important;
}

.divider {
    border: none;
    border-top: 1px solid #1a1f2e;
    margin: 28px 0;
}

textarea::-webkit-scrollbar { width: 4px; }
textarea::-webkit-scrollbar-track { background: transparent; }
textarea::-webkit-scrollbar-thumb { background: #1e2130; border-radius: 4px; }
"""

# ===================================================================
# ממשק
# ===================================================================

def build_interface() -> gr.Blocks:

    with gr.Blocks(css=CSS, title="NL → Terminal") as demo:

        level_state = gr.State("SAFE")
        lang_state  = gr.State("EN")

        with gr.Column(elem_classes="main-card"):

            with gr.Column(elem_classes="header-wrap"):
                gr.HTML("""
                    <h1>NL <span class="accent">→</span> Terminal</h1>
                    <p>// natural language to shell command — powered by gpt-4o + docker sandbox</p>
                """)

            gr.HTML('<div class="section-label">What do you want to do?</div>')
            user_input = gr.Textbox(
                placeholder="e.g. show disk usage  /  הצג שימוש בדיסק",
                lines=2, show_label=False,
            )

            gen_btn = gr.Button("⚡  Generate Command", elem_id="gen-btn")

            gr.HTML('<div class="section-label" style="margin-top:20px">Generated Command</div>')
            command_box = gr.Textbox(
                lines=2, interactive=True, show_label=False,
                elem_id="command-box",
                placeholder="command will appear here...",
            )

            risk_indicator = gr.HTML(value="")

            confirm_checkbox = gr.Checkbox(
                label="I acknowledge the risk and confirm",
                value=False, visible=False,
                elem_id="confirm-checkbox",
            )

            run_btn = gr.Button(
                "▶  Run in Docker Sandbox",
                elem_id="run-btn",
                variant="secondary",
                interactive=False,
            )

            gr.HTML('<hr class="divider">')
            gr.HTML('<div class="section-label">Results</div>')

            with gr.Row():
                stdout_box = gr.Textbox(label="Output", lines=8, elem_id="stdout-box")
                stderr_box = gr.Textbox(label="Errors", lines=8, elem_id="stderr-box")

            exit_box  = gr.Textbox(label="Exit Code", lines=1, elem_id="exit-box")
            clear_btn = gr.Button("✕  Clear All", elem_id="clear-btn")

        # ── Wiring ──

        gen_btn.click(
            fn=handle_generate,
            inputs=user_input,
            outputs=[command_box, level_state, lang_state, run_btn, confirm_checkbox, risk_indicator],
        )

        confirm_checkbox.change(
            fn=handle_checkbox,
            inputs=[confirm_checkbox, level_state, lang_state],
            outputs=run_btn,
        )

        run_btn.click(
            fn=handle_run,
            inputs=[command_box, level_state, lang_state],
            outputs=[stdout_box, stderr_box, exit_box],
        )

        clear_btn.click(
            fn=handle_clear,
            outputs=[
                user_input, command_box,
                level_state, lang_state,
                run_btn, confirm_checkbox,
                risk_indicator,
                stdout_box, stderr_box, exit_box,
            ],
        )

    return demo
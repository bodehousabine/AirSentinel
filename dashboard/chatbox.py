"""
chatbox.py — AirSentinel Cameroun
Chatbox IA flottante en bas à droite.
Utilise l'API Claude pour proposer des solutions aux problèmes saisis.
"""
import streamlit as st
import streamlit.components.v1 as components
from themes import get_theme
from translations import get_t


def render_chatbox():
    """
    Injecte la chatbox flottante IA dans la page.
    Le chatbox utilise l'API Anthropic via fetch côté client.
    """
    th   = get_theme(st.session_state.get("theme_name", "dark"))
    lang = st.session_state.get("lang", "fr")

    placeholder = (
        "Décrivez votre préoccupation..." if lang == "fr"
        else "Describe your concern..."
    )
    tooltip = (
        "Avez-vous une préoccupation ?" if lang == "fr"
        else "Do you have a concern?"
    )
    send_label = "Envoyer" if lang == "fr" else "Send"
    title      = "Assistant AirSentinel" if lang == "fr" else "AirSentinel Assistant"
    close_label= "✕"
    thinking   = "En cours de réflexion..." if lang == "fr" else "Thinking..."

    system_prompt_fr = """Tu es l'assistant IA d'AirSentinel Cameroun, un système de surveillance de la qualité de l'air et d'aide à la décision sanitaire.

Ton rôle : proposer des solutions concrètes, pratiques et adaptées au contexte camerounais et africain pour tout problème soumis par l'utilisateur.

Les problèmes peuvent concerner :
- La qualité de l'air (PM2.5, harmattan, feux de brousse, pollution urbaine)
- La santé publique (maladies respiratoires, asthme, populations vulnérables)
- La prise de décision (hôpitaux, mairies, gouvernement, ONG)
- Les données et modèles (statistiques, prédictions, IRS)

Réponds toujours en français si l'utilisateur écrit en français.
Sois concis (3-5 points maximum), pratique, et ancré dans le contexte africain.
Commence chaque solution par un emoji et un verbe d'action."""

    system_prompt_en = """You are the AI assistant for AirSentinel Cameroon, an air quality monitoring and health decision support system.

Your role: propose concrete, practical solutions adapted to the Cameroonian and African context for any problem submitted by the user.

Problems may concern:
- Air quality (PM2.5, harmattan, bushfires, urban pollution)
- Public health (respiratory diseases, asthma, vulnerable populations)
- Decision-making (hospitals, municipalities, government, NGOs)
- Data and models (statistics, predictions, HRI)

Always respond in English if the user writes in English.
Be concise (3-5 points maximum), practical, and grounded in the African context.
Start each solution with an emoji and an action verb."""

    system_prompt = system_prompt_fr if lang == "fr" else system_prompt_en

    # Couleurs selon thème
    is_dark = th["name"] == "dark"
    bg_chat      = "#0a2845" if is_dark else "#ffffff"
    bg_header    = "#071e35" if is_dark else "#e8f4fd"
    bg_input     = "#071e35" if is_dark else "#f0f7ff"
    text_color   = "#e0f2fe" if is_dark else "#0a1f33"
    text2_color  = "#7fb8d4" if is_dark else "#1a4a6e"
    border_color = "rgba(14,165,233,0.25)" if is_dark else "rgba(10,60,120,0.20)"
    msg_user_bg  = "#00d4b1" if is_dark else "#0ea5e9"
    msg_bot_bg   = "#0f2d4a" if is_dark else "#e1effe"
    msg_bot_text = "#e0f2fe" if is_dark else "#0a1f33"

    components.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{ font-family: 'Inter', 'Segoe UI', sans-serif; }}

  /* ── Bouton flottant ── */
  #chat-toggle {{
    position: fixed;
    bottom: 28px;
    right: 28px;
    width: 58px;
    height: 58px;
    border-radius: 50%;
    background: linear-gradient(135deg, #00d4b1 0%, #0ea5e9 100%);
    border: none;
    cursor: pointer;
    box-shadow: 0 6px 28px rgba(0,212,177,0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    z-index: 99999;
    transition: transform .2s, box-shadow .2s;
  }}
  #chat-toggle:hover {{
    transform: scale(1.08) translateY(-2px);
    box-shadow: 0 10px 36px rgba(0,212,177,0.60);
  }}

  /* ── Tooltip ── */
  #chat-tooltip {{
    position: fixed;
    bottom: 96px;
    right: 28px;
    background: {bg_chat};
    color: {text_color};
    border: 1px solid {border_color};
    border-radius: 10px;
    padding: 9px 14px;
    font-size: 13px;
    font-weight: 500;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    z-index: 99998;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    transition: opacity .25s;
  }}
  #chat-tooltip::after {{
    content: '';
    position: absolute;
    bottom: -6px;
    right: 20px;
    width: 12px;
    height: 12px;
    background: {bg_chat};
    border-right: 1px solid {border_color};
    border-bottom: 1px solid {border_color};
    transform: rotate(45deg);
  }}
  #chat-toggle:hover + #chat-tooltip,
  #chat-toggle.hovered + #chat-tooltip {{
    opacity: 1;
  }}

  /* ── Fenêtre chat ── */
  #chat-window {{
    position: fixed;
    bottom: 100px;
    right: 28px;
    width: 360px;
    max-height: 520px;
    background: {bg_chat};
    border: 1px solid {border_color};
    border-radius: 16px;
    box-shadow: 0 16px 56px rgba(0,0,0,0.35);
    display: none;
    flex-direction: column;
    z-index: 99997;
    overflow: hidden;
  }}
  #chat-window.open {{
    display: flex;
    animation: slideUp .25s ease;
  }}
  @keyframes slideUp {{
    from {{ opacity:0; transform:translateY(16px); }}
    to   {{ opacity:1; transform:translateY(0);    }}
  }}

  /* Header */
  #chat-header {{
    background: {bg_header};
    padding: 14px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid {border_color};
    flex-shrink: 0;
  }}
  #chat-header-left {{
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  #chat-avatar {{
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #00d4b1, #0ea5e9);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
  }}
  #chat-title {{
    font-size: 14px;
    font-weight: 600;
    color: {text_color};
  }}
  #chat-status {{
    font-size: 11px;
    color: #00d4b1;
    margin-top: 1px;
  }}
  #chat-close {{
    background: none;
    border: none;
    color: {text2_color};
    font-size: 18px;
    cursor: pointer;
    padding: 4px 6px;
    border-radius: 6px;
    transition: background .15s;
  }}
  #chat-close:hover {{ background: rgba(255,255,255,0.1); }}

  /* Messages */
  #chat-messages {{
    flex: 1;
    overflow-y: auto;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    scroll-behavior: smooth;
  }}
  #chat-messages::-webkit-scrollbar {{ width: 4px; }}
  #chat-messages::-webkit-scrollbar-thumb {{
    background: rgba(0,212,177,0.3);
    border-radius: 2px;
  }}

  .msg {{ display:flex; flex-direction:column; max-width:85%; }}
  .msg.user  {{ align-self: flex-end; align-items: flex-end; }}
  .msg.bot   {{ align-self: flex-start; align-items: flex-start; }}

  .msg-bubble {{
    padding: 10px 13px;
    border-radius: 12px;
    font-size: 13px;
    line-height: 1.6;
    word-break: break-word;
  }}
  .msg.user .msg-bubble {{
    background: {msg_user_bg};
    color: #020c18;
    font-weight: 500;
    border-bottom-right-radius: 4px;
  }}
  .msg.bot .msg-bubble {{
    background: {msg_bot_bg};
    color: {msg_bot_text};
    border-bottom-left-radius: 4px;
    border: 1px solid {border_color};
  }}
  .msg-time {{
    font-size: 10px;
    color: {text2_color};
    margin-top: 3px;
    opacity: 0.7;
  }}

  /* Indicateur de frappe */
  .typing .msg-bubble {{ background:{msg_bot_bg}; border:1px solid {border_color}; }}
  .dot {{ display:inline-block; width:6px; height:6px; border-radius:50%;
          background:{text2_color}; margin:0 2px; animation:bounce .9s infinite; }}
  .dot:nth-child(2) {{ animation-delay:.2s; }}
  .dot:nth-child(3) {{ animation-delay:.4s; }}
  @keyframes bounce {{ 0%,80%,100%{{transform:translateY(0)}} 40%{{transform:translateY(-6px)}} }}

  /* Zone de saisie */
  #chat-input-area {{
    padding: 12px 14px;
    border-top: 1px solid {border_color};
    background: {bg_header};
    flex-shrink: 0;
  }}
  #chat-input-row {{
    display: flex;
    gap: 8px;
    align-items: flex-end;
  }}
  #chat-input {{
    flex: 1;
    background: {bg_input};
    border: 1px solid {border_color};
    border-radius: 10px;
    padding: 10px 13px;
    font-size: 13px;
    color: {text_color};
    resize: none;
    outline: none;
    font-family: inherit;
    max-height: 100px;
    transition: border-color .15s;
  }}
  #chat-input::placeholder {{ color: {text2_color}; opacity:0.7; }}
  #chat-input:focus {{ border-color: rgba(0,212,177,0.5); }}
  #chat-send {{
    background: linear-gradient(135deg, #00d4b1, #0ea5e9);
    border: none;
    border-radius: 10px;
    width: 40px;
    height: 40px;
    cursor: pointer;
    color: #020c18;
    font-size: 16px;
    flex-shrink: 0;
    transition: opacity .15s, transform .15s;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  #chat-send:hover {{ opacity:.88; transform:scale(1.05); }}
  #chat-send:disabled {{ opacity:.4; cursor:default; transform:none; }}
</style>
</head>
<body>

<button id="chat-toggle" onmouseenter="showTooltip()" onmouseleave="hideTooltip()">💬</button>
<div id="chat-tooltip">{tooltip}</div>

<div id="chat-window">
  <div id="chat-header">
    <div id="chat-header-left">
      <div id="chat-avatar">🌍</div>
      <div>
        <div id="chat-title">{title}</div>
        <div id="chat-status">● Online</div>
      </div>
    </div>
    <button id="chat-close" onclick="toggleChat()">{close_label}</button>
  </div>

  <div id="chat-messages">
    <div class="msg bot">
      <div class="msg-bubble" id="welcome-msg"></div>
    </div>
  </div>

  <div id="chat-input-area">
    <div id="chat-input-row">
      <textarea id="chat-input" rows="1"
        placeholder="{placeholder}"
        onkeydown="handleKey(event)"
        oninput="autoResize(this)"></textarea>
      <button id="chat-send" onclick="sendMessage()">➤</button>
    </div>
  </div>
</div>

<script>
const LANG = "{lang}";
const SYSTEM_PROMPT = `{system_prompt}`;
const THINKING_MSG  = "{thinking}";
const SEND_LABEL    = "{send_label}";

const welcome = LANG === "fr"
  ? "👋 Bonjour ! Je suis l'assistant IA d'AirSentinel.\\n\\nPosez-moi n'importe quelle question sur la qualité de l'air, la santé publique au Cameroun, ou les données de l'application. Je vous proposerai des solutions concrètes."
  : "👋 Hello! I am the AirSentinel AI assistant.\\n\\nAsk me any question about air quality, public health in Cameroon, or the app's data. I will provide concrete solutions.";

document.getElementById("welcome-msg").innerText = welcome;

let isOpen    = false;
let isLoading = false;
const history = [];

function toggleChat() {{
  isOpen = !isOpen;
  const w = document.getElementById("chat-window");
  if (isOpen) {{
    w.classList.add("open");
    document.getElementById("chat-input").focus();
  }} else {{
    w.classList.remove("open");
  }}
}}

function showTooltip() {{
  document.getElementById("chat-toggle").classList.add("hovered");
}}
function hideTooltip() {{
  document.getElementById("chat-toggle").classList.remove("hovered");
}}

document.getElementById("chat-toggle").addEventListener("click", toggleChat);

function autoResize(el) {{
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 100) + "px";
}}

function handleKey(e) {{
  if (e.key === "Enter" && !e.shiftKey) {{
    e.preventDefault();
    sendMessage();
  }}
}}

function getTime() {{
  return new Date().toLocaleTimeString([], {{hour:"2-digit", minute:"2-digit"}});
}}

function addMsg(role, text) {{
  const msgs = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "msg " + (role === "user" ? "user" : "bot");
  div.innerHTML = `
    <div class="msg-bubble">${{text.replace(/\\n/g,"<br>")}}</div>
    <div class="msg-time">${{getTime()}}</div>
  `;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}}

function addTyping() {{
  const msgs = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "msg bot typing";
  div.id = "typing-indicator";
  div.innerHTML = `<div class="msg-bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}}

function removeTyping() {{
  const t = document.getElementById("typing-indicator");
  if (t) t.remove();
}}

async function sendMessage() {{
  if (isLoading) return;
  const input = document.getElementById("chat-input");
  const text  = input.value.trim();
  if (!text) return;

  // Afficher message utilisateur
  addMsg("user", text);
  history.push({{ role: "user", content: text }});
  input.value = "";
  input.style.height = "auto";

  // Désactiver bouton + afficher typing
  isLoading = true;
  const btn = document.getElementById("chat-send");
  btn.disabled = true;
  addTyping();

  try {{
    const response = await fetch("https://api.anthropic.com/v1/messages", {{
      method: "POST",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{
        model: "claude-sonnet-4-20250514",
        max_tokens: 1000,
        system: SYSTEM_PROMPT,
        messages: history,
      }}),
    }});

    const data = await response.json();
    const reply = (data.content && data.content[0] && data.content[0].text)
      ? data.content[0].text
      : (LANG === "fr" ? "Désolé, une erreur s'est produite. Réessayez." : "Sorry, an error occurred. Please try again.");

    removeTyping();
    addMsg("bot", reply);
    history.push({{ role: "assistant", content: reply }});

  }} catch (err) {{
    removeTyping();
    const errMsg = LANG === "fr"
      ? "⚠️ Connexion impossible. Vérifiez votre connexion Internet."
      : "⚠️ Connection failed. Please check your internet connection.";
    addMsg("bot", errMsg);
  }}

  isLoading = false;
  btn.disabled = false;
  document.getElementById("chat-input").focus();
}}
</script>
</body>
</html>
""", height=0, scrolling=False)

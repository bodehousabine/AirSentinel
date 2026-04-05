"""
chatbox.py — AirSentinel Cameroun
Chatbox IA flottante. Backend Python (Anthropic SDK) via st.session_state.
Évite les problèmes CORS de l'appel direct navigateur→API.
"""
import streamlit as st
import streamlit.components.v1 as components
from themes import get_theme
from translations import get_t

# Import optionnel de l'SDK Anthropic
try:
    import anthropic as _anthropic_sdk
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False


def _call_claude(messages: list, system_prompt: str, lang: str) -> str:
    """Appelle l'API Claude via le SDK Python (pas de CORS)."""
    if not _SDK_AVAILABLE:
        return ("⚠️ SDK Anthropic non installé. Lancez : pip install anthropic"
                if lang == "fr" else
                "⚠️ Anthropic SDK not installed. Run: pip install anthropic")
    try:
        import os
        api_key = (
            st.secrets.get("ANTHROPIC_API_KEY", "")
            or os.environ.get("ANTHROPIC_API_KEY", "")
        )
        if not api_key:
            return ("⚠️ Clé API manquante. Ajoutez ANTHROPIC_API_KEY dans .streamlit/secrets.toml"
                    if lang == "fr" else
                    "⚠️ API key missing. Add ANTHROPIC_API_KEY in .streamlit/secrets.toml")

        client = _anthropic_sdk.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=900,
            system=system_prompt,
            messages=messages,
        )
        return resp.content[0].text if resp.content else "..."
    except Exception as e:
        err = str(e)[:120]
        return f"⚠️ Erreur API : {err}" if lang == "fr" else f"⚠️ API Error: {err}"


def render_chatbox():
    """Chatbox flottante IA — UI HTML + backend Python."""

    th   = get_theme(st.session_state.get("theme_name", "dark"))
    lang = st.session_state.get("lang", "fr")
    is_dark = th["name"] == "dark"

    # ── Traduction labels ────────────────────────────────────────────────────
    placeholder = "Décrivez votre préoccupation..." if lang == "fr" else "Describe your concern..."
    send_label  = "Envoyer" if lang == "fr" else "Send"
    title       = "Assistant AirSentinel" if lang == "fr" else "AirSentinel Assistant"
    thinking    = "En cours de réflexion..." if lang == "fr" else "Thinking..."
    tooltip     = "Avez-vous une préoccupation ?" if lang == "fr" else "Do you have a concern?"

    system_prompt = (
        """Tu es l'assistant IA d'AirSentinel Cameroun, système de surveillance de la qualité de l'air.
Rôle : proposer des solutions concrètes et adaptées au contexte camerounais.
Thèmes : qualité de l'air (PM2.5, harmattan, feux), santé publique, prise de décision, données et modèles.
Réponds en français. Sois concis (3-5 points). Commence chaque point par un emoji et un verbe d'action."""
        if lang == "fr" else
        """You are the AI assistant for AirSentinel Cameroon, an air quality monitoring system.
Role: propose concrete solutions adapted to the Cameroonian context.
Topics: air quality (PM2.5, harmattan, fires), public health, decision-making, data and models.
Reply in English. Be concise (3-5 points). Start each point with an emoji and an action verb."""
    )

    # ── Session state pour l'historique et l'UI ─────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "chat_open" not in st.session_state:
        st.session_state["chat_open"] = False
    if "_chat_input_val" not in st.session_state:
        st.session_state["_chat_input_val"] = ""
    if "_chat_pending" not in st.session_state:
        st.session_state["_chat_pending"] = None

    # Traiter un message en attente (soumis au tour précédent)
    if st.session_state["_chat_pending"]:
        user_msg = st.session_state["_chat_pending"]
        st.session_state["_chat_pending"] = None
        st.session_state["chat_history"].append({"role": "user", "content": user_msg})
        bot_reply = _call_claude(st.session_state["chat_history"], system_prompt, lang)
        st.session_state["chat_history"].append({"role": "assistant", "content": bot_reply})
        st.rerun()

    # ── Couleurs ─────────────────────────────────────────────────────────────
    bg_chat   = "#0a2845" if is_dark else "#ffffff"
    bg_header = "#071e35" if is_dark else "#dceefb"
    bg_input  = "#071e35" if is_dark else "#f0f7ff"
    txt       = "#e0f2fe" if is_dark else "#0a1f33"
    txt2      = "#7fb8d4" if is_dark else "#1a4a6e"
    brd       = "rgba(14,165,233,0.25)" if is_dark else "rgba(10,60,120,0.20)"
    usr_bg    = "#00d4b1"
    bot_bg    = "#0f2d4a" if is_dark else "#dff0ff"
    bot_txt   = "#e0f2fe" if is_dark else "#0a1f33"
    scroll_bg = "#051525" if is_dark else "#f0f7ff"

    # ── Construire le HTML des messages ─────────────────────────────────────
    def escape_html(s):
        return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")

    msgs_html = ""
    for m in st.session_state["chat_history"]:
        if m["role"] == "user":
            msgs_html += (
                f'<div style="display:flex;justify-content:flex-end;margin-bottom:10px;">'
                f'<div style="background:{usr_bg};color:#020c18;border-radius:16px 16px 4px 16px;'
                f'padding:9px 14px;max-width:80%;font-size:13px;line-height:1.5;">'
                f'{escape_html(m["content"])}</div></div>'
            )
        else:
            msgs_html += (
                f'<div style="display:flex;gap:8px;margin-bottom:10px;">'
                f'<div style="width:28px;height:28px;border-radius:50%;background:{usr_bg};'
                f'display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0;">🌍</div>'
                f'<div style="background:{bot_bg};color:{bot_txt};border-radius:4px 16px 16px 16px;'
                f'padding:9px 14px;max-width:80%;font-size:13px;line-height:1.55;">'
                f'{escape_html(m["content"])}</div></div>'
            )

    open_state = "flex" if st.session_state.get("chat_open") else "none"

    components.html(f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Inter',sans-serif;background:transparent;overflow:hidden;}}

#chat-fab{{
    position:fixed;bottom:24px;right:24px;
    width:52px;height:52px;border-radius:50%;
    background:linear-gradient(135deg,#00d4b1,#0ea5e9);
    cursor:pointer;display:flex;align-items:center;justify-content:center;
    font-size:22px;box-shadow:0 6px 24px rgba(0,212,177,0.45);
    border:none;z-index:99999;
    transition:transform .2s, box-shadow .2s;
    animation:pulse 2.5s infinite;
}}
#chat-fab:hover{{transform:scale(1.1);box-shadow:0 10px 32px rgba(0,212,177,0.60);}}
@keyframes pulse{{0%,100%{{box-shadow:0 6px 24px rgba(0,212,177,0.45);}}
                  50%{{box-shadow:0 6px 32px rgba(0,212,177,0.70);}}}}

#chat-window{{
    position:fixed;bottom:88px;right:24px;
    width:340px;height:480px;
    background:{bg_chat};border:1px solid {brd};
    border-radius:18px;display:{open_state};flex-direction:column;
    box-shadow:0 20px 60px rgba(0,0,0,0.35);z-index:99998;
    overflow:hidden;animation:slideUp .2s ease;
}}
@keyframes slideUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}

#chat-header{{
    background:{bg_header};padding:12px 16px;
    display:flex;align-items:center;justify-content:space-between;
    border-bottom:1px solid {brd};flex-shrink:0;
}}
#chat-header-left{{display:flex;align-items:center;gap:8px;}}
#chat-avatar{{width:32px;height:32px;border-radius:50%;background:#00d4b1;
    display:flex;align-items:center;justify-content:center;font-size:16px;}}
#chat-title{{font-size:13px;font-weight:600;color:{txt};}}
#chat-status{{font-size:10px;color:#00d4b1;}}
#chat-close{{background:none;border:none;color:{txt2};font-size:18px;
    cursor:pointer;padding:2px 6px;border-radius:6px;transition:background .15s;}}
#chat-close:hover{{background:rgba(255,255,255,0.1);}}

#chat-messages{{
    flex:1;overflow-y:auto;padding:14px;
    background:{scroll_bg};
    scroll-behavior:smooth;
}}
#chat-messages::-webkit-scrollbar{{width:4px;}}
#chat-messages::-webkit-scrollbar-thumb{{background:rgba(14,165,233,0.3);border-radius:2px;}}

#chat-footer{{
    padding:10px 12px;background:{bg_input};
    border-top:1px solid {brd};flex-shrink:0;
}}
#chat-input-row{{display:flex;gap:8px;align-items:flex-end;}}
#chat-input{{
    flex:1;background:{'rgba(255,255,255,0.06)' if is_dark else 'rgba(10,60,120,0.06)'};
    border:1px solid {brd};border-radius:12px;
    padding:8px 12px;font-size:13px;color:{txt};resize:none;
    outline:none;font-family:'Inter',sans-serif;line-height:1.45;
    min-height:38px;max-height:90px;overflow-y:auto;
    transition:border-color .2s;
}}
#chat-input::placeholder{{color:{txt2};}}
#chat-input:focus{{border-color:#00d4b1;}}
#chat-send{{
    width:36px;height:36px;border-radius:10px;
    background:linear-gradient(135deg,#00d4b1,#0ea5e9);
    border:none;cursor:pointer;display:flex;
    align-items:center;justify-content:center;
    font-size:16px;flex-shrink:0;
    transition:opacity .15s, transform .15s;
}}
#chat-send:hover{{opacity:0.85;transform:scale(1.05);}}
#chat-send:disabled{{opacity:0.4;cursor:not-allowed;transform:none;}}

.tooltip{{
    position:fixed;bottom:84px;right:84px;
    background:{'#071e35' if is_dark else '#fff'};
    border:1px solid {brd};border-radius:10px;
    padding:7px 12px;font-size:12px;color:{txt};
    box-shadow:0 4px 16px rgba(0,0,0,0.2);
    white-space:nowrap;display:none;
    animation:slideUp .15s ease;
}}

#empty-state{{
    text-align:center;padding:30px 20px;
    color:{txt2};font-size:12.5px;line-height:1.6;
}}
#empty-icon{{font-size:36px;margin-bottom:10px;}}
</style>
</head>
<body>

<div class="tooltip" id="tooltip">{tooltip}</div>

<button id="chat-fab" onclick="toggleChat()" title="{tooltip}">💬</button>

<div id="chat-window">
    <div id="chat-header">
        <div id="chat-header-left">
            <div id="chat-avatar">🌍</div>
            <div>
                <div id="chat-title">{title}</div>
                <div id="chat-status">● En ligne</div>
            </div>
        </div>
        <button id="chat-close" onclick="toggleChat()">✕</button>
    </div>
    <div id="chat-messages">
        {'<div id="empty-state"><div id="empty-icon">🤖</div><div>' + placeholder + '</div></div>' if not msgs_html else ''}
        {msgs_html}
    </div>
    <div id="chat-footer">
        <div id="chat-input-row">
            <textarea id="chat-input" placeholder="{placeholder}" rows="1"
                onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
            <button id="chat-send" onclick="sendMsg()">➤</button>
        </div>
    </div>
</div>

<script>
var chatOpen = {'true' if st.session_state.get("chat_open") else 'false'};
var tooltipTimer;

function toggleChat() {{
    chatOpen = !chatOpen;
    document.getElementById('chat-window').style.display = chatOpen ? 'flex' : 'none';
    clearTimeout(tooltipTimer);
    document.getElementById('tooltip').style.display = 'none';
    if (chatOpen) scrollToBottom();
}}

function scrollToBottom() {{
    var msgs = document.getElementById('chat-messages');
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
}}

function autoResize(el) {{
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 90) + 'px';
}}

function handleKey(e) {{
    if (e.key === 'Enter' && !e.shiftKey) {{
        e.preventDefault();
        sendMsg();
    }}
}}

function sendMsg() {{
    var input = document.getElementById('chat-input');
    var text = input.value.trim();
    if (!text) return;
    // Envoyer le texte vers Streamlit via un formulaire caché
    var form = document.getElementById('hidden-form');
    if (form) {{
        document.getElementById('hidden-input').value = text;
        input.value = '';
        input.style.height = 'auto';
        // Signal Streamlit (l'utilisateur tape dans le champ caché)
        // On utilise window.parent pour communiquer
        window.parent.postMessage({{type: 'streamlit:setComponentValue', value: text}}, '*');
    }}
}}

// Tooltip au survol du FAB
document.getElementById('chat-fab').addEventListener('mouseenter', function() {{
    if (!chatOpen) {{
        tooltipTimer = setTimeout(function() {{
            document.getElementById('tooltip').style.display = 'block';
        }}, 600);
    }}
}});
document.getElementById('chat-fab').addEventListener('mouseleave', function() {{
    clearTimeout(tooltipTimer);
    document.getElementById('tooltip').style.display = 'none';
}});

// Scroll au bas au chargement si ouvert
window.addEventListener('load', function() {{
    if (chatOpen) scrollToBottom();
}});
</script>

<form id="hidden-form" style="display:none;">
    <input id="hidden-input" type="text"/>
</form>
</body>
</html>
""", height=500, scrolling=False)

    # Zone de saisie Streamlit (méthode fiable pour interagir avec le backend)
    with st.container():
        st.markdown("""
        <style>
        [data-testid="stForm"] { display:none !important; }
        </style>
        """, unsafe_allow_html=True)

        with st.form(key="chat_form", clear_on_submit=True, border=False):
            user_input = st.text_input(
                "Message",
                key="chat_text_field",
                label_visibility="collapsed",
                placeholder=placeholder,
            )
            submitted = st.form_submit_button("Envoyer", width='content')

        if submitted and user_input and user_input.strip():
            st.session_state["chat_open"] = True
            st.session_state["_chat_pending"] = user_input.strip()
            st.rerun()

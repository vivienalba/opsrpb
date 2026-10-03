CSS = '''<style>
:root {--green:#00813a;--ink:#14251a;--yellow:#ffc35b;}
html,body,[data-testid="stApp"] {background:#f7faf7;color:var(--ink);font-family:Arial,Helvetica,sans-serif;}
[data-testid="stMainBlockContainer"] {max-width:1180px;padding:1.5rem 2rem 2rem;}
[data-testid="stHeader"] {background:transparent;}
h1,h2,h3 {color:var(--ink)!important;letter-spacing:-.03em;}
[data-testid="stWidgetLabel"] p,[data-testid="stCaptionContainer"] p {color:#465f50!important;}
[data-testid="stBaseButton-primary"] {background:var(--yellow)!important;color:#151b14!important;border:1px solid #e7ad44!important;border-radius:4px!important;font-weight:750!important;}
[data-testid="stBaseButton-primary"] p {color:#151b14!important;font-weight:750!important;}
[data-testid="stBaseButton-primary"]:hover {background:#ffd183!important;}
[data-testid="stBaseButton-secondary"] {background:#fff!important;color:var(--ink)!important;border-color:#b5c8bb!important;}
button:focus-visible,a:focus-visible,input:focus-visible {outline:3px solid #b27712!important;outline-offset:3px;}
.hero {border-radius:12px 12px 0 0;background-color:var(--green);background-image:linear-gradient(rgba(255,255,255,.05) 3px,transparent 3px),linear-gradient(90deg,rgba(255,255,255,.05) 3px,transparent 3px);background-size:150px 150px;text-align:center;padding:38px 24px 12px;}
.hero-kicker {color:#d8ebdf;font-size:16px;letter-spacing:.06em;margin:0 0 22px;}
.hero h1 {font-size:clamp(36px,6.4vw,70px)!important;color:#fff!important;font-weight:850!important;line-height:1.06!important;letter-spacing:-.025em!important;margin:0!important;padding:0!important;}
.hero svg {display:block;width:min(100%,570px);height:auto;margin:26px auto 0;}
.st-key-hero_action {margin-top:-1rem!important;padding:14px 24px 28px!important;background:var(--green);border-radius:0 0 12px 12px;}
.st-key-hero_action button {min-height:49px;letter-spacing:.08em;}
.intro-note {text-align:center;color:#4c6455;font-size:14px;line-height:1.65;margin:22px auto 12px;max-width:690px;}
.brandbar {display:flex;align-items:center;justify-content:space-between;gap:16px;padding:8px 0 22px;border-bottom:1px solid #cfddd1;margin-bottom:24px;}
.brandbar strong {font-size:20px;letter-spacing:-.03em;}.brandbar span {font-size:12px;color:#567060;}
.step {font-size:12px;color:#007335;font-weight:750;letter-spacing:.08em;text-transform:uppercase;margin:14px 0 4px;}
.report-title {font-size:32px!important;line-height:1.15;margin-bottom:6px;}
.report-meta {color:#506b59;font-size:13px;margin:0 0 20px;}
.kpis {display:grid;grid-template-columns:repeat(4,1fr);border:1px solid #ceded1;background:white;border-radius:8px;overflow:hidden;margin:12px 0 24px;}
.kpi {padding:20px;border-right:1px solid #dce7df;}.kpi:last-child{border-right:0;}.kpi b{display:block;font-size:34px;color:#007a36;letter-spacing:-.03em;}.kpi span{font-size:13px;color:#4c6455;}
.summary {padding:18px 20px;border-left:4px solid #00813a;background:#e9f3eb;line-height:1.7;color:#213b2a;border-radius:0 6px 6px 0;margin-bottom:20px;}
.footer {display:flex;justify-content:space-between;align-items:center;gap:10px;border-top:1px solid #d4e0d7;margin-top:32px;padding-top:14px;font-size:12px;color:#4d6557;}
[data-testid="stExpander"] {background:white;border:1px solid #d2dfd5;border-radius:6px;}
[data-testid="stFileUploaderDropzone"] {background:white;border:1.5px dashed #00813a;}
[data-baseweb="tab-list"] {gap:18px;}button[data-baseweb="tab"]{color:#375b43!important;}button[data-baseweb="tab"][aria-selected="true"]{color:#007335!important;}[data-baseweb="tab-highlight"]{background:#00813a;}
@media(max-width:700px){[data-testid="stMainBlockContainer"]{padding:1.2rem 1rem 2rem;}.hero{padding:30px 16px 10px;background-size:100px 100px;}.hero-kicker{font-size:12px;}.hero svg{margin-top:22px;}.brandbar span{display:none;}.kpis{grid-template-columns:1fr 1fr;}.kpi{padding:16px;border-bottom:1px solid #dce7df;}.kpi:nth-child(2){border-right:0;}.kpi:nth-child(n+3){border-bottom:0;}.kpi b{font-size:28px;}.footer{font-size:11px;}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;}}
</style>'''

def monitor_svg():
    # Code-native illustration follows the supplied desktop/spreadsheet reference.
    grid=''.join(f'<path d="M{x} 130V325"/>' for x in range(57,554,39)) + ''.join(f'<path d="M42 {y}H558"/>' for y in range(130,326,17))
    bars=''.join(f'<rect x="{348+i*29}" y="{312-h}" width="18" height="{h}" fill="{c}"/>' for i,(h,c) in enumerate([(43,'#f02b39'),(57,'#f56520'),(81,'#ffee30'),(96,'#2f9c89'),(124,'#53a6d8'),(117,'#363636'),(145,'#7847a6')]))
    text=''.join(f'<rect x="112" y="{181+i*14}" width="{[113,90,37,81,29][i]}" height="7" fill="#7c8080"/>' for i in range(5))
    return f'''<svg viewBox="0 0 600 450" role="img" aria-label="Illustration of a desktop monitor displaying an operations spreadsheet and a colorful bar chart">
    <path d="M235 405h130l10 39H225Z" fill="#e9e9e8"/><path d="M239 405h122l3 12H236Z" fill="#cdcdca"/>
    <rect x="17" y="10" width="566" height="394" rx="30" fill="#11140f"/><path d="M17 362h566v12q0 30-30 30H47q-30 0-30-30Z" fill="#f4f4f3"/>
    <rect x="40" y="34" width="520" height="300" fill="#fafafa"/><rect x="40" y="34" width="520" height="29" fill="#409e35"/>
    <rect x="44" y="38" width="6" height="6" fill="white"/><rect x="52" y="38" width="5" height="6" fill="white"/><rect x="44" y="46" width="6" height="6" fill="white"/><rect x="52" y="46" width="5" height="6" fill="white"/>
    <rect x="66" y="41" width="138" height="7" fill="white"/><rect x="40" y="63" width="520" height="44" fill="#edf0ed"/>
    <rect x="48" y="70" width="16" height="19" fill="#ffcf2f"/><path d="M74 74h24M74 82h24M242 75h105M242 85h105M533 73h19M533 82h19M533 90h19" stroke="#65bb61" stroke-width="6"/>
    <path d="M116 85h85" stroke="#7ab6dd" stroke-width="6"/>
    <path d="M369 74h22M401 74h22M433 74h22M465 74h22M497 74h22" stroke="white" stroke-width="18"/>
    <rect x="40" y="113" width="520" height="13" fill="#c7c9c7"/><rect x="253" y="113" width="48" height="13" fill="#5f8190"/>
    <g stroke="#e3e6e3" stroke-width="2">{grid}</g><rect x="60" y="130" width="500" height="23" fill="#48b537"/>
    <path d="M188 138h246M237 147h140" stroke="white" stroke-width="5"/>
    <rect x="109" y="162" width="195" height="16" fill="#ffbd32"/><path d="M112 169h70M261 169h29" stroke="#f28514" stroke-width="7"/>
    {text}<path d="M276 186h25M282 200h19M278 214h23M269 228h32M272 242h29" stroke="#7c8080" stroke-width="7"/>
    <rect x="109" y="265" width="195" height="13" fill="#9833a6"/><path d="M112 286h52M216 286h35M263 286h32M112 300h46M216 300h32M276 300h17" stroke="#8e299a" stroke-width="6"/>
    {bars}<path d="M340 314h210" stroke="#8c3a99" stroke-width="3"/>
    <rect x="184" y="440" width="232" height="10" rx="4" fill="#f3f3f1"/></svg>'''

def hero_html():
    return '<section class="hero"><p class="hero-kicker">DATA ANALYSIS</p><h1>Make Your Data<br>Work for You</h1>'+monitor_svg()+'</section>'

CSS += '''<style>
.st-key-policy_footer {position:relative;min-height:60px;border-top:1px solid #d4e0d7;margin-top:30px;padding:8px 0;}
.st-key-policy_footer [data-testid="stVerticalBlock"],.st-key-policy_footer [data-testid="stElementContainer"] {position:static!important;}
.st-key-policy_footer .footer-copy {position:absolute;top:8px;left:0;margin:0!important;height:44px;display:flex;align-items:center;color:#4c6455;font-size:12px;}
.st-key-policy_footer .st-key-policies_button {position:absolute!important;top:8px;right:0;width:auto!important;}
.st-key-policies_button button {height:44px;min-height:44px;padding:0;color:#4c6455;}
[data-testid="stDialog"] [role="dialog"] {background:#fff!important;color:#14251a!important;}
[data-testid="stDialog"] [role="dialog"] h2 {padding:20px 48px 12px 24px!important;}
</style>'''

"""Graph-paper workspace inspired by the supplied roadmap reference."""

CSS = '''<style>
:root {--ink:#203a32;--muted:#526b60;--paper:#edf1ee;--cream:#fafbf7;--mustard:#cdc38b;--teal:#6ca7af;--orange:#eca466;--line:#d3ded6;}
html,body,[data-testid="stApp"] {color:var(--ink);font-family:"Avenir Next",Avenir,"Segoe UI",sans-serif;background-color:var(--paper);}
[data-testid="stApp"] {background-image:linear-gradient(#dfe6df70 1px,transparent 1px),linear-gradient(90deg,#dfe6df70 1px,transparent 1px);background-size:27px 27px;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stMainBlockContainer"] {max-width:1320px;padding:1.2rem 2.5rem 2rem;}
[data-testid="stVerticalBlock"] {gap:1rem;}
h1,h2,h3,h4 {color:var(--ink)!important;letter-spacing:-.045em;font-weight:750!important;}
h2{font-size:1.7rem!important;}h3{font-size:1.1rem!important;letter-spacing:-.02em;}
[data-testid="stMarkdownContainer"],[data-testid="stWidgetLabel"] p,[data-testid="stExpander"] summary p{color:var(--ink)!important;}
[data-testid="stCaptionContainer"] p{color:var(--muted)!important;opacity:1;line-height:1.6;}
::selection{background:#d8cba2;color:var(--ink);}
button:focus-visible,a:focus-visible,input:focus-visible,[role="tab"]:focus-visible{outline:3px solid #417e88!important;outline-offset:3px!important;}
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-secondary"]{border:1px solid var(--ink)!important;border-radius:100px!important;min-height:46px;box-shadow:none!important;}
[data-testid="stBaseButton-primary"]{background:var(--orange)!important;color:var(--ink)!important;}
[data-testid="stBaseButton-primary"] p,[data-testid="stBaseButton-primary"] svg{color:var(--ink)!important;font-weight:700!important;}
[data-testid="stBaseButton-primary"]:hover{background:#f3b582!important;}
[data-testid="stBaseButton-secondary"]{background:var(--cream)!important;color:var(--ink)!important;border-color:#bccdc0!important;}
[data-testid="stBaseButton-secondary"] p,[data-testid="stBaseButton-secondary"] svg{color:var(--ink)!important;}
[data-testid="stBaseButton-secondary"]:hover{background:#e3ede5!important;border-color:var(--ink)!important;}
[data-testid="stBaseButton-tertiary"],[data-testid="stBaseButton-tertiary"] p{color:var(--muted)!important;}
button:disabled{opacity:.55;}
.masthead{display:flex;align-items:center;justify-content:space-between;gap:20px;background:var(--mustard);border-radius:100px;padding:25px 40px;margin-bottom:30px;}
.masthead .brand{font-size:20px;font-weight:800;letter-spacing:-.035em;}.masthead .masthead-note{font-size:15px;font-style:italic;white-space:nowrap;}.masthead .brand span{font-weight:500;}
.hero{position:relative;display:grid;grid-template-columns:1fr 1.15fr;align-items:center;gap:4px;padding:48px 28px 26px;min-height:460px;}
.hero-copy{position:relative;z-index:1;}.hero-eyebrow{font-size:12px;letter-spacing:.16em;font-weight:700;margin:0 0 22px;color:var(--muted);}
.hero h1{font-size:clamp(44px,5.55vw,76px)!important;line-height:1.02!important;letter-spacing:-.065em!important;font-weight:800!important;margin:0 0 28px!important;padding:0!important;color:var(--ink)!important;}
.hero-lead{color:#607e69!important;font-size:19px;font-weight:650;line-height:1.55;max-width:410px;margin:0!important;}
.hero-art{position:relative;min-width:0;}.hero-art svg{display:block;width:100%;height:auto;overflow:visible;}
.hero-spark{position:absolute;right:0;top:-30px;color:var(--teal);font-size:54px;transform:rotate(8deg);line-height:1;}
.period-pill{display:inline-block;background:var(--teal);color:#183e43;padding:12px 21px;border-radius:100px;font-size:13px;letter-spacing:.025em;font-weight:650;margin-top:28px;}
.small-spark{position:absolute;left:-25px;bottom:55px;width:22px;height:22px;background:var(--orange);clip-path:polygon(43% 0,61% 0,63% 35%,100% 42%,100% 58%,64% 63%,58% 100%,40% 100%,36% 64%,0 58%,0 41%,36% 36%);transform:rotate(-10deg);}
.st-key-hero_action{padding:0 28px 26px!important;}
.st-key-start_report button{background:var(--teal)!important;border-color:#497b80!important;min-height:50px;}.st-key-start_report button:hover{background:#83b6bb!important;}.st-key-start_report button p{font-size:15px!important;}
.welcome-help{color:var(--muted);font-size:13px;line-height:1.6;margin:4px 0;max-width:430px;}
.how-it-works{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;border-top:1px solid #c8d6cb;margin:22px 28px 6px;padding-top:28px;}
.how-it-works div{display:flex;align-items:flex-start;gap:14px;}.how-it-works .step-number{display:flex;align-items:center;justify-content:center;flex:0 0 33px;height:33px;border:1px solid #9daf9f;border-radius:50%;font-size:12px;font-weight:700;}
.how-it-works strong{display:block;font-size:15px;letter-spacing:-.02em;}.how-it-works p{font-size:12px!important;color:var(--muted)!important;line-height:1.65;margin:7px 0 0;}
.workspace-heading{padding:5px 4px 18px;}.eyebrow{font-size:11px;letter-spacing:.15em;font-weight:750;color:var(--muted);text-transform:uppercase;margin:0 0 9px;}
.workspace-heading h1{font-size:42px!important;line-height:1.08!important;padding:0!important;margin:0 0 12px!important;}.workspace-heading p{margin:0;color:var(--muted);font-size:14px;line-height:1.6;}
.setup-heading{display:flex;align-items:center;gap:12px;margin:4px 0 12px;}.setup-heading b{width:30px;height:30px;border-radius:50%;background:#dcd4ac;color:var(--ink);display:flex;justify-content:center;align-items:center;font-size:12px;}.setup-heading h2{font-size:21px!important;margin:0!important;padding:0!important;letter-spacing:-.035em;}
.st-key-dataset_card,.st-key-mapping_card,.st-key-period_card,.st-key-report_card{background:#fafbf7f5;border:1px solid #cbd8ce;border-radius:22px;padding:24px!important;}
.st-key-period_card{background:#f5f2e5f7;border-color:#d5d0b4;}.st-key-build_action{border-radius:18px;background:#dce9e2;padding:20px!important;border:1px solid #c8dbce;}
.brief{display:grid;grid-template-columns:1.5fr 1fr 1fr;gap:15px;align-items:center;}.brief>div{min-width:0;}.brief p{margin:0;color:var(--muted);font-size:12px;overflow-wrap:anywhere;}.brief b{display:block;font-size:15px;color:var(--ink);margin-bottom:5px;overflow-wrap:anywhere;}.brief .brief-tag{display:inline-block;font-size:11px;letter-spacing:.06em;text-transform:uppercase;background:#f5f2e5;border-radius:100px;padding:7px 12px;}
[data-testid="stWidgetLabel"] p{font-size:13px!important;font-weight:600;}
[data-baseweb="select"]>div,[data-testid="stTextInputRootElement"],[data-testid="stDateInput"]>div>div{background:#fff!important;color:var(--ink)!important;border-radius:10px!important;border-color:#bbcbbf!important;}
[data-baseweb="select"] input,[data-baseweb="select"] span,[data-baseweb="select"] svg,[data-testid="stTextInput"] input,[data-testid="stDateInput"] input{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important;}
[data-testid="stTextInput"] input::placeholder{color:#6a7c6f!important;-webkit-text-fill-color:#6a7c6f!important;opacity:1!important;}
[data-baseweb="tag"]{background:#e0ece6!important;color:var(--ink)!important;}[data-baseweb="popover"],[role="listbox"],[role="option"]{background:#fff!important;color:var(--ink)!important;}[role="option"] *{color:var(--ink)!important;}[role="option"]:hover,[role="option"][aria-selected="true"]{background:#edf3ee!important;}
[data-testid="stExpander"]{background:#fff9;border:1px solid #cbd8ce;border-radius:12px;}[data-testid="stExpander"] summary,[data-testid="stExpander"] summary svg{color:var(--ink)!important;}
[data-testid="stFileUploaderDropzone"]{background:#f0f6f1!important;border:1.5px dashed #7d9e87!important;border-radius:16px;min-height:160px;}[data-testid="stFileUploaderDropzoneInstructions"]{color:var(--ink)!important;}[data-testid="stFileUploaderDropzoneInstructions"] small{color:var(--muted)!important;}
[data-testid="stAlert"]{border-radius:12px;}
.report-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin:10px 0 23px;}.report-heading>div{min-width:0;}.report-heading h2{font-size:30px!important;line-height:1.1;margin:7px 0 9px!important;padding:0!important;overflow-wrap:anywhere;}.report-heading p{font-size:12px;color:var(--muted);margin:0;}.report-label{display:inline-flex;align-items:center;gap:8px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;}.report-label:before{content:"";width:7px;height:7px;border-radius:50%;background:#53816b;}
.frequency-tag{font-size:12px;white-space:nowrap;border:1px solid #91a994;border-radius:100px;padding:9px 16px;margin-top:8px;}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:0 0 24px;}.kpi{border:1px solid #ced9cf;border-radius:17px;background:#fff;min-height:131px;padding:19px 22px;position:relative;}.kpi:nth-child(1){background:#e5eee5;}.kpi:nth-child(2){background:#e3eff0;}.kpi:nth-child(3){background:#f0ecd7;}.kpi:nth-child(4){background:#f7e8db;}.kpi b{display:block;font-size:38px;letter-spacing:-.05em;line-height:1.25;margin-bottom:10px;}.kpi span{font-size:12px;color:#435d4c;}.kpi:after{content:"";position:absolute;right:18px;top:21px;width:10px;height:10px;border:1.5px solid #6a8c77;border-radius:50%;}
.summary{border-left:3px solid #6d9c83;background:#eef3eb;border-radius:0 13px 13px 0;padding:19px 22px;line-height:1.7;font-size:14px;color:var(--ink);margin:0 0 17px;}.summary .eyebrow{margin:0 0 6px;font-size:10px;}
[data-testid="stMetric"]{padding:16px 19px;background:white;border-radius:14px;border:1px solid #d7e1d8;}[data-testid="stMetricValue"]{font-size:27px;color:var(--ink);}
[data-baseweb="tab-list"]{gap:24px;border-bottom:1px solid #cfddd1;margin:10px 0 12px;}button[data-baseweb="tab"]{color:#526b60!important;padding:10px 0;font-weight:600;}button[data-baseweb="tab"] p{font-size:13px!important;color:#526b60!important;}button[data-baseweb="tab"][aria-selected="true"],button[data-baseweb="tab"][aria-selected="true"] p{color:var(--ink)!important;}[data-baseweb="tab-highlight"]{background:#609a9f!important;height:3px;}
[data-testid="stDataFrame"]{border-radius:10px;overflow:hidden;}
.st-key-chart_status,.st-key-chart_trend,.st-key-export_excel,.st-key-export_pdf{border:1px solid #d6e0d8;border-radius:16px;background:#fff;padding:19px!important;}
.export-note{font-size:12px;color:var(--muted);line-height:1.6;margin:0 0 12px;}
.empty-report{padding:38px;text-align:center;border:1.5px dashed #b4cbbd;border-radius:18px;background:#f8faf6;margin:14px 0;}.empty-report h3{font-size:21px!important;margin:0 0 9px!important;}.empty-report p{font-size:13px;color:var(--muted);margin:0;line-height:1.6;}
.st-key-policy_footer{position:relative;min-height:65px;border-top:1px solid #cbd7cd;margin-top:32px;padding-top:12px;}.st-key-policy_footer [data-testid="stVerticalBlock"],.st-key-policy_footer [data-testid="stElementContainer"]{position:static!important;}.st-key-policy_footer .footer-copy{position:absolute;top:12px;left:0;margin:0!important;height:44px;display:flex;align-items:center;color:var(--muted);font-size:12px;}.st-key-policy_footer .st-key-policies_button{position:absolute!important;top:12px;right:0;width:auto!important;}.st-key-policies_button button{height:44px;min-height:44px;padding:0;color:var(--muted);}.st-key-policies_button button p{font-size:12px!important;white-space:nowrap;}
[data-testid="stDialog"] [role="dialog"]{background:var(--cream)!important;color:var(--ink)!important;border-radius:22px!important;}[data-testid="stDialog"] [role="dialog"] h2{padding:22px 50px 12px 24px!important;}
@media(max-width:900px){.masthead{padding:21px 27px;}.masthead .brand{font-size:17px;}.masthead-note{font-size:12px!important;}.hero{padding:25px 12px 20px;min-height:350px;}.hero h1{font-size:49px!important;}.hero-lead{font-size:16px;}.period-pill{font-size:11px;padding:10px 14px;}.how-it-works{margin-left:12px;margin-right:12px;gap:16px;}.st-key-hero_action{padding-left:12px!important;padding-right:12px!important;}}
@media(max-width:700px){[data-testid="stMainBlockContainer"]{padding:1.2rem 1rem 1.5rem;}.masthead{padding:19px 22px;border-radius:25px;margin-bottom:21px;}.masthead .brand{font-size:16px;}.masthead-note{display:none;}.masthead .brand span{display:block;font-size:12px;letter-spacing:0;margin-top:2px;}.hero{grid-template-columns:1fr;padding:18px 7px 6px;min-height:0;}.hero h1{font-size:52px!important;letter-spacing:-.06em!important;margin-bottom:20px!important;}.hero-eyebrow{font-size:10px;margin-bottom:16px;}.hero-lead{font-size:16px;max-width:330px;}.period-pill{margin-top:18px;font-size:11px;padding:11px 17px;}.hero-art{margin-top:8px;max-width:440px;}.hero-art svg{width:100%;}.hero-spark{font-size:40px;top:2px;right:5px;}.small-spark{display:none;}.st-key-hero_action{padding:0 7px 9px!important;}.how-it-works{grid-template-columns:1fr;gap:20px;padding-top:24px;margin:26px 7px 8px;}.how-it-works p{margin-top:4px;}.workspace-heading h1{font-size:34px!important;}.st-key-dataset_card,.st-key-mapping_card,.st-key-period_card,.st-key-report_card{padding:19px 16px!important;border-radius:18px;}.brief{grid-template-columns:1fr 1fr;gap:15px;}.brief>div:first-child{grid-column:1/-1;}.report-heading h2{font-size:25px!important;}.frequency-tag{font-size:10px;padding:7px 12px;}.kpis{grid-template-columns:1fr 1fr;gap:10px;}.kpi{min-height:115px;padding:16px;}.kpi b{font-size:32px;}.kpi span{font-size:11px;}.summary{padding:16px;font-size:13px;}[data-baseweb="tab-list"]{gap:19px;}[data-testid="stMetric"]{padding:13px 15px;}.empty-report{padding:26px 15px;}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important;}}
</style>'''


def masthead_html(workspace=False):
    note = 'Your reporting workspace' if workspace else 'A little clarity. A bigger picture.'
    return f'<header class="masthead"><div class="brand">Viv’s Operations <span>Report Builder</span></div><span class="masthead-note">{note}</span></header>'


def laptop_svg():
    return '''<svg viewBox="0 0 650 495" role="img" aria-label="Sketched laptop with a teal star, magnifying glass, and a small flag"><g stroke="#29463d" stroke-linecap="round" stroke-linejoin="round">
    <path d="M104 407Q158 427 503 449" fill="none" stroke="#b7c9bf" stroke-width="5" opacity=".35"/>
    <path d="M251 73 559 69 517 332 181 325Z" fill="#eca466" stroke-width="8"/><path d="M270 94 531 91 497 301 213 297Z" fill="#fffefa" stroke-width="7"/>
    <path d="M181 325 517 332 517 361Q513 382 490 393L382 453 80 432Q54 429 51 402Z" fill="#d1c88e" stroke-width="8"/>
    <path d="M181 325 517 332 382 416 51 402Z" fill="#6ca7af" stroke-width="8"/><path d="M382 416 382 449M517 332 517 352" fill="none" stroke-width="7"/>
    <path d="M155 344 455 351 397 387 112 374M206 329 142 375M253 331 193 379M300 333 245 382M351 335 297 385M398 337 348 387M135 357 428 364" fill="none" stroke-width="8"/>
    <path d="M206 389 284 393 264 409 183 404Z" fill="#203a32" stroke-width="4"/><path d="M301 402 348 405" stroke="#f6faf5" stroke-width="8"/><circle cx="362" cy="406" r="4" stroke="none" fill="#f6faf5"/>
    <path d="M367 142Q375 132 384 150L402 187 437 191Q453 194 440 208L410 231 417 271Q419 287 405 280L373 257 340 281Q324 291 327 272L335 232 308 211Q294 198 312 193L347 190Z" fill="#6ca7af" stroke-width="4"/>
    <path d="M405 144Q423 127 430 142Q433 149 425 155M433 155Q442 154 441 168M346 292Q366 272 381 290" fill="none" stroke-width="3"/>
    <path d="M458 264 480 249M471 278 490 266M481 288 493 281" fill="none" stroke-width="6"/><path d="M296 265 296 281" stroke="#829385" stroke-width="3"/>
    <path d="M194 174 235 216" stroke="#eca466" stroke-width="17"/><path d="M235 214 274 261Q282 273 269 282Q258 288 250 278L213 237Q208 226 217 219Q225 212 235 214Z" fill="#cdc38b" stroke="#75856e" stroke-width="3"/>
    <circle cx="263" cy="270" r="5" fill="none" stroke="#75856e" stroke-width="3"/><circle cx="165" cy="150" r="60" fill="#cfc58b" stroke="#66755e" stroke-width="3"/>
    <circle cx="165" cy="150" r="43" fill="#f8fbf6" stroke="#536c61" stroke-width="3"/><path d="M176 109 174 192" stroke="#e2ebe7" stroke-width="17"/>
    <ellipse cx="560" cy="413" rx="35" ry="13" fill="#7f9c80" stroke="#597561" stroke-width="3"/><ellipse cx="560" cy="405" rx="35" ry="12" fill="#d1c88e" stroke="none"/>
    <path d="M553 401 585 245" stroke="#7e9b80" stroke-width="13"/><path d="M583 258 648 276 616 305 640 343 570 323Z" fill="#6ca7af" stroke="#537e78" stroke-width="3"/>
    </g></svg>'''


def hero_html():
    return '<section class="hero"><div class="hero-copy"><p class="hero-eyebrow">FROM SPREADSHEET TO STORY</p><h1>Operations.<br>In perspective.</h1><p class="hero-lead">A clearer view of your team,<br>your workload, and what comes next.</p><span class="period-pill">Weekly · Monthly · Quarterly · Annual</span><span class="small-spark" aria-hidden="true"></span></div><div class="hero-art"><span class="hero-spark" aria-hidden="true">✳</span>'+laptop_svg()+'</div></section>'


def steps_html():
    return '<div class="how-it-works"><div><span class="step-number">01</span><section><strong>Bring your records</strong><p>Upload a CSV, TSV, or Excel sheet.<br>Or explore with the sample dataset.</p></section></div><div><span class="step-number">02</span><section><strong>Set your perspective</strong><p>Match the columns and choose<br>the period and counting rules.</p></section></div><div><span class="step-number">03</span><section><strong>Review, then share</strong><p>Check the story behind the numbers.<br>Download your Excel or PDF report.</p></section></div></div>'

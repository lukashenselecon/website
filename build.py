# -*- coding: utf-8 -*-
import os, io, shutil
from data import PUBS, WPS, WIP

SITE="https://lukashensel.com"
EMAIL="lukas.hensel@gsm.pku.edu.cn"

# --- things you may want to change -------------------------------------
# Office hours, shown on the home page and repeated on Teaching.
# For a fixed slot, write it out, e.g.
#   OFFICE_HOURS_EN = "Wednesdays 14:00–16:00, Guanghua Building 2, Room 217"
#   OFFICE_HOURS_ZH = "每周三 14:00–16:00，光华管理学院 2 号楼 217 室"
OFFICE_HOURS_EN = ("Tuesdays 10:30–11:45, Guanghua Building 2, Office 343. "
                   "Email ahead if you want to discuss something specific — otherwise just come by.")
OFFICE_HOURS_ZH = "每周二 10:30–11:45，光华管理学院 2 号楼 343 室。如需讨论特定问题，请提前发邮件；否则直接过来即可。"

# Profile links. Leave a value empty and the link is left off the page.
TWITTER = "LukasHenselEcon"
ORCID   = "0000-0002-4962-2885"
BLUESKY = "lukashenselecon.bsky.social"
SCHOLAR = "https://scholar.google.com/citations?user=_swX_6kAAAAJ"
# -----------------------------------------------------------------------

# Co-author pages. Add a name here and it becomes a link wherever it appears.
# Leave someone out and their name simply renders as text.
PEOPLE = {
  "Anselm Hager":        "https://anselmhager.com/",
  "Christopher Roth":    "https://cproth.com/",
  "Johannes Hermle":     "https://sites.google.com/berkeley.edu/johannes/home",
  "Andreas Stegmann":    "https://cepr.org/about/people/andreas-stegmann",
  "Marc Witte":          "https://www.marcwitte.com/",
  "Tsegay Tekleselassie":"https://sites.google.com/view/tsegaytekleselassie",
  "Thiemo Fetzer":       "https://www.trfetzer.com/",
  "Robert Garlick":      "https://www.robgarlick.com/",
  "Kate Orkin":          "https://sites.google.com/site/kateorkin/home",
  "François Gerard":     "https://sites.google.com/site/fransgerard/home",
  "Fran&ccedil;ois Gerard": "https://sites.google.com/site/fransgerard/home",
  "Girum Abebe":         "https://cepr.org/about/people/girum-abebe",
  "A. Stefano Caria":    "https://www.stefanocaria.com/",
  "Stefano Caria":       "https://www.stefanocaria.com/",
  "Ingo E. Isphording":  "https://sites.google.com/view/ingoeisphording/about-me",
  "Jonas Radbruch":      "https://sites.google.com/site/jonasradbruch01/",
  "Maria Balgova":       "https://www.iza.org/people/staff/28631/maria-balgova",
  "Andrea Kiss":         "https://www.andreakiss.net/",
  "Sara Spaziani":       "https://www.saraspaziani.com/home",
  "Cornelius Christian": "https://corneliuschristian.com/",
  "Stefano Fiorin":      "https://sites.google.com/site/stefanofiorineconomics/",
  "Damir Esenaliev":     "https://isdc.org/team/damir-esenaliev/",
  "Yuyu Chen":           "https://ideas.repec.org/e/pch138.html",
  "Jennifer Kades":      "https://jenniferkades.pythonanywhere.com",
}
# Surnames, for the Chinese pages where only the family name is printed.
SURNAMES = {}
for _n, _u in PEOPLE.items():
    _last = _n.split()[-1]
    if _last not in SURNAMES: SURNAMES[_last] = _u

def linkify(text, lang):
    """Turn co-author names into links, longest match first."""
    table = SURNAMES if lang == "zh" else PEOPLE
    out, i = [], 0
    keys = sorted(table, key=len, reverse=True)
    while i < len(text):
        for k in keys:
            if text.startswith(k, i):
                nxt = text[i+len(k):i+len(k)+1]
                if lang != "zh" and nxt.isalpha():
                    continue
                out.append('<a class="who" href="%s" rel="noopener">%s</a>' % (table[k], k))
                i += len(k)
                break
        else:
            out.append(text[i]); i += 1
    return "".join(out)

NAV=[("","Home","首页"),("publications","Publications","发表论文"),
     ("work-in-progress","Work in Progress","在研工作"),
     ("teaching","Teaching &amp; Supervision","教学与指导"),("references","Reference letters","推荐信"),
     ("cv","CV","个人简历")]

def url(lang,slug):
    base="/zh/" if lang=="zh" else "/"
    return base+slug if slug else base

def head(lang,slug,title,desc):
    L="zh-Hans" if lang=="zh" else "en"
    alt = url("en" if lang=="zh" else "zh", slug)
    can = SITE+url(lang,slug)
    return f'''<!doctype html>
<html lang="{L}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{can}">
<link rel="alternate" hreflang="en" href="{SITE}{url('en',slug)}">
<link rel="alternate" hreflang="zh-Hans" href="{SITE}{url('zh',slug)}">
<meta property="og:type" content="profile">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{can}">
<meta property="og:image" content="{SITE}/assets/photo.jpg">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="/assets/style.css">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''

def header(lang,slug):
    items=""
    for s,en,zh in NAV:
        cur=' aria-current="page"' if s==slug else ""
        items+=f'<a href="{url(lang,s)}"{cur}>{zh if lang=="zh" else en}</a>'
    en_cur=' aria-current="true"' if lang=="en" else ""
    zh_cur=' aria-current="true"' if lang=="zh" else ""
    return f'''<header class="head">
<a class="name" href="{url(lang,'')}">Lukas Hensel</a>
<div class="right">
<nav class="nav" aria-label="{'主导航' if lang=='zh' else 'Main'}">{items}</nav>
<div class="lang"><a href="{url('en',slug)}" hreflang="en"{en_cur}>EN</a><a href="{url('zh',slug)}" hreflang="zh-Hans"{zh_cur}>中文</a></div>
</div>
</header>
<main id="main">
'''

def _profiles(lang):
    zh = lang=="zh"
    out=[('Google Scholar', SCHOLAR),
         ('IZA','https://www.iza.org/en/people/fellows/27501/lukas-hensel'),
         ('J-PAL','https://www.povertyactionlab.org/invited-researchers')]
    if ORCID:  out.append(('ORCID','https://orcid.org/%s' % ORCID))
    if TWITTER:out.append(('Twitter','https://twitter.com/%s' % TWITTER))
    if BLUESKY:out.append(('Bluesky','https://bsky.app/profile/%s' % BLUESKY))
    links=['<a href="%s" rel="me noopener">%s</a>' % (u,n) for n,u in out]
    if zh:
        return "另见 " + "、".join(links) + "。"
    return "Also on " + ", ".join(links[:-1]) + " and " + links[-1] + "."

def footer(lang, profiles=True):
    if lang=="zh":
        place = "北京大学光华管理学院 · 北京"
    else:
        place = "Guanghua School of Management, Peking University, Beijing"
    prof = _profiles(lang) if profiles else ""
    return """</main>
<footer>
%s &nbsp;·&nbsp; <a href="mailto:%s">%s</a><br>
%s
</footer>
<script>
/* Copy buttons for citations. No external requests; if this does not run the
   text is still there to select. */
(function(){
  if(!navigator.clipboard) return;
  document.querySelectorAll("[data-copy]").forEach(function(b){
    b.hidden=false;
    b.addEventListener("click",function(){
      var box=b.parentNode, src=box.querySelector("pre")||box.querySelector("p");
      navigator.clipboard.writeText(src.innerText).then(function(){
        var t=b.textContent; b.textContent=b.dataset.done||"Copied"; b.dataset.done2=1;
        b.setAttribute("data-done","1");
        setTimeout(function(){b.textContent=t;b.removeAttribute("data-done");},1600);
      });
    });
  });
})();
</script>
</body>
</html>""" % (place, EMAIL, EMAIL, prof)

# ---------- citations ----------
import re, unicodedata, html as _html

def _plain(t):
    return _html.unescape(t)

def _names(p):
    """Ordered author list, Lukas included, alphabetical by surname (econ convention)."""
    if p.get("authors"):
        return list(p["authors"])
    raw = _plain(p["a_en"]).replace(" & ", ", ").replace(" and ", ", ")
    people = []
    for n in raw.split(","):
        n = re.sub(r"\s*\bet\s+al\.?\s*$", "", n.strip())
        if n: people.append(n)
    people.append("Lukas Hensel")
    seen, uniq = set(), []
    for n in people:
        if n not in seen:
            seen.add(n); uniq.append(n)
    return sorted(uniq, key=lambda n: n.split()[-1].lower())

def _split(n):
    parts = n.split()
    return " ".join(parts[:-1]), parts[-1]

def _ascii(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t) if c.isalnum()).lower()

def _volpages(vs):
    if not vs: return ("","","")
    m = re.match(r"\s*(\d+)\s*(?:\((\d+)\))?\s*(?:,\s*(.+))?$", _plain(vs))
    if not m: return ("","","")
    vol, num = m.group(1) or "", m.group(2) or ""
    pages = (m.group(3) or "").strip().replace("–","--").replace("—","--")
    return (vol, num, pages)

def _year(p):
    if p.get("cite_year"): return str(p["cite_year"])
    y = _plain(p["y"])
    return y if y.isdigit() else ""

def formatted(p):
    people = _names(p)
    bits = []
    for i, n in enumerate(people):
        first, last = _split(n)
        bits.append(("%s, %s" % (last, first)) if i == 0 else n)
    if p.get("random_order"): who = " \u24e1 ".join(bits)
    elif p.get("etal"): who = ", ".join(bits) + ", et al"
    elif len(bits) == 1: who = bits[0]
    elif len(bits) == 2: who = "%s, and %s" % (bits[0], bits[1])
    else: who = ", ".join(bits[:-1]) + ", and " + bits[-1]
    yr = _year(p) or "n.d"          # the format string adds the final period
    t = _plain(p["t"])
    t = t if t[-1:] in "?!" else t + "."
    out = '%s. %s. “%s” %s' % (who, yr, t, _plain(p.get("v","")))
    vol, num, pages = _volpages(p.get("vs"))
    if vol:
        out += " %s" % vol
        if num: out += " (%s)" % num
        if pages: out += ": %s" % pages.replace("--", "–")
    elif p.get("flag"):
        out += ", forthcoming"
    return out + "."

def bibtex(p):
    people = _names(p)
    auth = " and ".join("%s, %s" % (_split(n)[1], _split(n)[0]) for n in people)
    if p.get("etal"): auth += " and others"
    yr = _year(p); title = _plain(p["t"]); venue = _plain(p.get("v",""))
    vol, num, pages = _volpages(p.get("vs"))
    word = next((w for w in re.findall(r"[A-Za-z]+", title)
                 if w.lower() not in ("the","a","an","and","of","in","on","for","from","to","about","evidence")), "paper")
    key = "%s%s%s" % (_ascii(_split(people[0])[1]), yr or "wp", _ascii(word))
    forthcoming = bool(p.get("flag"))
    kind = "article" if (vol or forthcoming) else ("techreport" if "Discussion Paper" in venue else "unpublished")
    f = [("author", auth), ("title", "{%s}" % title)]
    note = None
    if kind == "article":
        f.append(("journal", venue))
        if vol: f.append(("volume", vol))
        if num: f.append(("number", num))
        if pages: f.append(("pages", pages))
        if forthcoming: note = "Forthcoming"
    elif kind == "techreport":
        m = re.search(r"(\d{4,6})", venue)
        f += [("institution", "IZA Institute of Labor Economics"), ("type", "IZA Discussion Paper")]
        if m: f.append(("number", m.group(1)))
    else:
        note = venue or "Working paper"
    if yr: f.append(("year", yr))
    if p.get("random_order"):
        note = (note + ". " if note else "") + "Author order randomized"
    if note: f.append(("note", note))
    w = max(len(k) for k,_ in f)
    return "@%s{%s,\n%s\n}" % (kind, key, ",\n".join("  %-*s = {%s}" % (w,k,v) for k,v in f))

# ---------- one entry ----------
BST = "https://ctan.org/pkg/econ-bst"

def entry(p,lang):
    zh = lang=="zh"
    yr = p.get("yz",p["y"]) if zh else p["y"]
    au = p["a_zh"] if zh else "with "+p["a_en"]
    ven = p.get("vz",p["v"]) if zh else p["v"]
    vs = (" &middot; "+p["vs"]) if p.get("vs") and not zh else (", "+p["vs"] if p.get("vs") else "")
    flag = f'<span class="flag">{"即将发表" if zh else "Forthcoming"}</span>' if p.get("flag") else ""
    sep = "，" if zh else " &middot; "
    out=[f'<article class="entry"><div class="yr">{yr}</div><div>',
         f'<h2 class="ti">{p["t"]}</h2>',
         f'<p class="au">{linkify(au, lang)}{sep}<b>{ven}</b>{vs}{flag}</p>']

    def panel(label, inner, extra=""):
        return (f'<details class="dd"><summary><span class="chip">'
                f'<span class="car">&#9656;</span>{label}</span></summary>'
                f'<div class="panel{extra}">{inner}</div></details>')

    # big row: the abstract leads, then the things to open or download
    big = []
    if p.get("ab"):
        big.append(panel("摘要" if zh else "Abstract", f'<p>{p["ab"]}</p>'))
    for en, zh_lab, u in p["links"]:
        if u.startswith("REPLICATION_URL"):     # not supplied yet — see README
            continue
        ext = ' rel="noopener"' if u.startswith("http") else ""
        big.append(f'<a class="chip" href="{u}"{ext}>{zh_lab if zh else en}</a>')
    if big:
        out.append('<div class="chips">'+"".join(big)+'</div>')

    # small row: how to cite
    if p.get("v"):
        copy_c = "复制" if zh else "Copy"
        bst_note = ("引用格式与 <a href=\"%s\" rel=\"noopener\">econ.bst</a> 一致。" % BST) if zh else \
                   ("Formatted for <a href=\"%s\" rel=\"noopener\">econ.bst</a>." % BST)
        rnd = ""
        if p.get("random_order"):
            rnd = ('<p class="fine">作者顺序为随机排列（AEA 作者顺序随机化工具），以 &#9441; 标示。</p>' if zh else
                   '<p class="fine">Author order was randomized using the AEA Author Randomization Tool, '
                   'marked with &#9441;.</p>')
        cite_row = [
            panel("引用格式" if zh else "Citation",
                  f'<p>{_html.escape(formatted(p))}</p>{rnd}'
                  f'<button class="copy" type="button" hidden data-copy>{copy_c}</button>', " cite"),
            panel("BibTeX",
                  f'<pre>{_html.escape(bibtex(p))}</pre>'
                  f'<p class="fine">{bst_note}</p>'
                  f'<button class="copy" type="button" hidden data-copy>{copy_c}</button>')]
        out.append('<div class="chips tight">'+"".join(cite_row)+'</div>')

    # coverage
    if p.get("coverage"):
        links = " ".join(
            f'<a class="cov" href="{u}" rel="noopener">{zh_lab if zh else en}</a>'
            for en, zh_lab, u in p["coverage"])
        out.append(f'<p class="coverage"><span>{"媒体报道" if zh else "Coverage"}</span>{links}</p>')

    out.append('</div></article>')
    return "\n".join(out)

# Portrait plus the profile buttons underneath it.
# Drop an SVG at assets/icons/<key>.svg (orcid, scholar, twitter, bluesky) and it
# is used in place of the text label. The official marks are published by each
# service under its own brand terms, so they are not bundled here.
PROFILE_BUTTONS = [
    ("orcid",   "ORCID",   "https://orcid.org/%s"          % ORCID   if ORCID   else ""),
    ("scholar", "Scholar", SCHOLAR),
    ("twitter", "Twitter", "https://twitter.com/%s"        % TWITTER if TWITTER else ""),
    ("bluesky", "Bluesky", "https://bsky.app/profile/%s"   % BLUESKY if BLUESKY else ""),
]

def portrait(lang):
    alt = "Lukas Hensel"
    items = []
    for key, label, url in PROFILE_BUTTONS:
        if not url: continue
        icon = os.path.join("assets", "icons", key + ".svg")
        inner = ('<img src="/assets/icons/%s.svg" alt="" width="16" height="16">' % key
                 if os.path.exists(icon) else label)
        items.append('<li><a href="%s" rel="me noopener" title="%s" aria-label="%s">%s</a></li>'
                     % (url, label, label, inner))
    return ('<figure class="portrait">'
            '<img class="shot" src="/assets/photo.jpg" alt="%s" width="184" height="230">'
            '<ul class="profiles">%s</ul></figure>' % (alt, "".join(items)))

def home(lang):
    if lang=="zh":
        return f"""<p class="lbl">北京大学 · 光华管理学院</p>
<h1>关于信念、信息与工作的实地实验</h1>
{portrait(lang)}
<p>我是北京大学光华管理学院经济学副教授，同时担任 <a class="lk" href="https://www.povertyactionlab.org/invited-researchers" rel="noopener">J-PAL</a> 特邀研究员与 <a class="lk" href="https://www.iza.org/en/people/fellows/27501/lukas-hensel" rel="noopener">IZA</a> 研究员。我主要采用自然实地实验的方法，研究人们如何形成关于劳动力市场的信念——关于自身的比较优势、关于雇主看重什么、关于其他人正在做什么——以及当这些信念出现偏差时，他们的职业发展会因此付出怎样的代价。</p>
<p>我的田野工作主要在埃塞俄比亚、南非、中国与越南展开，研究对象包括求职者、工厂工人与企业。另一条研究脉络关注管理者：你被分配到什么样的直接主管，会在多大程度上影响你多年之后的职业发展。第三条脉络把同样的实验方法用于政治行为：人们为何走上街头参与集会，以及在做出决定之前，他们对人群规模与他人动机的判断起到什么作用。</p>
<p>已发表的论文见<a class="lk" href="/zh/publications">发表论文</a>；工作论文与正在进行的田野项目见<a class="lk" href="/zh/work-in-progress">在研工作</a>。</p>

<h2 class="sec">联系方式</h2>
<ul class="cvlist">
  <li><span>邮箱</span><div><a class="lk" href="mailto:{EMAIL}">{EMAIL}</a></div></li>
  <li><span>办公时间</span><div>{OFFICE_HOURS_ZH}</div></li>
</ul>
<p class="meta">学生如需推荐信，请先阅读<a class="lk" href="/zh/references">推荐信</a>页面；关于论文指导，请见<a class="lk" href="/zh/teaching">教学与指导</a>页面。</p>"""
    return f"""<p class="lbl">Peking University &middot; Guanghua</p>
<h1>Field experiments on beliefs, information, and work</h1>
{portrait(lang)}
<p class="drop">I am an Associate Professor of Economics at the Guanghua School of Management, Peking University, a <a class="lk" href="https://www.povertyactionlab.org/invited-researchers" rel="noopener">J-PAL</a> Invited Researcher, and an <a class="lk" href="https://www.iza.org/en/people/fellows/27501/lukas-hensel" rel="noopener">IZA</a> Research Fellow. My work uses natural field experiments to study how people form beliefs about the labour market &mdash; about their own comparative advantage, about what employers want, about what everyone else is doing &mdash; and what happens to their careers when those beliefs are wrong.</p>
<p>Most of my field work runs in Ethiopia, South Africa, China, and Vietnam, with jobseekers, factory workers, and firms. A second strand is about managers: how much the quality of the manager you happen to be assigned shapes your own career years later. A third asks the same questions of political behaviour &mdash; why people turn out for a protest, and what they believe about the crowd before they do.</p>
<p>Published articles are on <a class="lk" href="/publications">Publications</a>; drafts and field work still under way are on <a class="lk" href="/work-in-progress">Work in Progress</a>.</p>

<h2 class="sec">How to get in touch</h2>
<ul class="cvlist">
  <li><span>Email</span><div><a class="lk" href="mailto:{EMAIL}">{EMAIL}</a></div></li>
  <li><span>Office hours</span><div>{OFFICE_HOURS_EN}</div></li>
</ul>
<p class="meta">Students asking for a letter should read the <a class="lk" href="/references">Reference letters</a> page first; on thesis supervision, see <a class="lk" href="/teaching">Teaching and Supervision</a>.</p>"""

def pubs(lang):
    lbl="同行评议论文" if lang=="zh" else "Peer-reviewed articles"
    h="发表论文" if lang=="zh" else "Publications"
    return f'<p class="lbl">{lbl}</p>\n<h1>{h}</h1>\n<div class="entries">\n'+"\n".join(entry(p,lang) for p in PUBS)+"\n</div>"

def wip(lang):
    lbl="审稿中与田野进行中" if lang=="zh" else "Under review and in the field"
    h="在研工作" if lang=="zh" else "Work in Progress"
    g1="工作论文" if lang=="zh" else "Working papers"
    g2="进行中" if lang=="zh" else "In progress"
    return (f'<p class="lbl">{lbl}</p>\n<h1>{h}</h1>\n'
            f'<p class="group">{g1}</p>\n<div class="entries">\n'+"\n".join(entry(p,lang) for p in WPS)+"\n</div>\n"
            f'<p class="group">{g2}</p>\n<div class="entries">\n'+"\n".join(entry(p,lang) for p in WIP)+"\n</div>")

def teaching(lang):
    if lang=="zh":
        return f"""<p class="lbl">北京大学光华管理学院</p>
<h1>教学与指导</h1>

<h2 class="sec">课程</h2>
<div class="courses">
  <div class="course"><div class="cname">发展经济学</div><div>
    <p class="cmeta">本科生与研究生 · 3 学分 · 2026 年秋季学期</p>
    <p>课程从发展、贫困与不平等的基本事实出发，回顾并批判性地讨论经济增长与贫困陷阱的基础理论，然后进入实证研究最活跃的若干领域：教育、迁移、劳动力市场、健康、信贷与企业、农业、扶贫项目、环境与气候，以及性别。贯穿全课程的是发展经济学常用的计量方法——随机对照试验、双重差分与断点回归——并用 Stata 做实际操作。研究生还需撰写并展示一份研究计划。</p>
  </div></div>
  <div class="course"><div class="cname">经管学术研讨会</div><div>
    <p class="cmeta">“未来领导者”国际本科项目 · 2 学分 · 2026 年秋季学期</p>
    <p>面向“未来领导者”国际本科项目的学生，目标是为本科毕业论文做好准备。课程采用讲授与学生报告相结合的形式，内容包括如何把兴趣转化为可研究的问题、如何使用学术数据库与梳理文献、如何收集与分析数据，以及如何撰写、引用与展示研究成果。</p>
  </div></div>
</div>
<p class="meta">课程大纲、阅读材料与作业通过北京大学教学网发布，选课学生可直接登录查看。</p>

<h2 class="sec">论文指导</h2>
<p>我指导本科、硕士与博士论文。指导过程全部使用英文——我无法指导以中文写作的论文。</p>
<p>我的学生大多研究广义上的应用微观经济学问题，并且带有较强的实证成分。这个范围比我自己的研究要宽得多：近年的论文题目包括地方法院的省级管理如何影响劳动争议与企业存续、工会如何影响企业减税红利的分配、美国医保扩大 GLP-1 药物覆盖的财政影响、基于世界银行企业调查的企业层面证据，以及人民币成为全球储备货币的前景。只要你的问题能用数据来回答，基本都在范围之内。</p>
<p>我看重的是你真正关心的问题，以及一条可信的回答路径——而不是题目是否贴近我自己的论文。如果你还不确定自己的想法是否成熟，那通常正是开始交谈的好时机。</p>
<p><b>如何联系我：</b>发邮件给我，说明你大致想研究什么。不需要写成正式的开题报告——一段话，说明你感兴趣的问题、为什么感兴趣，以及你设想可能用到的数据，就足够了。</p>
<p><b>博士生。</b>如果你考虑由我指导博士论文，请来信预约一次一对一面谈。博士阶段对双方都是长期投入，值得先坐下来谈一次，而不是只交换邮件。</p>
<p class="meta">邮箱：<a class="lk" href="mailto:{EMAIL}">{EMAIL}</a>。需要推荐信请见<a class="lk" href="/zh/references">推荐信</a>页面。</p>"""
    return f"""<p class="lbl">Guanghua School of Management</p>
<h1>Teaching and Supervision</h1>

<h2 class="sec">Courses</h2>
<div class="courses">
  <div class="course"><div class="cname">Development Economics</div><div>
    <p class="cmeta">Undergraduate and graduate &middot; 3 credits &middot; Autumn 2026</p>
    <p>The course opens with the facts about development, poverty and inequality, then works through the basic theories of growth and poverty traps before turning to the areas where most of the empirical work happens: education, migration, labour markets, health, credit and firms, agriculture, poverty alleviation programmes, environment and climate, and gender. Running alongside is the econometric toolkit development economists actually use &mdash; randomised controlled trials, difference-in-differences, regression discontinuity &mdash; applied in Stata. Graduate students also draft and present a research proposal.</p>
  </div></div>
  <div class="course"><div class="cname">Research Seminar</div><div>
    <p class="cmeta">Future Leaders international undergraduate programme &middot; 2 credits &middot; Autumn 2026</p>
    <p>For students in the Future Leaders international undergraduate programme, and built to prepare you for your undergraduate thesis. It runs as a mix of short lectures and student presentations: turning an interest into a research question, finding your way around academic databases and existing literature, collecting and analysing data, and writing, citing and presenting the result.</p>
  </div></div>
</div>
<p class="meta">Syllabi, readings, and problem sets are distributed through Peking University&rsquo;s course platform, which enrolled students can access directly.</p>

<h2 class="sec">Supervision</h2>
<p>I supervise Bachelor, Master, and PhD theses. All supervision is in English &mdash; I am not able to supervise a thesis written in Chinese.</p>
<p>Most of my students work on applied microeconomics, very broadly defined, with a strong empirical component. That is a wider tent than my own research. Recent theses have looked at how provincial management of local courts shapes labour disputes and firm survival, how trade unions affect the distribution of corporate tax cut windfalls, the fiscal impact of expanding Medicare coverage of GLP-1 drugs, firm-level evidence from the World Bank Enterprise Surveys, and the renminbi&rsquo;s prospects as a global reserve currency. If your question can be taken to data, it is probably in scope.</p>
<p>What I look for is a question you care about and a credible way of answering it &mdash; not a topic close to my own papers. If you are not sure whether your idea is far enough along, that is usually a good moment to come and talk.</p>
<p><b>How to approach me:</b> email me with a rough idea of what you would like to work on. It does not need to be a formal proposal &mdash; a paragraph saying what question interests you, why, and what data you imagine using is sufficient.</p>
<p><b>PhD students.</b> If you are considering writing your PhD with me, write to arrange a one-on-one meeting. A doctorate is a long commitment on both sides and is worth an hour of conversation rather than an exchange of emails.</p>
<p class="meta">Write to <a class="lk" href="mailto:{EMAIL}">{EMAIL}</a>. If you need a letter of reference, see the <a class="lk" href="/references">Reference letters</a> page.</p>"""

def references(lang):
    if lang=="zh":
        return f"""<p class="lbl">致学生</p>
<h1>推荐信</h1>
<p>下面写清楚了我可以为谁写推荐信、如何提出请求，以及需要提供哪些材料。事先读一遍，能让我写出更有分量的信。</p>

<p class="group">我可以为谁写</p>
<p>我为我教过或指导过、并且我能具体谈论其学术表现的学生写推荐信。通常意味着：你修读过我的课程并取得了不错的成绩，或由我指导完成论文，或担任过我的研究助理，或所在年级由我担任班主任。</p>
<p>如果以上都不适用，我写出来的信会很空泛。一封来自真正了解你工作的老师的信，对你的申请帮助大得多。</p>

<p class="group">如何提出请求</p>
<p>请发邮件至 <a class="lk" href="mailto:{EMAIL}">{EMAIL}</a>，邮件主题写明「推荐信申请」，<b>至少提前两周</b>，以最早的截止日期为准。邮件中请说明：申请的项目或职位、每一封信的截止日期，以及提交方式（在线系统、邮件或上传）。</p>

<p class="group">请随邮件附上</p>
<ul class="cvlist">
  <li><span>简历</span><div>最新版本</div></li>
  <li><span>成绩单</span><div>非正式版本即可</div></li>
  <li><span>个人陈述</span><div>草稿也可以，我需要知道你打算如何介绍自己</div></li>
  <li><span>希望我强调的内容</span><div>你在我课上写的论文、参与的项目、获得的奖项，或任何材料中看不出、但你希望我提到的背景</div></li>
</ul>

<p class="group">之后</p>
<p>我会在几天内回复是否能写。如果我认为自己写不出一封有力的推荐信，我会直接告诉你，而不是写一封平淡的信——这对你更有利。一旦答应，请在临近截止日期时提醒我一次，这样的提醒我一向欢迎。</p>"""
    return f"""<p class="lbl">For students</p>
<h1>Reference letters</h1>
<p>What follows is who I can write for, how to ask, and what to send. Reading it first makes the letter I write a better one.</p>

<p class="group">Who I can write for</p>
<p>I write letters for students I have taught or supervised and whose work I can speak to concretely. In practice that means you took one of my courses and did well in it, wrote a thesis under my supervision, worked with me as a research assistant, or were in a cohort I looked after as cohort mentor (班主任).</p>
<p>If none of those apply, anything I write will be thin. A specific letter from someone who knows your work will serve you considerably better than a general one from me.</p>

<p class="group">How to ask</p>
<p>Email me at <a class="lk" href="mailto:{EMAIL}">{EMAIL}</a> with &ldquo;Reference request&rdquo; in the subject line, <b>at least two weeks</b> before your earliest deadline. Tell me what you are applying for, the deadline for each letter, and how it is submitted &mdash; a portal, an email address, or a file you upload yourself.</p>

<p class="group">What to send with the request</p>
<ul class="cvlist">
  <li><span>CV</span><div>Current version</div></li>
  <li><span>Transcript</span><div>An unofficial copy is fine</div></li>
  <li><span>Letter of motivation</span><div>A draft is fine &mdash; I need to see how you are describing yourself</div></li>
  <li><span>Anything to highlight</span><div>A paper you wrote for me, a project, an award, or context the rest of the file does not show</div></li>
</ul>

<p class="group">What happens then</p>
<p>I will tell you within a few days whether I can write. If I do not think I can write you a strong letter I will say so rather than send a lukewarm one, which is the better outcome for you. Once I have agreed, a single reminder as the deadline approaches is always welcome.</p>"""

def cv(lang):
    if lang=="zh":
        return '''<p class="lbl">简历</p>
<h1>个人简历</h1>
<p><a class="cta" href="/cv.pdf">下载完整简历（PDF）</a></p>
<p class="group">现任职务</p>
<ul class="cvlist">
  <li><span>2026 —</span><div>经济学副教授，北京大学光华管理学院</div></li>
  <li><span>2023 — 2026</span><div>经济学助理教授，北京大学光华管理学院</div></li>
  <li><span>2021 — 2023</span><div>博士后研究员，北京大学光华管理学院</div></li>
</ul>
<p class="group">学术兼职</p>
<ul class="cvlist">
  <li><span>&nbsp;</span><div>J-PAL 特邀研究员</div></li>
  <li><span>&nbsp;</span><div>IZA 劳动经济研究所研究员</div></li>
</ul>
<p class="group">教育背景</p>
<ul class="cvlist">
  <li><span>牛津大学</span><div>经济学博士（DPhil）与硕士（MPhil）；曾访学于加州大学伯克利分校</div></li>
  <li><span>图宾根大学</span><div>国际经济学学士；曾交换于美国塔夫茨大学</div></li>
</ul>
<p class="meta">简历最后更新日期见 PDF 首页。</p>'''
    return '''<p class="lbl">Curriculum vitae</p>
<h1>CV</h1>
<p><a class="cta" href="/cv.pdf">Download the full CV (PDF)</a></p>
<p class="group">Positions</p>
<ul class="cvlist">
  <li><span>2026 —</span><div>Associate Professor of Economics, Guanghua School of Management, Peking University</div></li>
  <li><span>2023 &ndash; 2026</span><div>Assistant Professor of Economics, Guanghua School of Management</div></li>
  <li><span>2021 &ndash; 2023</span><div>Postdoctoral Researcher, Guanghua School of Management</div></li>
</ul>
<p class="group">Affiliations</p>
<ul class="cvlist">
  <li><span>&nbsp;</span><div>J-PAL Invited Researcher</div></li>
  <li><span>&nbsp;</span><div>IZA Research Fellow</div></li>
</ul>
<p class="group">Education</p>
<ul class="cvlist">
  <li><span>Oxford</span><div>DPhil and MPhil in Economics; visiting researcher at UC Berkeley</div></li>
  <li><span>T&uuml;bingen</span><div>BSc in International Economics; exchange at Tufts University</div></li>
</ul>
<p class="meta">The PDF carries the date it was last revised.</p>'''

PAGES=[("", home, "Lukas Hensel", "Lukas Hensel — 北京大学光华管理学院 经济学副教授",
        "Associate Professor of Economics at Guanghua School of Management, Peking University. Field experiments on beliefs, information, and labour markets.",
        "北京大学光华管理学院经济学副教授。研究方向为劳动与发展经济学领域的自然实地实验。"),
       ("publications", pubs, "Publications · Lukas Hensel", "发表论文 · Lukas Hensel",
        "Peer-reviewed articles by Lukas Hensel, with abstracts, ungated versions, and replication packages.",
        "Lukas Hensel 的同行评议论文，附摘要、免费版本与复现材料。"),
       ("work-in-progress", wip, "Work in Progress · Lukas Hensel", "在研工作 · Lukas Hensel",
        "Working papers and field projects in progress.", "工作论文与正在进行的田野项目。"),
       ("teaching", teaching, "Teaching and Supervision · Lukas Hensel", "教学与指导 · Lukas Hensel",
        "Courses at Guanghua, and how to approach me about a Bachelor, Master or PhD thesis.",
        "在光华管理学院讲授的课程，以及如何就本科、硕士与博士论文指导与我联系。"),
       ("references", references, "Reference letters · Lukas Hensel", "推荐信 · Lukas Hensel",
        "How to request a letter of reference: who I can write for, how to ask, and what to send.",
        "如何申请推荐信：我可以为谁写、如何提出请求、需要提供哪些材料。"),
       ("cv", cv, "CV · Lukas Hensel", "个人简历 · Lukas Hensel",
        "Positions, affiliations, and education. Full CV as a PDF.", "任职经历、学术兼职与教育背景，完整简历见 PDF。")]

def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    io.open(path,"w",encoding="utf-8").write(text)

n=0
for slug, fn, t_en, t_zh, d_en, d_zh in PAGES:
    for lang in ("en","zh"):
        title = t_zh if lang=="zh" else t_en
        desc  = d_zh if lang=="zh" else d_en
        html  = head(lang,slug,title,desc)+header(lang,slug)+fn(lang)+footer(lang, profiles=(slug!=""))
        out = ("zh/" if lang=="zh" else "")+((slug+".html") if slug else "index.html")
        write(out, html); n+=1

# 404
for lang in ("en","zh"):
    msg = ("<h1>页面不存在</h1><p>你要找的页面已被移动或从未存在。请从<a class=\"lk\" href=\"/zh/\">首页</a>重新开始。</p>"
           if lang=="zh" else
           "<h1>Page not found</h1><p>The page you asked for has moved or never existed. Start again from the <a class=\"lk\" href=\"/\">home page</a>.</p>")
    html = head(lang,"","Page not found · Lukas Hensel" if lang=="en" else "页面不存在 · Lukas Hensel","")+header(lang,"")+msg+footer(lang)
    write(("zh/404.html" if lang=="zh" else "404.html"), html); n+=1

# robots + sitemap
write("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)
urls=[]
for slug,_,_,_,_,_ in PAGES:
    for lang in ("en","zh"):
        urls.append(SITE+url(lang,slug))
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sm+="".join('  <url><loc>%s</loc></url>\n'%u for u in urls)+'</urlset>\n'
write("sitemap.xml", sm)
print("wrote", n, "pages")

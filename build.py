# -*- coding: utf-8 -*-
import os, io, shutil
from data import PUBS, WPS, WIP

SITE="https://lukashensel.com"
EMAIL="lukas.hensel@gsm.pku.edu.cn"

NAV=[("","Home","首页"),("publications","Publications","发表论文"),
     ("work-in-progress","Work in Progress","在研工作"),
     ("teaching","Teaching","教学"),("cv","CV","个人简历")]

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

def footer(lang):
    if lang=="zh":
        return f'''</main>
<footer>
北京大学光华管理学院 · 北京 &nbsp;·&nbsp; <a href="mailto:{EMAIL}">{EMAIL}</a><br>
另见 <a href="https://scholar.google.com/citations?user=_swX_6kAAAAJ">Google Scholar</a>、
<a href="https://www.iza.org/en/people/fellows/27501/lukas-hensel">IZA</a>、
<a href="https://cepr.org/about/people/lukas-hensel">CEPR</a>、
<a href="https://www.povertyactionlab.org/invited-researchers">J-PAL</a> 与
<a href="https://bsky.app/profile/lukashenselecon.bsky.social">Bluesky</a>。
</footer>
</body>
</html>'''
    return f'''</main>
<footer>
Guanghua School of Management, Peking University, Beijing &nbsp;·&nbsp; <a href="mailto:{EMAIL}">{EMAIL}</a><br>
Also on <a href="https://scholar.google.com/citations?user=_swX_6kAAAAJ">Google Scholar</a>,
<a href="https://www.iza.org/en/people/fellows/27501/lukas-hensel">IZA</a>,
<a href="https://cepr.org/about/people/lukas-hensel">CEPR</a>,
<a href="https://www.povertyactionlab.org/invited-researchers">J-PAL</a> and
<a href="https://bsky.app/profile/lukashenselecon.bsky.social">Bluesky</a>.
</footer>
</body>
</html>'''

def entry(p,lang):
    yr = p.get("yz",p["y"]) if lang=="zh" else p["y"]
    au = p["a_zh"] if lang=="zh" else "with "+p["a_en"]
    ven = p.get("vz",p["v"]) if lang=="zh" else p["v"]
    vs = (" &middot; "+p["vs"]) if p.get("vs") and lang=="en" else (", "+p["vs"] if p.get("vs") else "")
    flag=""
    if p.get("flag"):
        flag=f'<span class="flag">{"即将发表" if lang=="zh" else "Forthcoming"}</span>'
    sep = "，" if lang=="zh" else " &middot; "
    line=f'{au}{sep}<b>{ven}</b>{vs}{flag}'
    out=[f'<article class="entry"><div class="yr">{yr}</div><div>',
         f'<h2 class="ti">{p["t"]}</h2>',
         f'<p class="au">{line}</p>']
    if p.get("ab"):
        lab="摘要" if lang=="zh" else "Abstract"
        out.append(f'<details class="abs"><summary><span class="car">&#9656;</span>{lab}</summary>'
                   f'<div class="body"><p>{p["ab"]}</p></div></details>')
    if p["links"]:
        parts=[]
        for en,zh,u in p["links"]:
            ext=' rel="noopener"' if u.startswith("http") else ""
            parts.append(f'<a href="{u}"{ext}>{zh if lang=="zh" else en}</a>')
        out.append('<div class="acts">'+'<span class="sep">·</span>'.join(parts)+'</div>')
    out.append('</div></article>')
    return "\n".join(out)

SHOT='<img class="shot" src="/assets/photo.jpg" alt="Lukas Hensel" width="120" height="150">'

def home(lang):
    if lang=="zh":
        body=f'''<p class="lbl">北京大学 · 光华管理学院</p>
<h1>关于信念、信息与工作的实地实验</h1>
{SHOT}
<p>我是北京大学光华管理学院经济学副教授，同时担任 J-PAL 特邀研究员与 IZA 研究员。我主要采用自然实地实验的方法，研究人们如何形成关于劳动力市场的信念——关于自身的比较优势、关于雇主看重什么、关于其他人正在做什么——以及当这些信念出现偏差时，他们的职业发展会因此付出怎样的代价。</p>
<p>我的田野工作主要在埃塞俄比亚、南非、中国与越南展开，研究对象包括求职者、工厂工人与企业。另一条研究脉络将同样的实验方法用于政治行为：人们为何走上街头参与集会，以及在做出决定之前，他们对人群规模与他人动机的判断起到什么作用。</p>
<hr>
<p class="lbl">精选研究</p>
<div class="entries">
{entry(PUBS[0],lang)}
{entry(WPS[1],lang)}
{entry(PUBS[1],lang)}
</div>
<hr>
<p class="meta">完整列表见<a class="lk" href="/zh/publications">发表论文</a>与<a class="lk" href="/zh/work-in-progress">在研工作</a>。</p>'''
        return body
    body=f'''<p class="lbl">Peking University &middot; Guanghua</p>
<h1>Field experiments on beliefs, information, and work</h1>
{SHOT}
<p class="drop">I am an Associate Professor of Economics at the Guanghua School of Management, Peking University, a J-PAL Invited Researcher, and an IZA Research Fellow. My work uses natural field experiments to study how people form beliefs about the labour market &mdash; about their own comparative advantage, about what employers want, about what everyone else is doing &mdash; and what happens to their careers when those beliefs are wrong.</p>
<p>Most of my field work runs in Ethiopia, South Africa, China, and Vietnam, with jobseekers, factory workers, and firms. A second strand of my research asks the same question of political behaviour: why people turn out for a protest, and what they believe about the crowd before they do.</p>
<hr>
<p class="lbl">Selected work</p>
<div class="entries">
{entry(PUBS[0],lang)}
{entry(WPS[1],lang)}
{entry(PUBS[1],lang)}
</div>
<hr>
<p class="meta">Full lists on <a class="lk" href="/publications">Publications</a> and <a class="lk" href="/work-in-progress">Work in Progress</a>.</p>'''
    return body

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
        return '''<p class="lbl">北京大学光华管理学院</p>
<h1>教学</h1>
<p>我在光华管理学院讲授本科与研究生课程。课程大纲、阅读材料与作业通过北京大学教学网发布，选课学生可直接登录查看。</p>
<p>有意以我为导师撰写论文的学生，请先阅读<a class="lk" href="/zh/work-in-progress">在研工作</a>页面，再来信说明你希望研究的问题。</p>
<!-- 课程列表：按下面的格式增加条目即可
<p class="group">课程</p>
<ul class="cvlist">
  <li><span>2026 春</span><div>课程名称 · 本科 / 硕士 / 博士</div></li>
</ul>
-->
<p class="meta">课程相关问题请发送邮件至 <a class="lk" href="mailto:lukas.hensel@gsm.pku.edu.cn">lukas.hensel@gsm.pku.edu.cn</a>。</p>'''
    return '''<p class="lbl">Guanghua School of Management</p>
<h1>Teaching</h1>
<p>I teach undergraduate and graduate courses at Guanghua. Syllabi, readings, and problem sets are distributed through Peking University&rsquo;s course platform, which enrolled students can access directly.</p>
<p>Students interested in writing a thesis with me should read the <a class="lk" href="/work-in-progress">Work in Progress</a> page first, then write to me with the question they want to work on.</p>
<!-- Course list: add entries in this format
<p class="group">Courses</p>
<ul class="cvlist">
  <li><span>Spring 2026</span><div>Course title &middot; undergraduate / MSc / PhD</div></li>
</ul>
-->
<p class="meta">Questions about a course: <a class="lk" href="mailto:lukas.hensel@gsm.pku.edu.cn">lukas.hensel@gsm.pku.edu.cn</a>.</p>'''

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
  <li><span>&nbsp;</span><div>CEPR 研究成员</div></li>
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
  <li><span>&nbsp;</span><div>CEPR Research Affiliate</div></li>
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
       ("teaching", teaching, "Teaching · Lukas Hensel", "教学 · Lukas Hensel",
        "Courses taught at Guanghua School of Management, Peking University.", "在北京大学光华管理学院讲授的课程。"),
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
        html  = head(lang,slug,title,desc)+header(lang,slug)+fn(lang)+footer(lang)
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

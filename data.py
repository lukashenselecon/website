# -*- coding: utf-8 -*-
# Paper PDFs.
#   pdf("name.pdf", "https://fallback")  ->  uses /papers/name.pdf if that file
#   exists in the repo, otherwise falls back to the external URL.
#   So: drop a PDF into papers/ with the matching name and the link switches
#   to your own domain automatically on the next deploy. Nothing else to change.
import os
P = "/papers/"
def pdf(name, ext):
    return P + name if os.path.exists(os.path.join("papers", name)) else ext

PUBS = [
 dict(y="2026", t="Formalized Employee Search and Labor Demand",
  a_en="Tsegay Tekleselassie &amp; Marc Witte", a_zh="与 Tekleselassie、Witte 合著",
  authors=["Lukas Hensel","Tsegay Tekleselassie","Marc Witte"],
  v="Journal of Development Economics", flag=True,
  ab="Firms in low- and middle-income countries rarely advertise their vacancies formally and instead use social networks to find employees. We experimentally reduce the cost of formal employee search for small and medium-sized enterprises in Ethiopia to test whether informal search constrains the number and type of positions firms create. We find that treated firms increase formal search and shift their labor demand towards more demanding white-collar positions. However, they struggle to fill these newly created vacancies. We provide suggestive evidence that expectations contribute to this result, especially when firms lack prior experience with formal hiring channels: firms appear overly optimistic about the applicant pools formal search will generate, and jobseekers&rsquo; wage expectations exceed firms&rsquo; wages.",
  links=[("gated","期刊版本","https://doi.org/10.1016/j.jdeveco.2026.103876"),
         ("ungated","免费版本",pdf("formalized-employee-search.pdf","https://github.com/Luthor113/papers/raw/main/Hensel_Formal_Hiring_Processes.pdf")),
         ("replication package","复现材料","https://doi.org/10.17632/2fmcrwrt94.1")]),

 dict(y="2025", t="Voice and Political Engagement: Evidence from a Field Experiment",
  a_en="Anselm Hager, Christopher Roth &amp; Andreas Stegmann", a_zh="与 Hager、Roth、Stegmann 合著",
  authors=["Anselm Hager","Lukas Hensel","Christopher Roth","Andreas Stegmann"],
  v="Review of Economics and Statistics", vs="107(4), 1149&ndash;1158",
  ab="We conduct a natural field experiment with a major European party to test whether giving party supporters more voice increases their engagement in the party&rsquo;s electoral campaign. In the experiment, the party asked a random subset of supporters for their opinions on the importance of different policy areas. Giving supporters opportunities to voice their opinions increases their engagement in the campaign as measured using behavioral data from the party&rsquo;s smartphone application. Survey data reveals that giving voice also increases other margins of campaign effort as well as perceived voice. Our evidence highlights the importance of voice for increasing political engagement.",
  links=[("gated","期刊版本","https://direct.mit.edu/rest/article/doi/10.1162/rest_a_01320/115256/Voice-and-Political-Engagement-Evidence-from-a"),
         ("ungated","免费版本",pdf("voice-political-engagement.pdf","https://www.econtribute.de/RePEc/ajk/ajkdps/ECONtribute_133_2021.pdf")),
         ("replication package","复现材料","https://doi.org/10.7910/DVN/WCGYI2")]),

 dict(y="2025", t="Political Activists are Not Driven by Instrumental Motives",
  a_en="Anselm Hager, Johannes Hermle &amp; Christopher Roth", a_zh="与 Hager、Hermle、Roth 合著",
  authors=["Anselm Hager","Lukas Hensel","Johannes Hermle","Christopher Roth"],
  v="British Journal of Political Science", vs="55, e88",
  ab="Are political activists driven by instrumental motives such as making a career in politics or mobilizing voters? We implement two natural field experiments in which party activists are randomly informed that canvassing is i) effective at mobilizing voters, or ii) effective for enhancing activists&rsquo; political careers. We find no effect of the treatments on activists&rsquo; intended and actual canvassing behaviour. The null finding holds despite a successful manipulation check and replication study, high statistical power, a natural field setting, and an unobtrusive measurement strategy. Using an expert survey, we show that the null finding shifted Bayesian posterior beliefs about the treatment&rsquo;s effectiveness toward zero. The evidence thus casts doubt on two popular hypothesized instrumental drivers of political activism &ndash; voter persuasion and career concerns &ndash; and points toward expressive benefits as more plausible motives.",
  links=[("open access","开放获取","https://www.cambridge.org/core/journals/british-journal-of-political-science/article/political-activists-are-not-driven-by-instrumental-motives-evidence-from-two-natural-field-experiments/48F339234B1B450641A65A420AC6D3FD"),
         ("replication package","复现材料","https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/GDOPMX")]),

 dict(y="2023", t="Political Activists as Free-Riders",
  a_en="Anselm Hager, Johannes Hermle &amp; Christopher Roth", a_zh="与 Hager、Hermle、Roth 合著",
  authors=["Anselm Hager","Lukas Hensel","Johannes Hermle","Christopher Roth"],
  v="The Economic Journal", vs="133, 2068&ndash;2084",
  ab="How does a citizen&rsquo;s decision to participate in political activism depend on the participation of others? We conduct a nationwide natural field experiment in collaboration with a major European party during a recent national election. In a party survey, we randomly provide canvassers with true information about the canvassing intentions of their peers. When learning that more peers participate in canvassing than previously believed, canvassers significantly reduce both their canvassing intentions and behaviour. An additional survey among party supporters underscores the importance of free-riding motives and reveals that there is strong heterogeneity in motives underlying supporters&rsquo; behavioural responses.",
  links=[("gated","期刊版本","https://doi.org/10.1093/ej/uead020"),
         ("ungated","免费版本",pdf("political-activists-free-riders.pdf","https://github.com/Luthor113/papers/raw/main/Hensel_Political_Activists.pdf")),
         ("replication package","复现材料","https://doi.org/10.5281/zenodo.7663389")]),

 dict(y="2022", t="Group Size and Protest Mobilization across Movements and Countermovements",
  a_en="Anselm Hager, Johannes Hermle &amp; Christopher Roth", a_zh="与 Hager、Hermle、Roth 合著",
  authors=["Anselm Hager","Lukas Hensel","Johannes Hermle","Christopher Roth"],
  v="American Political Science Review", vs="116(3), 1051&ndash;1066",
  ab="Many social movements face fierce resistance in the form of a countermovement. Therefore, when deciding to become politically active, a movement supporter has to consider both her own movement&rsquo;s activity and that of the opponent. This paper studies the decision of a movement supporter to attend a protest when faced with a counterprotest. We implement two field experiments among supporters of a right- and left-leaning movement ahead of two protest&ndash;counterprotest interactions in Germany. Supporters were exposed to low or high official estimates about their own and the opposing group&rsquo;s turnout. We find that the size of the opposing group has no effect on supporters&rsquo; protest intentions. However, as the own protest gets larger, supporters of the right-leaning movement become less while supporters of the left-leaning movement become more willing to protest. We argue that the difference is best explained by stronger social motives on the political left.",
  links=[("open access","开放获取","https://www.cambridge.org/core/journals/american-political-science-review/article/group-size-and-protest-mobilization-across-movements-and-countermovements/258264834D40B96C3253CB7CF6671CE5"),
         ("replication package","复现材料","https://doi.org/10.7910/DVN/MUSFYH")]),

 dict(y="2022", t="Global Behaviors, Perceptions, and the Emergence of Social Norms at the Onset of the COVID-19 Pandemic",
  a_en="Marc Witte, A. Stefano Caria, Thiemo Fetzer, Stefano Fiorin et al.", a_zh="与 Witte、Caria、Fetzer、Fiorin 等合著", etal=True,
  authors=["Lukas Hensel","Marc Witte","A. Stefano Caria","Thiemo Fetzer","Stefano Fiorin"],
  v="Journal of Economic Behavior and Organization", vs="193, 473&ndash;496",
  ab="We conducted a large-scale survey covering 58 countries and over 100,000 respondents between late March and early April 2020 to study beliefs and attitudes towards citizens&rsquo; and governments&rsquo; responses at the onset of the COVID-19 pandemic. Most respondents reported holding normative beliefs in support of COVID-19 containment measures, as well as high rates of adherence to these measures. They also believed that their government and their country&rsquo;s citizens were not doing enough and underestimated the degree to which others in their country supported strong behavioral and policy responses to the pandemic. Normative beliefs were strongly associated with adherence, as well as beliefs about others&rsquo; and the government&rsquo;s response. Lockdowns were associated with greater optimism about others&rsquo; and the government&rsquo;s response, and improvements in measures of perceived mental well-being; these effects tended to be larger for those with stronger normative beliefs. Our findings highlight how social norms can arise quickly and effectively to support cooperation at a global scale.",
  links=[("gated","期刊版本","https://www.sciencedirect.com/science/article/pii/S016726812100487X"),
         ("ungated","免费版本",pdf("global-behaviors-covid.pdf","https://github.com/Luthor113/papers/raw/main/Hensel_etal_2022_Global_COVID.pdf")),
         ("data and analysis files","数据与分析文件","https://osf.io/3sn2k/")]),

 dict(y="2021", t="Coronavirus Perceptions and Economic Anxiety",
  a_en="Thiemo Fetzer, Johannes Hermle &amp; Christopher Roth", a_zh="与 Fetzer、Hermle、Roth 合著",
  authors=["Thiemo Fetzer","Lukas Hensel","Johannes Hermle","Christopher Roth"],
  v="Review of Economics and Statistics", vs="103(5), 968&ndash;978",
  ab="We provide one of the first systematic assessments of the development and determinants of economic anxiety at the onset of the coronavirus pandemic. Using a global data set on internet searches and two representative surveys from the United States, we document a substantial increase in economic anxiety during and after the arrival of the coronavirus. We also document a large dispersion in beliefs about the pandemic risk factors of the coronavirus and demonstrate that these beliefs causally affect individuals&rsquo; economic anxieties. Finally, we show that individuals&rsquo; mental models of infectious disease spread understate nonlinear growth and shape the extent of economic anxiety.",
  links=[("gated","期刊版本","https://www.mitpressjournals.org/doi/abs/10.1162/rest_a_00946"),
         ("ungated","免费版本",pdf("coronavirus-perceptions.pdf","https://arxiv.org/abs/2003.03848")),
         ("replication package","复现材料","https://doi.org/10.7910/DVN/NGHYPI")]),

 dict(y="2021", t="Does Party Competition Affect Political Activism?",
  a_en="Anselm Hager, Johannes Hermle &amp; Christopher Roth", a_zh="与 Hager、Hermle、Roth 合著",
  authors=["Anselm Hager","Johannes Hermle","Lukas Hensel","Christopher Roth"],
  v="The Journal of Politics", vs="83(4), 1681&ndash;1694",
  ab="Does party competition affect political activism? This paper studies the decision of party supporters to join political campaigns. We present a framework that incorporates supporters&rsquo; instrumental and expressive motives and illustrates that party competition can either increase or decrease party activism. To distinguish between these competing predictions, we implemented a field experiment with a European party during a national election. In a seemingly unrelated party survey, we randomly assigned 1,417 party supporters to true information that the canvassing activity of the main competitor party was exceptionally high. Using unobtrusive, real-time data on party supporters&rsquo; canvassing behavior, we find that respondents exposed to the high-competition treatment are 30% less likely to go canvassing. To investigate the causal mechanism, we leverage additional survey evidence collected two months after the campaign. Consistent with affective accounts of political activism, we show that increased competition lowered party supporters&rsquo; political self-efficacy, which plausibly led them to remain inactive.",
  links=[("gated","期刊版本","https://doi.org/10.1086/712140"),
         ("ungated","免费版本",pdf("party-competition-activism.pdf","https://doi.org/10.1086/712140")),
         ("replication package","复现材料","https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/2KLNFX")]),

 dict(y="2019", t="Income Shocks and Suicides: Causal Evidence From Indonesia",
  a_en="Cornelius Christian &amp; Christopher Roth", a_zh="与 Christian、Roth 合著",
  authors=["Cornelius Christian","Lukas Hensel","Christopher Roth"],
  v="Review of Economics and Statistics", vs="101(5), 905&ndash;920",
  ab="We examine how income shocks affect the suicide rate in Indonesia. We use a difference-in-differences approach, exploiting the cash transfer&rsquo;s nationwide rollout, and corroborate the findings using a randomized experiment. Our estimates show that the cash transfers reduce the yearly suicide rate by 0.36 per 100,000 people, corresponding to an 18% decrease. Moreover, a different type of income shock, variability in agricultural productivity, also affects the suicide rate. The cash transfer program reduces the causal impact of the agricultural productivity shocks, suggesting an important role for policy interventions. Finally, we provide evidence for depression as a psychological mechanism.",
  links=[("gated","期刊版本","https://www.mitpressjournals.org/doi/pdf/10.1162/rest_a_00777"),
         ("ungated","免费版本",pdf("income-shocks-suicides.pdf","https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2716684")),
         ("analysis code","分析代码","https://doi.org/10.7910/DVN/ETS5LV")]),
]

WPS = [
 dict(y="R&amp;R", yz="修改重投", t="Designing Severance Insurance: Theory and Evidence from Ethiopia",
  a_en="Girum Abebe, Stefano Caria, Sara Spaziani &amp; Fran&ccedil;ois Gerard", a_zh="与 Abebe、Caria、Spaziani、Gerard 合著",
  v="Conditionally accepted based on pre-results review: Journal of Development Economics",
  vz="基于结果前评审有条件接收：Journal of Development Economics",
  authors=["Girum Abebe","Stefano Caria","Sara Spaziani","Lukas Hensel","François Gerard"], cite_year=2025,
  ab="We propose the first study testing firms&rsquo; demand for insurance against layoff costs. Job-loss insurance policies for workers, such as severance pay, impose substantial financial burdens on firms precisely when they face shocks motivating layoffs. We evaluate demand for a novel product, Severance Insurance, which protects firms against these costs, among formal employers in Addis Ababa, Ethiopia. Guided by a model of firm behavior in the presence of layoff risk and Severance Insurance, we estimate key parameters to assess the welfare effects of this product: firms&rsquo; value of insurance and adverse selection in insurance purchase. We also provide evidence of hypothetical behavioral responses to insurance, including moral hazard through increased layoffs, firm growth and workforce formalization. Our findings offer critical insights for designing employer-based social insurance policies and shed light on firms&rsquo; capacity to manage risk.",
  links=[("draft","工作论文",pdf("designing-severance-insurance.pdf","https://afosterri.org/jdepreresults/wp-content/uploads/2025/11/abebe-caria-spaziani-hensel-gerard-designing-severance-insurance-0eec1b64a5769d0280159fc16bc1fcfd.pdf"))]),

 dict(y="R&amp;R", yz="修改重投", t="Jobseekers&rsquo; Beliefs about Comparative Advantage and (Mis)Directed Search",
  a_en="Andrea Kiss, Robert Garlick &amp; Kate Orkin", a_zh="与 Kiss、Garlick、Orkin 合著",
  authors=["Andrea Kiss","Robert Garlick","Kate Orkin","Lukas Hensel"], random_order=True, cite_year=2024,
  ab="Worker sorting into tasks and occupations has long been recognized as an important feature of labor markets. But this sorting may be inefficient if jobseekers have imperfect information about their skills and therefore apply to jobs that poorly match their skills. To test this idea, we study two field experiments that give young South African jobseekers information on their results from standardized assessments of job-relevant skills. Information redirects jobseekers&rsquo; search toward jobs that value skills where they score relatively highly, without raising their search effort. Information also substantially raises earnings, consistent with inefficient sorting due to imperfect information.",
  coverage=[("VoxDev","VoxDev","https://voxdev.org/topic/labour-markets/helping-jobseekers-understand-their-skills-boosted-earnings-south-africa")],
  v="Resubmitted to AEJ: Applied", vz="已重投 AEJ: Applied",
  links=[("draft","工作论文",pdf("comparative-advantage-beliefs.pdf","https://github.com/Luthor113/papers/raw/main/comparative_advantage_beliefs_and_misdirected_search.pdf"))]),

 dict(y="2026", t="Mitigating the Consequences of Job Loss in Lower-Income Countries: Evidence from Ethiopia",
  a_en="Girum Abebe, Stefano Caria &amp; Fran&ccedil;ois Gerard", a_zh="与 Abebe、Caria、Gerard 合著",
  authors=["Lukas Hensel","Girum Abebe","François Gerard","Stefano Caria"], random_order=True,
  coverage=[("VoxDev","VoxDev","https://voxdev.org/topic/social-protection/benefits-financial-support-after-job-loss-and-why-programme-design-matters")],
  v="IZA Discussion Paper 18537 &middot; April 2026 draft", vz="IZA 讨论稿 18537 · 2026 年 4 月稿",
  ab="Job loss is an understudied risk for formal workers in lower-income countries. In these settings, lump-sum severance pay is often the only source of job-loss insurance. We quasi-experimentally show that female factory workers in Ethiopia displaced by a tariff hike experience lasting declines in employment and consumption spending, and rising poverty. Experimentally, we find that additional lump-sum support induces early spending and reduces overall and manufacturing employment persistently. Disbursing an equivalent amount in tranches improves consumption smoothing and avoids adverse employment effects. Further, we document a high willingness to pay for additional insurance, alongside heterogeneous preferences over disbursement modality that shape responses to our interventions. These findings imply that increasing job-loss insurance raises welfare, although moving away from the lump-sum default can generate substantial additional gains.",
  links=[("draft","工作论文",pdf("mitigating-job-loss-ethiopia.pdf","https://github.com/Luthor113/papers/raw/main/Hensel_%28r%29_Displacement.pdf")),
         ("IZA discussion paper","IZA 讨论稿","https://www.iza.org/publications/dp/18537")]),

 dict(y="2026", t="Feedback, Confidence and Job Search Behavior",
  a_en="Tsegay Tekleselassie, Marc Witte, Jonas Radbruch &amp; Ingo E. Isphording", a_zh="与 Tekleselassie、Witte、Radbruch、Isphording 合著",
  authors=["Tsegay Tekleselassie","Marc Witte","Jonas Radbruch","Lukas Hensel","Ingo E. Isphording"], random_order=True,
  v="IZA Discussion Paper 17761 &middot; March 2026 update", vz="IZA 讨论稿 17761 · 2026 年 3 月更新",
  ab="We conduct a field experiment with job seekers to investigate how feedback influences job search and labor market outcomes. Job seekers who receive feedback on their ability compared to other job seekers update their beliefs and increase their search effort. Specifically, initially underconfident individuals intensify their job search. In contrast, overconfident individuals do not adjust their behavior. Moreover, job seekers&rsquo; willingness-to-pay (WTP) for feedback predicts treatment effects: only among underconfident individuals with positive WTP, we observe significant increases in both search effort and search success. We present suggestive evidence that this pattern arises from heterogeneity in how job seekers perceive the relevance of relative cognitive ability to job search returns. While the intervention appears cost-effective, job seekers&rsquo; WTP remains insufficient to cover its costs.",
  # The March 2026 draft here supersedes IZA DP 17761, so that link is not shown.
  links=[("draft","工作论文",pdf("feedback-confidence-job-search.pdf","https://www.iza.org/publications/dp/17761"))]),

 dict(y="2026", t="From Followers to Leaders: The Career Impact of High-quality Managers",
  a_en="Yuyu Chen &amp; Xinjue Yao", a_zh="与 Chen、Yao 合著",
  authors=["Yuyu Chen","Lukas Hensel","Xinjue Yao"],
  ab="How does manager quality affect subordinates&rsquo; career progression? We leverage frequent worker-manager reassignments to identify the causal effect of manager quality on workers&rsquo; career outcomes in the context of managerial teams at a large construction firm. Using both difference-in-differences and instrumental variable approaches, we find that exposure to a high-quality manager increases workers&rsquo; subsequent promotion rates by 9 to 13 percentage points. We provide evidence in support of managerial human capital transmission as the primary mechanism: effects are concentrated among workers and positions that require most managerial skills, and exposed workers earn significantly higher performance-based bonuses.",
  v="January 2026 update", vz="2026 年 1 月更新",
  links=[("draft","工作论文",pdf("followers-to-leaders.pdf","https://github.com/Luthor113/papers/raw/main/Chen_etal_2026.pdf"))]),

 dict(y="2025", t="Wage Information and Applicant Selection",
  a_en="Maria Balgova, Tsegay Tekleselassie &amp; Marc Witte", a_zh="与 Balgova、Tekleselassie、Witte 合著",
  authors=["Maria Balgova","Tsegay Tekleselassie","Lukas Hensel","Marc Witte"], random_order=True,
  v="IZA Discussion Paper 18220 &middot; October 2025 update", vz="IZA 讨论稿 18220 · 2025 年 10 月更新",
  ab="Wage information is rare in job adverts, yet crucial for search. To study this information friction, we run a field experiment with real vacancies, randomly adding or withholding wage information. Disclosing wages does not change average application volumes. Instead, it amplifies the wage elasticity of applications: higher-wage vacancies receive more applicants, while lower-wage vacancies receive fewer. Average applicant quality remains unchanged, challenging standard directed search models. We rationalize the lack of skill-based sorting with two-sided limited information about applicants&rsquo; skills. We further show that firms&rsquo; decision not to post wages can act as insurance against unproductive matches.",
  links=[("draft","工作论文",pdf("wage-information-applicant-selection.pdf","https://www.dropbox.com/scl/fi/qhu428mpnbwxemjo20fq9/Balgova_-r-_Wage_information.pdf?rlkey=xmzh89fi41hxnumw15hlrtrcd&amp;dl=0")),
         ("IZA discussion paper","IZA 讨论稿","https://www.iza.org/publications/dp/18220")]),

 dict(y="2025", t="Mutual Knowledge of Social Norms and Political Behavior",
  a_en="Anselm Hager, Elnura Kazakbaeva &amp; Damir Esenaliev", a_zh="与 Hager、Kazakbaeva、Esenaliev 合著",
  authors=["Anselm Hager","Elnura Kazakbaeva","Lukas Hensel","Damir Esenaliev"], random_order=True,
  v="IZA Discussion Paper 17748 &middot; March 2025 update", vz="IZA 讨论稿 17748 · 2025 年 3 月更新",
  ab="Social norms are crucial drivers of human behavior. However, misperceptions of others&rsquo; opinions may sustain norms and conforming behavior even if a majority opposes the norm. Privately shifting individuals&rsquo; beliefs about true societal support may be insufficient to change behavior if others are perceived to continue to hold incorrect beliefs (&ldquo;lack of mutual knowledge&rdquo;). We conduct a field experiment with 5,201 women in Kyrgyzstan to test whether creating mutual knowledge about social norms affects how perceived social norms influence behavior. We show that providing information about societal support for female political activism alone does not affect women&rsquo;s political engagement. However, when perceived mutual knowledge is created, the effect of information about social norms increases significantly. Using vignette experiments, we show that the effect of mutual knowledge on social punishment is a plausible mechanism behind the behavioral impact. These findings suggest that higher-order beliefs about social norms are an important force linking social norms and behavior.",
  links=[("draft","工作论文",pdf("mutual-knowledge-social-norms.pdf","https://docs.iza.org/dp17748.pdf"))]),
]

WIP = [
 dict(y="&mdash;", t="Hiring on Soft Skills or Qualifications",
  a_en="Rob Garlick, Kate Orkin &amp; Jennifer Kades", a_zh="与 Garlick、Orkin、Kades 合著",
  v="South Africa &middot; analysis underway", vz="南非 · 数据分析中", links=[]),
 dict(y="&mdash;", t="Women&rsquo;s Group Empowerment Can Increase Political Participation: Evidence from Five Coordinated Field Experiments",
  a_en="Damir Esenaliev, Anselm Hager &amp; Elnura Kazakbaeva", a_zh="与 Esenaliev、Hager、Kazakbaeva 合著",
  v="EGAP Metaketa V", vz="EGAP Metaketa V 项目",
  links=[("project page","项目主页","http://egap.org/metaketa/metaketa-v-womens-action-committees-and-local-services")]),
]

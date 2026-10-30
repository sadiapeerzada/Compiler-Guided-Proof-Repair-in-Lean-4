"""Editable manuscript changes only; original experiment records are never touched."""
import json
from pathlib import Path
import re
from .common import ROOT,OUT,read

TITLE='Compiler-Guided Proof Repair in Lean 4: A Controlled Local-Model Pilot on Fixed Theorem Types'


def main():
    path=ROOT/'paper/main.tex';text=path.read_text()
    text=re.sub(r'\\title\{[^\n]*?\}(?:\\subtitle\{[^\n]*?\})?',lambda _:r'\title{'+TITLE+'}',text,count=1)
    text=re.sub(r'\\titlerunning\{[^\n]*\}',lambda _:r'\titlerunning{Controlled Lean 4 Proof Repair Pilot}',text,count=1)
    text=text.replace('The frozen exact McNemar helper stores a null,\nnon-informative result; the conventional numerical value is $p=1$. Neither\nconvention supplies evidence of equivalence.',
                      'The conventional exact two-sided McNemar value is $p=1.0$ with\nzero discordant pairs. This does not establish equivalence.')
    text=text.replace('The three planned comparisons remain in multiplicity accounting; the\nnon-informative C--B slot is conservatively treated as 1 internally, but still\nreported as non-informative.',
                      'The three planned comparisons remain in Holm multiplicity accounting,\nincluding the conventional $p=1.0$ for zero-discordance C--B.')
    text=text.replace(r'\input{generated/review_v2/paired.tex}',r'\input{../outputs/post_hoc/latex/post_hoc_paired_p1.tex}')
    text=text.replace('a non-significant or non-informative test is not evidence of equivalence',
                      'a non-significant test is not evidence of equivalence')
    t=read(OUT/'post_hoc_task1.json');cal=read(OUT/'post_hoc_calibrated_null.json');ci=cal['contrasts'][0]['paired_score_sensitivity']['interval']
    paragraph=(r'\paragraph{Post-hoc calibration.} A separately labeled analysis uses Newcombe\x27s paired method 10~\cite{newcombe1998paired}: Wilson marginal score intervals with an adjusted phi coefficient. '
        +f'For the 58 C--B pairs this sensitivity interval is [{100*ci[0]:+.2f}, {100*ci[1]:+.2f}] percentage points. '
        +r'It assumes independent pairs and is not a replacement for family-cluster sensitivity; related families and unavailable outcomes limit inference. The degenerate empirical bootstrap does not rule out these larger effects. Full post-hoc method and power-assumption tables are provided separately.'+'\n')
    marker='% POST_HOC_CALIBRATION_BEGIN'
    if marker not in text:text=text.replace(r'\subsection{Unavailable outcomes and sensitivity}',marker+'\n'+paragraph+'% POST_HOC_CALIBRATION_END\n\n'+r'\subsection{Unavailable outcomes and sensitivity}')
    else:text=re.sub(r'% POST_HOC_CALIBRATION_BEGIN.*?% POST_HOC_CALIBRATION_END',lambda _:marker+'\n'+paragraph+'% POST_HOC_CALIBRATION_END',text,flags=re.S)
    process=r'''\subsection{Exploratory process diagnostics}
The following measurements were defined after observing the original outcomes
and do not alter the frozen success analysis. B repeated the immediately preceding
candidate in 90/178 completed repairs, C in 70/172. Whole-family resampling,
10,000 draws and seed 20271021, preserves repair and family dependence.
The exploratory C--B repetition difference is -9.86 percentage points
(95\% family-bootstrap interval [-19.77,-0.50]). This is one of several post-hoc
contrasts, not a confirmatory diagnostic-use test or a proof-success improvement.
At least one preceding unknown name disappears in B 12/76 eligible repairs and
C 14/70; B\x27s diagnostics are used by the analyst only. Syntactic name removal,
edit distance, fewer messages and category transitions are not certified fixes.
Character/token edits, grayscale transition matrices, prompt-length distributions,
and assumption-based power calculations are provided as post-hoc supplementary
artifacts. No new held-out inference, replay or outcome imputation occurs.
'''
    if '% POST_HOC_PROCESS_BEGIN' not in text:text=text.replace(r'\section{Qualitative Repair Cases}','% POST_HOC_PROCESS_BEGIN\n'+process+'% POST_HOC_PROCESS_END\n\n'+r'\section{Qualitative Repair Cases}')
    # Do not silently add unfinished development results to the manuscript.
    devpath=OUT/'post_hoc_dev_summary.json'
    if devpath.exists() and '% POST_HOC_DEV_BEGIN' not in text:
        dev=read(devpath);rates=', '.join(c.replace('_',r'\_')+f": {v['verified_successes']}/{v['observed_problems']}" for c,v in dev['conditions'].items())
        processes=[]
        for c in ['C','C_placebo']:
            fields=dev['conditions'][c]['repair_metrics'];rep=fields['identical'];fix=fields['any_unknown_removed']
            processes.append(c.replace('_',r'\_')+f" repetition {rep['sum']}/{rep['n']}, own-name removal {fix['sum']}/{fix['n']}")
        extra=r'\paragraph{Exploratory development placebo.} A separately frozen post-hoc control used fresh shared initials on 15 development problems, one seed, three repair arms and only genuine different-problem/family donor diagnostics. Only diagnostic filename metadata was normalized consistently; compiler-message content remained unchanged. Observed verified outcomes were '+rates+'. Completed-repair counts were '+('; '.join(processes))+'. '+dev['interpretation']+r' Five dev families, independent condition RNG streams, donor category/length matching and sequential execution limit inference; no hypothesis-test or proof-of-use claim is made.'+'\n'
        text=text.replace('% POST_HOC_PROCESS_END','% POST_HOC_DEV_BEGIN\n'+extra+'% POST_HOC_DEV_END\n% POST_HOC_PROCESS_END')
    text=text.replace(r'\x27',"'")
    path.write_text(text)
    bib=ROOT/'paper/references.bib';b=bib.read_text()
    if '@article{newcombe1998paired,' not in b:
        bib.write_text(b+'''\n@article{newcombe1998paired,
  author = {Newcombe, Robert G.},
  title = {Improved confidence intervals for the difference between binomial proportions based on paired data},
  journal = {Statistics in Medicine},
  volume = {17},
  number = {22},
  pages = {2635--2650},
  year = {1998},
  doi = {10.1002/(SICI)1097-0258(19981130)17:22<2635::AID-SIM954>3.0.CO;2-C}
}\n''')
    for name in ['README.md','paper/README.md']:
        doc=ROOT/name;parts=doc.read_text().splitlines();parts[0]='# '+TITLE;doc.write_text('\n'.join(parts)+'\n')
    print('Updated editable manuscript title and explicitly post-hoc calibration/process prose; no frozen artifacts changed.')


if __name__=='__main__':main()

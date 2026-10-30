"""Grayscale descriptive figures for the completed dev-only control."""
import csv
from .common import OUT,read


def main():
    from .render import plt
    import numpy as np
    summary=read(OUT/'post_hoc_dev_summary.json')
    transitions=list(csv.DictReader((OUT/'post_hoc_dev_transitions.csv').open()))
    names=['syntax_or_parser','unknown_identifier_or_name','type_mismatch_or_elaboration','tactic_or_unsolved_goal','other_compiler_error','verified','guard/infra/incomplete']
    short=['Parser','Name','Type','Tactic','Other','Verified','Guard/infra']
    arrays=[]
    for condition in ['B','C','C_placebo']:
        data=np.zeros((7,7),dtype=int)
        for row in transitions:
            if row['condition']==condition:data[names.index(row['before']),names.index(row['after'])]+=int(row['completed_repairs'])
        arrays.append(data)
    plt.rcParams.update({'font.size':8,'pdf.fonttype':42})
    fig,axes=plt.subplots(3,1,figsize=(4.6,10));vmax=max(int(a.max()) for a in arrays)
    for ax,data,c in zip(axes,arrays,['B','C','C_placebo']):
        ax.imshow(data,cmap='Greys',vmin=0,vmax=vmax)
        ax.set_xticks(range(7),short,rotation=30,ha='right');ax.set_yticks(range(7),short)
        ax.set(title=f'{c}: exploratory development transitions',xlabel='After',ylabel='Before')
        for i in range(7):
            for j in range(7):ax.text(j,i,str(data[i,j]),ha='center',va='center',color='white' if data[i,j]>vmax*.55 else 'black')
    fig.tight_layout();fig.savefig(OUT/'figures/post_hoc_dev_transitions.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(4.6,2.7));conditions=['A','B','C','C_placebo']
    for i,c in enumerate(conditions):
        row=summary['conditions'][c];n=row['observed_problems'];k=row['verified_successes']
        if n:
            lo,hi=row['Wilson95_success_nominal'];ax.errorbar(i,k/n,yerr=[[max(0,k/n-lo)],[max(0,hi-k/n)]],fmt='o',color='black',capsize=4)
        ax.text(i,.97,f'{k}/{n}',ha='center',va='top')
    ax.set(xticks=range(4),xticklabels=conditions,ylim=(0,1),ylabel='Verified / observed',title='Exploratory dev control: nominal Wilson intervals')
    fig.tight_layout();fig.savefig(OUT/'figures/post_hoc_dev_success.pdf');plt.close(fig)
    print('Development-only grayscale figures generated; intervals ignore five-family dependence.')


if __name__=='__main__':main()

"""Retained legal degree-preserving source generator, copied additively from focused training design.py."""
import hashlib
from copy import deepcopy
from research import digest
def graph_family(parent,seed):
    if seed==0:return deepcopy(parent)
    result=deepcopy(parent);edge={(u,v):j for u,v,j in result['edges']};done=0;attempt=0;swaps=[]
    while done<6:
        pairs=sorted(edge);h=hashlib.sha256(f'SPIN-FOCUSED-TOPOLOGY-V1|{seed}|{attempt}'.encode()).digest();attempt+=1
        a,b=pairs[int.from_bytes(h[:4],'big')%len(pairs)];c,d=pairs[int.from_bytes(h[4:8],'big')%len(pairs)]
        if len({a,b,c,d})<4:continue
        # Preserve the two retained-port glue edges and all degrees.
        if (a,b) in [(0,1),(2,3)] or (c,d) in [(0,1),(2,3)]:continue
        x=tuple(sorted((a,d)));y=tuple(sorted((c,b)))
        if x in edge or y in edge or x in [(0,1),(2,3)] or y in [(0,1),(2,3)]:continue
        j,k=edge.pop((a,b)),edge.pop((c,d));edge[x]=j;edge[y]=k;swaps.append([[a,b],[c,d],list(x),list(y)]);done+=1
    result['edges']=[[*uv,j] for uv,j in sorted(edge.items())];result['family']=f'N96_SIX_DEGREE_PRESERVING_SWAPS_V1_SEED{seed}';result.pop('source_sha256',None);result['source_sha256']=digest(result)
    return result

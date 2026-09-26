"""Source-bound numerical cost adapter: log ridge and nearest-experience models.

Timing regression uses NumPy CPU arithmetic. Exact spin arithmetic remains in
the qualified modular/CRT backend. Model selection sees development graphs only.
"""
import math
import numpy as np

COMPONENTS=['prepare_ns','arithmetic_ns','reconstruction_ns']
def fit(rows,kind,param):
    x=np.asarray([r['features'] for r in rows],float);mu=x.mean(0);scale=x.std(0);scale[scale<1]=1;z=(x-mu)/scale
    y=np.log(np.maximum(1,np.asarray([[r[c] for c in COMPONENTS] for r in rows],float)))
    model=dict(kind=kind,param=param,mu=mu.tolist(),scale=scale.tolist(),rows=len(rows),backend='NUMPY_CPU_TIMING_REGRESSION')
    if kind=='ridge':
        a=np.column_stack([np.ones(len(z)),z]);reg=np.eye(a.shape[1])*param;reg[0,0]=0;model['coef']=np.linalg.solve(a.T@a+reg,a.T@y).tolist()
    else:model.update(x=z.tolist(),y=y.tolist())
    return model

def predict(model,rows):
    z=(np.asarray([r['features'] for r in rows],float)-np.asarray(model['mu']))/np.asarray(model['scale'])
    if model['kind']=='ridge':y=np.column_stack([np.ones(len(z)),z])@np.asarray(model['coef'])
    else:
        x=np.asarray(model['x']);ys=np.asarray(model['y']);out=[]
        for v in z:
            distance=np.sum((x-v)**2,axis=1);ix=np.argsort(distance)[:int(model['param'])];weight=1/(np.sqrt(distance[ix])+.1);out.append((ys[ix]*weight[:,None]).sum(0)/weight.sum())
        y=np.asarray(out)
    return np.exp(np.clip(y,0,40)).sum(axis=1).tolist()

def choose(train,dev):
    candidates=[]
    for kind,params in [('ridge',[.1,1.,10.,100.]),('knn',[1,3,5,9])]:
        for param in params:
            model=fit(train,kind,param);times=predict(model,dev);total=oracle=0
            for group in sorted({r['group'] for r in dev}):
                ix=[i for i,r in enumerate(dev) if r['group']==group];pick=min(ix,key=lambda i:times[i]);total+=dev[pick]['total_ns'];oracle+=min(dev[i]['total_ns'] for i in ix)
            candidates.append(dict(model=model,development_total_ns=total,development_oracle_ns=oracle))
    winner=min(candidates,key=lambda x:x['development_total_ns'])
    return dict(selected=winner['model'],candidates=candidates,selection='minimum sum of development source selected median latency; no reserved labels')

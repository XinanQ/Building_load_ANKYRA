"""Target-free, single-series interface to the extracted frozen layer arithmetic.

The default strict policy preserves the known singular-signature failure. An explicit
source_prior policy is a new engineering boundary extension, not a re-scored model.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.resources import files
from types import SimpleNamespace
import hashlib
import json
import warnings

import numpy as np
import torch

from . import _eo, _level, _day
from ._signature import ScaledSignatures


class InputError(ValueError):
    """The supplied data do not meet the declared input contract."""


class SignatureDegeneracy(RuntimeError):
    """The frozen temperature-signature solver is undefined for this input."""


def frozen_config():
    """Return a fresh copy of all shipped settings and their source identities."""
    return json.loads(files(__package__).joinpath('frozen_config.json').read_text(encoding='utf-8'))


@dataclass(frozen=True)
class History:
    """Hourly pre-origin load/temperature and known calendar labels through the horizon.

    Index zero is January 1 00:00 UTC; no implicit time shifting, filling, DST
    conversion or load resampling is performed. Load and temperature stop at the
    origin. day_types has exactly len(load_kw)+744 known labels, Monday=0,...,
    Sunday=6, holiday=7. Missing load is allowed before the last 1,344 hours.
    """
    load_kw: np.ndarray
    temperature_c: np.ndarray
    day_types: np.ndarray
    start_timestamp: str
    observed: np.ndarray | None = None


def _validate_history(h):
    load = np.asarray(h.load_kw, dtype=np.float64)
    temp = np.asarray(h.temperature_c, dtype=np.float32)
    types = np.asarray(h.day_types)
    if load.ndim != 1 or len(load) < 1344:
        raise InputError('load_kw must contain at least 1344 hourly pre-origin values')
    n = len(load)
    if temp.shape != (n,) or not np.isfinite(temp).all():
        raise InputError('temperature_c must be finite and stop at the same origin as load_kw')
    if types.shape != (n+744,) or not np.issubdtype(types.dtype, np.integer):
        raise InputError('day_types must have integer labels for history plus exactly 744 future hours')
    if np.any((types < 0) | (types > 7)):
        raise InputError('day_types must lie in 0..7')
    if np.isinf(load).any():
        raise InputError('load_kw must not contain infinity')
    try:
        stamp = datetime.fromisoformat(h.start_timestamp.replace('Z', '+00:00'))
    except (ValueError, TypeError) as exc:
        raise InputError('start_timestamp must be an explicit ISO UTC timestamp') from exc
    if (stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp)
            or (stamp.month,stamp.day,stamp.hour,stamp.minute,stamp.second,stamp.microsecond)!=(1,1,0,0,0,0)):
        raise InputError('the frozen climate phase requires a January 1 00:00 UTC record anchor')
    # Day labels must be constant inside complete UTC calendar days. Origin-aligned
    # day types are later taken at block midpoints exactly as in the research code.
    full = types[:len(types)//24*24].reshape(-1,24)
    if np.any(full != full[:, :1]):
        raise InputError('day_types must be constant within each complete UTC calendar day')
    if h.observed is None:
        obs = np.isfinite(load)
    else:
        obs = np.asarray(h.observed)
        if obs.dtype != np.bool_ or obs.shape != load.shape:
            raise InputError('observed must be a boolean mask of the load history')
        if np.any(obs & ~np.isfinite(load)):
            raise InputError('an observed load value is non-finite')
    load = np.where(obs, load, np.nan).copy()
    if not np.isfinite(load[-1344:]).all():
        raise InputError('the final 1344 load hours must be completely observed')
    return load, temp.copy(), types.astype(np.int64, copy=True)


def _store(h, group_index, sigma):
    load,temp,types = _validate_history(h)
    n = len(load)
    total = ((n+744+23)//24)*24
    ld = np.full((1,total),np.nan,dtype=np.float64)
    ld[0,:n] = load
    tp = np.zeros((1,total),dtype=np.float32)
    tp[0,:n] = temp   # padding is internal only and never enters a pre-origin feature
    ty = np.zeros((1,total),dtype=np.int64)
    ty[0,:len(types)] = types
    finite = np.isfinite(ld)
    csum = np.concatenate([np.zeros((1,1)),np.cumsum(np.where(finite,ld,0.0),axis=1)],axis=1)
    ccnt = np.concatenate([np.zeros((1,1)),np.cumsum(finite,axis=1)],axis=1)
    t = torch.tensor(tp)
    feat = _eo.hinge_features(_eo.std_temp(t.double().reshape(1,-1,24).mean(2)))
    cum = torch.cat([torch.zeros((1,1,12),dtype=torch.float64),torch.cumsum(feat,dim=1)],dim=1)
    return SimpleNamespace(load_np=ld,temp=t,types=torch.tensor(ty),csum=torch.tensor(csum),
        ccnt=torch.tensor(ccnt),day_cum=cum,groups_np=np.array([group_index]),
        buildings=['supplied-series'],temp_sigma_std=float(sigma),origin=n,
        eval_origin=np.array([n]),eval_building=np.array([0]))


class _PredictionBatcher(_level.PseudoBatcher):
    """Separate real-origin availability from completed pseudo-window eligibility."""
    def observed(self,b,o,need_lag=False):
        b,o = int(b),int(o)
        n = self.store.origin
        ld = self.store.load_np
        if o < 1344 or o > n:
            return False
        if not np.isfinite(ld[b,o-1344:o]).all():
            return False
        if o != n and (o+744 > n or not np.isfinite(ld[b,o:o+744]).all()):
            return False
        if need_lag and (o < 8760 or not np.isfinite(ld[b,o-8760:o-8760+744]).all()):
            return False
        return True


class _BoundarySignatures(ScaledSignatures):
    def __init__(self,store,curves,policy):
        super().__init__(store,curves)
        self.policy = policy
        self.events = {}

    def fit(self,b,origin_day,scale,lam):
        key=(int(b),int(origin_day),float(lam),float(scale))
        if key in self._scaled:
            return self._scaled[key]
        days=np.arange(max(0,int(origin_day)-365),int(origin_day))
        days=days[np.isfinite(self.load_day[b,days])]
        curve=self.curves.get(int(self.groups[b]))
        status='fitted'
        if curve is None:
            status='unknown_group_zero_signature'
        elif len(days)<60:
            status='fewer_than_60_days_source_prior'
        try:
            result=super().fit(b,origin_day,scale,lam)
        except np.linalg.LinAlgError as exc:
            f=self.feat[b,days]
            f=f-f.mean(axis=0)
            trace=float(np.sum(f*f))
            if not np.isfinite(trace) or trace>0 or self.policy=='strict':
                raise SignatureDegeneracy(
                    f'frozen signature failed at day {origin_day}; centred design trace={trace}; '
                    'strict mode does not alter the frozen solver') from exc
            # Only the proven zero-information case has this specified extension.
            # Other solver failures are not silently converted to a fallback.
            result=curve.copy()
            self._scaled[key]=result
            status='zero_design_source_prior_extension'
        if not np.isfinite(result).all():
            raise SignatureDegeneracy('signature solver returned a non-finite curve')
        self.events[key]={'origin_day':int(origin_day),'scale':float(scale),
                          'usable_days':len(days),'status':status}
        return result


@dataclass
class Estimate:
    level_kw: float
    daily_path_kw: np.ndarray
    diagnostics: dict

    def _validate_fields(self):
        try:
            level=np.asarray(self.level_kw,dtype=np.float64)
            path=np.asarray(self.daily_path_kw,dtype=np.float64)
        except (ValueError,TypeError) as exc:
            raise InputError('Estimate fields must be numeric') from exc
        if level.ndim != 0 or not np.isfinite(level):
            raise InputError('level_kw must be a finite scalar')
        if path.shape != (31,) or not np.isfinite(path).all():
            raise InputError('daily_path_kw must be a finite array of shape (31,)')
        tolerance=1e-11*max(1.,float(np.max(np.abs(path))))
        if abs(float(path.mean()))>tolerance:
            raise InputError('daily_path_kw must be centred; no automatic recentering is applied')
        return float(level),path

    def __post_init__(self):
        level,path=self._validate_fields()
        self.level_kw=level
        self.daily_path_kw=path.copy()
        self.daily_path_kw.setflags(write=False)

    def replace(self,base_trajectory):
        self._validate_fields()  # Public fields may have been reassigned after construction.
        base=np.asarray(base_trajectory,dtype=np.float64)
        if base.shape not in ((744,),(31,24)) or not np.isfinite(base).all():
            raise InputError('base trajectory must be finite, shape (744,) or (31,24), in kW')
        cube=base.reshape(31,24)
        level=float(cube.mean())
        daily=cube.mean(axis=1)-level
        within=cube-cube.mean(axis=1,keepdims=True)
        outputs={
            'level_only':(self.level_kw+daily[:,None]+within).reshape(744),
            'day_only':(level+self.daily_path_kw[:,None]+within).reshape(744),
            'level_and_day':(self.level_kw+self.daily_path_kw[:,None]+within).reshape(744),
        }
        return {'trajectories_kw':outputs,
                'negative_hour_counts':{k:int((v<0).sum()) for k,v in outputs.items()},
                'clipped':False,'automatic_selection':False,
                'energy_kwh':{k:float(v.sum()) for k,v in outputs.items()}}


def estimate_from_history(history: History, *, group: str, temp_sigma_std: float,
                          boundary_policy: str='strict') -> Estimate:
    """Estimate the fixed level and auxiliary centred day path without future load.

    temp_sigma_std is the caller-supplied, previously frozen temperature anomaly
    scale in units of 10 degrees C. It is not estimated using the supplied horizon.
    No confidence interval or recommendation to use a replacement is returned.
    """
    if boundary_policy not in ('strict','source_prior'):
        raise InputError('boundary_policy must be strict or source_prior')
    if not np.isscalar(temp_sigma_std) or not np.isfinite(temp_sigma_std) or temp_sigma_std<=0:
        raise InputError('temp_sigma_std must be a finite, positive, pre-origin fixed scalar')
    groups=('Industrial','Office','Public','Residential','Commercial')
    if group not in groups:
        raise InputError('group must have a declared source mapping: '+', '.join(groups))
    cfg=frozen_config()
    group_i=groups.index(group)
    curves={i:np.asarray(cfg['source_curves'][g],dtype=np.float64)
            for i,g in enumerate(groups) if g in cfg['source_curves']}
    store=_store(history,group_i,temp_sigma_std)
    batcher=_PredictionBatcher(store)
    sigs=_BoundarySignatures(store,curves,boundary_policy)
    system=SimpleNamespace(lam=cfg['signature_lambda'],mu=np.zeros(len(groups)))
    b,o=np.array([0]),np.array([store.origin])
    a,c=cfg['level'],cfg['day']
    with torch.no_grad(),warnings.catch_warnings():
        warnings.filterwarnings('ignore',message='Mean of empty slice',category=RuntimeWarning)
        warnings.filterwarnings('ignore',message='All-NaN slice encountered',category=RuntimeWarning)
        h=_level.hypotheses(store,sigs,system,batcher,b,o,system.lam)
        err=_level.pseudo_errors(store,sigs,system,batcher,b,o,system.lam,a['K'])
        names,w,info=_level.weights(err,a['K'],a['K0'],scale=a['scale'],prior=a['prior'],annual_in_w=a['annual_in_w'])
        la,used=_level.level_path(h,names,w)
        weather_weight=used[:,[i for i,n in enumerate(names) if n in _level.W_SET]].sum(axis=1)
        paths,_,lag=_day.hypotheses_c(store,batcher,sigs,system,b,o,weather_weight)
        err_c=_day.pseudo_errors_c(store,batcher,sigs,system,b,o,weather_weight,c['K'])
        cn,cw,ci=_day.weights_c(err_c,c['K'],c['K0'],scale=c['scale'],prior=c['prior'],include_annual=c['include_annual'])
        lc=_day.arm_c_level(la,paths,cn,cw,lag_ok=lag)
    used_c=cw.copy()
    if not bool(lag[0]):
        for j,name in enumerate(cn):
            if name in _day.ANNUAL_C:
                used_c[0,j]=0
        used_c/=np.maximum(used_c.sum(axis=1,keepdims=True),1e-300)
    level=float(h['l0'][0]+h['s0'][0]*la[0].mean())
    path=h['s0'][0]*(lc[0]-lc[0].mean())
    if not np.isfinite(level) or not np.isfinite(path).all():
        raise InputError('the frozen estimator produced a non-finite output')
    diagnostics={
        'implementation':'eo-layers-reference-1.0.0','source_kind':'extracted frozen arithmetic with explicit target-free adapter',
        'boundary_policy':boundary_policy,
        'boundary_extension_triggered':any(e['status']=='zero_design_source_prior_extension' for e in sigs.events.values()),
        'config_sha256':hashlib.sha256(files(__package__).joinpath('frozen_config.json').read_bytes()).hexdigest(),
        'history_hours':store.origin,'origin_hour_offset':store.origin%24,'start_timestamp':history.start_timestamp,
        'group':group,'temp_sigma_std':float(temp_sigma_std),
        'level_k_eff':int(info['k_eff'][0]),'day_k_eff':int(ci['k_eff'][0]),
        'level_no_error_evidence':bool(info['no_evidence'][0]),'day_no_error_evidence':bool(ci['no_evidence'][0]),
        'annual_real_origin_available':bool(h['lag_ok'][0]),
        'level_error_counts':{n:int(np.isfinite(err[n][0]).sum()) for n in names},
        'day_error_counts':{n:int(np.isfinite(err_c[n][0]).sum()) for n in cn},
        'level_error_scales':{n:float(info['scale'][n][0]) if np.isfinite(info['scale'][n][0]) else None for n in names},
        'level_weights':dict(zip(names,used[0].tolist())),
        'day_weights':dict(zip(cn,used_c[0].tolist())),
        'weather_weight':float(weather_weight[0]),'origin_center_kw':float(h['l0'][0]),'origin_scale_kw':float(h['s0'][0]),
        'signature_fits':list(sigs.events.values()),
        'daily_cur_error_is_strictly_out_of_sample':False,
        'future_load_input':False,'automatic_selection':False,
        'scientific_status':'synthetic interface validation only; published scores belong to the original frozen implementation',
    }
    return Estimate(level,path,diagnostics)


def score_against_observations(predicted,observed):
    """Separate descriptive scoring helper; not called by the estimator."""
    p,y=np.asarray(predicted,dtype=np.float64),np.asarray(observed,dtype=np.float64)
    if p.shape!=(744,) or y.shape!=(744,) or not np.isfinite(p).all() or not np.isfinite(y).all():
        raise InputError('scoring requires two finite 744-hour vectors')
    return {'hourly_rmse_kw':float(np.sqrt(np.mean((p-y)**2))),
            'energy_error_kwh':float(p.sum()-y.sum())}


import json
from datetime import datetime
from collections import defaultdict

P = open(r'C:\Users\Public\inv_10b_compact.json', encoding='utf-8').read()

# --- Build NI (No Inventory) list from raw BQ data ---
HIER = {
    '366-A':{'mgr':'Antonio Vasquez',   'reg_mgr':'Israel Pino'},
    '367-A':{'mgr':'Michael Leanox',    'reg_mgr':'Israel Pino'},
    '368-A':{'mgr':'Thomas Balaci',     'reg_mgr':'Christopher Fuentes'},
    '369-A':{'mgr':'Alejandro Quijada', 'reg_mgr':'Christopher Fuentes'},
    '369-B':{'mgr':'Habib Musliu',      'reg_mgr':'Christopher Fuentes'},
    '370-A':{'mgr':'Aron Valdez',       'reg_mgr':'Ralph Vasquez'},
    '371-A':{'mgr':'Gustavo Ortiz',     'reg_mgr':'Ralph Vasquez'},
    '372-A':{'mgr':'Shane Christy',     'reg_mgr':'Ralph Vasquez'},
    '373-A':{'mgr':'Joshua Drezek',     'reg_mgr':'Israel Pino'},
    '375-A':{'mgr':'Cody Hoffer',       'reg_mgr':'Gabe Macias'},
    '384-A':{'mgr':'Jonathan Rivera',   'reg_mgr':'Gabe Macias'},
    '385-A':{'mgr':'Darien Molina',     'reg_mgr':'Gabe Macias'},
    '385-B':{'mgr':'John Swonger',      'reg_mgr':'Gabe Macias'},
    '387-A':{'mgr':'James Chacon',      'reg_mgr':'Gabe Macias'},
    '387-B':{'mgr':'Ward Cosgrove',     'reg_mgr':'Gabe Macias'},
}
EXCLUDE = {'eian palomino', 'omar zarate meza', 'enrique sanchez',
           'larry rossman', 'karl clymer', 'david trujillo',
           'james lashway', 'jason jackson', 'jason parker'}  # all have inventory per raw BQ; compress step drops them
JUNK    = {'1','366-A-FE','366-A-FS','367-A-FS','','NULL'}
_raw_lines = open(r'C:\Users\Public\inv_10b_raw.txt', encoding='utf-8-sig').read().splitlines()
_data = [l for l in _raw_lines if '|' in l]
_cols = [c.strip() for c in _data[0].split('|')]
_ci   = {c:i for i,c in enumerate(_cols)}
_raw_techs = defaultdict(set)
for _line in _data[1:]:
    if not _line.strip(): continue
    _vals = _line.split('|')
    _get  = lambda k: _vals[_ci[k]].strip() if k in _ci and _ci[k]<len(_vals) else ''
    _sub  = _get('fs_sub_market')
    _bqt  = _get('tech')
    if not _sub or not _bqt or _bqt in JUNK: continue
    if _bqt.upper() != 'STORE LOCATION':
        _raw_techs[_sub].add(_bqt.title())
_d = json.loads(P)
_inv_set = set(_d['techs'][t[0]].lower() for t in _d['tech_rows'])
NI_DATA = []
for _sub in sorted(HIER.keys()):
    _missing = sorted(t for t in _raw_techs.get(_sub, set())
                      if t.lower() not in _inv_set and t.lower() not in EXCLUDE)
    if _missing:
        NI_DATA.append({'sub':_sub, 'mgr':HIER[_sub]['mgr'],
                        'rm':HIER[_sub]['reg_mgr'], 'techs':_missing})
NI_JS = json.dumps(NI_DATA, separators=(',',':'))

HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Region 10B Parts Inventory - Global Search</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d1117;--s1:#161b22;--s2:#21262d;--bd:#30363d;--tx:#e6edf3;--sub:#8b949e;--blue:#58a6ff;--grn:#3fb950;--red:#f85149;--amb:#d29922;--pur:#bc8cff;--wmt:#0071ce;--wmt2:#004f9e;--gold:#ffc220}
body.light{--bg:#f6f8fa;--s1:#fff;--s2:#f6f8fa;--bd:#d0d7de;--tx:#1f2328;--sub:#57606a;--blue:#0969da;--grn:#1a7f37;--red:#cf222e;--amb:#9a6700;--pur:#8250df}
body{background:var(--bg);color:var(--tx);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:13px}
nav{background:var(--wmt);padding:6px 20px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;position:sticky;top:0;z-index:200;box-shadow:0 2px 8px rgba(0,0,0,.3)}
.navwrap{max-width:1600px;margin:0 auto;width:100%;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.nt{font-weight:700;font-size:1rem;color:#fff;white-space:nowrap;display:flex;align-items:center;gap:10px}
.nt-logo{height:44px;width:auto;display:block}
.nt-text{display:flex;flex-direction:column;line-height:1.15}
.nt-sub{font-size:.62rem;font-weight:600;color:#ffc220;letter-spacing:.03em;border-top:2px solid #e9bf3f;padding-top:2px;margin-top:1px}
.sw{flex:1;min-width:180px;max-width:340px;position:relative}
#srch{width:100%;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.35);border-radius:22px;padding:7px 34px 7px 36px;color:#fff;font-size:.85rem;outline:none;font-family:inherit}
#srch::placeholder{color:rgba(255,255,255,.65)}
#srch:focus{background:rgba(255,255,255,.26);border-color:rgba(255,255,255,.7)}
.si{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:rgba(255,255,255,.7);pointer-events:none}
.camf{position:absolute;right:8px;top:50%;transform:translateY(-50%);background:none;border:none;color:#ffc220;cursor:pointer;padding:2px;display:flex;align-items:center;justify-content:center;border-radius:50%}
.camf:hover{background:rgba(255,255,255,.18)}
.camf.busy svg{animation:camspin 1s linear infinite}
@keyframes camspin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.pmbar{max-width:1600px;margin:0 auto;padding:8px 20px 0;display:none;align-items:center;gap:10px}
.pmbar.on{display:flex}
.pmimg{width:38px;height:38px;object-fit:cover;border-radius:6px;border:1px solid var(--bd)}
.pmtxt{font-size:.72rem;color:var(--sub)}
.pmclr{background:var(--s1);border:1px solid var(--bd);border-radius:6px;padding:4px 10px;font-size:.68rem;color:var(--tx);cursor:pointer}
.pmclr:hover{background:var(--s2)}
.cropmodal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:10000;align-items:center;justify-content:center;padding:20px}
.cropmodal.on{display:flex}
.cropbox{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px;max-width:520px;width:100%;max-height:90vh;display:flex;flex-direction:column;gap:12px}
.crophdr{font-size:.8rem;color:var(--tx);text-align:center;font-weight:600}
.cropstage{position:relative;width:100%;max-height:60vh;overflow:hidden;background:#000;border-radius:6px;display:flex;align-items:center;justify-content:center;touch-action:none}
.cropstage img{max-width:100%;max-height:60vh;display:block;user-select:none;-webkit-user-drag:none}
.croprect{position:absolute;border:2px solid #ffc220;box-shadow:0 0 0 2000px rgba(0,0,0,.5);cursor:move;touch-action:none}
.cropHandle{position:absolute;width:18px;height:18px;background:#ffc220;border:2px solid #1a1a1a;border-radius:50%;touch-action:none}
.cropHandle[data-h=nw]{left:-10px;top:-10px;cursor:nwse-resize}
.cropHandle[data-h=ne]{right:-10px;top:-10px;cursor:nesw-resize}
.cropHandle[data-h=sw]{left:-10px;bottom:-10px;cursor:nesw-resize}
.cropHandle[data-h=se]{right:-10px;bottom:-10px;cursor:nwse-resize}
.cropftr{display:flex;justify-content:flex-end;gap:10px}
.pmnarrow{display:none;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 16px;background:var(--s2);border-bottom:1px solid var(--bd)}
.pmnarrow.on{display:flex}
.pmnarrow.pmnarrow-highlight{background:rgba(255,194,32,.12);border-bottom:1px solid var(--gold);animation:pmpulse 1.6s ease-in-out 2}
@keyframes pmpulse{0%,100%{background:rgba(255,194,32,.12)}50%{background:rgba(255,194,32,.28)}}
.pmnarrow-lbl{font-size:.72rem;color:var(--mut);font-weight:600;white-space:nowrap}
.pmkwinp{background:var(--s1);border:1px solid var(--bd);border-radius:6px;padding:6px 10px;font-size:.75rem;color:var(--tx);font-family:inherit;min-width:220px;flex:1;max-width:340px}
.pmnarrow-count{font-size:.72rem;color:var(--gold);font-weight:600;white-space:nowrap;margin-left:auto}
.btn{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:6px;padding:6px 12px;font-size:.72rem;color:#fff;cursor:pointer;font-family:inherit;display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.btn:hover{background:rgba(255,255,255,.28)}
.btn svg{display:block;flex-shrink:0}
.nr2{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.hsel{background:var(--wmt2);border:1.5px solid var(--gold);border-radius:20px;padding:5px 28px 5px 12px;font-size:.7rem;font-weight:600;color:#fff;cursor:pointer;font-family:inherit;appearance:none;-webkit-appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23ffc220' stroke-width='3'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 7px center;background-size:12px;min-width:120px;max-width:160px}
.hsel:hover{border-color:#fff}
.hsel:focus{outline:none;border-color:#fff;box-shadow:0 0 0 2px rgba(255,194,32,.35)}
.hsel option{background:var(--wmt2);color:#fff}
.nfl{font-size:.68rem;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.03em;white-space:nowrap;margin-left:4px}
.npl{background:var(--wmt2);border:1.5px solid var(--gold);border-radius:20px;padding:5px 13px;font-size:.7rem;font-weight:600;color:#fff;cursor:pointer;font-family:inherit;white-space:nowrap}
.npl:hover{border-color:#fff}
.npl.on{background:var(--gold);border-color:var(--gold);color:#1a1a1a}
.ndv{width:1px;height:20px;background:rgba(255,255,255,.3);flex-shrink:0;margin:0 2px}
@media(max-width:960px){.hsel{min-width:90px;max-width:110px;font-size:.66rem;padding:5px 22px 5px 10px}}
.fb{background:var(--s1);border-bottom:1px solid var(--bd);padding:7px 20px;display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.fl{font-size:.67rem;color:var(--sub);font-weight:700;text-transform:uppercase;letter-spacing:.04em;white-space:nowrap}
.pl{background:var(--s2);border:1px solid var(--bd);border-radius:20px;padding:3px 11px;font-size:.7rem;color:var(--sub);cursor:pointer;white-space:nowrap;font-family:inherit}
.pl:hover{border-color:var(--blue);color:var(--blue)}.pl.on{background:var(--blue);border-color:var(--blue);color:#fff;font-weight:600}
.pl.gold{border-color:var(--gold);color:var(--gold)}
.pl.gold:hover{background:rgba(255,194,32,.15);border-color:var(--gold);color:var(--gold)}
.pl.gold.on{background:var(--gold);border-color:var(--gold);color:#1a1a1a}
.btn.gold{background:var(--gold);border-color:var(--gold);color:#1a1a1a;font-weight:700}
.btn.gold:hover{background:#e0ab1c}
.pl.r{border-color:var(--red);color:var(--red)}
.pl.r:hover{background:rgba(248,81,73,.15);border-color:var(--red);color:var(--red)}
.pl.r.on{background:var(--red);border-color:var(--red);color:#fff}
.aib{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding:6px;border:1.5px dashed var(--bd);border-radius:6px;cursor:pointer;color:var(--sub);font-size:.68rem;text-align:center;transition:.12s;min-height:90px}
.aib:hover{border-color:var(--gold);color:var(--gold)}
.aib .plus{font-size:1.3rem;line-height:1}
.mbadge{position:absolute;top:2px;left:2px;background:var(--gold);color:#1a1a1a;font-size:.55rem;font-weight:700;padding:1px 5px;border-radius:3px;z-index:1}
.pl.g.on{background:var(--grn);border-color:var(--grn);color:#fff}
.dv{width:1px;height:18px;background:var(--bd);flex-shrink:0}
#fc{font-size:.7rem;color:var(--sub);margin-left:auto}
.sts{max-width:1600px;margin:12px auto 0;padding:0 20px;display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px}
.sc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 14px;text-align:center}
.sv{font-size:1.3rem;font-weight:800;color:var(--tx);line-height:1}
.sl{font-size:.6rem;color:var(--sub);text-transform:uppercase;letter-spacing:.06em;margin-top:3px}
.wr{max-width:1600px;margin:12px auto 0;padding:0 20px 30px;display:flex;gap:16px}
.sb-shell{display:flex;align-items:flex-start;flex-shrink:0;gap:6px;position:sticky;top:120px}
.sb{width:228px;flex-shrink:0;max-height:calc(100vh - 130px);overflow-y:auto;overflow-x:hidden;transition:width .2s ease,opacity .15s ease;opacity:1}
.sb.collapsed{width:0;opacity:0;pointer-events:none}
.sb-tab{width:20px;height:32px;flex-shrink:0;display:flex;align-items:center;justify-content:center;cursor:pointer;background:var(--s1);border:1px solid var(--bd);border-radius:6px;user-select:none}
.sb-tab:hover{background:var(--s2);border-color:var(--gold)}
.sb-arrow{color:var(--gold);font-size:.8rem;line-height:1;transition:transform .2s ease;display:block}
.sb-arrow.collapsed{transform:rotate(180deg)}
@media(max-width:960px){.wr{padding:0 12px 20px}}
@media(max-width:960px) and (orientation:portrait){.sb-shell{display:none}}
.mn{flex:1;min-width:0}
.sg{font-size:.65rem;font-weight:700;color:var(--sub);text-transform:uppercase;letter-spacing:.08em;padding:0 4px 5px;border-bottom:1px solid var(--bd);margin-bottom:6px;white-space:nowrap}
.sgl{font-size:.65rem;font-weight:700;color:var(--sub);padding:3px 6px;background:var(--s2);border-radius:4px;margin:6px 0 3px}
.sr{display:flex;align-items:center;gap:7px;padding:4px 6px;border-radius:6px;cursor:pointer}
.sr:hover{background:var(--s2)}.sr.on{background:var(--s2);box-shadow:inset 2px 0 0 var(--blue)}
.sd{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.sn{font-size:.7rem;color:var(--tx);flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ss{font-size:.6rem;color:var(--sub)}
.sk{font-size:.63rem;color:var(--sub);flex-shrink:0}
.sk.low{color:var(--red);font-weight:700}
.tbox{background:var(--s1);border:1px solid var(--bd);border-radius:8px;overflow:hidden}
.th{display:flex;align-items:center;gap:8px;padding:10px 14px;border-bottom:1px solid var(--bd);background:var(--s2);flex-wrap:wrap}
.tt{font-size:.88rem;font-weight:700;color:var(--tx)}
.ts{font-size:.7rem;color:var(--sub)}
.tsc{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:.78rem}
thead th{padding:7px 10px;text-align:left;font-size:.6rem;font-weight:700;color:var(--sub);text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid var(--bd);white-space:nowrap;cursor:pointer;user-select:none;background:var(--s2)}
thead th:hover{color:var(--tx)}.srt{color:var(--blue)!important}
.sic{margin-left:2px;opacity:.35;font-size:.58rem}.srt .sic{opacity:1}
tbody tr{border-bottom:1px solid var(--bd);cursor:pointer}
tbody tr:hover td{background:var(--s2)}
td{padding:7px 10px;vertical-align:middle}
.xr td{background:var(--bg)!important;padding:0!important;border-bottom:2px solid var(--bd)!important;cursor:default!important}
.xi{padding:12px 14px 14px 38px;display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:8px}
.ec{background:var(--s1);border:1px solid var(--bd);border-radius:6px;padding:8px 11px}
.el{font-size:.58rem;font-weight:700;color:var(--sub);text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px}
.ev{font-size:.9rem;font-weight:700;color:var(--tx)}.ev.ok{color:var(--grn)}
.es{font-size:.63rem;color:var(--sub);margin-top:2px}
.rb{border-radius:10px;padding:2px 8px;font-size:.62rem;font-weight:700;white-space:nowrap;border:1px solid}
.gm{background:rgba(88,166,255,.1);color:var(--blue);border-color:rgba(88,166,255,.3)}
.hv{background:rgba(63,185,80,.1);color:var(--grn);border-color:rgba(63,185,80,.3)}
.fe{background:rgba(210,153,34,.1);color:var(--amb);border-color:rgba(210,153,34,.3)}
.st{background:rgba(188,140,255,.1);color:var(--pur);border-color:rgba(188,140,255,.3)}
.ry{border-radius:10px;padding:2px 7px;font-size:.62rem;font-weight:700;background:rgba(63,185,80,.1);color:var(--grn);border:1px solid rgba(63,185,80,.3)}
.rn{border-radius:10px;padding:2px 7px;font-size:.62rem;background:var(--s2);color:var(--sub);border:1px solid var(--bd)}
.sbg{background:var(--s2);border:1px solid var(--bd);border-radius:6px;padding:1px 7px;font-size:.62rem;font-weight:700;color:var(--sub);font-family:monospace}
.hid{display:none!important}
.lbtn{width:100%;padding:12px;background:var(--s2);border:none;border-top:1px solid var(--bd);color:var(--blue);cursor:pointer;font-size:.8rem;font-family:inherit;font-weight:600}
.lbtn:hover{background:var(--s1)}
.nores{text-align:center;padding:50px;color:var(--sub);font-size:.85rem}
footer{border-top:1px solid var(--bd);padding:10px 20px;font-size:.63rem;color:var(--sub);display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;margin-top:16px}
.lb-overlay{position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:9999;display:flex;align-items:center;justify-content:center;padding:24px;overflow:auto}
.lb-overlay.hid{display:none!important}
.lb-overlay img{max-width:100%;max-height:100%;object-fit:contain;border-radius:4px}
.lb-close{position:fixed;top:14px;right:18px;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);color:#fff;font-size:1.3rem;line-height:1;width:40px;height:40px;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:10000}
.lb-close:hover{background:rgba(255,255,255,.3)}
.lb-hint{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);color:rgba(255,255,255,.6);font-size:.68rem;z-index:10000;white-space:nowrap}
.aim-overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:10001;display:flex;align-items:center;justify-content:center;padding:20px}
.aim-overlay.hid{display:none}
.aim-box{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:20px;max-width:360px;width:100%;box-shadow:0 10px 40px rgba(0,0,0,.5)}
.aim-title{font-weight:700;font-size:.95rem;color:var(--tx);margin-bottom:2px}
.aim-sub{font-size:.72rem;color:var(--sub);margin-bottom:16px}
.aim-btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:12px;border-radius:8px;border:1.5px solid var(--bd);background:var(--s2);color:var(--tx);font-size:.85rem;font-weight:600;cursor:pointer;margin-bottom:10px;font-family:inherit}
.aim-btn:hover{border-color:var(--gold);color:var(--gold)}
.aim-btn.cancel{background:none;border:none;color:var(--sub);font-weight:500;margin-bottom:0;padding:8px}
.aim-preview{width:100%;max-height:280px;object-fit:contain;border-radius:8px;margin-bottom:14px;background:var(--bg)}
.aim-confirm-row{display:flex;gap:10px}
.aim-confirm-row .aim-btn{margin-bottom:0}
.aim-btn.yes{background:var(--gold);border-color:var(--gold);color:#1a1a1a}
.aim-btn.yes:hover{filter:brightness(1.08);color:#1a1a1a}
</style></head><body>
<script>var _D=""" + P + """;</script>
<script>var NI=NI_PLACEHOLDER;</script>
<nav><div class="navwrap">
  <div class="nt"><img class="nt-logo" src="upstream_logo.png" alt="Upstream Facility Services"><div class="nt-text"><span>Region 10B</span><span class="nt-sub">Global Search</span></div></div>
  <div class="sw"><span class="si">&#128269;</span>
    <input id="srch" type="text" placeholder="Search part, tech, role, manager, location, mfr, date&#8230;" autocomplete="off">
    <button class="camf" id="camBtn" title="Search by Photo" onclick="document.getElementById('camInp').click()"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h3l1.5-2h7L17 8h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13.5" r="3.4"/></svg></button>
    <input type="file" id="camInp" accept="image/*" capture="environment" style="display:none" onchange="onPhotoPick(event)">
  </div>
  <div class="hc"><select class="hsel" id="rmSel" onchange="sRM(this.value)"></select></div>
  <div class="hc"><select class="hsel" id="mgrSel" onchange="sMGR(this.value)"></select></div>
  <div class="hc"><select class="hsel" id="techSel" onchange="sTechSel(this.value)"></select></div>
  <div class="ndv"></div>
  <div class="hc"><select class="hsel" id="roleSel" onchange="sRole(this.value)"></select></div>
  <div class="ndv"></div>
  <span class="nfl">Rep:</span>
  <button class="npl on" data-g="rep" data-v="" onclick="sF('rep','',this)">All</button>
  <button class="npl" data-g="rep" data-v="Y" onclick="sF('rep','Y',this)">&#10003; Yes</button>
  <button class="npl" data-g="rep" data-v="N" onclick="sF('rep','N',this)">No</button>
</div></nav>
<div class="fb">
  <button class="pl gold" id="imgf" onclick="toggleImgF()">Has Image</button>
  <button class="pl r" id="noimgf" onclick="toggleNoImgF()" title="Show only parts that still need a photo">No Image</button>
  <div class="dv"></div><span id="fc"></span>
  <div class="nr2" style="margin-left:auto">
    <button class="btn" onclick="cpLink(this)" title="Copy share link"><svg width="16" height="16" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#ffc220"/><circle cx="8.5" cy="10" r="1.4" fill="#1a1a1a"/><circle cx="15.5" cy="10" r="1.4" fill="#1a1a1a"/><path d="M7.5 14.5c1 1.6 2.7 2.5 4.5 2.5s3.5-.9 4.5-2.5" stroke="#1a1a1a" stroke-width="1.6" fill="none" stroke-linecap="round"/></svg> Share</button>
    <button class="btn" onclick="togT()" title="Toggle light/dark"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2 12h2.5M19.5 12H22M4.2 19.8l1.8-1.8M18 6l1.8-1.8"/></svg></button>
  </div>
</div>
<div class="pmbar" id="pmbar">
  <img class="pmimg" id="pmimg" src="" alt="">
  <span class="pmtxt" id="pmtxt">Matching photo against catalog images&#8230;</span>
  <button class="pmclr" onclick="clearPhotoMatch()">&#10005; Clear Photo Search</button>
</div>
<div class="pmnarrow" id="pmnarrow">
  <span class="pmnarrow-lbl">Narrow it down (optional):</span>
  <select class="hsel" id="pmMfrSel" onchange="pmApplyNarrow()">
    <option value="">Any manufacturer</option>
  </select>
  <input type="text" id="pmKeywordInp" class="pmkwinp" placeholder="Details you know: voltage, amps, color, size&#8230;" oninput="pmApplyNarrowDebounced()">
  <button class="btn" id="pmNarrowReset" onclick="pmResetNarrow()" style="display:none">&#10005; Reset</button>
  <span class="pmnarrow-count" id="pmNarrowCount"></span>
</div>
<div class="cropmodal" id="cropModal">
  <div class="cropbox">
    <div class="crophdr">Drag the box so it tightly frames just the part (no background), then tap Search</div>
    <div class="cropstage" id="cropStage">
      <img id="cropImg" src="" alt="">
      <div class="croprect" id="cropRect">
        <div class="cropHandle" data-h="nw"></div>
        <div class="cropHandle" data-h="ne"></div>
        <div class="cropHandle" data-h="sw"></div>
        <div class="cropHandle" data-h="se"></div>
      </div>
    </div>
    <div class="cropftr">
      <button class="btn" onclick="cropCancel()">Cancel</button>
      <button class="btn gold" onclick="cropConfirm()">&#128269; Search This Crop</button>
    </div>
  </div>
</div>
<div class="sts">
  <div class="sc"><div class="sv" id="si">-</div><div class="sl">Line Items</div></div>
  <div class="sc"><div class="sv" id="sv">-</div><div class="sl">Total Value</div></div>
  <div class="sc"><div class="sv" id="sc2">-</div><div class="sl">Technicians</div></div>
  <div class="sc"><div class="sv" id="sm">-</div><div class="sl">FS Managers</div></div>
  <div class="sc"><div class="sv" id="sl2">-</div><div class="sl">Locations</div></div>
  <div class="sc"><div class="sv" id="srp">-</div><div class="sl">Replenishable</div></div>
</div>
<div class="wr">
  <div class="sb-shell">
    <div class="sb" id="sb">
      <div class="sg">Technicians</div>
      <div id="sb-body"></div>
    </div>
    <div class="sb-tab" onclick="toggleSB()" title="Show/hide technician list">
      <span class="sb-arrow" id="sb-arrow">&#9668;</span>
    </div>
  </div>
  <div class="mn">
    <div class="tbox">
      <div class="th">
        <div><div class="tt">Parts Inventory - Region 10B</div><div class="ts" id="tsl">All 15 Sub-Markets</div></div>
      </div>
      <div class="tsc"><table><thead><tr id="thr"></tr></thead><tbody id="tby"></tbody></table></div>
      <div class="nores hid" id="nores">No items match your filters.</div>
      <button class="lbtn hid" id="lbtn" onclick="lM()">Load more</button>
    </div>
  </div>
</div>
<footer>
  <span>Region 10B - 15 Sub-Markets</span>
  <span id="rts"></span>
</footer>
<div class="lb-overlay hid" id="lbov" onclick="closeLb()">
  <button class="lb-close" onclick="event.stopPropagation();closeLb()" title="Close">&#10005;</button>
  <img id="lbimg" src="" alt="" onclick="event.stopPropagation()">
  <div class="lb-hint">Tap outside image or press Esc to close &middot; pinch to zoom</div>
</div>

<input type="file" id="aim-camera-input" accept="image/*" capture="environment" style="display:none" onchange="aimHandleFile(this)">
<input type="file" id="aim-library-input" accept="image/*" style="display:none" onchange="aimHandleFile(this)">

<div class="aim-overlay hid" id="aim-picker" onclick="aimClosePicker()">
  <div class="aim-box" onclick="event.stopPropagation()">
    <div class="aim-title">Add a Part Photo</div>
    <div class="aim-sub" id="aim-picker-desc"></div>
    <button class="aim-btn" onclick="aimTriggerCamera()">Take Photo</button>
    <button class="aim-btn" onclick="aimTriggerLibrary()">Choose from Library</button>
    <button class="aim-btn cancel" onclick="aimClosePicker()">Cancel</button>
  </div>
</div>

<div class="aim-overlay hid" id="aim-confirm">
  <div class="aim-box" onclick="event.stopPropagation()">
    <div class="aim-title">Is this the correct part?</div>
    <div class="aim-sub" id="aim-confirm-desc"></div>
    <img class="aim-preview" id="aim-confirm-img" src="" alt="Preview">
    <div class="aim-confirm-row">
      <button class="aim-btn" onclick="aimRetake()">Retake</button>
      <button class="aim-btn yes" onclick="aimConfirmYes()">Yes, use this</button>
    </div>
  </div>
</div>
<script>
window.onerror=function(msg,src,line,col,err){var d=document.createElement('div');d.style='background:#f85149;color:#fff;padding:20px;font-size:14px;font-family:monospace;position:fixed;top:10px;left:10px;right:10px;z-index:99999;white-space:pre-wrap';d.textContent='JS ERR: '+msg+' | line:'+line+' col:'+col;document.body.prepend(d);return true;};
</script>
<script>
var _ERR=null;
try{
var SI=0,RI=1,MI=2,TI=3,ROI=4,AR=5,ID=6,DS=7,MF=8,PN=9,QT=10,UC=11,TC=12,AT=13,RP=14,MQ=15,RE=16,PU=17,LO=18,GO=19,FD=20,IMG=21;
var R=_D;
var RMSV=R.rms,MGRSV=R.mgrs,TECHSV=R.techs,SUBSV=R.subs,ROLESV=R.roles;
var PG=150,F={rm:'',mgr:'',tech:'',role:'',rep:'',img:false,noimg:false},SRT={c:13,a:false},filtered=[],page=0;
var photoMatchActive=false,photoMatchSimByPno=null;
// "Narrow it down" -- optional manufacturer/keyword filters applied ON TOP
// of the visual similarity ranking, since MobileNet's embedding alone often
// can't reliably distinguish visually-similar-but-different industrial
// parts. Letting the user supply a manufacturer name (if known) and/or a
// few descriptive keywords (voltage, amps, color, size, etc.) lets us hard-
// filter the candidate pool using exact catalog data instead of relying
// purely on possibly-ambiguous visual similarity.
var photoMatchMfrFilter='',photoMatchKeywords=[];
var dark=localStorage.getItem('t10b')!=='light';
var RM_MGRS={},MGR_RM={},MGR_TECHS={};
R.tech_rows.forEach(function(t){
  var rm=RMSV[t[2]],mgr=MGRSV[t[1]],tech=TECHSV[t[0]];
  if(!RM_MGRS[rm])RM_MGRS[rm]=[];
  if(RM_MGRS[rm].indexOf(mgr)<0)RM_MGRS[rm].push(mgr);
  MGR_RM[mgr]=rm;
  if(!MGR_TECHS[mgr])MGR_TECHS[mgr]=[];
  if(MGR_TECHS[mgr].indexOf(tech)<0)MGR_TECHS[mgr].push(tech);
});
var ALL_RMS=Object.keys(RM_MGRS).sort(),ALL_MGRS=Object.keys(MGR_RM).sort();
var LOW_ITEM_THRESHOLD=25;
}catch(e){_ERR='INIT: '+e.message;}
var RCLS={GM:'gm',HVACR:'hv',FE:'fe',Store:'st'};
var RCOL={GM:'#58a6ff',HVACR:'#3fb950',FE:'#d29922',Store:'#bc8cff'};
var SYNS={
  'valve':['vlv'],'vlv':['valve'],
  'condenser':['cndsr','cond'],'cndsr':['condenser'],'cond':['condenser'],
  'compressor':['comp','comprs'],'comp':['compressor'],
  'filter':['fltr','flt'],'fltr':['filter'],
  'motor':['mtr','mot'],'mtr':['motor'],
  'thermostat':['tstat'],'tstat':['thermostat'],
  'sensor':['snsr'],'snsr':['sensor'],
  'relay':['rly'],'rly':['relay'],
  'capacitor':['cap'],'cap':['capacitor'],
  'contactor':['cont'],'cont':['contactor'],
  'solenoid':['sol'],'sol':['solenoid'],
  'pressure':['pres'],'pres':['pressure'],
  'evaporator':['evap'],'evap':['evaporator'],
  'refrigerant':['refrig'],'refrig':['refrigerant'],
  'temperature':['temp'],'temp':['temperature'],
  'control':['ctrl'],'ctrl':['control'],
  'assembly':['assy'],'assy':['assembly'],
  'electrical':['elec'],'elec':['electrical'],
  'switch':['sw'],'sw':['switch'],
  'heater':['htr'],'htr':['heater'],
  'blower':['blwr'],'blwr':['blower'],
  'pump':['pmp'],'pmp':['pump'],
  'liquid':['liq'],'liq':['liquid'],
  'suction':['suct'],'suct':['suction'],
  'discharge':['disch'],'disch':['discharge'],
  'bearing':['brng'],'brng':['bearing'],
  'bracket':['brkt'],'brkt':['bracket']
};

function f$(v){return '$'+Number(v).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});}
function fK(v){var n=Number(v);return n>=1000000?'$'+(n/1000000).toFixed(1)+'M':n>=1000?'$'+(n/1000).toFixed(0)+'K':f$(n);}
function fN(v){return Number(v).toLocaleString();}
function ge(id){return document.getElementById(id);}
function esc(s){return s?String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'):'';} 
function togT(){dark=!dark;localStorage.setItem('t10b',dark?'dark':'light');document.body.classList.toggle('light',!dark);}

var COLS=['Part #','Part / Item ID','Technician','FS Manager','Sub-Mkt','Role','Location #','Qty','Truck Total','Rep?'];
var CSRT=[PN,DS,TI,MI,SI,ROI,AR,QT,AT,RE];

function bH(){
  var h='';
  COLS.forEach(function(c,i){
    var s=SRT.c===CSRT[i];
    h+='<th class="'+(s?'srt':'')+'" onclick="cS('+i+')">'+c+'<span class="sic">'+(s?(SRT.a?'&#9650;':'&#9660;'):'&#8645;')+'</span></th>';
  });
  ge('thr').innerHTML=h;
}

function af(){
  var q=ge('srch').value.trim().toLowerCase();
  filtered=R.parts.filter(function(p){
    var rm=RMSV[p[RI]],mgr=MGRSV[p[MI]],tech=TECHSV[p[TI]],role=ROLESV[p[ROI]];
    if(F.rm&&rm!==F.rm)return false;
    if(F.mgr&&mgr!==F.mgr)return false;
    if(F.tech&&!(tech===F.tech&&mgr===F.mgr))return false;
    if(F.role&&role!==F.role)return false;
    if(F.rep&&p[RE]!==F.rep)return false;
    if(F.img&&!(p[IMG]||getManualImg(p[PN])))return false;
    if(F.noimg&&(p[IMG]||getManualImg(p[PN])))return false;
    if(photoMatchActive){
      var pno=p[PN];
      if(!pno||!(pno in photoMatchSimByPno))return false;
      // No hard similarity cutoff here -- always surface the closest available
      // matches (ranked below) rather than risking zero results. PM_TOPN below
      // caps how many we actually show, and the status message is honest
      // about confidence (strong/possible/rough-guess) based on the score.
      if(photoMatchMfrFilter&&(p[MF]||'')!==photoMatchMfrFilter)return false;
      if(photoMatchKeywords.length){
        var hay=((p[FD]||'')+' '+(p[DS]||'')+' '+(p[MF]||'')+' '+(p[PN]||'')).toLowerCase();
        for(var ki=0;ki<photoMatchKeywords.length;ki++){
          if(hay.indexOf(photoMatchKeywords[ki])===-1)return false;
        }
      }
    }
    if(q){
      var h=[tech||'',mgr||'',rm||'',p[AR]||'',SUBSV[p[SI]]||'',p[ID]||'',p[DS]||'',p[FD]||'',p[MF]||'',p[PN]||'',role||'',p[PU]||'',p[LO]||''].join(' ').toLowerCase();
      var words=q.split(' ');
      for(var wi=0;wi<words.length;wi++){
        var w=words[wi];if(!w)continue;
        var terms=SYNS[w]?[w].concat(SYNS[w]):[w];
        var found=false;
        for(var ti=0;ti<terms.length;ti++){if(h.indexOf(terms[ti])>=0){found=true;break;}}
        if(!found)return false;
      }
    }
    return true;
  });
  // Note: data arrives from BigQuery pre-sorted by tcost DESC (a column
  // we no longer display/sort-by), so that "skip re-sort when already in
  // natural order" shortcut no longer applies to any remaining column --
  // always sort explicitly now.
  if(photoMatchActive){
    filtered.sort(function(a,b){return photoMatchSimByPno[b[PN]]-photoMatchSimByPno[a[PN]];});
    filtered=filtered.slice(0,PM_TOPN);
  }else{
    filtered.sort(function(a,b){
      var va=a[SRT.c],vb=b[SRT.c];
      if(typeof va==='number')return SRT.a?va-vb:vb-va;
      return SRT.a?String(va).localeCompare(String(vb)):String(vb).localeCompare(String(va));
    });
  }
  page=0;rP();uS();bP();bSB();
}

function rP(){
  var sl=filtered.slice(0,PG*(page+1)),h='';
  sl.forEach(function(p,i){h+=rH(p,i);});
  ge('tby').innerHTML=h;
  var rem=filtered.length-sl.length,lb=ge('lbtn');
  if(rem>0){lb.classList.remove('hid');lb.textContent='Load '+Math.min(PG,rem)+' more ('+rem.toLocaleString()+' remaining)';}
  else lb.classList.add('hid');
  ge('nores').classList.toggle('hid',filtered.length>0);
}
function lM(){page++;rP();}

function rH(p,i){
  var sl='r'+i,rc=RCLS[ROLESV[p[ROI]]]||'st';
  var tech=TECHSV[p[TI]],mgr=MGRSV[p[MI]],rm=RMSV[p[RI]],sub=SUBSV[p[SI]],role=ROLESV[p[ROI]];
  var td=tech.indexOf('WM#')===0?'<em style="color:var(--sub)">'+esc(tech)+'</em>':esc(tech);
  var manualImg=getManualImg(p[PN]);
  var imgSrc=p[IMG]||manualImg;
  var imgBlock;
  if(imgSrc){
    imgBlock='<div class="ec" style="display:flex;align-items:center;justify-content:center;padding:6px;cursor:zoom-in;position:relative" onclick="openLb(this.querySelector(&#39;img&#39;).src,&#39;'+esc(p[DS]).replace(/'/g,"\\'")+'&#39;)">'+(manualImg&&!p[IMG]?'<span class="mbadge">Added by you</span>':'')+'<img src="'+esc(imgSrc)+'" alt="" loading="lazy" style="max-width:100%;max-height:110px;object-fit:contain;border-radius:4px" onerror="this.parentElement.style.display=&#39;none&#39;"></div>';
  }else if(p[PN]){
    imgBlock='<div class="aib" onclick="event.stopPropagation();openAddImagePicker(&#39;'+esc(p[PN]).replace(/'/g,"\\'")+'&#39;,&#39;'+esc(p[DS]).replace(/'/g,"\\'")+'&#39;)"><span class="plus">+</span>Add Image</div>';
  }else{
    imgBlock='';
  }
  var x='<tr class="xr hid" id="x'+sl+'"><td colspan="10"><div class="xi">'
    +imgBlock
    +'<div class="ec" style="grid-column:1/-1"><div class="el">Full Description</div><div class="ev" style="font-size:.78rem;font-weight:500">'+esc(p[FD]||p[DS]||'—')+'</div></div>'
    +'<div class="ec"><div class="el">Regional Mgr</div><div class="ev" style="font-size:.8rem">'+esc(rm)+'</div><div class="es">Sub: '+esc(sub)+'</div></div>'
    +'<div class="ec"><div class="el">Manufacturer</div><div class="ev" style="font-size:.78rem">'+esc(p[MF])+'</div><div class="es">Part#: '+esc(p[PN])+' - '+role+'</div></div>'
    +'<div class="ec"><div class="el">Reorder Pt</div><div class="ev'+(p[RP]>0?' ok':'')+'">'+fN(p[RP])+'</div><div class="es">Max: '+fN(p[MQ])+'</div></div>'
    +'<div class="ec"><div class="el">Global OH</div><div class="ev">'+fN(p[GO])+'</div></div>'
    +'<div class="ec"><div class="el">Last Putaway</div><div class="ev" style="font-size:.78rem">'+esc(p[PU])+'</div></div>'
    +'<div class="ec"><div class="el">Last Order</div><div class="ev" style="font-size:.78rem">'+esc(p[LO])+'</div></div>'
    +'</div></td></tr>';
  var fdSub=(p[FD]&&p[FD]!==p[DS])?'<div style="font-size:.66rem;color:var(--sub);line-height:1.25;margin-top:1px;max-width:260px">'+esc(p[FD])+'</div>':'';
  return '<tr onclick="tX(&#39;'+sl+'&#39;)"><td style="font-size:.85rem;font-weight:700;color:#58a6ff;font-family:monospace">'+esc(p[PN])+'</td><td><div style="font-weight:600;line-height:1.3;max-width:260px">'+esc(p[DS])+'</div>'+fdSub+'<div style="font-size:.63rem;color:var(--sub);font-family:monospace;margin-top:1px">'+esc(p[ID])+'</div></td>'
    +'<td style="max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500">'+td+'</td>'
    +'<td style="font-size:.7rem;color:var(--sub)">'+esc(mgr)+'</td>'
    +'<td><span class="sbg">'+esc(sub)+'</span></td>'
    +'<td><span class="rb '+rc+'">'+role+'</span></td>'
    +'<td style="font-family:monospace;font-size:.75rem;font-weight:600">'+esc(p[AR])+'</td>'
    +'<td style="text-align:right">'+fN(p[QT])+'</td>'
    +'<td style="text-align:right;font-weight:600">'+f$(p[AT])+'</td>'
    +'<td><span class="'+(p[RE]==='Y'?'ry':'rn')+'">'+(p[RE]==='Y'?'&#10003; Yes':'-')+'</span></td>'
    +'</tr>'+x;
}

function tX(sl){var x=ge('x'+sl);if(x)x.classList.toggle('hid');}

function uS(){
  var vis=filtered.length,val=0,ts={},ms={},ls={},rc=0;
  filtered.forEach(function(p){
    val+=p[TC];ts[p[TI]]=1;ms[p[MI]]=1;ls[p[AR]]=1;if(p[RE]==='Y')rc++;
  });
  ge('si').textContent=vis.toLocaleString();ge('sv').textContent=fK(val);
  ge('sc2').textContent=Object.keys(ts).length;ge('sm').textContent=Object.keys(ms).length;
  ge('sl2').textContent=Object.keys(ls).length;ge('srp').textContent=rc;
  ge('fc').textContent=vis<R.parts.length?vis.toLocaleString()+' of '+R.parts.length.toLocaleString()+' shown':'';
  ge('tsl').textContent=(F.mgr?F.mgr:F.rm?F.rm:'All 15 Sub-Markets');
}

function bP(){
  var vm=F.rm?(RM_MGRS[F.rm]||[]).slice().sort():ALL_MGRS;
  var rh='<option value="">RGM</option>';
  ALL_RMS.forEach(function(r){rh+='<option value="'+esc(r)+'"'+(F.rm===r?' selected':'')+'>'+esc(r)+'</option>';});
  ge('rmSel').innerHTML=rh;
  ge('rmSel').value=F.rm||'';

  var mh='<option value="">FSM</option>';
  vm.forEach(function(m){mh+='<option value="'+esc(m)+'"'+(F.mgr===m?' selected':'')+'>'+esc(m)+'</option>';});
  ge('mgrSel').innerHTML=mh;
  ge('mgrSel').value=F.mgr||'';

  var vt=F.mgr?(MGR_TECHS[F.mgr]||[]).slice().sort():vm.reduce(function(acc,m){return acc.concat(MGR_TECHS[m]||[]);},[]).sort();
  var th='<option value="">TECH</option>';
  vt.forEach(function(t){th+='<option value="'+esc(t)+'"'+(F.tech===t?' selected':'')+'>'+esc(t)+'</option>';});
  ge('techSel').innerHTML=th;
  ge('techSel').value=F.tech||'';

  var oh='<option value="">ROLE</option>';
  ['GM','HVACR','FE','Store'].forEach(function(r){oh+='<option value="'+r+'"'+(F.role===r?' selected':'')+'>'+r+'</option>';});
  ge('roleSel').innerHTML=oh;
  ge('roleSel').value=F.role||'';
}

function sRole(v){F.role=v;af();}

function sTechSel(t){
  if(!t){F.tech='';af();return;}
  var mgr=null;
  Object.keys(MGR_TECHS).forEach(function(m){if(MGR_TECHS[m].indexOf(t)>=0)mgr=m;});
  F.tech=t;
  if(mgr){F.mgr=mgr;F.rm=MGR_RM[mgr]||F.rm;}
  af();
}

function bSB(){
  var vm=F.rm?(RM_MGRS[F.rm]||[]).slice().sort():F.mgr?[F.mgr]:ALL_MGRS;
  var bm={};
  R.tech_rows.forEach(function(t){
    var mgr=MGRSV[t[1]],rm=RMSV[t[2]];
    if(vm.indexOf(mgr)<0)return;
    if(F.mgr&&mgr!==F.mgr)return;
    if(!bm[mgr])bm[mgr]=[];
    bm[mgr].push({tech:TECHSV[t[0]],mgr:mgr,rm:rm,role:ROLESV[t[3]],area:t[4],items:t[5],value:t[6]});
  });
  var h='';
  Object.keys(bm).sort().forEach(function(mgr){
    var tl=bm[mgr].sort(function(a,b){return b.value-a.value;});
    h+='<div class="sgl">'+esc(mgr)+'</div>';
    h+='<div class="sr '+((!F.tech&&F.mgr===mgr)?'on':'')+'" onclick="sMGR(&#39;'+esc(mgr)+'&#39;)">'
      +'<div class="sd" style="background:var(--blue)"></div><div style="flex:1"><div class="sn">All Techs</div></div>'
      +'<div class="sk">'+fK(tl.reduce(function(s,t){return s+t.value;},0))+'</div></div>';
    tl.forEach(function(t){
      var col=RCOL[t.role]||'#bc8cff',on=F.tech===t.tech&&F.mgr===mgr;
      var itemCls=t.items<LOW_ITEM_THRESHOLD?' style="color:var(--red);font-weight:700"':'';
      h+='<div class="sr '+(on?'on':'')+'" onclick="sTech(&#39;'+esc(t.tech)+'&#39;,&#39;'+esc(mgr)+'&#39;)">'        +'<div class="sd" style="background:'+col+'"></div>'
        +'<div style="flex:1;min-width:0"><div class="sn" title="'+esc(t.tech)+'">'+esc(t.tech)+'</div>'
        +'<div class="ss">'+t.role+' - <span'+itemCls+'>'+t.items+'</span></div></div>'
        +'<div class="sk">'+fK(t.value)+'</div></div>';
    });
  });
  // No Inventory section at bottom of sidebar
  var niVisible=NI.filter(function(n){
    if(F.rm&&n.rm!==F.rm)return false;
    if(F.mgr&&n.mgr!==F.mgr)return false;
    return true;
  });
  if(niVisible.length){
    h+='<div class="sg" style="margin-top:12px;color:var(--red);border-color:#f8514940">No Inventory:</div>';
    niVisible.forEach(function(n){
      h+='<div class="sgl">'+esc(n.mgr)+' &bull; <span style="color:var(--sub)">'+esc(n.sub)+'</span></div>';
      n.techs.forEach(function(t){
        h+='<div class="sr" style="opacity:.75">'
          +'<div class="sd" style="background:#555"></div>'
          +'<div style="flex:1;min-width:0">'
          +'<div class="sn" style="color:var(--sub)">'+esc(t)+'</div>'
          +'<div class="ss" style="color:var(--red)">No items on record</div>'
          +'</div></div>';
      });
    });
  }
  ge('sb-body').innerHTML=h;
}

function toggleSB(){
  var panel=ge('sb'),arrow=ge('sb-arrow');
  var collapsed=panel.classList.toggle('collapsed');
  arrow.classList.toggle('collapsed',collapsed);
  localStorage.setItem('sb-collapsed',collapsed?'1':'0');
}


function sRM(v){F.rm=v;F.mgr='';F.tech='';af();}
function sMGR(v){F.mgr=v;F.tech='';if(v)F.rm=MGR_RM[v]||F.rm;af();}
function sTech(t,m){if(F.tech===t&&F.mgr===m){F.tech='';F.mgr='';}else{F.tech=t;F.mgr=m;F.rm=MGR_RM[m]||'';}af();}
function sF(g,v,btn){F[g]=v;document.querySelectorAll('.pl[data-g="'+g+'"],.npl[data-g="'+g+'"]').forEach(function(b){b.classList.remove('on');});btn.classList.add('on');af();}
function toggleImgF(){F.img=!F.img;if(F.img){F.noimg=false;ge('noimgf').classList.remove('on');}ge('imgf').classList.toggle('on',F.img);af();}
function toggleNoImgF(){F.noimg=!F.noimg;if(F.noimg){F.img=false;ge('imgf').classList.remove('on');}ge('noimgf').classList.toggle('on',F.noimg);af();}
function openLb(src,alt){ge('lbimg').src=src;ge('lbimg').alt=alt||'';ge('lbov').classList.remove('hid');}
function closeLb(){ge('lbov').classList.add('hid');ge('lbimg').src='';}
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeLb();});

// -- SEARCH BY PHOTO (real learned visual features via MobileNetV2, no server) --
// A previous version used a coarse 9x9 "difference hash" (blurry light/dark
// gradient pattern only) which could not reliably tell apart visually
// distinct parts -- it confused completely different items because it had
// no real concept of shape/texture/object identity. This version instead
// uses MobileNetV2 (a small pretrained image-classification neural network,
// loaded on demand from a public CDN, running fully client-side via
// TensorFlow.js -- no server, no per-query cost) to extract a real 1280-
// dimension learned feature vector per image, then ranks catalog parts by
// cosine similarity of that vector. This is a fundamentally more capable
// signal because the model has actually learned to recognize real-world
// object shape/texture/edges from millions of training images, rather than
// just comparing raw brightness patterns.
//
// Precomputed catalog embeddings live in a separate lazy-loaded file
// (catalog_embeddings.json, written by build_10b_inventory.py from
// sdi_scraper/embeddings_cache.json) so the ~3MB of vector data never
// slows down a normal page visit -- it's only fetched the first time a
// user actually clicks the camera button.
var PM_TOPN=30;
var PM_MODEL_READY=false, PM_MODEL_LOADING=false;
var PM_CATALOG_EMBEDDINGS=null; // {pno: {q:[int8...], s:scale}}
var PM_MOBILENET_MODEL=null;

function pmLoadScript(src){
  return new Promise(function(resolve,reject){
    var s=document.createElement('script');
    s.src=src;s.onload=resolve;s.onerror=function(){reject(new Error('failed to load '+src));};
    document.head.appendChild(s);
  });
}

function pmEnsureModelAndData(onProgress){
  if(PM_MODEL_READY)return Promise.resolve();
  if(PM_MODEL_LOADING)return PM_MODEL_LOADING;
  PM_MODEL_LOADING=(async function(){
    onProgress('Loading visual search model (first time only, ~10-20s)...');
    await pmLoadScript('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js');
    await pmLoadScript('https://cdn.jsdelivr.net/npm/@tensorflow-models/mobilenet@2.1.1/dist/mobilenet.min.js');
    var modelPromise=mobilenet.load({version:2,alpha:1.0});
    onProgress('Loading catalog photo index...');
    var dataPromise=fetch('catalog_embeddings.json').then(function(r){
      if(!r.ok)throw new Error('catalog_embeddings.json fetch failed: '+r.status);
      return r.json();
    });
    var results=await Promise.all([modelPromise,dataPromise]);
    PM_MOBILENET_MODEL=results[0];
    PM_CATALOG_EMBEDDINGS=results[1];
    PM_MODEL_READY=true;
  })();
  return PM_MODEL_LOADING;
}

// Must stay byte-identical to the equivalent logic in
// sdi_scraper/compute_embeddings_shard.py (LOAD_MODEL_JS's
// window.__autoCropToSubject + EMBED_DATAURL_JS) -- catalog embeddings and
// live user-photo embeddings MUST go through identical preprocessing or
// cosine similarity comparisons between them become meaningless. This
// auto-crop step (detect background color from image corners, crop to the
// bounding box of pixels that differ from it) was empirically verified to
// be critical: without it, a real phone photo's true catalog match ranked
// ~221st out of ~2300 parts (background dominated the embedding); with it,
// the true match ranks #1 with clean separation from the next-best guess.
function pmAutoCropToSubject(img){
  var sw=img.naturalWidth||img.width,sh=img.naturalHeight||img.height;
  var sampleW=200,sampleH=Math.max(1,Math.round(200*sh/sw));
  var cv=document.createElement('canvas');cv.width=sampleW;cv.height=sampleH;
  var ctx=cv.getContext('2d');
  ctx.drawImage(img,0,0,sampleW,sampleH);
  var data=ctx.getImageData(0,0,sampleW,sampleH).data;
  function pxAt(x,y){var i=(y*sampleW+x)*4;return [data[i],data[i+1],data[i+2]];}
  var patch=6,br=0,bg=0,bb=0,bn=0;
  [0,sampleH-patch].forEach(function(cy){
    [0,sampleW-patch].forEach(function(cx){
      for(var y=cy;y<cy+patch&&y<sampleH&&y>=0;y++){
        for(var x=cx;x<cx+patch&&x<sampleW&&x>=0;x++){
          var px=pxAt(x,y);br+=px[0];bg+=px[1];bb+=px[2];bn++;
        }
      }
    });
  });
  br/=bn;bg/=bn;bb/=bn;
  var THRESH=28,minX=sampleW,minY=sampleH,maxX=0,maxY=0,found=false;
  for(var y=0;y<sampleH;y++){
    for(var x=0;x<sampleW;x++){
      var px=pxAt(x,y);
      var d=Math.sqrt(Math.pow(px[0]-br,2)+Math.pow(px[1]-bg,2)+Math.pow(px[2]-bb,2));
      if(d>THRESH){
        found=true;
        if(x<minX)minX=x;if(x>maxX)maxX=x;
        if(y<minY)minY=y;if(y>maxY)maxY=y;
      }
    }
  }
  if(!found||(maxX-minX)<sampleW*0.05||(maxY-minY)<sampleH*0.05)return null;
  var marginX=(maxX-minX)*0.15,marginY=(maxY-minY)*0.15;
  minX=Math.max(0,minX-marginX);minY=Math.max(0,minY-marginY);
  maxX=Math.min(sampleW,maxX+marginX);maxY=Math.min(sampleH,maxY+marginY);
  var scaleX=sw/sampleW,scaleY=sh/sampleH;
  return {sx:minX*scaleX,sy:minY*scaleY,sw:(maxX-minX)*scaleX,sh:(maxY-minY)*scaleY};
}

// box (optional): {sx,sy,sw,sh} in the image's natural pixel coordinates,
// e.g. from the user-adjustable crop UI (see cropConfirm()). This is now
// the PRIMARY way real user photos get cropped -- an earlier version tried
// to auto-detect "background vs. part" purely from pixel-color heuristics,
// but that proved unreliable on real-world photos (uneven lighting,
// reflections, cluttered backgrounds all fool it, silently feeding the
// model a crop of the wrong region and producing garbage matches with no
// visible sign anything went wrong). Letting the user confirm/adjust the
// crop for a couple seconds guarantees the model always sees the actual
// part. pmAutoCropToSubject() is kept only as an initial best-guess
// starting position for that crop box, never as the final answer.
function pmEmbedImage(img,box){
  var cv=document.createElement('canvas');cv.width=224;cv.height=224;
  var ctx=cv.getContext('2d');
  if(box){
    ctx.drawImage(img,box.sx,box.sy,box.sw,box.sh,0,0,224,224);
  }else{
    var autoBox=pmAutoCropToSubject(img);
    if(autoBox){
      ctx.drawImage(img,autoBox.sx,autoBox.sy,autoBox.sw,autoBox.sh,0,0,224,224);
    }else{
      var sw=img.naturalWidth||img.width,sh=img.naturalHeight||img.height;
      var side=Math.min(sw,sh);
      ctx.drawImage(img,(sw-side)/2,(sh-side)/2,side,side,0,0,224,224);
    }
  }
  var t=PM_MOBILENET_MODEL.infer(cv,true); // true = return 1280-d embedding, not classification
  var arr=Array.from(t.dataSync());
  t.dispose();
  return arr;
}

function pmCosineSimQuantized(queryVec,q,scale){
  // queryVec: plain float array from the live model. q/scale: precomputed
  // catalog entry (int8 quantized). Dequantize on the fly and compare.
  var dot=0,na=0,nb=0;
  for(var i=0;i<queryVec.length;i++){
    var a=queryVec[i];
    var b=q[i]*scale;
    dot+=a*b;na+=a*a;nb+=b*b;
  }
  if(na===0||nb===0)return 0;
  return dot/(Math.sqrt(na)*Math.sqrt(nb));
}

// -- CROP CONFIRMATION UI --
// Real-world photos are too unpredictable for a fully automatic
// "guess where the background ends and the part begins" heuristic to be
// trustworthy (see pmAutoCropToSubject's comment). Instead, after a photo
// is picked we show it with a draggable/resizable box (seeded from that
// heuristic as a starting guess) and require the user to confirm/adjust
// it before running the match -- a couple seconds of user input in
// exchange for a huge, verifiable accuracy improvement.
var CROP_STATE=null; // {img, natW, natH, dispW, dispH, x,y,w,h (in DISPLAY px), drag:{...}}

function onPhotoPick(evt){
  var file=evt.target.files&&evt.target.files[0];
  if(!file)return;
  var reader=new FileReader();
  reader.onload=function(){
    var img=new Image();
    img.onload=function(){ openCropModal(img,reader.result); };
    img.onerror=function(){ alert('Could not load that photo, please try another one.'); };
    img.src=reader.result;
  };
  reader.onerror=function(){ alert('Could not read that photo, please try another one.'); };
  reader.readAsDataURL(file);
  evt.target.value='';
}

function openCropModal(img,dataUrl){
  var cropImgEl=ge('cropImg');
  cropImgEl.src=dataUrl;
  cropImgEl.onload=function(){
    // BUG FIX: the modal (and therefore its contents, including this <img>)
    // starts as display:none. Any element with a display:none ancestor
    // reports clientWidth/clientHeight as 0 -- so the modal MUST be made
    // visible BEFORE reading those values, or dispW/dispH are always 0 and
    // the crop box renders as an invisible 0x0 rectangle (this was a
    // 100%-reproducible bug on every photo, not a device/photo-specific one).
    ge('cropModal').classList.add('on');
    // Let the browser paint/layout the now-visible modal before measuring.
    requestAnimationFrame(function(){
      var dispW=cropImgEl.clientWidth,dispH=cropImgEl.clientHeight;
      var natW=img.naturalWidth,natH=img.naturalHeight;
      CROP_STATE={img:img,natW:natW,natH:natH,dispW:dispW,dispH:dispH};

      // Seed the initial box from the auto-detect heuristic (best-guess
      // starting point only -- user still confirms/adjusts it visually).
      var guess=pmAutoCropToSubject(img);
      var gx,gy,gw,gh;
      if(guess){
        gx=guess.sx/natW*dispW; gy=guess.sy/natH*dispH;
        gw=guess.sw/natW*dispW; gh=guess.sh/natH*dispH;
        // Cap to 90% of frame so there's always visible room to drag/enlarge
        // the box further if the auto-guess came back too close to full-size.
        if(gw>dispW*0.9){var cxm=gx+gw/2;gw=dispW*0.9;gx=cxm-gw/2;}
        if(gh>dispH*0.9){var cym=gy+gh/2;gh=dispH*0.9;gy=cym-gh/2;}
        gx=Math.max(0,Math.min(gx,dispW-gw)); gy=Math.max(0,Math.min(gy,dispH-gh));
      }else{
        gw=dispW*0.6; gh=dispH*0.6; gx=(dispW-gw)/2; gy=(dispH-gh)/2;
      }
      CROP_STATE.x=gx; CROP_STATE.y=gy; CROP_STATE.w=gw; CROP_STATE.h=gh;
      cropRenderRect();
    });
  };
}

function cropRenderRect(){
  var r=ge('cropRect');
  r.style.left=CROP_STATE.x+'px';
  r.style.top=CROP_STATE.y+'px';
  r.style.width=CROP_STATE.w+'px';
  r.style.height=CROP_STATE.h+'px';
}

function cropCancel(){
  ge('cropModal').classList.remove('on');
  CROP_STATE=null;
}

function cropConfirm(){
  if(!CROP_STATE)return;
  var s=CROP_STATE;
  var scaleX=s.natW/s.dispW,scaleY=s.natH/s.dispH;
  var box={sx:s.x*scaleX,sy:s.y*scaleY,sw:s.w*scaleX,sh:s.h*scaleY};
  var img=s.img;
  var previewDataUrl=ge('cropImg').src;
  ge('cropModal').classList.remove('on');

  // Build a small preview thumbnail of EXACTLY what will be searched, so
  // the result bar is self-explanatory (shows the crop, not the whole photo).
  var thumbCv=document.createElement('canvas');thumbCv.width=80;thumbCv.height=80;
  thumbCv.getContext('2d').drawImage(img,box.sx,box.sy,box.sw,box.sh,0,0,80,80);
  var croppedPreviewUrl=thumbCv.toDataURL('image/jpeg',0.85);

  var camBtn=ge('camBtn');
  camBtn.classList.add('busy');
  ge('pmbar').classList.add('on');
  ge('pmtxt').textContent='Preparing...';
  pmEnsureModelAndData(function(msg){ge('pmtxt').textContent=msg;})
    .then(function(){
      ge('pmtxt').textContent='Analyzing cropped photo...';
      var queryVec=pmEmbedImage(img,box);
      runPhotoMatch(queryVec,croppedPreviewUrl);
    })
    .catch(function(e){
      console.error(e);
      alert('Could not load the visual search model (check your internet connection) -- please try again.');
      ge('pmbar').classList.remove('on');
    })
    .finally(function(){camBtn.classList.remove('busy');CROP_STATE=null;});
}

(function(){
  function pos(e){
    if(e.touches&&e.touches.length)return {x:e.touches[0].clientX,y:e.touches[0].clientY};
    return {x:e.clientX,y:e.clientY};
  }
  function onDown(e){
    if(!CROP_STATE)return;
    var handle=e.target.getAttribute&&e.target.getAttribute('data-h');
    var stage=ge('cropStage');
    var stageRect=stage.getBoundingClientRect();
    var p=pos(e);
    CROP_STATE.drag={
      mode:handle?('resize-'+handle):'move',
      startX:p.x,startY:p.y,
      origX:CROP_STATE.x,origY:CROP_STATE.y,origW:CROP_STATE.w,origH:CROP_STATE.h,
      stageRect:stageRect
    };
    e.preventDefault();
  }
  // BUG FIX: the previous clamping math computed nw/nh first and only
  // capped them AFTER against the box's CURRENT x/y -- so whenever the
  // starting box already filled (or nearly filled) the image, which is
  // common since pmAutoCropToSubject's guess is often close to full-frame,
  // there was zero room left to grow into and dragging silently did
  // nothing at all (100% reproducible whenever the initial box was large,
  // which is exactly what the user's screenshots showed). Fix: for each
  // resize handle, compute the FIXED anchor corner (the opposite corner
  // from the handle being dragged) first, then clamp size against the
  // real distance from that anchor to the image edge.
  function onMove(e){
    if(!CROP_STATE||!CROP_STATE.drag)return;
    var p=pos(e);
    var d=CROP_STATE.drag;
    var dx=p.x-d.startX,dy=p.y-d.startY;
    var minSize=24;
    var dispW=CROP_STATE.dispW,dispH=CROP_STATE.dispH;
    if(d.mode==='move'){
      CROP_STATE.x=Math.max(0,Math.min(dispW-CROP_STATE.w,d.origX+dx));
      CROP_STATE.y=Math.max(0,Math.min(dispH-CROP_STATE.h,d.origY+dy));
    }else{
      var nx,ny,nw,nh;
      if(d.mode==='resize-se'){
        nx=d.origX; ny=d.origY;
        nw=Math.max(minSize,Math.min(d.origW+dx,dispW-nx));
        nh=Math.max(minSize,Math.min(d.origH+dy,dispH-ny));
      }else if(d.mode==='resize-sw'){
        var anchorRX=d.origX+d.origW;
        nw=Math.max(minSize,Math.min(d.origW-dx,anchorRX));
        nx=anchorRX-nw;
        ny=d.origY;
        nh=Math.max(minSize,Math.min(d.origH+dy,dispH-ny));
      }else if(d.mode==='resize-ne'){
        var anchorBY=d.origY+d.origH;
        nx=d.origX;
        nw=Math.max(minSize,Math.min(d.origW+dx,dispW-nx));
        nh=Math.max(minSize,Math.min(d.origH-dy,anchorBY));
        ny=anchorBY-nh;
      }else{
        var anchorRX2=d.origX+d.origW,anchorBY2=d.origY+d.origH;
        nw=Math.max(minSize,Math.min(d.origW-dx,anchorRX2));
        nx=anchorRX2-nw;
        nh=Math.max(minSize,Math.min(d.origH-dy,anchorBY2));
        ny=anchorBY2-nh;
      }
      CROP_STATE.x=nx; CROP_STATE.y=ny; CROP_STATE.w=nw; CROP_STATE.h=nh;
    }
    cropRenderRect();
    e.preventDefault();
  }
  function onUp(){ if(CROP_STATE)CROP_STATE.drag=null; }
  // BUG FIX: this script runs from a <script> tag placed deep in <body>,
  // AFTER the DOM (including #cropRect) has already been parsed -- so
  // document.readyState is already 'complete' by the time this code runs,
  // meaning 'DOMContentLoaded' has ALREADY FIRED and will never fire again.
  // Waiting for it here meant these listeners were never attached at all,
  // so dragging the crop box silently did nothing (100% reproducible).
  // Fix: attach immediately since the element already exists at this point.
  var rect=ge('cropRect');
  if(rect){
    rect.addEventListener('mousedown',onDown);
    rect.addEventListener('touchstart',onDown,{passive:false});
    document.addEventListener('mousemove',onMove);
    document.addEventListener('touchmove',onMove,{passive:false});
    document.addEventListener('mouseup',onUp);
    document.addEventListener('touchend',onUp);
  }
})();

function runPhotoMatch(queryVec,previewDataUrl){
  var simByPno={};
  var bestSim=-1;
  for(var pno in PM_CATALOG_EMBEDDINGS){
    var entry=PM_CATALOG_EMBEDDINGS[pno];
    var sim=pmCosineSimQuantized(queryVec,entry.q,entry.s);
    simByPno[pno]=sim;
    if(sim>bestSim)bestSim=sim;
  }
  photoMatchActive=true;
  photoMatchSimByPno=simByPno;
  photoMatchMfrFilter='';
  photoMatchKeywords=[];
  ge('pmimg').src=previewDataUrl;
  ge('pmbar').classList.add('on');
  var pmtxt=ge('pmtxt');
  var pct=Math.round(bestSim*100);

  // "Close call" detector: visual embeddings genuinely cannot read text on
  // a label (voltage/amperage/model suffix), so parts from the same
  // product family (e.g. different amp ratings of the same contactor line)
  // often look nearly identical and score within a few points of each
  // other. When that happens, the top-1 guess is not reliably trustworthy
  // even at a decent absolute similarity score -- so detect it explicitly
  // and steer the user toward the manufacturer/keyword narrowing fields
  // (which use exact catalog text, not vision) rather than implying
  // confidence the vision model doesn't actually have.
  var rankedSims=Object.keys(simByPno).map(function(k){return simByPno[k];}).sort(function(a,b){return b-a;});
  var closeCallMargin=0.04; // within 4 similarity points of the top score
  var closeCallCount=1;
  for(var ci=1;ci<rankedSims.length && ci<10;ci++){
    if(rankedSims[0]-rankedSims[ci]<=closeCallMargin)closeCallCount++;
    else break;
  }
  var isCloseCall=closeCallCount>=3; // 3+ near-tied candidates

  if(bestSim<0){
    pmtxt.textContent='No catalog photos available to compare against -- try clearing the search/filters above and try again.';
  }else if(isCloseCall){
    pmtxt.textContent=closeCallCount+' very similar-looking parts found (all within a few points of '+pct+'% similarity) -- the photo alone can\'t tell them apart (likely same product family, different rating printed on the label). Use the manufacturer/detail fields below to narrow it down.';
  }else if(bestSim>=0.72){
    pmtxt.textContent='Strong visual match found ('+pct+'% similarity) -- showing the closest '+PM_TOPN+' matches, best first.';
  }else if(bestSim>=0.5){
    pmtxt.textContent='Possible matches found ('+pct+'% similarity) -- showing the closest '+PM_TOPN+' matches, best first. Double-check these against the part before ordering.';
  }else{
    pmtxt.textContent='No confident visual matches in the catalog ('+pct+'% similarity at best) -- showing the closest available anyway, but treat these as rough guesses. Try a clearer, well-lit, close-up photo of just the part against a plain background.';
  }
  pmPopulateNarrowMfrs();
  ge('pmnarrow').classList.add('on');
  ge('pmMfrSel').value='';
  ge('pmKeywordInp').value='';
  ge('pmNarrowReset').style.display='none';
  if(isCloseCall){
    ge('pmnarrow').classList.add('pmnarrow-highlight');
  }else{
    ge('pmnarrow').classList.remove('pmnarrow-highlight');
  }
  af();
}

// BUG FIX: the manufacturer dropdown was previously scoped to only the
// manufacturers present among the TOP 150 visual-similarity candidates.
// That's backwards -- if the AI's visual guess is off (which is exactly
// when a user most needs this narrowing tool), the correct manufacturer
// may not even be in that top-150 slice, making it literally impossible to
// select. The manufacturer filter itself (in af()) already checks against
// the full parts list, not just the top-150 -- so there's no reason to
// artificially restrict the dropdown. Now sourced from the ENTIRE catalog's
// manufacturer list (~430 distinct values) so any real manufacturer can
// always be selected, regardless of how good or bad the visual guess was.
function pmPopulateNarrowMfrs(){
  var mfrSet={};
  for(var i=0;i<R.parts.length;i++){
    var p=R.parts[i];
    if(p[MF]){mfrSet[p[MF]]=true;}
  }
  var mfrList=Object.keys(mfrSet).sort();
  var sel=ge('pmMfrSel');
  var html='<option value="">Any manufacturer</option>';
 mfrList.forEach(function(m){html+='<option value="'+esc(m)+'">'+esc(m)+'</option>';});
  sel.innerHTML=html;
}

// BUG FIX: previously this only re-filtered/re-sorted the table (via af())
// but never touched the confidence message at the top (#pmtxt) -- so after
// narrowing to a manufacturer, the header kept showing the ORIGINAL
// best-similarity score from the unfiltered full-catalog search, even
// though that score almost always belongs to a COMPLETELY DIFFERENT part
// from a different manufacturer. This produced a genuinely misleading
// result: e.g. narrowing to a manufacturer whose closest photo match to
// the query is actually a poor ~20% similarity would still show the old
// "54% similarity" headline from before narrowing, falsely implying the
// now-displayed top result was a decent match when it might be a terrible
// one. Fix: recompute the best similarity WITHIN the currently active
// filter (manufacturer + keywords) every time narrowing changes, and show
// honest, re-tiered confidence messaging against that scoped result set,
// exactly like the initial (unfiltered) message does.
function pmApplyNarrow(){
  photoMatchMfrFilter=ge('pmMfrSel').value;
  var kwRaw=ge('pmKeywordInp').value.trim().toLowerCase();
  photoMatchKeywords=kwRaw?kwRaw.split(/\s+/).filter(Boolean):[];
  var anyActive=!!photoMatchMfrFilter||photoMatchKeywords.length>0;
  ge('pmNarrowReset').style.display=anyActive?'':'none';
  af();
  var matchCount=filtered.length;
  ge('pmNarrowCount').textContent=anyActive?(matchCount+' match'+(matchCount===1?'':'es')+' with these details'):'';
  pmUpdateConfidenceMessage();
}

// Recomputes the best similarity score among whatever is CURRENTLY shown
// (i.e. respecting any active manufacturer/keyword narrowing) and rewrites
// the header message accordingly, so the confidence claim always matches
// what the user is actually looking at.
function pmUpdateConfidenceMessage(){
  var pmtxt=ge('pmtxt');
  if(!filtered.length){
    pmtxt.textContent=photoMatchMfrFilter||photoMatchKeywords.length
      ?'No parts match both the photo AND these details -- try removing a detail, or double-check the manufacturer/spelling.'
      :'No catalog photos available to compare against -- try clearing the search/filters above and try again.';
    return;
  }
  var bestSimNow=-1;
  for(var i=0;i<filtered.length;i++){
    var s=photoMatchSimByPno[filtered[i][PN]];
    if(typeof s==='number'&&s>bestSimNow)bestSimNow=s;
  }
  var pct=Math.round(bestSimNow*100);
  var scopeNote=(photoMatchMfrFilter||photoMatchKeywords.length)?' among parts matching your details':'';
  if(bestSimNow<0){
    pmtxt.textContent='No similarity data available for the current results.';
  }else if(bestSimNow>=0.72){
    pmtxt.textContent='Strong visual match found'+scopeNote+' ('+pct+'% similarity) -- showing the closest matches, best first.';
  }else if(bestSimNow>=0.5){
    pmtxt.textContent='Possible match found'+scopeNote+' ('+pct+'% similarity) -- double-check against the part before ordering.';
  }else{
    pmtxt.textContent='No confident visual match'+scopeNote+' (best is only '+pct+'% similarity) -- the photo doesn\'t closely resemble any of these results. Treat this as a rough guess, or try removing/adjusting the manufacturer/detail filters.';
  }
}

var pmNarrowDebounceTimer=null;
function pmApplyNarrowDebounced(){
  clearTimeout(pmNarrowDebounceTimer);
  pmNarrowDebounceTimer=setTimeout(pmApplyNarrow,300);
}

function pmResetNarrow(){
  photoMatchMfrFilter='';
  photoMatchKeywords=[];
  ge('pmMfrSel').value='';
  ge('pmKeywordInp').value='';
  ge('pmNarrowReset').style.display='none';
  ge('pmNarrowCount').textContent='';
  af();
  pmUpdateConfidenceMessage();
}

function clearPhotoMatch(){
  photoMatchActive=false;
  photoMatchSimByPno=null;
  photoMatchMfrFilter='';
  photoMatchKeywords=[];
  ge('pmbar').classList.remove('on');
  ge('pmnarrow').classList.remove('on');
  ge('pmimg').src='';
  af();
}

// -- MANUAL IMAGE OVERRIDES (localStorage, this browser only until exported) --
var MANUAL_IMG_KEY='10b_manual_images_v1';
function getManualImgStore(){
  try{return JSON.parse(localStorage.getItem(MANUAL_IMG_KEY)||'{}');}catch(e){return{};}
}
function getManualImg(pno){
  if(!pno)return'';
  return getManualImgStore()[pno.toUpperCase()]||'';
}
var ADD_IMAGE_EMAIL='Michael.Leanox@walmart.com';
var aimState={pno:'',desc:'',dataUrl:'',blob:null};

function openAddImagePicker(pno,desc){
  if(!pno){alert('This part has no part number on file, so an image cannot be linked to it.');return;}
  aimState={pno:pno,desc:desc||'',dataUrl:'',blob:null};
  ge('aim-picker-desc').textContent=desc||pno;
  ge('aim-picker').classList.remove('hid');
}
function aimClosePicker(){
  ge('aim-picker').classList.add('hid');
}
function aimTriggerCamera(){
  ge('aim-camera-input').click();
}
function aimTriggerLibrary(){
  ge('aim-library-input').click();
}
function aimHandleFile(input){
  var file=input.files&&input.files[0];
  input.value='';
  if(!file)return;
  aimResizeImage(file,900,0.72,function(dataUrl,blob){
    aimState.dataUrl=dataUrl;
    aimState.blob=blob;
    ge('aim-picker').classList.add('hid');
    ge('aim-confirm-desc').textContent=aimState.desc||aimState.pno;
    ge('aim-confirm-img').src=dataUrl;
    ge('aim-confirm').classList.remove('hid');
  },function(){
    alert('Could not read that photo. Please try again.');
  });
}
function aimResizeImage(file,maxDim,quality,onDone,onErr){
  var img=new Image();
  var reader=new FileReader();
  reader.onload=function(e){
    img.onload=function(){
      var w=img.width,h=img.height;
      if(w>maxDim||h>maxDim){
        if(w>h){h=Math.round(h*maxDim/w);w=maxDim;}
        else{w=Math.round(w*maxDim/h);h=maxDim;}
      }
      var canvas=document.createElement('canvas');
      canvas.width=w;canvas.height=h;
      canvas.getContext('2d').drawImage(img,0,0,w,h);
      var dataUrl=canvas.toDataURL('image/jpeg',quality);
      canvas.toBlob(function(blob){onDone(dataUrl,blob);},'image/jpeg',quality);
    };
    img.onerror=onErr;
    img.src=e.target.result;
  };
  reader.onerror=onErr;
  reader.readAsDataURL(file);
}
function aimRetake(){
  ge('aim-confirm').classList.add('hid');
  ge('aim-picker').classList.remove('hid');
}
function aimConfirmYes(){
  ge('aim-confirm').classList.add('hid');
  var store=getManualImgStore();
  store[aimState.pno.toUpperCase()]=aimState.dataUrl;
  try{
    localStorage.setItem(MANUAL_IMG_KEY,JSON.stringify(store));
  }catch(e){
    console.warn('localStorage full -- image will still be emailed but will not persist locally',e);
  }
  af();
  sendAddImagePhoto(aimState.pno,aimState.desc,aimState.blob);
}
function sendAddImagePhoto(pno,desc,blob){
  var subject='10B Portal - New Part Image: '+(pno||'')+(desc?' - '+desc:'');
  var bodyText='A new part photo was submitted from the 10B Parts Inventory portal.\n\n'
    +'Part Number: '+(pno||'(none)')+'\n'
    +'Description: '+(desc||'(none)')+'\n\n'
    +'Photo is attached. Please add it to manual_overrides.json so it applies for everyone.';
  var fileName='part_'+(pno||'photo').replace(/[^a-z0-9]+/gi,'_')+'.jpg';
  var file=new File([blob],fileName,{type:blob.type||'image/jpeg'});
  // NOTE: navigator.share() used to run first here, but on iPhone it just
  // pops the generic Share Sheet (Messages/Mail/Outlook/AirDrop/etc) and
  // makes the user manually pick an app -- it also can NEVER pre-fill a
  // recipient (a Web Share API limitation on every browser). That looked
  // like "nothing happened" to users. mailto: is the only thing that
  // reliably auto-launches the default mail app addressed straight to
  // ADD_IMAGE_EMAIL with Subject/Body pre-filled, so we go straight there.
  var sendFallback=function(){
    var a=document.createElement('a');
    a.href=URL.createObjectURL(file);
    a.download=fileName;
    document.body.appendChild(a);a.click();document.body.removeChild(a);
    var mailto='mailto:'+ADD_IMAGE_EMAIL
      +'?subject='+encodeURIComponent(subject)
      +'&body='+encodeURIComponent(bodyText+'\n\n(Your browser downloaded '+fileName+' -- please attach it to this email before sending.)');
    setTimeout(function(){window.location.href=mailto;},400);
  };
  sendFallback();
}

function cS(i){var c=CSRT[i];if(SRT.c===c)SRT.a=!SRT.a;else{SRT.c=c;SRT.a=[DS,TI,MI,AR,PN,SI].indexOf(c)>=0;}bH();af();}
function cpLink(btn){var o=btn.textContent;btn.textContent='Copied!';setTimeout(function(){btn.textContent=o;},1500);try{navigator.clipboard.writeText(location.href);}catch(e){}}

document.body.classList.toggle('light',!dark);
if(_ERR){
  var eb=document.createElement('div');
  eb.style='background:#f85149;color:#fff;padding:16px 20px;font-size:.9rem;font-weight:700;position:fixed;top:0;left:0;right:0;z-index:9999';
  eb.textContent='ERROR: '+_ERR;
  document.body.prepend(eb);
}else{
  try{
    // (item-count badge removed from nav per user request)
    ge('rts').textContent='Data as of BUILT_TS';
    bH();af();
    if(localStorage.getItem('sb-collapsed')==='1'){
      ge('sb').classList.add('collapsed');
      ge('sb-arrow').classList.add('collapsed');
    }
    ge('srch').addEventListener('input',af);
  }catch(err){
    var eb2=document.createElement('div');
    eb2.style='background:#f85149;color:#fff;padding:16px 20px;font-size:.9rem;font-weight:700;position:fixed;top:0;left:0;right:0;z-index:9999';
    eb2.textContent='RENDER ERROR: '+err.message;
    document.body.prepend(eb2);
  }
}
</script></body></html>"""

out = r'C:\Users\Public\10b-inventory.html'
ts = datetime.now().strftime('%b %d, %Y %I:%M %p').replace(' 0', ' ')
final = HTML.replace('BUILT_TS', ts).replace('NI_PLACEHOLDER', NI_JS)
with open(out, 'w', encoding='utf-8') as f:
    f.write(final)
print('Built: ' + out + '  (' + str(len(final)//1024) + ' KB)')

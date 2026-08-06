
import json
P = open(r'C:\Users\Public\inv_payload.json', encoding='utf-8').read()

HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>367-A - Region 10B Parts Inventory</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d1117;--s1:#161b22;--s2:#21262d;--bd:#30363d;--tx:#e6edf3;--sub:#8b949e;--blue:#58a6ff;--grn:#3fb950;--red:#f85149;--amb:#d29922;--pur:#bc8cff;--wmt:#0071ce;--gold:#ffc220}
body.light{--bg:#f6f8fa;--s1:#fff;--s2:#f6f8fa;--bd:#d0d7de;--tx:#1f2328;--sub:#57606a;--blue:#0969da;--grn:#1a7f37;--red:#cf222e;--amb:#9a6700;--pur:#8250df}
body{background:var(--bg);color:var(--tx);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:13px;min-height:100vh}
/* NAV */
nav{background:var(--wmt);padding:6px 20px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;position:sticky;top:0;z-index:200;box-shadow:0 2px 8px rgba(0,0,0,.3)}
.nav-title{font-weight:700;font-size:1rem;color:#fff;white-space:nowrap;display:flex;align-items:center;gap:10px}
.nav-logo{height:44px;width:auto;display:block}
.nav-title-text{display:flex;flex-direction:column;line-height:1.15}
.nav-title-main{color:#fff}
.nav-title-sub{font-size:.62rem;font-weight:600;color:#ffc220;letter-spacing:.03em;border-top:2px solid #e9bf3f;padding-top:2px;margin-top:1px}
.nav-badge{background:rgba(255,255,255,.2);color:#fff;border-radius:12px;padding:2px 9px;font-size:.7rem;white-space:nowrap}
/* KEY FIX: search is a persistent input — never destroyed/recreated */
.srch-wrap{flex:1;min-width:200px;max-width:460px;position:relative}
#srch{width:100%;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.35);border-radius:22px;padding:7px 14px 7px 36px;color:#fff;font-size:.85rem;outline:none;font-family:inherit}
#srch::placeholder{color:rgba(255,255,255,.6)}
#srch:focus{background:rgba(255,255,255,.26);border-color:rgba(255,255,255,.7);box-shadow:0 0 0 3px rgba(255,255,255,.15)}
.srch-ico{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:rgba(255,255,255,.7);pointer-events:none}
.srch-clr{position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;color:rgba(255,255,255,.6);cursor:pointer;font-size:.9rem;padding:0;line-height:1;display:none}
#srch:not(:placeholder-shown)~.srch-clr{display:block}
.nav-r{margin-left:auto;display:flex;gap:6px}
.nbtn{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:6px;padding:5px 12px;font-size:.72rem;color:#fff;cursor:pointer;white-space:nowrap;font-family:inherit}
.nbtn:hover{background:rgba(255,255,255,.28)}
/* FILTER BAR */
.fbar{background:var(--s1);border-bottom:1px solid var(--bd);padding:7px 20px;display:flex;align-items:center;gap:7px;flex-wrap:wrap;position:sticky;top:53px;z-index:100}
.fl{font-size:.67rem;color:var(--sub);font-weight:700;text-transform:uppercase;letter-spacing:.04em;white-space:nowrap}
.pill{background:var(--s2);border:1px solid var(--bd);border-radius:20px;padding:3px 11px;font-size:.7rem;color:var(--sub);cursor:pointer;white-space:nowrap;transition:.12s;font-family:inherit}
.pill:hover{border-color:var(--blue);color:var(--blue)}.pill.on{background:var(--blue);border-color:var(--blue);color:#fff;font-weight:600}
.pill.g.on{background:var(--grn);border-color:var(--grn);color:#fff}
.pill.gold{border-color:var(--gold);color:var(--gold)}
.pill.gold:hover{background:rgba(255,194,32,.15);border-color:var(--gold);color:var(--gold)}
.pill.gold.on{background:var(--gold);border-color:var(--gold);color:#1a1a1a}
.add-img-box{grid-row:span 2;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding:6px;border:1.5px dashed var(--bd);border-radius:6px;cursor:pointer;color:var(--sub);font-size:.68rem;text-align:center;transition:.12s;min-height:90px}
.add-img-box:hover{border-color:var(--gold);color:var(--gold)}
.add-img-box .plus{font-size:1.3rem;line-height:1}
.manual-badge{position:absolute;top:2px;left:2px;background:var(--gold);color:#1a1a1a;font-size:.55rem;font-weight:700;padding:1px 5px;border-radius:3px;z-index:1}
.pill.r{border-color:var(--red);color:var(--red)}
.pill.r:hover{background:rgba(248,81,73,.15);border-color:var(--red);color:var(--red)}
.pill.r.on{background:var(--red);border-color:var(--red);color:#fff}
.divr{width:1px;height:18px;background:var(--bd);flex-shrink:0;margin:0 3px}
#filter-cnt{font-size:.7rem;color:var(--sub);margin-left:auto;white-space:nowrap}
/* STATS */
.stats{max-width:1600px;margin:12px auto 0;padding:0 20px;display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px}
.stat{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 14px;text-align:center}
.stat-v{font-size:1.35rem;font-weight:800;color:var(--tx);line-height:1}
.stat-l{font-size:.6rem;color:var(--sub);text-transform:uppercase;letter-spacing:.06em;margin-top:3px}
/* LAYOUT */
.wrap{max-width:1600px;margin:12px auto 0;padding:0 20px 30px;display:flex;gap:16px}
.sb-shell{display:flex;align-items:flex-start;flex-shrink:0;gap:6px;position:sticky;top:96px}
.sidebar{width:224px;flex-shrink:0;max-height:calc(100vh - 110px);overflow-y:auto;overflow-x:hidden;transition:width .2s ease,opacity .15s ease;opacity:1}
.sidebar.collapsed{width:0;opacity:0;pointer-events:none}
.sb-tab{width:20px;height:32px;flex-shrink:0;display:flex;align-items:center;justify-content:center;cursor:pointer;background:var(--s1);border:1px solid var(--bd);border-radius:6px;user-select:none}
.sb-tab:hover{background:var(--s2);border-color:var(--gold)}
.sb-arrow{color:var(--gold);font-size:.8rem;line-height:1;transition:transform .2s ease;display:block}
.sb-arrow.collapsed{transform:rotate(180deg)}
@media(max-width:900px){.wrap{padding:0 12px 20px}}
@media(max-width:900px) and (orientation:portrait){.sb-shell{display:none}}
.main{flex:1;min-width:0}
/* SIDEBAR */
.sb-hd{font-size:.65rem;font-weight:700;color:var(--sub);text-transform:uppercase;letter-spacing:.08em;padding:0 4px 5px;border-bottom:1px solid var(--bd);margin-bottom:6px;white-space:nowrap}
.sb-row{display:flex;align-items:center;gap:7px;padding:5px 6px;border-radius:6px;cursor:pointer;transition:background .1s}
.sb-row:hover{background:var(--s2)}.sb-row.on{background:var(--s2);box-shadow:inset 2px 0 0 var(--blue)}
.sb-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.sb-info{flex:1;min-width:0}
.sb-name{font-size:.72rem;color:var(--tx);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:500}
.sb-bar-wrap{height:3px;background:var(--bd);border-radius:2px;margin-top:3px;overflow:hidden}
.sb-bar{height:100%;border-radius:2px}
.sb-ct{font-size:.65rem;color:var(--sub);flex-shrink:0}
.sb-ct.low{color:var(--red);font-weight:700}
.sb-footer{margin-top:14px;padding:8px;background:var(--s2);border:1px solid var(--bd);border-radius:6px;font-size:.65rem;color:var(--sub);line-height:1.7}
.sb-footer b{color:var(--tx);display:block;margin-bottom:2px}
/* TABLE */
.tbl-box{background:var(--s1);border:1px solid var(--bd);border-radius:8px;overflow:hidden;margin-top:12px}
.tbl-hdr{display:flex;align-items:center;gap:8px;padding:10px 14px;border-bottom:1px solid var(--bd);background:var(--s2);flex-wrap:wrap}
.tbl-title{font-size:.88rem;font-weight:700;color:var(--tx)}
.tbl-sub{font-size:.7rem;color:var(--sub)}
.tbl-scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:.78rem}
thead th{padding:7px 10px;text-align:left;font-size:.6rem;font-weight:700;color:var(--sub);text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid var(--bd);white-space:nowrap;cursor:pointer;user-select:none;background:var(--s2)}
thead th:hover{color:var(--tx)}.srt-col{color:var(--blue)!important}
.si{margin-left:2px;opacity:.35;font-size:.58rem}.srt-col .si{opacity:1}
tbody tr.data-row{border-bottom:1px solid var(--bd);cursor:pointer;transition:background .08s}
tbody tr.data-row:hover td,tbody tr.data-row.open td{background:var(--s2)}
tbody tr.hidden{display:none!important}
td{padding:7px 10px;vertical-align:middle}
/* CELL STYLES */
.c-desc{font-weight:600;color:var(--tx);line-height:1.3;max-width:260px}
.c-fdesc{font-size:.66rem;color:var(--sub);line-height:1.25;margin-top:1px;max-width:260px}
.c-id{font-size:.63rem;color:var(--sub);font-family:monospace;margin-top:1px}
.c-tech{font-weight:500;white-space:nowrap}
.c-area{font-family:monospace;font-size:.75rem;font-weight:600}
/* ROLE BADGES */
.rb{border-radius:10px;padding:2px 8px;font-size:.62rem;font-weight:700;white-space:nowrap;border:1px solid}
.rb-gm{background:rgba(88,166,255,.1);color:var(--blue);border-color:rgba(88,166,255,.3)}
.rb-hv{background:rgba(63,185,80,.1);color:var(--grn);border-color:rgba(63,185,80,.3)}
.rb-fe{background:rgba(210,153,34,.1);color:var(--amb);border-color:rgba(210,153,34,.3)}
.rb-st{background:rgba(188,140,255,.1);color:var(--pur);border-color:rgba(188,140,255,.3)}
.rep-y{background:rgba(63,185,80,.1);color:var(--grn);border:1px solid rgba(63,185,80,.3);border-radius:10px;padding:2px 7px;font-size:.62rem;font-weight:700}
.rep-n{background:var(--s2);color:var(--sub);border:1px solid var(--bd);border-radius:10px;padding:2px 7px;font-size:.62rem}
/* EXPAND */
.exp-row td{background:var(--bg)!important;padding:0!important;border-bottom:2px solid var(--bd)!important;cursor:default!important}
.exp-inner{padding:12px 14px 14px 38px;display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:8px}
.ec{background:var(--s1);border:1px solid var(--bd);border-radius:6px;padding:8px 11px}
.ec-l{font-size:.58rem;font-weight:700;color:var(--sub);text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px}
.ec-v{font-size:.92rem;font-weight:700;color:var(--tx);line-height:1.2}
.ec-v.ok{color:var(--grn)}.ec-v.warn{color:var(--amb)}.ec-v.bad{color:var(--red)}
.ec-s{font-size:.63rem;color:var(--sub);margin-top:2px}
.no-res{text-align:center;padding:50px 20px;color:var(--sub);font-size:.85rem}
footer{border-top:1px solid var(--bd);padding:10px 20px;font-size:.63rem;color:var(--sub);display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;margin-top:20px}
/* LIGHTBOX */
.lb-overlay{position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:9999;display:flex;align-items:center;justify-content:center;padding:24px;overflow:auto}
.lb-overlay.hidden{display:none}
.lb-overlay img{max-width:100%;max-height:100%;object-fit:contain;border-radius:4px}
.lb-close{position:fixed;top:14px;right:18px;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);color:#fff;font-size:1.3rem;line-height:1;width:40px;height:40px;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:10000}
.lb-close:hover{background:rgba(255,255,255,.3)}
.lb-hint{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);color:rgba(255,255,255,.6);font-size:.68rem;z-index:10000;white-space:nowrap}
/* ADD-IMAGE MODAL */
.aim-overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:10001;display:flex;align-items:center;justify-content:center;padding:20px}
.aim-overlay.hidden{display:none}
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
</style>
</head>
<body>
<!-- PERSISTENT SEARCH — lives in nav, never destroyed -->
<nav>
  <div class="nav-title"><img class="nav-logo" src="upstream_logo.png" alt="Upstream Facility Services"><div class="nav-title-text"><span class="nav-title-main">Region 10B</span><span class="nav-title-sub">367-A</span></div></div>
  <span class="nav-badge" id="total-badge"></span>
  <div class="srch-wrap">
    <span class="srch-ico">🔍</span>
    <input id="srch" type="text" placeholder="Search tech, location #, part #, description…" autocomplete="off" spellcheck="false">
    <button class="srch-clr" onclick="clearSearch()" title="Clear search">✕</button>
  </div>
  <div class="nav-r">
    <button class="nbtn" onclick="copyLink(this)">🔗 Share</button>
    <button class="nbtn" onclick="toggleTheme()">☀️/🌙</button>
  </div>
</nav>

<!-- FILTER BAR — persistent too -->
<div class="fbar">
  <span class="fl">Role:</span>
  <button class="pill on" data-g="role" data-v="" onclick="setFilter('role','',this)">All</button>
  <button class="pill" data-g="role" data-v="GM" onclick="setFilter('role','GM',this)">GM</button>
  <button class="pill" data-g="role" data-v="HVACR" onclick="setFilter('role','HVACR',this)">HVACR</button>
  <button class="pill" data-g="role" data-v="FE" onclick="setFilter('role','FE',this)">FE</button>
  <button class="pill" data-g="role" data-v="Store" onclick="setFilter('role','Store',this)">Store</button>
  <div class="divr"></div>
  <span class="fl">Rep:</span>
  <button class="pill on" data-g="rep" data-v="" onclick="setFilter('rep','',this)">All</button>
  <button class="pill g" data-g="rep" data-v="Y" onclick="setFilter('rep','Y',this)">&#10003; Yes</button>
  <button class="pill" data-g="rep" data-v="N" onclick="setFilter('rep','N',this)">No</button>
  <div class="divr"></div>
  <button class="pill gold" id="img-filter-btn" onclick="toggleImgFilter()">Has Image</button>
  <button class="pill r" id="noimg-filter-btn" onclick="toggleNoImgFilter()" title="Show only parts that still need a photo">No Image</button>
  <div class="divr"></div>
  <span id="filter-cnt"></span>
</div>

<!-- STATS (updated in-place) -->
<div class="stats">
  <div class="stat"><div class="stat-v" id="st-items">—</div><div class="stat-l">Line Items</div></div>
  <div class="stat"><div class="stat-v" id="st-val">—</div><div class="stat-l">Total Value</div></div>
  <div class="stat"><div class="stat-v" id="st-techs">—</div><div class="stat-l">Technicians</div></div>
  <div class="stat"><div class="stat-v" id="st-locs">—</div><div class="stat-l">Locations</div></div>
  <div class="stat"><div class="stat-v" id="st-rep">—</div><div class="stat-l">Replenishable</div></div>
</div>

<div class="wrap">
  <div class="sb-shell">
    <div class="sidebar" id="sidebar">
      <div class="sb-hd">Technician</div>
      <div id="sidebar-body"></div>
    </div>
    <div class="sb-tab" onclick="toggleSidebar()" title="Show/hide technician list">
      <span class="sb-arrow" id="sb-arrow">&#9668;</span>
    </div>
  </div>
  <div class="main">
    <div class="tbl-box">
      <div class="tbl-hdr">
        <div>
          <div class="tbl-title">Parts Inventory — 367-A</div>
          <div class="tbl-sub">Michael Leanox · Manager 367-A · Source: semantic_fs_zeus_parts_inventory</div>
        </div>
      </div>
      <div class="tbl-scroll">
        <table id="inv-table">
          <thead><tr id="thead-row"></tr></thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
      <div class="no-res" id="no-res">No items match your search.</div>
    </div>
  </div>
</div>

<footer>
  <span>367-A · re-ods-prod.us_re_ods_prod_semantic_pub.semantic_fs_zeus_parts_inventory · Manager: M0L0IGD</span>
  <span id="refresh-ts"></span>
</footer>

<div class="lb-overlay hidden" id="lb-overlay" onclick="closeLightbox()">
  <button class="lb-close" onclick="event.stopPropagation();closeLightbox()" title="Close">&#10005;</button>
  <img id="lb-img" src="" alt="" onclick="event.stopPropagation()">
  <div class="lb-hint">Tap outside image or press Esc to close &middot; pinch to zoom</div>
</div>

<input type="file" id="aim-camera-input" accept="image/*" capture="environment" style="display:none" onchange="aimHandleFile(this)">
<input type="file" id="aim-library-input" accept="image/*" style="display:none" onchange="aimHandleFile(this)">

<div class="aim-overlay hidden" id="aim-picker" onclick="aimClosePicker()">
  <div class="aim-box" onclick="event.stopPropagation()">
    <div class="aim-title">Add a Part Photo</div>
    <div class="aim-sub" id="aim-picker-desc"></div>
    <button class="aim-btn" onclick="aimTriggerCamera()">Take Photo</button>
    <button class="aim-btn" onclick="aimTriggerLibrary()">Choose from Library</button>
    <button class="aim-btn cancel" onclick="aimClosePicker()">Cancel</button>
  </div>
</div>

<div class="aim-overlay hidden" id="aim-confirm">
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
const D=PAYLOAD_PLACEHOLDER;

// ── state ──────────────────────────────────────────────────────────────────
let filters={role:'',rep:'',tech:'',img:false,noimg:false};
let sortS={c:'area_total',a:false};
let dark = localStorage.getItem('inv-theme')!=='light';

const ROLE_CLS={GM:'rb-gm',HVACR:'rb-hv',FE:'rb-fe',Store:'rb-st'};
const ROLE_COL={GM:'#58a6ff',HVACR:'#3fb950',FE:'#d29922',Store:'#bc8cff'};
const fmt$=v=>'$'+Number(v).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
const fmtN=v=>Number(v).toLocaleString();

// ── THEME ──────────────────────────────────────────────────────────────────
function applyTheme(){document.body.classList.toggle('light',!dark);}
function toggleTheme(){dark=!dark;localStorage.setItem('inv-theme',dark?'dark':'light');applyTheme();}

// ── COLUMNS ────────────────────────────────────────────────────────────────
const COLS=[
  {k:'pno',   l:'Part #',         w:'120px'},
  {k:'desc',  l:'Part / Item ID',  w:'auto'},
  {k:'tech',  l:'Technician',      w:'160px'},
  {k:'role',  l:'Role',            w:'80px'},
  {k:'area',  l:'Location #',      w:'90px'},
  {k:'qty',   l:'Qty',             w:'60px', align:'right'},
  {k:'area_total',l:'Truck Total', w:'100px',align:'right'},
  {k:'rep',   l:'Rep?',            w:'70px'},
];

function buildHeader(){
  const tr=document.getElementById('thead-row');
  tr.innerHTML=COLS.map(c=>{
    const s=sortS.c===c.k;
    const ico=s?(sortS.a?'▲':'▼'):'⇅';
    return`<th class="${s?'srt-col':''}" onclick="colSort('${c.k}')">${c.l}<span class="si">${ico}</span></th>`;
  }).join('');
}

// ── BUILD ALL ROWS ONCE ────────────────────────────────────────────────────
function buildRows(){
  const tbody=document.getElementById('tbody');
  const sorted=[...D.parts].sort(cmp);
  tbody.innerHTML=sorted.map((p,i)=>{
    const sl='r'+i;
    // search string baked into data attribute — covers all searchable fields
    const srchStr=[p.tech,p.area,p.id,p.desc,p.fdesc,p.mfr,p.pno].join(' ').toLowerCase();
    const rep=p.rep==='Y';
    const manualImg=getManualImg(p.pno);
    const imgSrc=p.img||manualImg;
    const imgHtml = imgSrc
      ? `<div class="ec" style="grid-row:span 2;display:flex;align-items:center;justify-content:center;padding:6px;cursor:zoom-in;position:relative" onclick="event.stopPropagation();openLightbox(this.querySelector('img').src,'${(p.desc||'').replace(/'/g,"\\'")}')">${manualImg&&!p.img?'<span class="manual-badge">Added by you</span>':''}<img src="${imgSrc}" alt="${p.desc}" loading="lazy" style="max-width:100%;max-height:110px;object-fit:contain;border-radius:4px" onerror="this.parentElement.style.display='none'"></div>`
      : (p.pno ? `<div class="add-img-box" onclick="event.stopPropagation();openAddImagePicker('${p.pno.replace(/'/g,"\\'")}','${(p.desc||'').replace(/'/g,"\\'")}')"><span class="plus">+</span>Add Image</div>` : '');
    const det=`<tr class="exp-row hidden" id="exp-${sl}">
      <td colspan="${COLS.length}"><div class="exp-inner">
        ${imgHtml}
        <div class="ec"><div class="ec-l">Full Description</div><div class="ec-v" style="font-size:.75rem;font-weight:500">${p.fdesc||p.desc||'—'}</div></div>
        <div class="ec"><div class="ec-l">Manufacturer</div><div class="ec-v" style="font-size:.8rem">${p.mfr||'—'}</div><div class="ec-s">Part #: ${p.pno||'—'} · UOM: ${p.uom}</div></div>
        <div class="ec"><div class="ec-l">Reorder Point</div><div class="ec-v ${p.rop>0?'ok':''}">${fmtN(p.rop)}</div><div class="ec-s">Max Qty: ${fmtN(p.maxq)}</div></div>
        <div class="ec"><div class="ec-l">Global On-Hand</div><div class="ec-v">${fmtN(p.goh)}</div></div>
        <div class="ec"><div class="ec-l">Last Putaway</div><div class="ec-v" style="font-size:.78rem">${p.putaway||'—'}</div></div>
        <div class="ec"><div class="ec-l">Last Order</div><div class="ec-v" style="font-size:.78rem">${p.last_order||'—'}</div></div>
        <div class="ec"><div class="ec-l">Storage Type</div><div class="ec-v" style="font-size:.78rem">${p.loc||'—'}</div></div>
      </div></td></tr>`;
    return`<tr class="data-row"
        data-sl="${sl}"
        data-srch="${srchStr}"
        data-role="${p.role}"
        data-rep="${p.rep}"
        data-img="${imgSrc?'1':'0'}"
        data-tech="${p.tech}"
        onclick="togExp('${sl}')">
      <td style="font-size:.78rem;font-weight:700;color:#58a6ff;font-family:monospace">${p.pno||'—'}</td>
      <td><div class="c-desc">${p.desc}</div>${(p.fdesc&&p.fdesc!==p.desc)?`<div class="c-fdesc">${p.fdesc}</div>`:''}<div class="c-id">${p.id}</div></td>
      <td class="c-tech">${p.tech==='Store Inventory'?'<em style="color:var(--sub)">Store Inventory</em>':p.tech}</td>
      <td><span class="rb ${ROLE_CLS[p.role]||'rb-st'}">${p.role}</span></td>
      <td class="c-area">${p.area}</td>
      <td style="text-align:right">${fmtN(p.qty)}</td>
      <td style="text-align:right;font-weight:600">${fmt$(p.area_total)}</td>
      <td><span class="${rep?'rep-y':'rep-n'}">${rep?'&#10003; Yes':'—'}</span></td>
    </tr>${det}`;
  }).join('');
}

// ── FILTER — only toggles .hidden, never rebuilds DOM ─────────────────────
function applyFilters(){
  const q=document.getElementById('srch').value.trim().toLowerCase();
  const rows=document.querySelectorAll('tr.data-row');
  let vis=0,val=0,techSet=new Set(),locSet=new Set(),repCt=0;

  rows.forEach(row=>{
    const expRow=document.getElementById('exp-'+row.dataset.sl);
    const show=
      (!q || row.dataset.srch.includes(q)) &&
      (!filters.role || row.dataset.role===filters.role) &&
      (!filters.rep  || row.dataset.rep ===filters.rep)  &&
      (!filters.img  || row.dataset.img ==='1')  &&
      (!filters.noimg || row.dataset.img ==='0')  &&
      (!filters.tech || row.dataset.tech===filters.tech);
    row.classList.toggle('hidden',!show);
    if(expRow && !show) expRow.classList.add('hidden');
    if(show){
      vis++;
      const idx=row.rowIndex-1; // rough — use data instead
      const p=D.parts.find(p=>p.id===row.querySelector('.c-id').textContent);
      if(p){val+=p.tcost;if(p.rep==='Y')repCt++;}
      techSet.add(row.dataset.tech);
      locSet.add(row.querySelector('.c-area').textContent);
    }
  });

  // stats
  document.getElementById('st-items').textContent=vis.toLocaleString();
  document.getElementById('st-val').textContent=fmt$(val);
  document.getElementById('st-techs').textContent=techSet.size;
  document.getElementById('st-locs').textContent=locSet.size;
  document.getElementById('st-rep').textContent=repCt;
  document.getElementById('filter-cnt').textContent=
    vis<D.parts.length?`${vis} of ${D.parts.length} shown`:'';
  document.getElementById('no-res').style.display=vis===0?'block':'none';

  // sidebar highlight
  document.querySelectorAll('.sb-row').forEach(r=>{
    r.classList.toggle('on',r.dataset.tech===filters.tech);
  });
}

// ── SIDEBAR ────────────────────────────────────────────────────────────────
const LOW_ITEM_THRESHOLD=25;
function buildSidebar(){
  const maxV=Math.max(...D.techs.map(t=>t.value));
  const rows=D.techs.map(t=>{
    const pct=Math.round(t.value/maxV*100);
    const col=ROLE_COL[t.role]||'#bc8cff';
    const lowCls=t.items<LOW_ITEM_THRESHOLD?' low':'';
    return`<div class="sb-row" data-tech="${t.tech}" onclick="techFilter('${t.tech.replace(/'/g,"\\'")}')">
      <div class="sb-dot" style="background:${col}"></div>
      <div class="sb-info">
        <div class="sb-name" title="${t.tech}">${t.tech}</div>
        <div class="sb-bar-wrap"><div class="sb-bar" style="width:${pct}%;background:${col}"></div></div>
      </div>
      <div class="sb-ct${lowCls}">${t.items}</div>
    </div>`;
  }).join('');
  const noInv=D.no_inv.map(n=>`<div style="font-size:.65rem;color:var(--sub);padding:2px 4px">— ${n}</div>`).join('');
  document.getElementById('sidebar-body').innerHTML=
    `<div class="sb-row ${!filters.tech?'on':''}" data-tech="" onclick="techFilter('')">
       <div class="sb-dot" style="background:var(--sub)"></div>
       <div class="sb-info"><div class="sb-name">All Techs</div></div>
       <div class="sb-ct">${D.parts.length}</div>
     </div>
     ${rows}
     <div class="sb-footer"><b>No Inventory:</b>${noInv}</div>`;
}

function toggleSidebar(){
  const panel=document.getElementById('sidebar');
  const arrow=document.getElementById('sb-arrow');
  const collapsed=panel.classList.toggle('collapsed');
  arrow.classList.toggle('collapsed',collapsed);
  localStorage.setItem('sb-collapsed',collapsed?'1':'0');
}

// ── SORT ───────────────────────────────────────────────────────────────────
function cmp(a,b){
  const va=a[sortS.c]??'',vb=b[sortS.c]??'';
  if(typeof va==='number') return sortS.a?va-vb:vb-va;
  return sortS.a?String(va).localeCompare(String(vb)):String(vb).localeCompare(String(va));
}
function colSort(c){
  if(sortS.c===c)sortS.a=!sortS.a;else{sortS.c=c;sortS.a=c==='desc'||c==='tech'||c==='area'||c==='pno';}
  buildHeader();buildRows();applyFilters();
}

// ── EXPAND ─────────────────────────────────────────────────────────────────
function togExp(sl){
  const row=document.querySelector(`[data-sl="${sl}"]`);
  const det=document.getElementById('exp-'+sl);
  if(!det)return;
  det.classList.toggle('hidden');
  row.classList.toggle('open',!det.classList.contains('hidden'));
}

// ── FILTER SETTERS — never touch search input ──────────────────────────────
function setFilter(g,v,btn){
  filters[g]=v;
  document.querySelectorAll(`.pill[data-g="${g}"]`).forEach(b=>b.classList.remove('on'));
  btn.classList.add('on');
  applyFilters();
}
function techFilter(v){
  filters.tech=v;
  applyFilters();
  buildSidebar();
}
function toggleImgFilter(){
  filters.img=!filters.img;
  if(filters.img){filters.noimg=false;document.getElementById('noimg-filter-btn').classList.remove('on');}
  document.getElementById('img-filter-btn').classList.toggle('on',filters.img);
  applyFilters();
}
function toggleNoImgFilter(){
  filters.noimg=!filters.noimg;
  if(filters.noimg){filters.img=false;document.getElementById('img-filter-btn').classList.remove('on');}
  document.getElementById('noimg-filter-btn').classList.toggle('on',filters.noimg);
  applyFilters();
}
function clearSearch(){
  const s=document.getElementById('srch');s.value='';s.focus();applyFilters();
}

// -- LIGHTBOX -----------------------------------------------------------
function openLightbox(src,alt){
  document.getElementById('lb-img').src=src;
  document.getElementById('lb-img').alt=alt||'';
  document.getElementById('lb-overlay').classList.remove('hidden');
}
function closeLightbox(){
  document.getElementById('lb-overlay').classList.add('hidden');
  document.getElementById('lb-img').src='';
}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeLightbox();});

// -- MANUAL IMAGE OVERRIDES (localStorage, this browser only until exported) --
const MANUAL_IMG_KEY='10b_manual_images_v1';
function getManualImgStore(){
  try{return JSON.parse(localStorage.getItem(MANUAL_IMG_KEY)||'{}');}catch(e){return{};}
}
function getManualImg(pno){
  if(!pno)return'';
  return getManualImgStore()[pno.toUpperCase()]||'';
}
const ADD_IMAGE_EMAIL='Michael.Leanox@walmart.com';
let aimState={pno:'',desc:'',dataUrl:'',blob:null};

function openAddImagePicker(pno,desc){
  if(!pno){alert('This part has no part number on file, so an image cannot be linked to it.');return;}
  aimState={pno:pno,desc:desc||'',dataUrl:'',blob:null};
  document.getElementById('aim-picker-desc').textContent=desc||pno;
  document.getElementById('aim-picker').classList.remove('hidden');
}
function aimClosePicker(){
  document.getElementById('aim-picker').classList.add('hidden');
}
function aimTriggerCamera(){
  document.getElementById('aim-camera-input').click();
}
function aimTriggerLibrary(){
  document.getElementById('aim-library-input').click();
}
function aimHandleFile(input){
  const file=input.files&&input.files[0];
  input.value='';
  if(!file)return;
  aimResizeImage(file,900,0.72).then(({dataUrl,blob})=>{
    aimState.dataUrl=dataUrl;
    aimState.blob=blob;
    document.getElementById('aim-picker').classList.add('hidden');
    document.getElementById('aim-confirm-desc').textContent=aimState.desc||aimState.pno;
    document.getElementById('aim-confirm-img').src=dataUrl;
    document.getElementById('aim-confirm').classList.remove('hidden');
  }).catch(()=>{alert('Could not read that photo. Please try again.');});
}
function aimResizeImage(file,maxDim,quality){
  return new Promise((resolve,reject)=>{
    const img=new Image();
    const reader=new FileReader();
    reader.onload=e=>{
      img.onload=()=>{
        let w=img.width,h=img.height;
        if(w>maxDim||h>maxDim){
          if(w>h){h=Math.round(h*maxDim/w);w=maxDim;}
          else{w=Math.round(w*maxDim/h);h=maxDim;}
        }
        const canvas=document.createElement('canvas');
        canvas.width=w;canvas.height=h;
        canvas.getContext('2d').drawImage(img,0,0,w,h);
        const dataUrl=canvas.toDataURL('image/jpeg',quality);
        canvas.toBlob(blob=>resolve({dataUrl,blob}),'image/jpeg',quality);
      };
      img.onerror=reject;
      img.src=e.target.result;
    };
    reader.onerror=reject;
    reader.readAsDataURL(file);
  });
}
function aimRetake(){
  document.getElementById('aim-confirm').classList.add('hidden');
  document.getElementById('aim-picker').classList.remove('hidden');
}
function aimConfirmYes(){
  document.getElementById('aim-confirm').classList.add('hidden');
  const store=getManualImgStore();
  store[aimState.pno.toUpperCase()]=aimState.dataUrl;
  try{
    localStorage.setItem(MANUAL_IMG_KEY,JSON.stringify(store));
  }catch(e){
    console.warn('localStorage full -- image will still be emailed but will not persist locally',e);
  }
  buildRows();applyFilters();
  sendAddImagePhoto(aimState.pno,aimState.desc,aimState.blob);
}
async function sendAddImagePhoto(pno,desc,blob){
  const subject='10B Portal - New Part Image: '+(pno||'')+(desc?' - '+desc:'');
  const bodyText='A new part photo was submitted from the 10B Parts Inventory portal.\n\n'
    +'Part Number: '+(pno||'(none)')+'\n'
    +'Description: '+(desc||'(none)')+'\n\n'
    +'Photo is attached. Please add it to manual_overrides.json so it applies for everyone.';
  const fileName='part_'+(pno||'photo').replace(/[^a-z0-9]+/gi,'_')+'.jpg';
  const file=new File([blob],fileName,{type:blob.type||'image/jpeg'});
  // NOTE: navigator.share() used to run first here, but on iPhone it just
  // pops the generic Share Sheet (Messages/Mail/Outlook/AirDrop/etc) and
  // makes the user manually pick an app -- it also can NEVER pre-fill a
  // recipient (a Web Share API limitation on every browser). That looked
  // like "nothing happened" to users. mailto: is the only thing that
  // reliably auto-launches the default mail app with To/Subject/Body
  // pre-filled, so we go straight there instead of gambling on Share.
  const a=document.createElement('a');
  a.href=URL.createObjectURL(file);
  a.download=fileName;
  document.body.appendChild(a);a.click();document.body.removeChild(a);
  const mailto='mailto:'+ADD_IMAGE_EMAIL
    +'?subject='+encodeURIComponent(subject)
    +'&body='+encodeURIComponent(bodyText+'\n\n(Your browser downloaded '+fileName+' -- please attach it to this email before sending.)');
  setTimeout(()=>{window.location.href=mailto;},400);
}
function copyLink(btn){
  const u=new URL(location.href.split('?')[0]);
  const q=document.getElementById('srch').value.trim();
  if(q)u.searchParams.set('q',q);
  if(filters.tech)u.searchParams.set('tech',filters.tech);
  if(filters.role)u.searchParams.set('role',filters.role);
  if(filters.rep)u.searchParams.set('rep',filters.rep);
  navigator.clipboard.writeText(u.toString()).catch(()=>{});
  const o=btn.textContent;btn.textContent='✓ Copied!';setTimeout(()=>btn.textContent=o,1600);
}

// ── INIT ───────────────────────────────────────────────────────────────────
applyTheme();
document.getElementById('total-badge').textContent=D.parts.length+' items';
document.getElementById('refresh-ts').textContent='Refreshed '+new Date().toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});

buildHeader();
buildRows();
buildSidebar();
if(localStorage.getItem('sb-collapsed')==='1'){
  document.getElementById('sidebar').classList.add('collapsed');
  document.getElementById('sb-arrow').classList.add('collapsed');
}
// restore URL params (read-only, don't write back on init)
const sp=new URLSearchParams(location.search);
const qp=sp.get('q');
if(qp){document.getElementById('srch').value=qp;}
if(sp.get('tech'))filters.tech=decodeURIComponent(sp.get('tech'));
if(sp.get('role')){
  filters.role=sp.get('role');
  document.querySelectorAll(`.pill[data-g="role"]`).forEach(b=>{
    b.classList.toggle('on',b.dataset.v===filters.role);
  });
}
if(sp.get('rep')){
  filters.rep=sp.get('rep');
  document.querySelectorAll(`.pill[data-g="rep"]`).forEach(b=>{
    b.classList.toggle('on',b.dataset.v===filters.rep);
  });
}
applyFilters();

// ── SEARCH: input event only — never re-renders, never steals focus ────────
document.getElementById('srch').addEventListener('input',applyFilters);

// initial stats
applyFilters();
</script>
</body></html>"""

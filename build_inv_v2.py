
import json
P = open(r'C:\Users\Public\inv_payload.json', encoding='utf-8').read()

HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>367-A Parts Inventory</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d1117;--s1:#161b22;--s2:#21262d;--bd:#30363d;--tx:#e6edf3;--sub:#8b949e;--blue:#58a6ff;--grn:#3fb950;--red:#f85149;--amb:#d29922;--pur:#bc8cff;--wmt:#0071ce}
body.light{--bg:#f6f8fa;--s1:#fff;--s2:#f6f8fa;--bd:#d0d7de;--tx:#1f2328;--sub:#57606a;--blue:#0969da;--grn:#1a7f37;--red:#cf222e;--amb:#9a6700;--pur:#8250df}
body{background:var(--bg);color:var(--tx);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:13px;min-height:100vh}
/* NAV */
nav{background:var(--wmt);padding:10px 20px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;position:sticky;top:0;z-index:200;box-shadow:0 2px 8px rgba(0,0,0,.3)}
.nav-title{font-weight:700;font-size:1rem;color:#fff;white-space:nowrap}
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
.sidebar{width:224px;flex-shrink:0;position:sticky;top:96px;max-height:calc(100vh - 110px);overflow-y:auto}
@media(max-width:900px){.sidebar{display:none}.wrap{padding:0 12px 20px}}
.main{flex:1;min-width:0}
/* SIDEBAR */
.sb-hd{font-size:.65rem;font-weight:700;color:var(--sub);text-transform:uppercase;letter-spacing:.08em;padding:0 4px 5px;border-bottom:1px solid var(--bd);margin-bottom:6px}
.sb-row{display:flex;align-items:center;gap:7px;padding:5px 6px;border-radius:6px;cursor:pointer;transition:background .1s}
.sb-row:hover{background:var(--s2)}.sb-row.on{background:var(--s2);box-shadow:inset 2px 0 0 var(--blue)}
.sb-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.sb-info{flex:1;min-width:0}
.sb-name{font-size:.72rem;color:var(--tx);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:500}
.sb-bar-wrap{height:3px;background:var(--bd);border-radius:2px;margin-top:3px;overflow:hidden}
.sb-bar{height:100%;border-radius:2px}
.sb-ct{font-size:.65rem;color:var(--sub);flex-shrink:0}
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
</style>
</head>
<body>
<!-- PERSISTENT SEARCH — lives in nav, never destroyed -->
<nav>
  <div class="nav-title">📦 367-A Parts Inventory</div>
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
  <button class="pill g" data-g="rep" data-v="Y" onclick="setFilter('rep','Y',this)">✓ Yes</button>
  <button class="pill" data-g="rep" data-v="N" onclick="setFilter('rep','N',this)">No</button>
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
  <div class="sidebar" id="sidebar"></div>
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

<script>
const D=PAYLOAD_PLACEHOLDER;

// ── state ──────────────────────────────────────────────────────────────────
let filters={role:'',rep:'',tech:''};
let sortS={c:'tcost',a:false};
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
  {k:'desc',  l:'Part / Item ID',  w:'auto'},
  {k:'tech',  l:'Technician',      w:'160px'},
  {k:'role',  l:'Role',            w:'80px'},
  {k:'area',  l:'Location #',      w:'90px'},
  {k:'qty',   l:'Qty',             w:'60px', align:'right'},
  {k:'tcost', l:'Value',           w:'90px', align:'right'},
  {k:'area_total',l:'Truck Total', w:'100px',align:'right'},
  {k:'rep',   l:'Rep?',            w:'70px'},
  {k:'pno',   l:'Part #',         w:'120px'},
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
    const imgHtml = p.img ? `<div class="ec" style="grid-row:span 2;display:flex;align-items:center;justify-content:center;padding:6px"><img src="${p.img}" alt="${p.desc}" loading="lazy" style="max-width:100%;max-height:110px;object-fit:contain;border-radius:4px" onerror="this.parentElement.style.display='none'"></div>` : '';
    const det=`<tr class="exp-row hidden" id="exp-${sl}">
      <td colspan="${COLS.length}"><div class="exp-inner">
        ${imgHtml}
        <div class="ec"><div class="ec-l">Full Description</div><div class="ec-v" style="font-size:.75rem;font-weight:500">${p.fdesc||p.desc||'—'}</div></div>
        <div class="ec"><div class="ec-l">Manufacturer</div><div class="ec-v" style="font-size:.8rem">${p.mfr||'—'}</div><div class="ec-s">Part #: ${p.pno||'—'} · UOM: ${p.uom}</div></div>
        <div class="ec"><div class="ec-l">Unit Cost</div><div class="ec-v">${fmt$(p.ucost)}</div></div>
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
        data-tech="${p.tech}"
        onclick="togExp('${sl}')">
      <td><div class="c-desc">${p.desc}</div>${(p.fdesc&&p.fdesc!==p.desc)?`<div class="c-fdesc">${p.fdesc}</div>`:''}<div class="c-id">${p.id}</div></td>
      <td class="c-tech">${p.tech==='Store Inventory'?'<em style="color:var(--sub)">Store Inventory</em>':p.tech}</td>
      <td><span class="rb ${ROLE_CLS[p.role]||'rb-st'}">${p.role}</span></td>
      <td class="c-area">${p.area}</td>
      <td style="text-align:right">${fmtN(p.qty)}</td>
      <td style="text-align:right;font-weight:600">${fmt$(p.tcost)}</td>
      <td style="text-align:right;font-size:.7rem;color:var(--sub)">${fmt$(p.area_total)}</td>
      <td><span class="${rep?'rep-y':'rep-n'}">${rep?'✓ Yes':'—'}</span></td>
      <td style="font-size:.68rem;color:var(--sub);font-family:monospace">${p.pno||'—'}</td>
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
function buildSidebar(){
  const maxV=Math.max(...D.techs.map(t=>t.value));
  const rows=D.techs.map(t=>{
    const pct=Math.round(t.value/maxV*100);
    const col=ROLE_COL[t.role]||'#bc8cff';
    return`<div class="sb-row" data-tech="${t.tech}" onclick="techFilter('${t.tech.replace(/'/g,"\\'")}')">
      <div class="sb-dot" style="background:${col}"></div>
      <div class="sb-info">
        <div class="sb-name" title="${t.tech}">${t.tech}</div>
        <div class="sb-bar-wrap"><div class="sb-bar" style="width:${pct}%;background:${col}"></div></div>
      </div>
      <div class="sb-ct">${t.items}</div>
    </div>`;
  }).join('');
  const noInv=D.no_inv.map(n=>`<div style="font-size:.65rem;color:var(--sub);padding:2px 4px">— ${n}</div>`).join('');
  document.getElementById('sidebar').innerHTML=
    `<div class="sb-hd">Technician</div>
     <div class="sb-row ${!filters.tech?'on':''}" data-tech="" onclick="techFilter('')">
       <div class="sb-dot" style="background:var(--sub)"></div>
       <div class="sb-info"><div class="sb-name">All Techs</div></div>
       <div class="sb-ct">${D.parts.length}</div>
     </div>
     ${rows}
     <div class="sb-footer"><b>No Inventory:</b>${noInv}</div>`;
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
function clearSearch(){
  const s=document.getElementById('srch');s.value='';s.focus();applyFilters();
}

// ── LINK ───────────────────────────────────────────────────────────────────
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

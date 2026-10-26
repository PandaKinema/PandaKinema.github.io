(() => {
const MM_TO_PX=3.7795275591;

/* 画像(data URL)は1枚で数MBになる。取り消し履歴や複製のたびに丸ごとコピーするとメモリがふくらむので、
   同じ画像は1つの文字列を共有し、履歴と自動保存では短いIDに置き換えて持つ。 */
const IMG_TOKEN="cmm-img://";
const imgIdByUrl=new Map(),imgUrlById=new Map();
function newImgId(){return Date.now().toString(36)+Math.random().toString(36).slice(2,8)}
function isBigDataUrl(v){return typeof v==="string"&&v.length>512&&v.startsWith("data:")}
function internImage(url,id){let k=imgIdByUrl.get(url);if(k===undefined){k=id||newImgId();imgIdByUrl.set(url,k);imgUrlById.set(k,url)}else if(id&&id!==k)imgUrlById.set(id,imgUrlById.get(k));return k}
function packImages(k,v){return isBigDataUrl(v)?IMG_TOKEN+internImage(v):v}
function unpackImages(k,v){if(typeof v==="string"&&v.startsWith(IMG_TOKEN)){const u=imgUrlById.get(v.slice(IMG_TOKEN.length));return u===undefined?null:u}return v}
function canonicalImage(url){return isBigDataUrl(url)?imgUrlById.get(internImage(url)):url}
/* ---- 単位:中では 文字=pt・長さ=mm で持ち、表示だけ設定した単位に換算する ---- */
const TEXT_UNITS={pt:{label:"pt",k:1,step:.5},Q:{label:"Q",k:72/25.4/4,step:1},px:{label:"px",k:.75,step:1}};
const LEN_UNITS={mm:{label:"mm",k:1,dp:2},cm:{label:"cm",k:10,dp:3},inch:{label:"in",k:25.4,dp:3},pt:{label:"pt",k:25.4/72,dp:2},px:{label:"px",k:25.4/96,dp:1}};
let units={len:"mm",text:"pt"};
try{const u=JSON.parse(localStorage.getItem("cmm-units")||"{}");if(LEN_UNITS[u.len])units.len=u.len;if(TEXT_UNITS[u.text])units.text=u.text}catch(e){}
function saveUnits(){try{localStorage.setItem("cmm-units",JSON.stringify(units))}catch(e){}}
function textToDisp(pt){return +(pt/TEXT_UNITS[units.text].k).toFixed(1)}
function dispToText(v){return +(Number(v)*TEXT_UNITS[units.text].k).toFixed(2)}
function fmtLen(mm,withUnit=true){const u=LEN_UNITS[units.len],v=+(mm/u.k).toFixed(u.dp);return withUnit?`${v} ${u.label}`:String(v)}
/* 文字サイズの入力欄:表示は設定の単位、読むときはptに戻す */
function setSizeInput(input,pt){
  if(!input)return;const u=TEXT_UNITS[units.text];
  input.step=u.step;input.min=textToDisp(4);input.max=textToDisp(400);input.value=textToDisp(pt);
  const suf=input.parentElement?.querySelector(".unit-suffix");if(suf)suf.textContent=u.label;
}
function readSizeInput(input,fallbackPt){const v=Number(input?.value);return v>0?dispToText(v):fallbackPt}
/* ---- フォント:Google Fonts(SIL OFL、商用・印刷物に使える)。system は端末の標準書体 ---- */
const FONTS=[
  {id:"gothic",label:"ゴシック",css:"'Noto Sans JP',sans-serif"},
  {id:"mincho",label:"明朝",css:"'Noto Serif JP',serif"},
  {id:"maru",label:"丸ゴシック",css:"'Zen Maru Gothic',sans-serif"},
  {id:"heavy",label:"極太",css:"'Dela Gothic One',sans-serif"},
  {id:"system",label:"端末の標準",css:"-apple-system,BlinkMacSystemFont,'Segoe UI','Hiragino Sans','Yu Gothic',sans-serif"}
];
function fontCss(id){return (FONTS.find(f=>f.id===id)||FONTS.find(f=>f.id===(deck.font||"system"))||FONTS[4]).css}
function fontOptions(withDefault){return (withDefault?'<option value="">基本</option>':"")+FONTS.map(f=>`<option value="${f.id}">${f.label}</option>`).join("")}
/* 印刷・PDFの前に、使っているフォントを読み込み終えるまで待つ(最大4秒) */
async function fontsReady(){
  if(!document.fonts)return;
  const texts=new Map(),add=(id,t)=>{const css=fontCss(id||deck.font);texts.set(css,(texts.get(css)||"")+(t||""))};
  Object.values(deck.cards).flatMap(c=>[c.front,c.back]).forEach(f=>{if(!f)return;
    (f.textBoxes||[]).forEach(t=>add(t.style?.font,t.text));(f.frameTexts||[]).forEach(t=>add(t.style?.font,t.text));
    add(f.nameStyle?.font,f.name);add(f.descStyle?.font,f.desc);add(f.mainStyle?.font,f.main);add(f.numberStyle?.font,f.number);add("",sheetTitle)});
  const jobs=[];texts.forEach((t,css)=>{const sample=[...new Set((t||"Aあ").split(""))].join("").slice(0,600)||"Aあ";["400","700"].forEach(w=>jobs.push(document.fonts.load(`${w} 16px ${css}`,sample).catch(()=>{})))});
  await Promise.race([Promise.all(jobs).then(()=>document.fonts.ready),new Promise(r=>setTimeout(r,4000))]);
}
/* 文字サイズの初期値(pt) */
const SIZE={text:10.5,frame:10.5,tcgName:11,tcgDesc:9,word:40,number:88};
/* 以前のデータ(文字はpx、トランプの数字はmm)をptに直す */
function migrateFaceUnits(f){
  if(!f)return;const cv=(st,k)=>{if(st&&typeof st.size==="number")st.size=+(st.size*k).toFixed(2)};
  (f.textBoxes||[]).forEach(t=>cv(t.style,.75));(f.frameTexts||[]).forEach(t=>cv(t.style,.75));
  ["nameStyle","descStyle","mainStyle","textStyle","subStyle"].forEach(k=>cv(f[k],.75));
  cv(f.numberStyle,72/25.4);
}
const PRESET=["#111111","#ffffff","#d94a4a","#e48a2a","#e4c62a","#6bbf59","#2fa67f","#3a8dde","#5967d8","#8b5cc7","#d45aa1","#8a6b4c"];
let recentColors=[];

const makePlain=()=>({type:"plain",bgColor:"#ffffff",bgImage:null,bgBorderColor:"#222222",bgBorderWidth:1,bgBorderNone:true,bgBorderAlign:"inside"});
const makePlaying=()=>({type:"template",template:"playing",number:"7",suit:"●",suitSize:"medium",suitCount:1,suitMode:"text",suitImage:null,cornerPlacement:"four",
  numberColor:"#d94a4a",text:"",textColor:"#222222",bgColor:"#ffffff",bgImage:null,bgBorderColor:"#222222",bgBorderWidth:1,bgBorderNone:true,bgBorderAlign:"inside",
  numberStyle:{size:SIZE.number,bold:true,italic:false}});
const makeImageFace=()=>({type:"image",src:null,bgColor:"#ffffff",bgImage:null});
/* ---- デッキ:カードの一覧(deck.cards)と、印刷する並び(deck.order) ----
   deck.cards[id]={front,back}。deck.order=[id,...] で、同じidが並べば同じカードを複数枚刷る。
   pages は表示用に deck から作り直す配列(中身は各カードの面そのものを指すので、面の中身を直せばカードに反映される)。 */
const MAX_PAGES=25;
let deck={cards:{},order:[]};
let pages=[],currentPage=0,selected=0,sheetTitle="";
let viewSide="front";                 // 両面印刷モードのPC表示:オモテ面/ウラ面
let printSettings={backFlip:"horizontal",backOffsetX:0,backOffsetY:0};
let lastArrangement=null,lastN=null;
function newCardId(){return "c"+Date.now().toString(36)+Math.random().toString(36).slice(2,7)}
function newCardFaces(){return {front:makePlaying(),back:makePlain()}}
function addCard(front,back){const id=newCardId(),d=newCardFaces();deck.cards[id]={front:front||d.front,back:back||d.back};return id}

const el=id=>document.getElementById(id);
const paper=el("paper"),grid=el("sheetGrid");

const CARD_SIZES={
  poker:{label:"ポーカー",w:63,h:88},
  bridge:{label:"ブリッジ",w:58,h:89},
  business:{label:"名刺",w:55,h:91},
  yugioh:{label:"遊戯王サイズ",w:59,h:86},
  credit:{label:"クレジット",w:54,h:86},
  half:{label:"ハーフ",w:44,h:63}
};
function cardMM(){return CARD_SIZES[el("cardSize")?.value]||CARD_SIZES.poker}
/* 面付け:fold=表裏を並べて折る / both=両面印刷 / single=片面 */
function layoutMode(){const v=el("impositionMode")?.value;return v==="single"?"single":v==="both"?"both":"fold"}
function isPairLayout(){return layoutMode()==="fold"}
function isSingleMode(){return layoutMode()==="single"}
/* 表示の並べ方:pairs=カードごとにオモテ・ウラ / single=オモテだけ / front・back=両面印刷のシート */
function arrangement(){const m=layoutMode();if(m==="fold")return "pairs";if(m==="single")return "single";return mobileUIActive()?"pairs":(viewSide==="back"?"back":"front")}
let cardOrientation="portrait";
function isLandscapeCard(){ return cardOrientation==="landscape"; }
function optimalPaperOrientationForMode(){ return !isPairLayout()?(isLandscapeCard()?"landscape":"portrait"):(isLandscapeCard()?"portrait":"landscape"); }
function paperMM(){const l=el("paperOrientation").value==="landscape",a3=el("paperSize")?.value==="a3";return a3?(l?{w:420,h:297}:{w:297,h:420}):(l?{w:297,h:210}:{w:210,h:297})}
function faceMM(){const c=cardMM();return isLandscapeCard()?{w:c.h,h:c.w}:{w:c.w,h:c.h}}
function pairMM(){const f=faceMM();if(!isPairLayout())return f;return isLandscapeCard()?{w:f.w,h:f.h*2}:{w:f.w*2,h:f.h}}
function gridRC(){const p=paperMM(),q=pairMM();return {cols:Math.max(1,Math.floor(p.w/q.w)),rows:Math.max(1,Math.floor(p.h/q.h))}}
function cardsPerPage(){const g=gridRC();return g.cols*g.rows}
function facesPerPage(){return pages[currentPage]?.length||cardsPerPage()}
function blockMM(){const q=pairMM(),g=gridRC();return {w:q.w*g.cols,h:q.h*g.rows}}
/* 用紙・カード・面付けを変えたとき:カードはそのまま、1ページの枚数だけ変わる */
function resizePagesForLayout(){trimTrailingBlanks();syncPages()}

function isBlankFace(f){
  if(!f)return true;
  return f.type==="plain"&&!f.bgImage&&!f.bgNone&&String(f.bgColor||"#ffffff").toLowerCase()==="#ffffff"&&f.bgBorderNone!==false
    &&!(f.textBoxes||[]).length&&!(f.frameTexts||[]).length&&!(f.optionImages||[]).length&&!(f.shapes||[]).length;
}
function isBlankCard(id){const c=deck.cards[id];return !c||(isBlankFace(c.front)&&isBlankFace(c.back))}
function cardCount(id){let n=0;for(const x of deck.order)if(x===id)n++;return n}
function padOrder(){const n=cardsPerPage(),want=Math.max(1,Math.ceil(deck.order.length/n))*n;while(deck.order.length<want)deck.order.push(addCard())}
function trimTrailingBlanks(){
  const n=cardsPerPage();
  while(deck.order.length>n){const id=deck.order[deck.order.length-1];if(!isBlankCard(id)||cardCount(id)>1)break;deck.order.pop()}
}
function gcCards(){const used=new Set(deck.order);for(const id in deck.cards)if(!used.has(id))delete deck.cards[id]}
function pageCount(){return Math.max(1,Math.ceil(deck.order.length/cardsPerPage()))}
/* 両面印刷のウラ面:紙を裏返したとき重なるよう、左右(または上下)を入れ替えた位置に置く */
function backIndex(i){const g=gridRC(),r=Math.floor(i/g.cols),c=i%g.cols;return printSettings.backFlip==="vertical"?(g.rows-1-r)*g.cols+c:r*g.cols+(g.cols-1-c)}
function slotAt(p,i,a=arrangement(),n=cardsPerPage()){
  if(a==="pairs")return {slot:p*n+Math.floor(i/2),side:i%2?"back":"front"};
  if(a==="back")return {slot:p*n+backIndex(i),side:"back"};
  return {slot:p*n+i,side:"front"};
}
function indexOfSlot(slot,side,a=arrangement()){
  const n=cardsPerPage(),k=slot%n;
  if(a==="pairs")return k*2+(side==="back"?1:0);
  if(a==="back"){for(let i=0;i<n;i++)if(backIndex(i)===k)return i}
  return k;
}
function facesOf(p,a=arrangement()){
  const n=cardsPerPage(),len=a==="pairs"?n*2:n,out=[];
  for(let i=0;i<len;i++){const {slot,side}=slotAt(p,i,a);const c=deck.cards[deck.order[slot]];out.push(c?c[side]:makePlain())}
  return out;
}
function selectedRef(){return pages[currentPage]&&lastArrangement?slotAt(currentPage,selected,lastArrangement,lastN||cardsPerPage()):null}
function selectSlot(slot,side){currentPage=Math.floor(slot/cardsPerPage());selected=indexOfSlot(slot,arrangement()==="single"?"front":side)}
/* deck から表示用の pages を作り直す(並べ方が変わったら、選んでいたカードを選び直す) */
function syncPages(){
  const a=arrangement(),n=cardsPerPage(),ref=(lastArrangement&&(lastArrangement!==a||lastN!==n))?selectedRef():null;
  padOrder();gcCards();
  pages=Array.from({length:pageCount()},(_,p)=>facesOf(p,a));
  lastArrangement=a;lastN=n;
  if(ref){const slot=clamp(ref.slot,0,deck.order.length-1);currentPage=Math.floor(slot/n);selected=indexOfSlot(slot,a==="single"?"front":ref.side)}
  currentPage=clamp(currentPage,0,pages.length-1);
  selected=clamp(selected,0,pages[currentPage].length-1);
}
function setFaceAt(p,i,face){const {slot,side}=slotAt(p,i);deck.cards[deck.order[slot]][side]=face;syncPages()}
function cardIdAt(p,i){return deck.order[slotAt(p,i).slot]}
function startDeck(){deck={cards:{},order:[],fmt:2,font:"gothic"};currentPage=0;selected=0;padOrder();syncPages()}
function applyCardGeometry(container){
  const f=faceMM(),q=pairMM(),g=gridRC();
  container.style.setProperty("--face-w",f.w+"mm");
  container.style.setProperty("--face-h",f.h+"mm");
  container.style.setProperty("--pair-w",q.w+"mm");
  container.style.setProperty("--pair-h",q.h+"mm");
  container.style.setProperty("--grid-w",q.w*g.cols+"mm");
  container.style.setProperty("--grid-h",q.h*g.rows+"mm");
  container.style.setProperty("--fold-pos",(isLandscapeCard()?f.h:f.w)+"mm");
  container.style.gridTemplateColumns=`repeat(${g.cols}, var(--pair-w))`;
  container.style.gridTemplateRows=`repeat(${g.rows}, var(--pair-h))`;
}
function currentFaces(){if(!pages.length)syncPages();return pages[currentPage]}
function deep(v){return JSON.parse(JSON.stringify(v,packImages),unpackImages)}
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}
function esc(s){return String(s??"").replace(/[&<>"']/g,x=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[x]))}


function ensureTextBoxes(d){ if(!Array.isArray(d.textBoxes)) d.textBoxes=[]; return d.textBoxes; }
function makeTextBox(i=0){return {id:"tb_"+Date.now()+"_"+Math.random().toString(36).slice(2,7),text:"テキスト",style:{size:SIZE.text,bold:false,italic:false,underline:false,color:"#222222",colorNone:false},box:{x:20,y:18+i*16,w:60,h:14},centerSnap:false}}
function ensureFrameTexts(d){if(!Array.isArray(d.frameTexts))d.frameTexts=[];return d.frameTexts}
function makeFrameText(i=0){return {id:"ft_"+Date.now()+"_"+Math.random().toString(36).slice(2,7),text:"フレームテキスト",style:{size:SIZE.frame,bold:false,italic:false,underline:false,color:"#222222",colorNone:false},borderColor:"#222222",borderNone:false,borderWidth:1,fillColor:"#ffffff",fillNone:false,box:{x:18,y:22+i*14,w:64,h:18},centerSnap:false}}
function ensureOptionImages(d){if(!Array.isArray(d.optionImages))d.optionImages=[];if(!Array.isArray(d.shapes))d.shapes=[];return d.optionImages}
function ensureShapes(d){if(!Array.isArray(d.shapes))d.shapes=[];return d.shapes}
function makeShape(type,i=0){return {id:"sh_"+Date.now()+"_"+Math.random().toString(36).slice(2,7),type,points:(type==="star"?5:6),fillColor:"#ffffff",fillNone:false,borderColor:"#222222",borderNone:false,borderWidth:1,borderAlign:"inside",box:{x:30,y:30+i*4,w:38,h:38},centerSnap:false}}
function shapePoints(type,n){n=Math.max(3,Math.min(12,Number(n)||5));let pts=[];if(type==="triangle")n=3;if(type==="polygon"||type==="triangle"){for(let i=0;i<n;i++){let a=-Math.PI/2+i*2*Math.PI/n;pts.push(`${50+46*Math.cos(a)},${50+46*Math.sin(a)}`)}}else if(type==="star"){for(let i=0;i<n*2;i++){let a=-Math.PI/2+i*Math.PI/n,r=i%2?21:46;pts.push(`${50+r*Math.cos(a)},${50+r*Math.sin(a)}`)}}return pts.join(" ")}
function makeOptionImage(src,i=0){return {id:"oi_"+Date.now()+"_"+Math.random().toString(36).slice(2,7),src,box:{x:30,y:28+i*5,w:40,h:30},rotation:0,centerSnap:false}}
function renderGenericTextBoxes(faceEl,d,selectable=false,idx=-1){
  const items=ensureTextBoxes(d);
  const gx=document.createElement("div");gx.className="snap-guide-x";faceEl.appendChild(gx);
  const gy=document.createElement("div");gy.className="snap-guide-y";faceEl.appendChild(gy);
  items.forEach((item,n)=>{
    const st=item.style||{size:SIZE.text,bold:false,italic:false,color:"#222222"},b=item.box||{x:20,y:18+n*16,w:60,h:14};
    const div=document.createElement("div");div.className="generic-textbox"+(selectable?" editable":"");
    div.style.left=b.x+"%";div.style.top=b.y+"%";div.style.width=b.w+"%";div.style.height=b.h+"%";
    div.style.fontSize=(st.size||SIZE.text)+"pt";if(st.font)div.style.fontFamily=fontCss(st.font);div.style.fontWeight=st.bold?700:400;div.style.fontStyle=st.italic?"italic":"normal";div.style.textDecoration=st.underline?"underline":"none";div.style.color=st.colorNone?"transparent":(st.color||"#222");div.textContent=item.text||"";
    if(selectable){const h=document.createElement("div");h.className="resize-handle";div.appendChild(h);enableGenericTextBox(div,idx,item.id)}
    faceEl.appendChild(div);
  });
  renderFrameTexts(faceEl,d,selectable,idx);
  renderOptionImages(faceEl,d,selectable,idx);
  renderShapes(faceEl,d,selectable,idx);
}

function renderFrameTexts(faceEl,d,selectable=false,idx=-1){
  const items=ensureFrameTexts(d);
  items.forEach((item,n)=>{
    const st=item.style||{size:SIZE.frame,bold:false,italic:false,underline:false,color:"#222222",colorNone:false};
    const b=item.box||{x:18,y:22+n*14,w:64,h:18};
    const div=document.createElement("div");
    div.className="frame-text"+(selectable?" editable":"");
    div.style.left=b.x+"%";div.style.top=b.y+"%";div.style.width=b.w+"%";div.style.height=b.h+"%";
    div.style.fontSize=(st.size||SIZE.frame)+"pt";if(st.font)div.style.fontFamily=fontCss(st.font);div.style.fontWeight=st.bold?700:400;div.style.fontStyle=st.italic?"italic":"normal";div.style.textDecoration=st.underline?"underline":"none";
    div.style.color=st.colorNone?"transparent":(st.color||"#222");
    div.style.border="0";if(!item.borderNone){const w=Number(item.borderWidth)||1,c=item.borderColor||"#222",a=item.borderAlign||"inside";if(a==="outside")div.style.boxShadow=`0 0 0 ${w}mm ${c}`;else if(a==="center")div.style.boxShadow=`inset 0 0 0 ${w/2}mm ${c},0 0 0 ${w/2}mm ${c}`;else div.style.boxShadow=`inset 0 0 0 ${w}mm ${c}`}
    div.style.background=item.fillNone?"transparent":(item.fillColor||"#fff");
    div.textContent=item.text||"";
    if(selectable){const h=document.createElement("div");h.className="resize-handle";div.appendChild(h);enableFrameText(div,idx,item.id)}
    faceEl.appendChild(div);
  });
}
function renderOptionImages(faceEl,d,selectable=false,idx=-1){
  ensureOptionImages(d).forEach((item,n)=>{if(!item.src)return;const b=item.box||{x:30,y:28+n*5,w:40,h:30};const div=document.createElement("div");div.className="option-image"+(selectable?" editable":"");div.style.left=b.x+"%";div.style.top=b.y+"%";div.style.width=b.w+"%";div.style.height=b.h+"%";div.style.transform=`rotate(${Number(item.rotation)||0}deg)`;div.innerHTML=`<img src="${item.src}" alt="">`;if(selectable){div.innerHTML+=`<div class="resize-handle"></div><div class="rotate-handle"></div>`;enableOptionImage(div,idx,item.id)}faceEl.appendChild(div)})
}
function renderShapes(faceEl,d,selectable=false,idx=-1){
  ensureShapes(d).forEach(item=>{const b=item.box||{x:30,y:30,w:38,h:38},div=document.createElement("div");div.className="option-shape"+(selectable?" editable":"");div.style.left=b.x+"%";div.style.top=b.y+"%";div.style.width=b.w+"%";div.style.aspectRatio="1 / 1";
    let tag=item.type==="circle"?'<ellipse cx="50" cy="50" rx="46" ry="46"/>':item.type==="rect"?'<rect x="4" y="4" width="92" height="92"/>':`<polygon points="${shapePoints(item.type,item.points)}"/>`;
    const sw=Math.max(.1,Number(item.borderWidth)||1), align=item.borderAlign||"inside"; let svgStroke=sw*MM_TO_PX; if(align==="inside")svgStroke*=2; else if(align==="outside")svgStroke*=2;
    div.innerHTML=`<svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet"><g fill="${item.fillNone?'none':item.fillColor||'#fff'}" stroke="${item.borderNone?'none':item.borderColor||'#222'}" stroke-width="${svgStroke}" vector-effect="non-scaling-stroke">${tag}</g></svg>${selectable?'<div class="resize-handle"></div>':''}`;
    if(selectable)enableShape(div,idx,item.id);faceEl.appendChild(div)})
}
function enableShape(node,idx,itemId){let mode=null,sx=0,sy=0,start=null;const h=node.querySelector('.resize-handle'),get=()=>ensureShapes(currentFaces()[idx]).find(x=>x.id===itemId);const down=(e,m)=>{e.preventDefault();e.stopPropagation();mode=m;sx=e.clientX;sy=e.clientY;start={...(get().box)};window.addEventListener('pointermove',move);window.addEventListener('pointerup',up,{once:true})};node.addEventListener('pointerdown',e=>{if(e.target!==h)down(e,'move')});h&&h.addEventListener('pointerdown',e=>down(e,'resize'));function move(e){const it=get(),r=node.closest('.face').getBoundingClientRect(),dx=(e.clientX-sx)/r.width*100,dy=(e.clientY-sy)/r.height*100;const currentH=it.box.h||start.h||38;if(mode==='move'){const visualH=(it.box.w||start.w)*r.width/r.height;it.box={...start,x:clamp(start.x+dx,0,100-start.w),y:clamp(start.y+dy,0,100-visualH),h:visualH}}else{let nw=start.w+(Math.abs(dx)>=Math.abs(dy)?dx:dy*r.height/r.width);nw=clamp(nw,8,100-start.x);let nh=nw*r.width/r.height;if(nh>100-start.y){nh=100-start.y;nw=nh*r.height/r.width}it.box={...start,w:nw,h:nh}}Object.assign(node.style,{left:it.box.x+'%',top:it.box.y+'%',width:it.box.w+'%',height:'auto',aspectRatio:'1 / 1'})}function up(){mode=null;window.removeEventListener('pointermove',move);syncControls()}}

function enableOptionImage(node,idx,itemId){
  let mode=null,startX=0,startY=0,start=null,startAngle=0;const resize=node.querySelector(".resize-handle"),rotate=node.querySelector(".rotate-handle");
  const getItem=()=>ensureOptionImages(currentFaces()[idx]).find(x=>x.id===itemId);
  const down=(e,m)=>{e.preventDefault();e.stopPropagation();mode=m;startX=e.clientX;startY=e.clientY;const item=getItem();if(!item)return;start={...(item.box||{x:30,y:28,w:40,h:30})};startAngle=Number(item.rotation)||0;window.addEventListener("pointermove",move);window.addEventListener("pointerup",up,{once:true})};
  node.addEventListener("pointerdown",e=>{if(e.target!==resize&&e.target!==rotate)down(e,"move")});resize.addEventListener("pointerdown",e=>down(e,"resize"));rotate.addEventListener("pointerdown",e=>down(e,"rotate"));
  function move(e){const item=getItem();if(!item||!mode)return;const face=node.closest(".face"),r=face.getBoundingClientRect();if(mode==="rotate"){const nr=node.getBoundingClientRect(),cx=nr.left+nr.width/2,cy=nr.top+nr.height/2;item.rotation=Math.round(Math.atan2(e.clientY-cy,e.clientX-cx)*180/Math.PI+90);node.style.transform=`rotate(${item.rotation}deg)`;return}const dx=(e.clientX-startX)/r.width*100,dy=(e.clientY-startY)/r.height*100;if(mode==="move"){let x=clamp(start.x+dx,0,100-start.w),y=clamp(start.y+dy,0,100-start.h);face.classList.remove("show-snap-x","show-snap-y");if(item.centerSnap){const th=4.5;if(Math.abs(x+start.w/2-50)<=th){x=50-start.w/2;face.classList.add("show-snap-x")}if(Math.abs(y+start.h/2-50)<=th){y=50-start.h/2;face.classList.add("show-snap-y")}}item.box={...start,x,y}}else{const ratio=start.w/start.h;let nw=start.w+dx,nh=nw/ratio;if(Math.abs(dy)>Math.abs(dx)){nh=start.h+dy;nw=nh*ratio}nw=clamp(nw,8,100-start.x);nh=nw/ratio;if(nh>100-start.y){nh=100-start.y;nw=nh*ratio}item.box={...start,w:nw,h:nh}}const b=item.box;node.style.left=b.x+"%";node.style.top=b.y+"%";node.style.width=b.w+"%";node.style.height=b.h+"%"}
  function up(){const face=node.closest(".face");if(face)face.classList.remove("show-snap-x","show-snap-y");mode=null;window.removeEventListener("pointermove",move);syncControls()}
}

function enableFrameText(node,idx,itemId){
  let mode=null,startX=0,startY=0,start=null;const handle=node.querySelector(".resize-handle");
  const down=(e,m)=>{e.preventDefault();e.stopPropagation();mode=m;startX=e.clientX;startY=e.clientY;const item=ensureFrameTexts(currentFaces()[idx]).find(x=>x.id===itemId);if(!item)return;start={...(item.box||{x:18,y:22,w:64,h:18})};window.addEventListener("pointermove",move);window.addEventListener("pointerup",up,{once:true})};
  node.addEventListener("pointerdown",e=>{if(e.target!==handle)down(e,"move")});handle.addEventListener("pointerdown",e=>down(e,"resize"));
  function move(e){if(!mode)return;const face=node.closest(".face"),r=face.getBoundingClientRect();const dx=(e.clientX-startX)/r.width*100,dy=(e.clientY-startY)/r.height*100;const item=ensureFrameTexts(currentFaces()[idx]).find(x=>x.id===itemId);if(!item)return;
    if(mode==="move"){let x=clamp(start.x+dx,0,100-start.w),y=clamp(start.y+dy,0,100-start.h);face.classList.remove("show-snap-x","show-snap-y");if(item.centerSnap){const cx=x+start.w/2,cy=y+start.h/2,th=4.5;if(Math.abs(cx-50)<=th){x=50-start.w/2;face.classList.add("show-snap-x")}if(Math.abs(cy-50)<=th){y=50-start.h/2;face.classList.add("show-snap-y")}}item.box={...start,x,y}}
    else{item.box={...start,w:clamp(start.w+dx,12,100-start.x),h:clamp(start.h+dy,7,100-start.y)}}
    const b=item.box;node.style.left=b.x+"%";node.style.top=b.y+"%";node.style.width=b.w+"%";node.style.height=b.h+"%";
  }
  function up(){const face=node.closest(".face");if(face)face.classList.remove("show-snap-x","show-snap-y");mode=null;window.removeEventListener("pointermove",move)}
}

function enableGenericTextBox(node,idx,itemId){
  let mode=null,startX=0,startY=0,start=null;const handle=node.querySelector(".resize-handle");
  const down=(e,m)=>{e.preventDefault();e.stopPropagation();mode=m;startX=e.clientX;startY=e.clientY;const item=ensureTextBoxes(currentFaces()[idx]).find(x=>x.id===itemId);if(!item)return;start={...(item.box||{x:20,y:20,w:60,h:14})};window.addEventListener("pointermove",move);window.addEventListener("pointerup",up,{once:true})};
  node.addEventListener("pointerdown",e=>{if(e.target!==handle)down(e,"move")});handle.addEventListener("pointerdown",e=>down(e,"resize"));
  function move(e){if(!mode)return;const face=node.closest(".face"),r=face.getBoundingClientRect();const dx=(e.clientX-startX)/r.width*100,dy=(e.clientY-startY)/r.height*100;const item=ensureTextBoxes(currentFaces()[idx]).find(x=>x.id===itemId);if(!item)return;
    if(mode==="move"){let x=clamp(start.x+dx,0,100-start.w),y=clamp(start.y+dy,0,100-start.h);face.classList.remove("show-snap-x","show-snap-y");if(item.centerSnap){const cx=x+start.w/2,cy=y+start.h/2,th=4.5;if(Math.abs(cx-50)<=th){x=50-start.w/2;face.classList.add("show-snap-x")}if(Math.abs(cy-50)<=th){y=50-start.h/2;face.classList.add("show-snap-y")}}item.box={...start,x,y}}
    else{const ratio=start.w/start.h;let nw=start.w+dx,nh=nw/ratio;if(Math.abs(dy)>Math.abs(dx)){nh=start.h+dy;nw=nh*ratio}nw=clamp(nw,12,100-start.x);nh=nw/ratio;if(nh>100-start.y){nh=100-start.y;nw=nh*ratio}if(nh<6){nh=6;nw=nh*ratio}item.box={...start,w:nw,h:nh}}
    const b=item.box;node.style.left=b.x+"%";node.style.top=b.y+"%";node.style.width=b.w+"%";node.style.height=b.h+"%";
  }
  function up(){const face=node.closest(".face");if(face)face.classList.remove("show-snap-x","show-snap-y");mode=null;window.removeEventListener("pointermove",move)}
}

/* 読み込む画像は長辺2400pxまでに縮小する(ポーカーサイズ全面でも500dpi超)。
   透明部分のある画像はPNGのまま、それ以外はJPEGにする。小さい画像はそのまま使う。 */
const IMG_MAX_SIDE=2400,IMG_KEEP_BYTES=1.2e6;
function readAsDataURL(file){return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result);r.onerror=()=>rej(r.error);r.readAsDataURL(file)})}
function loadImageEl(src){return new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=()=>rej(new Error("image decode failed"));i.src=src})}
async function readImageFile(file){
  const original=await readAsDataURL(file);
  if(!/^image\/(jpeg|png|webp|gif|bmp)$/i.test(file.type||""))return canonicalImage(original);
  try{
    const img=await loadImageEl(original),w=img.naturalWidth,h=img.naturalHeight;
    if(!w||!h)return canonicalImage(original);
    const s=Math.min(1,IMG_MAX_SIDE/Math.max(w,h));
    if(s===1&&file.size<=IMG_KEEP_BYTES)return canonicalImage(original);
    const cw=Math.max(1,Math.round(w*s)),ch=Math.max(1,Math.round(h*s));
    const c=document.createElement("canvas");c.width=cw;c.height=ch;
    const ctx=c.getContext("2d");ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality="high";ctx.drawImage(img,0,0,cw,ch);
    let alpha=false;
    if(!/jpeg/i.test(file.type)){const d=ctx.getImageData(0,0,cw,ch).data;for(let i=3;i<d.length;i+=8){if(d[i]<255){alpha=true;break}}}
    const out=alpha?c.toDataURL("image/png"):c.toDataURL("image/jpeg",.92);
    return canonicalImage(out.length<original.length?out:original);
  }catch(err){console.warn(err);return canonicalImage(original)}
}
function onImagePicked(input,apply){
  input.addEventListener("change",async e=>{
    const file=e.target.files[0];if(!file)return;
    try{apply(await readImageFile(file))}
    catch(err){console.error(err);alert("画像を読み込めませんでした。")}
    finally{e.target.value=""}
  });
}

/* 面の種類やテンプレートを切り替えても引き継ぐもの(背景・線・オプション) */
function keepCommon(old){
  return {bgColor:old.bgColor||"#ffffff",bgNone:!!old.bgNone,bgImage:old.bgImage||null,
    bgBorderColor:old.bgBorderColor||"#222222",bgBorderWidth:old.bgBorderWidth??1,bgBorderNone:old.bgBorderNone!==false,bgBorderAlign:old.bgBorderAlign||"inside",
    textBoxes:deep(ensureTextBoxes(old)),frameTexts:deep(ensureFrameTexts(old)),optionImages:deep(ensureOptionImages(old)),shapes:deep(ensureShapes(old))};
}
/* 以前の「カスタム」テンプレートは無地と同じ見た目なので、無地として開く */
function normalizeFaces(list){
  (list||[]).forEach(pg=>(pg||[]).forEach((d,i)=>{if(d&&d.type==="template"&&d.template==="custom")pg[i]={type:"plain",...keepCommon(d)}}));
  return list;
}

function faceName(i){
  const {slot,side}=slotAt(currentPage,i),n=cardsPerPage(),num=slot+1,inPage=slot%n+1;
  if(isSingleMode())return `カード${num}（ページ内${inPage}）`;
  return `カード${num}（ページ内${inPage}）・${side==="front"?"オモテ":"ウラ"}`;
}

function setPaper(){
  const p=paperMM();
  paper.style.width=p.w*MM_TO_PX+"px";
  paper.style.height=p.h*MM_TO_PX+"px";
  paper.className="paper "+(el("paperOrientation").value==="landscape"?"landscape-paper":"portrait-paper");
  grid.className="sheet-grid "+(isLandscapeCard()?"landscape-card":"portrait-card")+" card-size-"+el("cardSize").value;
  updateFit();
  fitPaper();
  renderSheet();
}
function fitPaper(){
  const p=paperMM(),area=document.querySelector(".canvas-area");
  const mobile=window.matchMedia("(max-width:720px)").matches;
  const pad=mobile?20:44;
  const mainWidth=Math.max(1,area.clientWidth-pad);
  const raw=p.w*MM_TO_PX,scale=Math.min(1,mainWidth/raw);

  if(mobile){
    paper.style.left="50%";
    paper.style.transform=`translateX(-50%) scale(${scale})`;
    paper.parentElement.style.minWidth="";
  }else{
    paper.style.left="";
    paper.style.transform=`scale(${scale})`;
    paper.parentElement.style.minWidth=Math.ceil(raw*scale)+"px";
  }

  paper.parentElement.style.height=p.h*MM_TO_PX*scale+"px";
}
/* 線の太さ・カードサイズの表示を、設定した長さの単位に */
function relabelLengths(root=document){
  root.querySelectorAll("select.stroke-width-select option").forEach(o=>{o.textContent=fmtLen(Number(o.value))});
  const cs=el("cardSize");if(cs)[...cs.options].forEach(o=>{const c=CARD_SIZES[o.value];if(!c)return;o.textContent=`${c.label} (${fmtLen(c.w,false)}×${fmtLen(c.h,false)}${units.len==="mm"?"":" "+LEN_UNITS[units.len].label})`});
}
function updateFit(){
  const p=paperMM(),b=blockMM(),x=(p.w-b.w)/2,y=(p.h-b.h)/2,c=cardMM();
  const paperName=(el("paperSize")?.value==="a3"?"A3":"A4")+(el("paperOrientation").value==="landscape"?"横":"縦");
  const L=LEN_UNITS[units.len].label;
  el("fitStatus").textContent=`${paperName}：${cardsPerPage()}枚 / 余白 左右${fmtLen(x)}・上下${fmtLen(y)}`;
  document.querySelectorAll(".fit-note").forEach(n=>{n.textContent=`${paperName}に${fmtLen(c.w,false)}×${fmtLen(c.h,false)} ${L}のカードが${cardsPerPage()}枚（余白 左右${fmtLen(x)}・上下${fmtLen(y)}）。印刷は「実際のサイズ（100%）」で。`});
}


function addRecentColor(c){ refreshOpenColorPopup(); }
function getUsedColors(){
  const out=[],seen=new Set();const add=c=>{if(!c)return;c=String(c).toLowerCase();if(!seen.has(c)){seen.add(c);out.push(c)}};
  Object.values(deck.cards).flatMap(c=>[c.front,c.back]).forEach(d=>{if(!d)return;[d.bgColor,d.color,d.numberColor,d.textColor,d.borderColor,d.panelColor,d.mainColor].forEach(add);if(Array.isArray(d.textBoxes))d.textBoxes.forEach(tb=>add(tb&&tb.style&&!tb.style.colorNone&&tb.style.color));if(Array.isArray(d.frameTexts))d.frameTexts.forEach(ft=>{add(ft&&ft.style&&!ft.style.colorNone&&ft.style.color);if(ft&&!ft.borderNone)add(ft.borderColor);if(ft&&!ft.fillNone)add(ft.fillColor)})});
  return out.slice(0,24);
}
let colorPopup=null,activeColorInput=null;
function hexToRgb(hex){const h=String(hex||"#000000").replace("#","");const n=parseInt(h.length===3?h.split("").map(x=>x+x).join(""):h,16)||0;return {r:(n>>16)&255,g:(n>>8)&255,b:n&255}}
function rgbToHex(r,g,b){const f=n=>clamp(Math.round(n),0,255).toString(16).padStart(2,"0");return "#"+f(r)+f(g)+f(b)}
function rgbToHsv(r,g,b){r/=255;g/=255;b/=255;const mx=Math.max(r,g,b),mn=Math.min(r,g,b),d=mx-mn;let h=0;if(d){if(mx===r)h=((g-b)/d)%6;else if(mx===g)h=(b-r)/d+2;else h=(r-g)/d+4;h*=60;if(h<0)h+=360}return {h,s:mx?d/mx:0,v:mx}}
function hsvToRgb(h,s,v){const c=v*s,x=c*(1-Math.abs((h/60)%2-1)),m=v-c;let r=0,g=0,b=0;if(h<60){r=c;g=x}else if(h<120){r=x;g=c}else if(h<180){g=c;b=x}else if(h<240){g=x;b=c}else if(h<300){r=x;b=c}else{r=c;b=x}return {r:(r+m)*255,g:(g+m)*255,b:(b+m)*255}}
function rgbToCmyk(r,g,b){r/=255;g/=255;b/=255;const k=1-Math.max(r,g,b);if(k>=.9999)return {c:0,m:0,y:0,k:100};return {c:(1-r-k)/(1-k)*100,m:(1-g-k)/(1-k)*100,y:(1-b-k)/(1-k)*100,k:k*100}}
function cmykToRgb(c,m,y,k){
  c=clamp(Number(c)||0,0,100)/100;
  m=clamp(Number(m)||0,0,100)/100;
  y=clamp(Number(y)||0,0,100)/100;
  k=clamp(Number(k)||0,0,100)/100;
  return {r:255*(1-c)*(1-k),g:255*(1-m)*(1-k),b:255*(1-y)*(1-k)}
}
function closeColorPopup(){if(colorPopup){colorPopup.remove();colorPopup=null}activeColorInput=null}
function colorRoleForInput(input){
  if(!input)return "fill";
  /* Same semantic role = same icon everywhere. Parent role classes are the source of truth. */
  if(input.closest?.(".stroke-color") || input.classList.contains("shape-stroke") || input.classList.contains("ft-border-color")) return "stroke";
  if(
    ["playingNumberColor","tcgTextColor","wordMainColor"].includes(input.id) ||
    input.classList.contains("tb-color") ||
    input.classList.contains("ft-text-color")
  ) return "text";
  return "fill";
}
function refreshColorTrigger(input){
  if(!input||!input._colorTrigger)return;
  const btn=input._colorTrigger;
  btn.classList.toggle("is-none",input.dataset.none==="1");
  btn.style.setProperty("--trigger-color",input.value||"#222222");
}
function applyColorToInput(input,color){
  input.dataset.none="0";
  input.value=color;
  input.dispatchEvent(new Event("input",{bubbles:true}));
  refreshColorTrigger(input);
}
function applyNoColor(input){
  input.dataset.none="1";
  input.dispatchEvent(new CustomEvent("colornone",{bubbles:true}));
  refreshColorTrigger(input);
  refreshOpenColorPopup();
}
function setupColorInput(input){
  if(!input||input.dataset.colorReady)return;
  input.dataset.colorReady="1";
  input.classList.add("color-source");

  const role=colorRoleForInput(input);
  const btn=document.createElement("button");
  btn.type="button";
  btn.className="color-trigger color-trigger-"+role;
  btn.title=input.getAttribute("aria-label")||input.title||"カラー";

  if(role==="text"){
    btn.innerHTML='<span class="color-trigger-icon color-trigger-text-icon">A</span>';
  }else if(role==="stroke"){
    btn.innerHTML='<span class="color-trigger-icon color-trigger-stroke-icon"></span>';
  }else{
    btn.innerHTML='<span class="color-trigger-icon color-trigger-fill-icon"></span>';
  }

  input.insertAdjacentElement("afterend",btn);
  input._colorTrigger=btn;
  btn.addEventListener("click",e=>{
    e.preventDefault();e.stopPropagation();
    openColorPopup(input,btn);
  });
  input.addEventListener("input",()=>refreshColorTrigger(input));
  refreshColorTrigger(input);
}
function setupAllColorInputs(){document.querySelectorAll('input[type="color"]').forEach(setupColorInput)}
function refreshOpenColorPopup(){if(colorPopup&&colorPopup._renderUsed)colorPopup._renderUsed()}
function openColorPopup(input,anchor){
  if(colorPopup && activeColorInput===input){closeColorPopup();return}
  closeColorPopup();activeColorInput=input;let rgb=hexToRgb(input.value),hsv=rgbToHsv(rgb.r,rgb.g,rgb.b),mode="CMYK";
  const pop=document.createElement("div");pop.className="color-popup";pop.innerHTML=`<div class="color-popup-head"><strong>カラー</strong><button type="button" class="color-popup-close">×</button></div><div class="color-field"><span class="color-field-marker"></span></div><input class="color-hue" type="range" min="0" max="359" value="${Math.round(hsv.h)}"><div class="color-popup-row"><span class="color-preview"></span><select class="color-mode"><option value="CMYK">CMYK</option><option value="RGB">RGB</option></select><div class="color-values"></div></div><div class="color-bottom-row"><button type="button" class="color-none-btn"><span class="none-icon"></span><span>なし</span></button><label class="hex-wrap"><input class="color-hex" type="text" maxlength="7" spellcheck="false" aria-label="カラーコード" placeholder="#D94A4A"></label></div><div class="color-popup-section">基本の色</div><div class="swatches preset-swatches"></div><div class="color-popup-section">使われている色</div><div class="swatches used-swatches"></div>`;
  document.body.appendChild(pop);colorPopup=pop;
  const field=pop.querySelector(".color-field"),marker=pop.querySelector(".color-field-marker"),hue=pop.querySelector(".color-hue"),preview=pop.querySelector(".color-preview"),values=pop.querySelector(".color-values"),modeSel=pop.querySelector(".color-mode"),hexInput=pop.querySelector(".color-hex");
  const currentHex=()=>{const x=hsvToRgb(hsv.h,hsv.s,hsv.v);return rgbToHex(x.r,x.g,x.b)};
  function renderValues(){
    const r=hexToRgb(currentHex());
    values.innerHTML="";
    const arr=mode==="CMYK"
      ?(()=>{const c=rgbToCmyk(r.r,r.g,r.b);return [["C",c.c,100],["M",c.m,100],["Y",c.y,100],["K",c.k,100]]})()
      :[["R",r.r,255],["G",r.g,255],["B",r.b,255]];

    arr.forEach(([lab,val,max],index)=>{
      const cell=document.createElement("div");
      cell.className="color-value";
      cell.innerHTML=`<input type="number" inputmode="numeric" step="1" min="0" max="${max}" value="${Math.round(val)}" aria-label="${lab}"><label>${lab}</label>`;
      const num=cell.querySelector("input");

      const commitNumber=()=>{
        const inputs=[...values.querySelectorAll("input")];
        inputs.forEach(x=>{
          const mx=Number(x.max);
          x.value=String(Math.round(clamp(Number(x.value)||0,0,mx)));
        });
        const nums=inputs.map(x=>Number(x.value)||0);
        const rr=mode==="CMYK"
          ?cmykToRgb(nums[0],nums[1],nums[2],nums[3])
          :{r:clamp(nums[0],0,255),g:clamp(nums[1],0,255),b:clamp(nums[2],0,255)};
        hsv=rgbToHsv(rr.r,rr.g,rr.b);
        hue.value=Math.round(hsv.h);
        update(true,false);
      };

      // Commit when leaving a field. Because the numeric controls are not rebuilt,
      // normal Tab order remains C→M→Y→K (or R→G→B).
      num.addEventListener("change",commitNumber);
      num.addEventListener("keydown",e=>{
        if(e.key==="Enter"){
          e.preventDefault();
          commitNumber();
          const inputs=[...values.querySelectorAll("input")];
          const next=inputs[index+1];
          if(next){next.focus();next.select()}
        }
      });
      values.appendChild(cell);
    });
  }
  function swatches(container,colors){container.innerHTML="";colors.forEach(c=>{const b=document.createElement("button");b.type="button";b.className="swatch";b.style.background=c;b.title=c;b.addEventListener("click",e=>{e.stopPropagation();const r=hexToRgb(c);hsv=rgbToHsv(r.r,r.g,r.b);hue.value=Math.round(hsv.h);update(true)});container.appendChild(b)})}
  function renderUsed(){const box=pop.querySelector(".used-swatches"),colors=getUsedColors();swatches(box,colors);if(!colors.length){const x=document.createElement("div");x.className="color-used-empty";x.textContent="まだありません";box.appendChild(x)}}pop._renderUsed=renderUsed;
  function update(commit,syncNumbers=true){
    field.style.background=`hsl(${hsv.h} 100% 50%)`;
    marker.style.left=(hsv.s*100)+"%";
    marker.style.top=((1-hsv.v)*100)+"%";
    const hex=currentHex();
    preview.style.background=hex;
    if(document.activeElement!==hexInput)hexInput.value=hex.toUpperCase();
    if(commit)applyColorToInput(input,hex);
    if(syncNumbers)renderValues();
    renderUsed();
  }
  swatches(pop.querySelector(".preset-swatches"),PRESET);renderUsed();update(false);
  field.addEventListener("pointerdown",e=>{const move=ev=>{const r=field.getBoundingClientRect();hsv.s=clamp((ev.clientX-r.left)/r.width,0,1);hsv.v=1-clamp((ev.clientY-r.top)/r.height,0,1);update(true)};move(e);window.addEventListener("pointermove",move);window.addEventListener("pointerup",()=>window.removeEventListener("pointermove",move),{once:true})});
  hue.addEventListener("input",()=>{hsv.h=Number(hue.value);update(true)});hexInput.addEventListener("change",()=>{let v=hexInput.value.trim();if(!v.startsWith("#"))v="#"+v;if(/^#[0-9a-fA-F]{6}$/.test(v)){const rr=hexToRgb(v);hsv=rgbToHsv(rr.r,rr.g,rr.b);hue.value=Math.round(hsv.h);update(true)}else hexInput.value=currentHex().toUpperCase()});modeSel.addEventListener("change",()=>{mode=modeSel.value;renderValues()});pop.querySelector(".color-popup-close").onclick=closeColorPopup;pop.querySelector(".color-none-btn").onclick=()=>{applyNoColor(input);closeColorPopup()};
  const r=anchor.getBoundingClientRect(),w=Math.min(320,window.innerWidth-16);
  pop.style.width=w+"px";
  let left=Math.min(window.innerWidth-w-8,Math.max(8,r.left)),top=r.bottom+6;
  requestAnimationFrame(()=>{
    if(top+pop.offsetHeight>window.innerHeight-8)top=Math.max(8,r.top-pop.offsetHeight-6);
    pop.style.left=left+"px";pop.style.top=top+"px";
  });
}
function renderSwatches(){refreshOpenColorPopup()}

function renderSuitHTML(d){
  const size=d.suitSize||"medium",count=clamp(Number(d.suitCount)||1,1,5);
  const one=()=>d.suitMode==="image"&&d.suitImage?`<img class="suit-img ${size}" src="${d.suitImage}" alt="">`:`<span class="suit-text ${size}">${esc(d.suit||"")}</span>`;
  return `<span class="suit-stack">${Array.from({length:count},one).join("")}</span>`;
}
function cornerVisible(pos,key){pos=pos||"four";if(pos==="top")return key==="tl"||key==="tr";if(pos==="diagRight")return key==="tr"||key==="bl";if(pos==="diagLeft")return key==="tl"||key==="br";return true}

function renderFace(faceEl,d,selectable=false,idx=-1){
  faceEl.innerHTML="";
  faceEl.style.fontFamily=fontCss(deck.font);
  faceEl.style.background=d.bgNone?"transparent":(d.bgColor||"#ffffff");
  const faceBorderW=Number(d.bgBorderWidth)||1;
  const faceBorderAlign=d.bgBorderAlign||"inside";
  if(d.bgBorderNone) faceEl.style.boxShadow="none";
  else{
    const c=d.bgBorderColor||"#222222";
    if(faceBorderAlign==="outside") faceEl.style.boxShadow=`0 0 0 ${faceBorderW}mm ${c}`;
    else if(faceBorderAlign==="center"){const half=faceBorderW/2;faceEl.style.boxShadow=`inset 0 0 0 ${half}mm ${c}, 0 0 0 ${half}mm ${c}`;}
    else faceEl.style.boxShadow=`inset 0 0 0 ${faceBorderW}mm ${c}`;
  }

  if(d.bgImage){
    const bg=document.createElement("img");
    bg.src=d.bgImage;
    bg.style.position="absolute";
    bg.style.inset="0";
    bg.style.width="100%";
    bg.style.height="100%";
    bg.style.objectFit="cover";
    bg.style.zIndex="0";
    bg.style.pointerEvents="none";
    faceEl.appendChild(bg);
  }

  if(d.type==="plain"){renderGenericTextBoxes(faceEl,d,selectable,idx);return;}
  if(d.type==="image"){
    if(d.src){const img=document.createElement("img");img.src=d.src;img.style.width="100%";img.style.height="100%";img.style.objectFit="cover";img.style.position="relative";img.style.zIndex="1";faceEl.appendChild(img)}
    else faceEl.innerHTML='<div class="empty ph">画像未設定</div>';
    renderGenericTextBoxes(faceEl,d,selectable,idx);
    return
  }

  if(d.template==="tcg"){
    const layout = isLandscapeCard() ? (d.horizontalLayout||1) : 1;
    const wrap=document.createElement("div");
    wrap.className="tcg-card layout"+layout;
    const legacy=d.color||"#222222";
    wrap.style.setProperty("--tcg-text",d.textColorNone?"transparent":(d.textColor||legacy));
    wrap.style.setProperty("--tcg-border",d.borderNone?"transparent":(d.borderColor||legacy));wrap.style.setProperty("--tcg-border-width",(Number(d.borderWidth)||1)+"mm");wrap.dataset.borderAlign=d.borderAlign||"inside";
    wrap.style.setProperty("--tcg-panel",d.panelNone?"transparent":(d.panelColor||"#ffffff"));
    // Three independently sized zones. Clamp the requested values so adjacent frames
    // always keep a proportional gap and can never collide, even on Half size.
    let topP=(Number(d.tcgTopHeight)||16)/100, midP=(Number(d.tcgMiddleHeight)||50)/100, botP=(Number(d.tcgBottomHeight)||28)/100;
    const gapP=0.035; // proportional minimum gap between neighbouring frames
    const maxTop=Math.max(.10,.5-midP/2-gapP);
    const maxBot=Math.max(.14,.5-midP/2-gapP);
    topP=Math.min(topP,maxTop); botP=Math.min(botP,maxBot);
    const maxMid=Math.max(.20,1-2*gapP-topP-botP);
    midP=Math.min(midP,maxMid);
    wrap.style.setProperty("--tcg-top-p",topP);wrap.style.setProperty("--tcg-mid-p",midP);wrap.style.setProperty("--tcg-bottom-p",botP);

    const ns=d.nameStyle||{size:SIZE.tcgName,bold:true,italic:false};
    const ds=d.descStyle||{size:SIZE.tcgDesc,bold:false,italic:false};
    wrap.innerHTML=`<div class="tcg-name" style="${ns.font?`font-family:${fontCss(ns.font)};`:""}font-size:${ns.size||SIZE.tcgName}pt;font-weight:${ns.bold?700:400};font-style:${ns.italic?"italic":"normal"};text-decoration:${ns.underline?"underline":"none"}">${d.name?esc(d.name):'<span class="ph">カード名</span>'}</div>
      <div class="tcg-image">${d.image?`<img src="${d.image}">`:'<span class="ph">画像</span>'}</div>
      <div class="tcg-desc" style="${ds.font?`font-family:${fontCss(ds.font)};`:""}font-size:${ds.size||SIZE.tcgDesc}pt;font-weight:${ds.bold?700:400};font-style:${ds.italic?"italic":"normal"};text-decoration:${ds.underline?"underline":"none"}">${d.desc?esc(d.desc):'<span class="ph">テキスト</span>'}</div>`;
    faceEl.appendChild(wrap);renderGenericTextBoxes(faceEl,d,selectable,idx);return
  }

  if(d.template==="word"){
    const wrap=document.createElement("div");wrap.className="word-card";
    const main=document.createElement("div");main.className="word-main"+(!isLandscapeCard()?" vertical":"");
    const ms=d.mainStyle||{size:SIZE.word,bold:true,italic:false};main.style.fontSize=(ms.size||SIZE.word)+"pt";if(ms.font)main.style.fontFamily=fontCss(ms.font);main.style.fontWeight=ms.bold?800:400;main.style.fontStyle=ms.italic?"italic":"normal";main.style.textDecoration=ms.underline?"underline":"none";main.style.color=d.mainColorNone?"transparent":(d.mainColor||d.color||"#222222");if(d.main)main.textContent=d.main;else main.innerHTML='<span class="ph">ことば</span>';
    wrap.appendChild(main);faceEl.appendChild(wrap);renderGenericTextBoxes(faceEl,d,selectable,idx);return
  }

  if(d.template==="custom"){
    const wrap=document.createElement("div");wrap.className="custom-card";faceEl.appendChild(wrap);renderGenericTextBoxes(faceEl,d,selectable,idx);return
  }

  const wrap=document.createElement("div");wrap.className="card-template";
  if(d.numberStyle?.font)wrap.style.fontFamily=fontCss(d.numberStyle.font);
  const nc=d.numberColorNone?"transparent":(d.numberColor||d.color||"#d94a4a");
  wrap.innerHTML=`
    ${cornerVisible(d.cornerPlacement,"tl")?`<div class="corner tl" style="color:${nc}">${esc(d.number||"")}${renderSuitHTML(d)}</div>`:""}
    ${cornerVisible(d.cornerPlacement,"tr")?`<div class="corner tr" style="color:${nc}">${esc(d.number||"")}${renderSuitHTML(d)}</div>`:""}
    ${cornerVisible(d.cornerPlacement,"bl")?`<div class="corner bl" style="color:${nc}">${esc(d.number||"")}${renderSuitHTML(d)}</div>`:""}
    ${cornerVisible(d.cornerPlacement,"br")?`<div class="corner br" style="color:${nc}">${esc(d.number||"")}${renderSuitHTML(d)}</div>`:""}
    <div class="center-num" style="color:${nc};font-size:${d.numberStyle?.size||SIZE.number}pt;font-weight:${d.numberStyle?.bold===false?400:800};font-style:${d.numberStyle?.italic?"italic":"normal"};text-decoration:${d.numberStyle?.underline?"underline":"none"}">${esc(d.number||"")}</div>`;
  faceEl.appendChild(wrap);
  renderGenericTextBoxes(faceEl,d,selectable,idx);
}


// ---------- Undo / Redo ----------
let undoStack=[];
let redoStack=[];
let historyLastSnapshot=null;
let historyRestoring=false;
let historyPendingStart=null;
let historyTimer=null;
const HISTORY_LIMIT=80;
const HISTORY_GROUP_MS=900;

function historyState(){
  return JSON.stringify({
    deck,
    printSettings,
    sheetTitle,
    paperSize:el("paperSize").value,
    paperOrientation:el("paperOrientation").value,
    cardSize:el("cardSize").value,
    impositionMode:el("impositionMode").value,
    cardOrientation
  },packImages);
}

function updateHistoryButtons(){
  const u=el("undoBtn"),r=el("redoBtn");
  if(u)u.disabled=!undoStack.length && !historyPendingStart;
  if(r)r.disabled=!redoStack.length;
}

function initHistory(){
  if(historyTimer){clearTimeout(historyTimer);historyTimer=null}
  historyLastSnapshot=historyState();
  historyPendingStart=null;
  undoStack=[];
  redoStack=[];
  updateHistoryButtons();
  scheduleAutosave();
}

function beginGroupedHistory(){
  if(historyRestoring)return;
  const now=historyState();
  if(historyLastSnapshot===null)historyLastSnapshot=now;

  if(historyPendingStart===null){
    historyPendingStart=historyLastSnapshot;
    redoStack=[];
  }

  historyLastSnapshot=now;

  if(historyTimer)clearTimeout(historyTimer);
  historyTimer=setTimeout(commitGroupedHistory,HISTORY_GROUP_MS);
  updateHistoryButtons();
}

function commitGroupedHistory(){
  if(historyTimer){clearTimeout(historyTimer);historyTimer=null}
  if(historyPendingStart===null)return;

  const now=historyState();
  // Only create a history step when something actually changed.
  if(now!==historyPendingStart){
    undoStack.push(historyPendingStart);
    if(undoStack.length>HISTORY_LIMIT)undoStack.shift();
    redoStack=[];
  }

  historyLastSnapshot=now;
  historyPendingStart=null;
  updateHistoryButtons();
  scheduleAutosave();
}

function recordHistory(){
  if(historyRestoring)return;
  const now=historyState();
  if(historyLastSnapshot===null){
    historyLastSnapshot=now;
    return;
  }
  if(now===historyLastSnapshot)return;
  beginGroupedHistory();
}

function flushHistoryBeforeNavigation(){
  commitGroupedHistory();
}

function applyHistorySnapshot(snapshot){
  const st=JSON.parse(snapshot,unpackImages);
  historyRestoring=true;

  const ref=selectedRef();
  deck=st.deck?normalizeDeck(st.deck):deckFromPages(st.pages,st.impositionMode);
  if(st.printSettings)printSettings={...printSettings,...st.printSettings};
  sheetTitle=st.sheetTitle||"";
  el("paperSize").value=st.paperSize||"a4";
  el("paperOrientation").value=st.paperOrientation||"landscape";
  el("cardSize").value=st.cardSize||"poker";
  el("impositionMode").value=st.impositionMode||"duplex";el("impositionMode").dataset.prev=el("impositionMode").value;cardOrientation=st.cardOrientation||((el("impositionMode").value==="single")?el("paperOrientation").value:(el("paperOrientation").value==="portrait"?"landscape":"portrait"));
  el("sheetTitleInput").value=sheetTitle;

  syncPages();
  if(ref&&ref.slot<deck.order.length)selectSlot(ref.slot,ref.side);

  setPaper();
  syncControls();

  historyLastSnapshot=snapshot;
  historyPendingStart=null;
  historyRestoring=false;
  updateHistoryButtons();
}

function undoHistory(){
  flushHistoryBeforeNavigation();
  if(!undoStack.length)return;

  const current=historyState();
  const previous=undoStack.pop();
  redoStack.push(current);
  applyHistorySnapshot(previous);
}

function redoHistory(){
  flushHistoryBeforeNavigation();
  if(!redoStack.length)return;

  const current=historyState();
  const next=redoStack.pop();
  undoStack.push(current);
  applyHistorySnapshot(next);
}

function buildSheet(container,faces,selectable=true,a=arrangement()){
  const paired=a==="pairs"&&isPairLayout();   // 用紙上でオモテ・ウラが並ぶのは「両面(折り)」だけ
  container.innerHTML="";
  container.className="sheet-grid "+(isLandscapeCard()?"landscape-card":"portrait-card")+(paired?" duplex-mode":" single-mode");
  applyCardGeometry(container);
  for(let c=0;c<cardsPerPage();c++){
    const pair=document.createElement("div");pair.className="pair";
    const sides=paired?2:1;
    for(let side=0;side<sides;side++){
      const idx=paired?c*2+side:c,f=document.createElement("div");
      f.className="face"+(selectable&&idx===selected?" selected":"");
      if(selectable&&paired&&idx===selected)f.dataset.sideLabel=side===0?"オモテ面":"ウラ面";
      renderFace(f,faces[idx],selectable&&idx===selected,idx);
      if(selectable) f.addEventListener("click",()=>{selected=idx;renderSheet();syncControls()});
      pair.appendChild(f);
    }
    if(paired){const fold=document.createElement("div");fold.className="fold screen-guide";pair.appendChild(fold);}
    container.appendChild(pair);
  }
}

function renderSheet(){
  syncPages();
  recordHistory();
  el("sheetTitle").textContent=sheetTitle;
  buildSheet(grid,currentFaces(),true);
  el("pageCount").textContent=`${currentPage+1} / ${pages.length}`;
  el("addPage").disabled=pages.length>=MAX_PAGES;
  el("dupPage").disabled=pages.length>=MAX_PAGES;
  el("deletePage").disabled=pages.length<=1;
  renderPageSidebar();
  renderMobileCardPreview();
  scheduleAutosave();
}




function mobileUIActive(){
  return window.matchMedia("(max-width:720px)").matches;
}
let mobilePanelOpen="";

function mobileAddPage(){
  const add=el("addPage");
  if(!add || add.disabled)return;
  closeMobilePanel();
  add.click();
}

function closeMobilePanel(){
  mobilePanelOpen="";
  document.body.classList.remove("m-panel-open");
  rescaleMobileFaces();
  if(mobileSheetMode)renderMobileSheet();
  document.querySelectorAll(".mobile-tool-panel").forEach(p=>{
    p.classList.remove("open");
    p.setAttribute("aria-hidden","true");
  });
  document.querySelectorAll(".mobile-quick-bar button").forEach(b=>b.classList.remove("active"));
}

function openMobilePanel(name,buttonId){
  if(!mobileUIActive())return;
  if(mobileSheetMode&&["Face","Template","Options"].includes(name))setMobileSheetMode(false);
  if(mobilePanelOpen===name){ closeMobilePanel(); return; }
  closeMobilePanel();
  const p=el("mobile"+name+"Panel");
  if(!p)return;
  mobilePanelOpen=name;
  document.body.classList.add("m-panel-open");
  rescaleMobileFaces();
  if(mobileSheetMode)renderMobileSheet();
  placeMobilePanel();
  p.classList.add("open");
  p.setAttribute("aria-hidden","false");
  el(buttonId)?.classList.add("active");
}

/* スマホでは、PC用の設定パネルの部品そのものを各パネルへ移す(以前は複製していたため、
   テキストボックスの編集・色の変更・テンプレートの切り替えがスマホで効かなかった)。PC幅に戻ったら元の場所へ戻す */
const mobileHomes=new Map();
let mobilePlaced=false;
function moveForMobile(node,host){
  if(!node||!host)return;
  if(!mobileHomes.has(node)){const m=document.createComment("home");node.parentNode.insertBefore(m,node);mobileHomes.set(node,m)}
  host.appendChild(node);
}
function cloneControlsForMobile(){
  const want=mobileUIActive();
  if(want===mobilePlaced)return;
  if(want){
    const q=s=>document.querySelector(s);
    [[ "mobileFacePanelBody",[".face-section","#imageControls"]],
     [ "mobileTemplatePanelBody",["#templateSelector","#playingControls","#tcgControls","#wordControls","#customControls"]],
     [ "mobileOptionsPanelBody",["#textBoxControls","aside .public-beta-note"]]
    ].forEach(([host,sels])=>sels.forEach(sel=>moveForMobile(q(sel),el(host))));
    document.querySelectorAll("#mobilePaperPanelBody [data-slot]").forEach(slot=>slot.dataset.slot.split(" ").forEach(id=>moveForMobile(el(id),slot)));
  }else{
    closeMobilePanel();
    mobileHomes.forEach((m,node)=>m.parentNode.insertBefore(node,m));
  }
  mobilePlaced=want;
}
window.matchMedia("(max-width:720px)").addEventListener("change",()=>{cloneControlsForMobile();fitPaper()});

/* パネルはカードのすぐ下からタブの上までを使う(狭い画面でも最低220pxは確保) */
function placeMobilePanel(){
  if(!mobileUIActive())return;
  const labels=document.querySelector(".mobile-face-labels"),pair=el("mobileCardPair"),bar=el("mobileQuickBar");
  const sheetFrame=mobileSheetMode?document.querySelector("#mobileSheetView .m-sheet-frame"):null;
  const ref=sheetFrame||((labels&&labels.offsetParent)?labels:pair);if(!ref||!bar)return;
  const barTop=bar.getBoundingClientRect().top;
  const top=Math.max(56,Math.min(ref.getBoundingClientRect().bottom+8,barTop-8-220));
  document.documentElement.style.setProperty("--m-panel-top",Math.round(top)+"px");
  document.documentElement.style.setProperty("--m-panel-bottom",Math.round(innerHeight-barTop+8)+"px");
}
window.addEventListener("resize",placeMobilePanel);

document.querySelectorAll('input[type=file]').forEach(inp=>{
  if(!inp.id||inp.classList.contains("hidden"))return;
  const lab=document.createElement("label");lab.htmlFor=inp.id;lab.className="file-btn";lab.textContent="画像を選ぶ";
  inp.classList.add("file-native");inp.insertAdjacentElement("afterend",lab);
});
window.addEventListener("DOMContentLoaded",()=>{
  document.querySelectorAll(".mobile-panel-close").forEach(b=>b.addEventListener("click",closeMobilePanel));
  cloneControlsForMobile();
  placeMobilePanel();
});

function mobileCardIndex(){
  return currentPage*cardsPerPage() + (arrangement()==="pairs"?Math.floor(selected/2):selected);
}
function goToMobileCard(delta){
  const total=pages.length*cardsPerPage();
  if(delta>0&&mobileCardIndex()>=total-1){if(pages.length<MAX_PAGES){const side=arrangement()==="pairs"?selected%2:0;el("addPage").click();selected=side;renderSheet();syncControls()}return}
  const side=selected%2;
  let next=clamp(mobileCardIndex()+delta,0,total-1);
  const n=cardsPerPage(); currentPage=Math.floor(next/n);
  selected=arrangement()==="pairs"?(next%n)*2+side:(next%n);
  renderSheet();
  syncControls();
}
/* ---- スマホ:ページ全体の表示(1枚ずつの表示と切り替え) ---- */
let mobileSheetMode=false;
function setMobileSheetMode(on){
  mobileSheetMode=!!on;
  document.body.classList.toggle("m-sheet-mode",mobileSheetMode);
  const t=el("mobileViewToggle");if(t){t.textContent=mobileSheetMode?"1枚ずつ":"ページ全体";t.setAttribute("aria-pressed",String(mobileSheetMode))}
  el("mobileSheetView").hidden=!mobileSheetMode;
  renderMobileCardPreview();
  if(mobilePanelOpen)placeMobilePanel();
}
function renderMobileSheet(){
  const host=el("mobileSheetView");if(!host||!mobileSheetMode)return;
  host.innerHTML="";
  const p=paperMM(),W=p.w*MM_TO_PX,H=p.h*MM_TO_PX;
  const frame=document.createElement("div");frame.className="m-sheet-frame";
  const sheet=document.createElement("div");sheet.className="m-sheet "+(el("paperOrientation").value==="landscape"?"landscape-paper":"portrait-paper");
  sheet.style.width=W+"px";sheet.style.height=H+"px";
  const title=document.createElement("div");title.className="sheet-title";title.textContent=sheetTitle;sheet.appendChild(title);
  const sa=isPairLayout()?"pairs":"front";
  const sg=document.createElement("div");buildSheet(sg,facesOf(currentPage,sa),false,sa);sheet.appendChild(sg);
  frame.appendChild(sheet);host.appendChild(frame);
  const cur=arrangement()==="pairs"?Math.floor(selected/2):selected;
  sg.querySelectorAll(".pair").forEach((pair,i)=>{
    if(i===cur)pair.classList.add("m-current");
    pair.addEventListener("click",()=>{selected=arrangement()==="pairs"?i*2+(selected%2):i;setMobileSheetMode(false);syncControls()});
  });
  // 幅いっぱい、ただし下のバー(パネルを開いていればパネル)にかからない大きさに
  const bar=el("mobileQuickBar"),top=host.getBoundingClientRect().top;
  const limit=(bar?bar.getBoundingClientRect().top:innerHeight)-(mobilePanelOpen?228:12);
  const k=Math.max(.1,Math.min(host.clientWidth/W,(limit-top)/H));
  sheet.style.transform=`scale(${k})`;frame.style.width=W*k+"px";frame.style.height=H*k+"px";
}
function goToMobilePage(delta){
  if(delta>0&&currentPage>=pages.length-1){if(pages.length<MAX_PAGES){const keep=selected;el("addPage").click();selected=keep;renderSheet();syncControls()}return}
  currentPage=clamp(currentPage+delta,0,pages.length-1);renderSheet();syncControls();
}

function rescaleMobileFaces(){
  document.querySelectorAll("#mobileCardPair .m-face-inner").forEach(n=>{const w=n.parentElement.clientWidth;if(w)n.style.transform=`scale(${w/parseFloat(n.style.width)})`});
}
window.addEventListener("resize",()=>{if(mobileUIActive())rescaleMobileFaces()});
function renderMobileCardPreview(){
  const host=el("mobileCardPair");if(!host)return;
  const faces=currentFaces(),c=cardMM(),landscape=isLandscapeCard();
  const paired=arrangement()==="pairs";
  host.innerHTML="";host.className="mobile-card-pair "+(landscape?"mobile-landscape-card":"mobile-portrait-card")+(paired?"":" single-mode");
  const indices=paired?[Math.floor(selected/2)*2,Math.floor(selected/2)*2+1]:[selected];
  indices.forEach(idx=>{const f=document.createElement("div");f.className="face"+(idx===selected?" selected":"");f.style.setProperty("--mobile-card-ratio",landscape?`${c.h}/${c.w}`:`${c.w}/${c.h}`);const fm=faceMM(),inner=document.createElement("div");inner.className="m-face-inner";inner.style.width=fm.w*MM_TO_PX+"px";inner.style.height=fm.h*MM_TO_PX+"px";f.appendChild(inner);renderFace(inner,faces[idx],idx===selected,idx);f.addEventListener("click",()=>{selected=idx;renderMobileCardPreview();syncControls()});host.appendChild(f)});
  rescaleMobileFaces();
  const absolute=mobileCardIndex();
  const total=pages.length*cardsPerPage();
  if(mobileSheetMode){
    renderMobileSheet();
    const n=cardsPerPage(),first=currentPage*n+1;
    el("mobileCardCount").textContent=`ページ ${currentPage+1} / ${pages.length}`;
    if(el("mobilePageCount"))el("mobilePageCount").textContent=`カード ${first}〜${first+n-1}`;
    el("mobilePrevCard").disabled=currentPage<=0;
    const atEnd=currentPage>=pages.length-1,nb=el("mobileNextCard");
    nb.disabled=atEnd&&pages.length>=MAX_PAGES;nb.textContent=atEnd?"＋":"→";nb.setAttribute("aria-label",atEnd?"ページを追加":"次のページ");nb.classList.toggle("is-add",atEnd);
    el("mobilePrevCard").setAttribute("aria-label","前のページ");
    if(mobilePanelOpen)requestAnimationFrame(placeMobilePanel);
    return;
  }
  el("mobilePrevCard").setAttribute("aria-label","前のカード");
  el("mobileCardCount").textContent=`カード ${absolute+1} / ${total}`;if(el("mobilePageCount"))el("mobilePageCount").textContent=`ページ ${currentPage+1} / ${pages.length}`;
  el("mobilePrevCard").disabled=absolute<=0;
  const atEnd=absolute>=total-1,nb=el("mobileNextCard");
  nb.disabled=atEnd&&pages.length>=MAX_PAGES;nb.textContent=atEnd?"＋":"→";nb.setAttribute("aria-label",atEnd?"ページを追加":"次のカード");nb.classList.toggle("is-add",atEnd);
  const labels=document.querySelector(".mobile-face-labels");if(labels){labels.style.display=paired?"":"none";labels.classList.toggle("stacked",landscape)}
  if(mobilePanelOpen)requestAnimationFrame(placeMobilePanel);
}

function renderPageSidebar(){
  const box=el("pageThumbs");
  if(!box)return;
  box.innerHTML="";
  const p=paperMM();
  const viewportW=116;
  const fullW=p.w*MM_TO_PX, fullH=p.h*MM_TO_PX;
  const scale=viewportW/fullW;
  const viewportH=fullH*scale;

  let dragFrom=null;

  function makeDropZone(insertIndex){
    const zone=document.createElement("div");
    zone.className="page-drop-zone";
    zone.addEventListener("dragover",e=>{
      e.preventDefault();
      e.dataTransfer.dropEffect="move";
      zone.classList.add("drag-over");
    });
    zone.addEventListener("dragleave",()=>zone.classList.remove("drag-over"));
    zone.addEventListener("drop",e=>{
      e.preventDefault();
      zone.classList.remove("drag-over");
      const from=dragFrom ?? Number(e.dataTransfer.getData("text/plain"));
      if(from===null || Number.isNaN(from))return;

      movePage(from,insertIndex);
      dragFrom=null;
      renderSheet();
      syncControls();
    });
    return zone;
  }

  pages.forEach((pg,i)=>{
    box.appendChild(makeDropZone(i));

    const item=document.createElement("div");
    item.className="page-thumb"+(i===currentPage?" active":"");
    item.draggable=true;
    item.dataset.index=i;
    item.onclick=()=>{
      currentPage=i;selected=0;renderSheet();syncControls();
    };
    item.addEventListener("dragstart",e=>{
      dragFrom=i;
      e.dataTransfer.setData("text/plain",String(i));
      e.dataTransfer.effectAllowed="move";
      item.classList.add("dragging");
    });
    item.addEventListener("dragend",()=>{
      item.classList.remove("dragging");
      document.querySelectorAll(".page-drop-zone.drag-over").forEach(z=>z.classList.remove("drag-over"));
    });

    const n=document.createElement("div");
    n.className="page-thumb-num";
    n.textContent=`${i+1}`;
    item.appendChild(n);

    const menuBtn=document.createElement("button");
    menuBtn.type="button";
    menuBtn.className="page-thumb-menu-btn";
    menuBtn.textContent="…";
    menuBtn.title="ページメニュー";
    menuBtn.addEventListener("click",e=>{
      e.preventDefault();e.stopPropagation();
      document.querySelectorAll(".page-thumb-menu").forEach(m=>m.remove());
      const menu=document.createElement("div");
      menu.className="page-thumb-menu";

      const dup=document.createElement("button");
      dup.type="button";dup.textContent="複製";dup.disabled=pages.length>=MAX_PAGES;
      dup.addEventListener("click",ev=>{ev.stopPropagation();duplicatePage(i)});

      const del=document.createElement("button");
      del.type="button";del.textContent="削除";del.disabled=pages.length<=1;
      del.addEventListener("click",ev=>{ev.stopPropagation();deletePage(i)});

      menu.appendChild(dup);menu.appendChild(del);
      item.appendChild(menu);
    });
    item.appendChild(menuBtn);

    const vp=document.createElement("div");
    vp.className="thumb-viewport";
    vp.style.height=viewportH+"px";

    const thumb=document.createElement("div");
    thumb.className="thumb-paper "+(el("paperOrientation").value==="landscape"?"landscape-paper":"portrait-paper");
    thumb.style.width=fullW+"px";
    thumb.style.height=fullH+"px";
    thumb.style.transform=`scale(${scale})`;

    const title=document.createElement("div");
    title.className="sheet-title";
    title.textContent=sheetTitle;
    thumb.appendChild(title);

    const sg=document.createElement("div");
    buildSheet(sg,pg,false);
    thumb.appendChild(sg);

    vp.appendChild(thumb);
    item.appendChild(vp);
    box.appendChild(item);
  });

  box.appendChild(makeDropZone(pages.length));
}


function renderTextBoxEditors(d){
  const list=el("textBoxList"),items=ensureTextBoxes(d);
  list.innerHTML="";

  items.forEach((item,index)=>{
    const st=item.style||{size:SIZE.text,bold:false,italic:false,underline:false,color:"#222222",colorNone:false};
    const wrap=document.createElement("div");
    wrap.className="textbox-editor";
    wrap.innerHTML=`
      <div class="textbox-editor-head">
        <strong>テキストボックス${index+1}</strong>
        <button type="button" class="textbox-delete">削除</button>
      </div>
      <input class="tb-text" type="text" value="${esc(item.text||"")}" placeholder="テキスト${index+1}">
      <div class="tool-strip tool-strip-secondary">
        <div class="tool-number-wrap" title="文字サイズ（px）">
          <span class="size-icon">A</span>
          <input class="tb-size tool-number" type="number"><span class="unit-suffix"></span>
        </div>
        <label class="style-toggle" title="太字"><input class="tb-bold" type="checkbox" ${st.bold?"checked":""}><span class="bold-mark">B</span></label>
        <label class="style-toggle" title="斜体"><input class="tb-italic" type="checkbox" ${st.italic?"checked":""}><span class="italic-mark">I</span></label>
        <label class="style-toggle" title="下線"><input class="tb-underline" type="checkbox" ${st.underline?"checked":""}><span class="underline-mark">U</span></label>
        <div class="tool-color" title="文字色"><input class="tb-color" type="color" value="${st.color||"#222222"}" aria-label="文字色"></div>
      </div>
      <div class="font-row"><span class="font-row-label">フォント</span><select class="tb-font font-select" aria-label="フォント">${fontOptions(true)}</select></div>
      <label class="checkline" style="margin:6px 0 0"><input class="tb-center" type="checkbox" ${item.centerSnap?"checked":""}>中央にスナップ</label>`;

    const text=wrap.querySelector(".tb-text");
    const size=wrap.querySelector(".tb-size");
    const bold=wrap.querySelector(".tb-bold");
    const italic=wrap.querySelector(".tb-italic");
    const underline=wrap.querySelector(".tb-underline");
    const color=wrap.querySelector(".tb-color");
    const center=wrap.querySelector(".tb-center");
    const del=wrap.querySelector(".textbox-delete"),font=wrap.querySelector(".tb-font");
    setSizeInput(size,st.size||SIZE.text);
    font.value=st.font||"";font.onchange=()=>{item.style={...item.style,font:font.value};renderSheet()};

    text.oninput=()=>{item.text=text.value;renderSheet()};
    [size,bold,italic,underline].forEach(inp=>inp.oninput=()=>{
      item.style={
        ...item.style,
        size:readSizeInput(size,SIZE.text),
        bold:bold.checked,
        italic:italic.checked,
        underline:underline.checked
      };
      renderSheet();
    });

    color.dataset.none=st.colorNone?"1":"0";
    color.oninput=()=>{
      item.style={...item.style,color:color.value,colorNone:false};
      color.dataset.none="0";
      renderSheet();
      refreshOpenColorPopup();
    };
    color.addEventListener("colornone",()=>{
      item.style={...item.style,colorNone:true};
      renderSheet();
    });

    center.onchange=()=>{item.centerSnap=center.checked;renderSheet()};
    del.onclick=()=>{items.splice(index,1);renderSheet();syncControls()};

    list.appendChild(wrap);
    setupColorInput(color);
    refreshColorTrigger(color);
  });

  el("addTextBox").disabled=items.length>=5;
}

function renderOptionImageEditors(d){
  const list=el("optionImageList"),items=ensureOptionImages(d);list.innerHTML="";
  items.forEach((item,index)=>{const wrap=document.createElement("div");wrap.className="option-image-editor";wrap.innerHTML=`<div class="option-image-editor-head"><strong>画像${index+1}</strong><button type="button" class="textbox-delete">削除</button></div><div class="option-image-row"><img src="${item.src}" alt=""><label>回転 <input class="option-image-angle" type="number" min="-180" max="180" value="${Number(item.rotation)||0}">°</label></div><label class="checkline" style="margin:6px 0 0"><input class="oi-center" type="checkbox" ${item.centerSnap?"checked":""}>中央にスナップ</label>`;const angle=wrap.querySelector(".option-image-angle"),center=wrap.querySelector(".oi-center"),del=wrap.querySelector(".textbox-delete");angle.oninput=()=>{item.rotation=Number(angle.value)||0;renderSheet()};center.onchange=()=>{item.centerSnap=center.checked;renderSheet()};del.onclick=()=>{items.splice(index,1);renderSheet();syncControls()};list.appendChild(wrap)});el("addOptionImage").disabled=items.length>=5
}

function renderShapeEditors(d){const list=el('shapeList'),items=ensureShapes(d);list.innerHTML='';items.forEach((item,i)=>{const w=document.createElement('div');w.className='shape-editor';const names={circle:'円',triangle:'三角形',rect:'四角形',polygon:'多角形',star:'星'};w.innerHTML=`<div class="shape-editor-head"><strong>${names[item.type]||'図形'}${i+1}</strong><button class="textbox-delete" type="button">削除</button></div><div class="shape-editor-row">${['polygon','star'].includes(item.type)?`<label>頂点 <input class="shape-points" type="number" min="${item.type==='star'?4:3}" max="12" value="${item.points||5}" style="width:54px"></label>`:''}<div class="tool-color fill-color" title="面色"><input class="shape-fill" type="color" value="${item.fillColor||'#fff'}"></div><div class="tool-color stroke-color" title="線色"><input class="shape-stroke" type="color" value="${item.borderColor||'#222'}"></div><select class="shape-width stroke-width-select"><option value="0.5">0.5 mm</option><option value="0.75">0.75 mm</option><option value="1">1 mm</option><option value="2">2 mm</option><option value="3">3 mm</option></select><select class="shape-align stroke-align-select"><option value="inside">内側</option><option value="center">中央</option><option value="outside">外側</option></select></div>`;const pts=w.querySelector('.shape-points'),fill=w.querySelector('.shape-fill'),stroke=w.querySelector('.shape-stroke'),width=w.querySelector('.shape-width'),align=w.querySelector('.shape-align');width.value=String(item.borderWidth||1);align.value=item.borderAlign||'inside';if(pts)pts.oninput=()=>{item.points=clamp(Number(pts.value)||5,item.type==='star'?4:3,12);renderSheet()};fill.dataset.none=item.fillNone?'1':'0';stroke.dataset.none=item.borderNone?'1':'0';fill.oninput=()=>{item.fillColor=fill.value;item.fillNone=false;renderSheet()};stroke.oninput=()=>{item.borderColor=stroke.value;item.borderNone=false;renderSheet()};fill.addEventListener('colornone',()=>{item.fillNone=true;renderSheet()});stroke.addEventListener('colornone',()=>{item.borderNone=true;renderSheet()});width.onchange=()=>{item.borderWidth=Number(width.value)||1;renderSheet()};align.onchange=()=>{item.borderAlign=align.value;renderSheet()};w.querySelector('.textbox-delete').onclick=()=>{items.splice(i,1);renderSheet();syncControls()};list.appendChild(w);[fill,stroke].forEach(setupColorInput)})}

function renderFrameTextEditors(d){
  const list=el("frameTextList"),items=ensureFrameTexts(d);list.innerHTML="";
  items.forEach((item,index)=>{
    const st=item.style||{size:SIZE.frame,bold:false,italic:false,underline:false,color:"#222222",colorNone:false};
    const wrap=document.createElement("div");wrap.className="frame-editor";
    wrap.innerHTML=`<div class="frame-editor-head"><strong>フレームテキスト${index+1}</strong><button type="button" class="textbox-delete">削除</button></div>
      <input class="ft-text" type="text" value="${esc(item.text||"")}" placeholder="フレームテキスト">
      <div class="tool-strip tool-strip-secondary">
        <div class="tool-number-wrap" title="文字サイズ（px）"><span class="size-icon">A</span><input class="ft-size tool-number" type="number"><span class="unit-suffix"></span></div>
        <label class="style-toggle"><input class="ft-bold" type="checkbox" ${st.bold?"checked":""}><span class="bold-mark">B</span></label>
        <label class="style-toggle"><input class="ft-italic" type="checkbox" ${st.italic?"checked":""}><span class="italic-mark">I</span></label>
        <label class="style-toggle"><input class="ft-underline" type="checkbox" ${st.underline?"checked":""}><span class="underline-mark">U</span></label>
      </div>
      <div class="font-row"><span class="font-row-label">フォント</span><select class="ft-font font-select" aria-label="フォント">${fontOptions(true)}</select></div>
      <div class="frame-color-row">
        <div class="tool-color" title="文字色"><input class="ft-text-color" aria-label="文字色" type="color" value="${st.color||"#222222"}"></div>
        <div class="tool-color fill-color" title="面色"><input class="ft-fill-color" aria-label="面色" type="color" value="${item.fillColor||"#ffffff"}"></div>
        <div class="tool-color stroke-color" title="線色"><input class="ft-border-color" aria-label="線色" type="color" value="${item.borderColor||"#222222"}"></div>
        <div class="tool-number-wrap stroke-width-control" title="線の太さ">
          <span class="stroke-width-icon" aria-hidden="true"></span>
          <select class="ft-border-width stroke-width-select" aria-label="線の太さ">
            <option value="0.5" ${Number(item.borderWidth)===0.5?"selected":""}>0.5 mm</option><option value="0.75" ${Number(item.borderWidth)===0.75?"selected":""}>0.75 mm</option><option value="1" ${Number(item.borderWidth??1)===1?"selected":""}>1 mm</option><option value="2" ${Number(item.borderWidth)===2?"selected":""}>2 mm</option><option value="3" ${Number(item.borderWidth)===3?"selected":""}>3 mm</option></select><select class="ft-border-align stroke-align-select" aria-label="線の位置"><option value="inside" ${(item.borderAlign||"inside")==="inside"?"selected":""}>内側</option><option value="center" ${item.borderAlign==="center"?"selected":""}>中央</option><option value="outside" ${item.borderAlign==="outside"?"selected":""}>外側</option></select>
        </div>
      </div>
      <label class="checkline" style="margin:6px 0 0"><input class="ft-center" type="checkbox" ${item.centerSnap?"checked":""}>中央にスナップ</label>`;
    const text=wrap.querySelector(".ft-text"),size=wrap.querySelector(".ft-size"),bold=wrap.querySelector(".ft-bold"),italic=wrap.querySelector(".ft-italic"),underline=wrap.querySelector(".ft-underline"),tc=wrap.querySelector(".ft-text-color"),bc=wrap.querySelector(".ft-border-color"),bw=wrap.querySelector(".ft-border-width"),ba=wrap.querySelector(".ft-border-align"),fc=wrap.querySelector(".ft-fill-color"),center=wrap.querySelector(".ft-center"),del=wrap.querySelector(".textbox-delete");
    text.oninput=()=>{item.text=text.value;renderSheet()};
    setSizeInput(size,st.size||SIZE.frame);
    const font=wrap.querySelector(".ft-font");font.value=st.font||"";font.onchange=()=>{item.style={...item.style,font:font.value};renderSheet()};
    [size,bold,italic,underline].forEach(x=>x.oninput=()=>{item.style={...item.style,size:readSizeInput(size,SIZE.frame),bold:bold.checked,italic:italic.checked,underline:underline.checked};renderSheet()});
    tc.dataset.none=st.colorNone?"1":"0";bc.dataset.none=item.borderNone?"1":"0";fc.dataset.none=item.fillNone?"1":"0";
    tc.oninput=()=>{item.style={...item.style,color:tc.value,colorNone:false};tc.dataset.none="0";renderSheet();refreshOpenColorPopup()};
    bc.oninput=()=>{item.borderColor=bc.value;item.borderNone=false;bc.dataset.none="0";renderSheet();refreshOpenColorPopup()};bw.onchange=()=>{item.borderWidth=Number(bw.value)||1;renderSheet()};ba.onchange=()=>{item.borderAlign=ba.value;renderSheet()};
    fc.oninput=()=>{item.fillColor=fc.value;item.fillNone=false;fc.dataset.none="0";renderSheet();refreshOpenColorPopup()};
    tc.addEventListener("colornone",()=>{item.style.colorNone=true;renderSheet()});
    bc.addEventListener("colornone",()=>{item.borderNone=true;renderSheet()});
    fc.addEventListener("colornone",()=>{item.fillNone=true;renderSheet()});
    center.onchange=()=>{item.centerSnap=center.checked;renderSheet()};
    del.onclick=()=>{items.splice(index,1);renderSheet();syncControls()};
    list.appendChild(wrap);[tc,bc,fc].forEach(x=>{setupColorInput(x);refreshColorTrigger(x)});
  });
  el("addFrameText").disabled=items.length>=5;
}

function syncControls(){
  const d=currentFaces()[selected];
  el("selectedLabel").textContent=faceName(selected);
  refreshCopyButtonLabels();
  el("faceType").value=d.type;
  const templ=d.type==="template";
  el("templateSelector").classList.toggle("hidden",!templ);
  el("playingControls").classList.add("hidden");el("tcgControls").classList.add("hidden");el("wordControls").classList.add("hidden");el("customControls").classList.add("hidden");
  el("imageControls").classList.toggle("hidden",d.type!=="image");
  el("mobileTemplateHint")?.classList.toggle("hidden",templ);
  el("mobileTemplateBar")?.classList.toggle("hidden",!templ);
  if(el("mobileFaceTypeName"))el("mobileFaceTypeName").textContent=d.type==="image"?"画像":"無地";


  el("suitImageControls").classList.add("hidden");
  if(templ){
    el("templateType").value=d.template||"playing";
    if((d.template||"playing")==="playing"){
      el("playingControls").classList.remove("hidden");
      el("numInput").value=d.number??"";el("suitInput").value=d.suit??"●";
      el("playingNumberColor").value=d.numberColor||d.color||"#d94a4a";el("playingNumberColor").dataset.none=d.numberColorNone?"1":"0";
      el("suitSize").value=d.suitSize||"medium";
      el("suitCount").value=String(d.suitCount||1);
      el("cornerPlacement").value=d.cornerPlacement||"four";
      el("suitMode").value=d.suitMode||"text";
      el("suitImageControls").classList.toggle("hidden",(d.suitMode||"text")!=="image");
      const st=d.numberStyle||{size:SIZE.number,bold:true,italic:false};
      setSizeInput(el("playingSize"),st.size||SIZE.number);el("playingFont").value=st.font||"";el("playingBold").checked=st.bold!==false;el("playingItalic").checked=!!st.italic;el("playingUnderline").checked=!!st.underline;
    }else if(d.template==="tcg"){
      el("tcgControls").classList.remove("hidden");
      el("tcgName").value=d.name??"";el("tcgDesc").value=d.desc??"";
      const legacy=d.color||"#222222";
      el("tcgTextColor").value=d.textColor||legacy;el("tcgTextColor").dataset.none=d.textColorNone?"1":"0";
      el("tcgBorderColor").value=d.borderColor||legacy;el("tcgBorderColor").dataset.none=d.borderNone?"1":"0";el("tcgBorderWidth").value=String(d.borderWidth??1);el("tcgBorderAlign").value=d.borderAlign||"inside";
            el("tcgPanelColor").value=d.panelColor||"#ffffff";el("tcgPanelColor").dataset.none=d.panelNone?"1":"0";
      document.querySelectorAll('input[name="tcgLayout"]').forEach(r=>r.checked=String(d.horizontalLayout||1)===r.value);
      el("tcgTopHeight").value=String(d.tcgTopHeight??16);el("tcgMiddleHeight").value=String(d.tcgMiddleHeight??50);el("tcgBottomHeight").value=String(d.tcgBottomHeight??28);
      const ns=d.nameStyle||{size:SIZE.tcgName,bold:true,italic:false},ds=d.descStyle||{size:SIZE.tcgDesc,bold:false,italic:false};
      setSizeInput(el("tcgNameSize"),ns.size||SIZE.tcgName);el("tcgNameFont").value=ns.font||"";el("tcgDescFont").value=ds.font||"";el("tcgNameBold").checked=!!ns.bold;el("tcgNameItalic").checked=!!ns.italic;el("tcgNameUnderline").checked=!!ns.underline;
      setSizeInput(el("tcgDescSize"),ds.size||SIZE.tcgDesc);el("tcgDescBold").checked=!!ds.bold;el("tcgDescItalic").checked=!!ds.italic;el("tcgDescUnderline").checked=!!ds.underline;
    }else if(d.template==="word"){
      el("wordControls").classList.remove("hidden");
      el("wordMain").value=d.main??"";
      el("wordMainColor").value=d.mainColor||d.color||"#222222";el("wordMainColor").dataset.none=d.mainColorNone?"1":"0";
      const ms=d.mainStyle||{size:SIZE.word,bold:true,italic:false};
      setSizeInput(el("wordMainSize"),ms.size||SIZE.word);el("wordMainFont").value=ms.font||"";el("wordMainBold").checked=!!ms.bold;el("wordMainItalic").checked=!!ms.italic;el("wordMainUnderline").checked=!!ms.underline;
    }else if(d.template==="custom"){el("customControls").classList.remove("hidden");}
  }
  el("faceBgColor").value=d.bgColor||"#ffffff";el("faceBgColor").dataset.none=d.bgNone?"1":"0";
  el("faceBorderColor").value=d.bgBorderColor||"#222222";el("faceBorderColor").dataset.none=d.bgBorderNone?"1":"0";
  el("faceBorderWidth").value=String(d.bgBorderWidth??1);el("faceBorderAlign").value=d.bgBorderAlign||"inside";
  renderTextBoxEditors(d);
  renderFrameTextEditors(d);
  renderOptionImageEditors(d);
  renderShapeEditors(d);
  setupAllColorInputs();
  const showTcgLayout = templ && d.template==="tcg" && isLandscapeCard();
  el("tcgLayoutControls").classList.toggle("hidden",!showTcgLayout);
  relabelLengths(document);
  if(el("deckFont"))el("deckFont").value=deck.font||"system";
  renderSwatches();
}
function updateSelected(patch){setFaceAt(currentPage,selected,{...currentFaces()[selected],...patch});renderSheet()}

el("sheetTitleInput").addEventListener("input",e=>{sheetTitle=e.target.value;renderSheet()});

// Finish one undo step when the current UI interaction ends.
document.addEventListener("pointerup",()=>commitGroupedHistory(),true);
document.addEventListener("change",()=>commitGroupedHistory(),true);
document.addEventListener("blur",e=>{
  if(e.target.matches("input, textarea, select"))commitGroupedHistory();
},true);

el("undoBtn").addEventListener("click",undoHistory);
el("redoBtn").addEventListener("click",redoHistory);

document.addEventListener("keydown",e=>{
  const mod=e.metaKey||e.ctrlKey;
  if(!mod)return;
  const key=e.key.toLowerCase();
  if(key==="z"){
    e.preventDefault();
    if(e.shiftKey)redoHistory();
    else undoHistory();
  }else if(key==="y"){
    e.preventDefault();
    redoHistory();
  }
});


el("mobileAddPage")?.addEventListener("click",mobileAddPage);
el("mobileFaceTab")?.addEventListener("click",()=>{cloneControlsForMobile();openMobilePanel("Face","mobileFaceTab")});
el("mobileTemplateTab")?.addEventListener("click",()=>{cloneControlsForMobile();openMobilePanel("Template","mobileTemplateTab")});
el("mobileOptionsJump")?.addEventListener("click",()=>{cloneControlsForMobile();openMobilePanel("Options","mobileOptionsJump")});
el("mobileMore")?.addEventListener("click",()=>openMobilePanel("More","mobileMore"));
el("mobilePaperTab")?.addEventListener("click",()=>{cloneControlsForMobile();updateFit();openMobilePanel("Paper","mobilePaperTab")});
el("mobileMakeTemplate")?.addEventListener("click",()=>{const f=el("faceType");f.value="template";f.dispatchEvent(new Event("change",{bubbles:true}))});
el("mobileMakePlain")?.addEventListener("click",()=>{const f=el("faceType");f.value="plain";f.dispatchEvent(new Event("change",{bubbles:true}))});
["mobilePdfSave","mobilePdfLoad","mobilePrint","mobileDupPage","mobileDeletePage"].forEach(id=>el(id)?.addEventListener("click",closeMobilePanel));
el("mobileUndo")?.addEventListener("click",()=>el("undoBtn")?.click());
el("mobileRedo")?.addEventListener("click",()=>el("redoBtn")?.click());
el("mobilePdfSave")?.addEventListener("click",()=>el("editablePdfBtn")?.click());
el("mobilePdfLoad")?.addEventListener("click",()=>el("loadPdfBtn")?.click());
el("mobilePrint")?.addEventListener("click",()=>el("printBtn")?.click());
el("mobileDupPage")?.addEventListener("click",()=>el("dupPage")?.click());
el("mobileDeletePage")?.addEventListener("click",()=>el("deletePage")?.click());
el("mobilePrevCard")?.addEventListener("click",()=>mobileSheetMode?goToMobilePage(-1):goToMobileCard(-1));
el("mobileViewToggle")?.addEventListener("click",()=>{if(!mobileSheetMode&&["Face","Template","Options"].includes(mobilePanelOpen))closeMobilePanel();setMobileSheetMode(!mobileSheetMode)});
[el("mobileCardPair"),el("mobileSheetView")].forEach(area=>{if(!area)return;let sx=null,sy=0;
  area.addEventListener("pointerdown",e=>{if(e.pointerType==="mouse"||e.target.closest(".editable"))return;sx=e.clientX;sy=e.clientY});
  area.addEventListener("pointerup",e=>{if(sx===null)return;const dx=e.clientX-sx,dy=e.clientY-sy;sx=null;
    if(!(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.5))return;
    if(mobileSheetMode){if(dx<0&&currentPage>=pages.length-1)return;goToMobilePage(dx<0?1:-1)}
    else{if(dx<0&&mobileCardIndex()>=pages.length*cardsPerPage()-1)return;goToMobileCard(dx<0?1:-1)}});
  area.addEventListener("pointercancel",()=>{sx=null});
});
el("mobileNextCard")?.addEventListener("click",()=>mobileSheetMode?goToMobilePage(1):goToMobileCard(1));
el("paperSize").addEventListener("change",()=>{resizePagesForLayout();setPaper();syncControls()});
el("paperOrientation").addEventListener("change",()=>{cardOrientation=(el("paperOrientation").value==="landscape")?(!isPairLayout()?"landscape":"portrait"):(!isPairLayout()?"portrait":"landscape");resizePagesForLayout();setPaper();syncControls()});
el("cardSize").addEventListener("change",()=>{resizePagesForLayout();setPaper();syncControls()});
el("impositionMode").addEventListener("change",e=>{el("paperOrientation").value=optimalPaperOrientationForMode();resizePagesForLayout();e.target.dataset.prev=e.target.value;setPaper();syncControls()});
window.addEventListener("resize",fitPaper);

el("faceType").addEventListener("change",e=>{
  const t=e.target.value,keep=keepCommon(currentFaces()[selected]);
  if(t==="plain")setFaceAt(currentPage,selected,{type:"plain",...keep});
  else if(t==="template")setFaceAt(currentPage,selected,{...makePlaying(),...keep});
  else if(t==="image")setFaceAt(currentPage,selected,{type:"image",src:null,...keep});
  renderSheet();syncControls();
});
el("templateType").addEventListener("change",e=>{
  const t=e.target.value,keep=keepCommon(currentFaces()[selected]);let nextFace=null;
  const keepBg=currentFaces()[selected].bgColor||"#ffffff";
  const keepBgImage=currentFaces()[selected].bgImage||null;
  const keepBgBorderColor=currentFaces()[selected].bgBorderColor||"#222222";
  const keepBgBorderWidth=currentFaces()[selected].bgBorderWidth??1;
  const keepBgBorderNone=currentFaces()[selected].bgBorderNone!==false;
  const keepBgBorderAlign=currentFaces()[selected].bgBorderAlign||"inside";
  const keepTextBoxes=deep(ensureTextBoxes(currentFaces()[selected]));
  const keepFrameTexts=deep(ensureFrameTexts(currentFaces()[selected]));
  const keepOptionImages=deep(ensureOptionImages(currentFaces()[selected]));
  if(t==="playing")nextFace={...makePlaying(),bgColor:keepBg,bgImage:keepBgImage,bgBorderColor:keepBgBorderColor,bgBorderWidth:keepBgBorderWidth,bgBorderNone:keepBgBorderNone,bgBorderAlign:keepBgBorderAlign,textBoxes:keepTextBoxes,frameTexts:keepFrameTexts,optionImages:keepOptionImages};
  if(t==="tcg")nextFace={type:"template",template:"tcg",name:"カード名",desc:"テキスト",image:null,bgColor:keepBg,bgImage:keepBgImage,
    bgBorderColor:keepBgBorderColor,bgBorderWidth:keepBgBorderWidth,bgBorderNone:keepBgBorderNone,bgBorderAlign:keepBgBorderAlign,
    textColor:"#222222",borderColor:"#222222",borderNone:false,panelColor:"#ffffff",horizontalLayout:1,tcgTopHeight:16,tcgMiddleHeight:50,tcgBottomHeight:28,textBoxes:keepTextBoxes,frameTexts:keepFrameTexts,optionImages:keepOptionImages,
    nameStyle:{size:SIZE.tcgName,bold:true,italic:false},descStyle:{size:SIZE.tcgDesc,bold:false,italic:false}};
  if(t==="word")nextFace={type:"template",template:"word",main:"ことば",bgColor:keepBg,bgImage:keepBgImage,bgBorderColor:keepBgBorderColor,bgBorderWidth:keepBgBorderWidth,bgBorderNone:keepBgBorderNone,bgBorderAlign:keepBgBorderAlign,mainColor:"#222222",textBoxes:keepTextBoxes,frameTexts:keepFrameTexts,optionImages:keepOptionImages,mainStyle:{size:SIZE.word,bold:true,italic:false}};
  if(nextFace)setFaceAt(currentPage,selected,Object.assign(nextFace,keep));   // 図形・背景の「なし」も含めて引き継ぐ
  renderSheet();syncControls();
});

["numInput","suitInput","suitSize","suitCount","suitMode","cornerPlacement"].forEach(id=>el(id).addEventListener("input",()=>{
  updateSelected({
    number:el("numInput").value,
    suit:el("suitInput").value,
    suitSize:el("suitSize").value,
    suitCount:Number(el("suitCount").value)||1,
    suitMode:el("suitMode").value,
    cornerPlacement:el("cornerPlacement").value
  });
  el("suitImageControls").classList.toggle("hidden",el("suitMode").value!=="image");
}));
el("playingNumberColor").addEventListener("input",()=>{const c=el("playingNumberColor").value;addRecentColor(c);updateSelected({numberColor:c,numberColorNone:false});renderSwatches()});
onImagePicked(el("suitImageInput"),src=>updateSelected({suitMode:"image",suitImage:src}));
["playingSize","playingBold","playingItalic","playingUnderline"].forEach(id=>el(id).addEventListener("input",()=>{
  const cur=currentFaces()[selected].numberStyle||{};
  updateSelected({numberStyle:{...cur,size:readSizeInput(el("playingSize"),SIZE.number),bold:el("playingBold").checked,italic:el("playingItalic").checked,underline:el("playingUnderline").checked}})
}));

["tcgName","tcgDesc"].forEach(id=>el(id).addEventListener("input",()=>updateSelected({name:el("tcgName").value,desc:el("tcgDesc").value})));
el("tcgTextColor").addEventListener("input",()=>{const c=el("tcgTextColor").value;addRecentColor(c);updateSelected({textColor:c,textColorNone:false});renderSwatches()});
el("tcgBorderColor").addEventListener("input",()=>{const c=el("tcgBorderColor").value;addRecentColor(c);updateSelected({borderColor:c,borderNone:false});renderSwatches()});
el("tcgPanelColor").addEventListener("input",()=>{const c=el("tcgPanelColor").value;addRecentColor(c);updateSelected({panelColor:c,panelNone:false});renderSwatches()});
document.querySelectorAll('input[name="tcgLayout"]').forEach(r=>r.addEventListener("change",()=>{
  if(r.checked) updateSelected({horizontalLayout:Number(r.value)});
}));
["tcgNameSize","tcgNameBold","tcgNameItalic","tcgNameUnderline","tcgDescSize","tcgDescBold","tcgDescItalic","tcgDescUnderline"].forEach(id=>el(id).addEventListener("input",()=>{
  updateSelected({
    nameStyle:{...(currentFaces()[selected].nameStyle||{}),size:readSizeInput(el("tcgNameSize"),SIZE.tcgName),bold:el("tcgNameBold").checked,italic:el("tcgNameItalic").checked,underline:el("tcgNameUnderline").checked},
    descStyle:{...(currentFaces()[selected].descStyle||{}),size:readSizeInput(el("tcgDescSize"),SIZE.tcgDesc),bold:el("tcgDescBold").checked,italic:el("tcgDescItalic").checked,underline:el("tcgDescUnderline").checked}
  })
}));
["tcgTopHeight","tcgMiddleHeight","tcgBottomHeight"].forEach(id=>el(id).addEventListener("input",()=>{
  updateSelected({tcgTopHeight:Number(el("tcgTopHeight").value)||16,tcgMiddleHeight:Number(el("tcgMiddleHeight").value)||50,tcgBottomHeight:Number(el("tcgBottomHeight").value)||28});
}));
onImagePicked(el("tcgImageInput"),src=>updateSelected({image:src}));

el("wordMain").addEventListener("input",()=>updateSelected({main:el("wordMain").value}));
el("wordMainColor").addEventListener("input",()=>{const c=el("wordMainColor").value;addRecentColor(c);updateSelected({mainColor:c,mainColorNone:false});renderSwatches()});
["wordMainSize","wordMainBold","wordMainItalic","wordMainUnderline"].forEach(id=>el(id).addEventListener("input",()=>{updateSelected({mainStyle:{...(currentFaces()[selected].mainStyle||{}),size:readSizeInput(el("wordMainSize"),SIZE.word),bold:el("wordMainBold").checked,italic:el("wordMainItalic").checked,underline:el("wordMainUnderline").checked}})}));



el("addTextBox").addEventListener("click",()=>{const d=currentFaces()[selected],items=ensureTextBoxes(d);if(items.length>=5)return;items.push(makeTextBox(items.length));renderSheet();syncControls()});
el("addFrameText").addEventListener("click",()=>{const d=currentFaces()[selected],items=ensureFrameTexts(d);if(items.length>=5)return;items.push(makeFrameText(items.length));renderSheet();syncControls()});
document.querySelectorAll(".add-shape").forEach(b=>b.addEventListener("click",()=>{const d=currentFaces()[selected],items=ensureShapes(d);if(items.length>=10)return;items.push(makeShape(b.dataset.shape,items.length));renderSheet();syncControls()}));
el("addOptionImage").addEventListener("click",()=>{if(ensureOptionImages(currentFaces()[selected]).length>=5)return;el("optionImageInput").click()});
onImagePicked(el("optionImageInput"),src=>{const items=ensureOptionImages(currentFaces()[selected]);if(items.length<5)items.push(makeOptionImage(src,items.length));renderSheet();syncControls()});

onImagePicked(el("imageInput"),src=>{
  setFaceAt(currentPage,selected,{type:"image",src,...keepCommon(currentFaces()[selected])});renderSheet();
});
el("faceBgColor").addEventListener("input",()=>{const c=el("faceBgColor").value;addRecentColor(c);updateSelected({bgColor:c,bgNone:false});renderSwatches()});

el("faceBorderColor").addEventListener("input",()=>{const c=el("faceBorderColor").value;updateSelected({bgBorderColor:c,bgBorderNone:false});refreshOpenColorPopup()});
el("faceBorderWidth").addEventListener("change",()=>updateSelected({bgBorderWidth:Number(el("faceBorderWidth").value)||1}));
el("faceBorderAlign").addEventListener("change",()=>updateSelected({bgBorderAlign:el("faceBorderAlign").value||"inside"}));
el("faceBorderColor").addEventListener("colornone",()=>updateSelected({bgBorderNone:true}));


el("faceBgColor").addEventListener("colornone",()=>updateSelected({bgNone:true}));
el("playingNumberColor").addEventListener("colornone",()=>updateSelected({numberColorNone:true}));
el("tcgTextColor").addEventListener("colornone",()=>updateSelected({textColorNone:true}));
el("tcgBorderColor").addEventListener("colornone",()=>updateSelected({borderNone:true}));
el("tcgBorderWidth").addEventListener("change",()=>updateSelected({borderWidth:Number(el("tcgBorderWidth").value)||1}));
el("tcgBorderAlign").addEventListener("change",()=>updateSelected({borderAlign:el("tcgBorderAlign").value||"inside"}));
el("tcgPanelColor").addEventListener("colornone",()=>updateSelected({panelNone:true}));
el("wordMainColor").addEventListener("colornone",()=>updateSelected({mainColorNone:true}));

onImagePicked(el("faceBgImageInput"),src=>updateSelected({bgImage:src}));
el("clearFaceBgImage").addEventListener("click",()=>{
  updateSelected({bgImage:null});
  el("faceBgImageInput").value="";
});

let faceClipboard=null;
function refreshCopyButtonLabels(){
  if(arrangement()==="single"){
    el("copyToPageSide").textContent="このページのすべての面にコピー";
    el("copyToAllPagesSide").textContent="すべてのページのすべての面にコピー";
  }else{
    el("copyToPageSide").textContent="この面をこのページの同じ面にコピー";
    el("copyToAllPagesSide").textContent="この面をすべてのページの同じ面にコピー";
  }
  el("pasteFace").disabled=!faceClipboard;
}
el("copyFace").addEventListener("click",()=>{faceClipboard=deep(currentFaces()[selected]);refreshCopyButtonLabels()});
el("pasteFace").addEventListener("click",()=>{if(!faceClipboard)return;setFaceAt(currentPage,selected,deep(faceClipboard));renderSheet();syncControls()});
/* 選んでいる面を、同じ側(オモテ/ウラ)の面にコピー。片面のときはすべての面 */
function copyFaceToSlots(slots){
  const {side}=slotAt(currentPage,selected),src=deep(currentFaces()[selected]),self=cardIdAt(currentPage,selected);
  new Set(slots.map(s=>deck.order[s])).forEach(id=>{if(id!==self)deck.cards[id][side]=deep(src)});
  syncPages();renderSheet();syncControls();
}
el("copyToPageSide").addEventListener("click",()=>{const n=cardsPerPage();copyFaceToSlots(Array.from({length:n},(_,k)=>currentPage*n+k))});
el("copyToAllPagesSide").addEventListener("click",()=>{padOrder();copyFaceToSlots(deck.order.map((_,k)=>k))});

document.addEventListener("click",()=>document.querySelectorAll(".page-thumb-menu").forEach(m=>m.remove()));

/* ---- ページの追加・複製・削除・並べ替え(デッキの並びを操作する) ---- */
function addPage(){
  if(pages.length>=MAX_PAGES)return;
  const n=cardsPerPage();padOrder();for(let i=0;i<n;i++)deck.order.push(addCard());
  syncPages();currentPage=pages.length-1;selected=0;renderSheet();syncControls();
}
function duplicatePage(p){
  if(pages.length>=MAX_PAGES)return;
  const n=cardsPerPage();padOrder();
  const copies=deck.order.slice(p*n,(p+1)*n).map(id=>{const c=deck.cards[id];return addCard(deep(c.front),deep(c.back))});
  deck.order.splice((p+1)*n,0,...copies);
  syncPages();currentPage=p+1;selected=0;renderSheet();syncControls();
}
function deletePage(p){
  if(pages.length<=1)return;
  const n=cardsPerPage();padOrder();deck.order.splice(p*n,n);
  syncPages();currentPage=Math.min(p,pages.length-1);selected=0;renderSheet();syncControls();
}
function movePage(from,insertIndex){
  const n=cardsPerPage();padOrder();
  const active=currentPage,chunk=deck.order.splice(from*n,n);
  let target=insertIndex;if(from<insertIndex)target--;
  target=clamp(target,0,Math.ceil(deck.order.length/n));
  deck.order.splice(target*n,0,...chunk);
  currentPage=active===from?target:(active>from&&active<=target?active-1:(active<from&&active>=target?active+1:active));
}
el("addPage").addEventListener("click",addPage);
/* ---- フォントの選択 ---- */
document.querySelectorAll("select.font-select[id]").forEach(x=>x.innerHTML=fontOptions(true));
if(el("deckFont")){el("deckFont").innerHTML=fontOptions(false);el("deckFont").addEventListener("change",e=>{deck.font=e.target.value;renderSheet();syncControls()})}
[["playingFont","numberStyle"],["tcgNameFont","nameStyle"],["tcgDescFont","descStyle"],["wordMainFont","mainStyle"]].forEach(([id,key])=>el(id)?.addEventListener("change",e=>{
  updateSelected({[key]:{...(currentFaces()[selected][key]||{}),font:e.target.value}});
}));
/* ---- 設定(単位) ---- */
function applyUnits(){saveUnits();relabelLengths(document);updateFit();syncControls()}
if(el("unitLen")){el("unitLen").value=units.len;el("unitLen").addEventListener("change",e=>{units.len=e.target.value;applyUnits()})}
if(el("unitText")){el("unitText").value=units.text;el("unitText").addEventListener("change",e=>{units.text=e.target.value;applyUnits()})}
function toggleSettings(force){const pop=el("settingsPop");if(!pop)return;const open=force??pop.hidden;pop.hidden=!open;el("settingsBtn")?.setAttribute("aria-expanded",String(open))}
el("settingsBtn")?.addEventListener("click",e=>{e.stopPropagation();toggleSettings()});
document.addEventListener("click",e=>{const pop=el("settingsPop");if(pop&&!pop.hidden&&!e.target.closest("#settingsPop,#settingsBtn"))toggleSettings(false)});
el("dupPage").addEventListener("click",()=>duplicatePage(currentPage));
el("deletePage").addEventListener("click",()=>deletePage(currentPage));

function getProject(){
  padOrder();
  return {app:"card-mock-maker",version:2,paperSize:el("paperSize").value,paperOrientation:el("paperOrientation").value,cardSize:el("cardSize").value,impositionMode:el("impositionMode").value,cardOrientation,sheetTitle,printSettings,deck};
}

function migrateGenericTextBoxes(project){(project.pages||[]).forEach(pg=>pg.forEach(d=>{if(!d)return;if(!Array.isArray(d.textBoxes))d.textBoxes=[];if(!Array.isArray(d.optionImages))d.optionImages=[];if(d.template==="custom"&&d.customTexts&&!d.textBoxes.length){["t1","t2","t3","t4","t5"].forEach((k,i)=>{if(d.customTexts[k])d.textBoxes.push({id:"tb_legacy_"+Date.now()+"_"+i,text:d.customTexts[k],style:(d.customStyles&&d.customStyles[k])||{size:i?14:18,bold:false,italic:false,color:"#222222"},box:(d.customBoxes&&d.customBoxes[k])||{x:20,y:18+i*16,w:60,h:14},centerSnap:false})});delete d.customTexts;delete d.customStyles;delete d.customBoxes;delete d.customCount}if(d.template==="word"&&d.sub){if(d.textBoxes.length<5)d.textBoxes.push({id:"tb_word_"+Date.now(),text:d.sub,style:d.subStyle||{size:12,bold:false,italic:false,color:d.subColor||"#222222"},box:d.subBox||{x:20,y:73,w:60,h:14},centerSnap:false});delete d.sub;delete d.subStyle;delete d.subColor;delete d.subBox}}));return project}


function migrateBgBorders(project){
  (project.pages||[]).forEach(pg=>pg.forEach(d=>{
    if(!d)return;
    if(d.bgBorderColor===undefined){
      if(!(d.type==="template" && d.template==="tcg") && d.borderColor!==undefined){
        d.bgBorderColor=d.borderColor||"#222222";
        d.bgBorderWidth=Number(d.borderWidth)>0?Number(d.borderWidth):1.5;
        d.bgBorderNone=d.borderNone===true || !(Number(d.borderWidth)>0);
      }else{
        d.bgBorderColor="#222222";
        d.bgBorderWidth=1.5;
        d.bgBorderNone=true;
      }
    }
  }));
  return project;
}

/* 古い形式(ページごとの面の配列)を、カードの一覧に直す */
function deckFromPages(list,mode){
  const d={cards:{},order:[]},single=mode==="single";
  const project=migrateBgBorders(migrateGenericTextBoxes({pages:list||[]}));
  (project.pages||[]).slice(0,MAX_PAGES).forEach(pg=>{
    for(let i=0;i<(pg||[]).length;i+=single?1:2){
      const id=newCardId();d.cards[id]={front:pg[i]||makePlain(),back:single?makePlain():(pg[i+1]||makePlain())};d.order.push(id);
    }
  });
  return normalizeDeck(d);
}
function normalizeDeck(d){
  const out={cards:{},order:[],fmt:2,font:(d&&d.font)||"system"};
  (d&&d.order||[]).forEach(id=>{const c=d.cards&&d.cards[id];if(!c)return;if(!out.cards[id])out.cards[id]={front:c.front||makePlain(),back:c.back||makePlain()};out.order.push(id)});
  const faces=Object.values(out.cards).flatMap(c=>[c.front,c.back]);
  migrateBgBorders(migrateGenericTextBoxes({pages:[faces]}));
  Object.values(out.cards).forEach(c=>{const pg=[c.front,c.back];normalizeFaces([pg]);c.front=pg[0];c.back=pg[1]});
  if(!(d&&d.fmt>=2))Object.values(out.cards).forEach(c=>{migrateFaceUnits(c.front);migrateFaceUnits(c.back)});
  return out;
}
function restoreProject(p){
  if(!p.deck&&!p.pages)throw new Error("invalid project");
  deck=p.deck?normalizeDeck(deep(p.deck)):deckFromPages(deep(p.pages),p.impositionMode);
  printSettings={backFlip:"horizontal",backOffsetX:0,backOffsetY:0,...(p.printSettings||{})};
  sheetTitle=p.sheetTitle||"";
  el("paperSize").value=p.paperSize||"a4";el("paperOrientation").value=p.paperOrientation||"landscape";el("cardSize").value=p.cardSize||"poker";el("impositionMode").value=p.impositionMode||"duplex";el("impositionMode").dataset.prev=el("impositionMode").value;cardOrientation=p.cardOrientation||((el("impositionMode").value==="single")?el("paperOrientation").value:(el("paperOrientation").value==="portrait"?"landscape":"portrait"));el("sheetTitleInput").value=sheetTitle;
  currentPage=0;selected=0;lastArrangement=null;syncPages();setupAllColorInputs();
  setPaper();renderSheet();syncControls();
  initHistory();
}
document.addEventListener("click",e=>{if(colorPopup&&!e.target.closest(".color-popup")&&!e.target.closest(".color-trigger"))closeColorPopup()});



function dataUrlToAsset(dataUrl){
  const m=/^data:([^;]+);base64,(.+)$/.exec(dataUrl||"");
  if(!m)return null;
  const mime=m[1],bin=atob(m[2]),bytes=new Uint8Array(bin.length);
  for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);
  let ext="bin";
  if(mime==="image/png")ext="png";
  else if(mime==="image/jpeg")ext="jpg";
  else if(mime==="image/webp")ext="webp";
  else if(mime==="image/svg+xml")ext="svg";
  return {mime,bytes,ext};
}

function bytesToDataUrl(bytes,mime){
  let bin="";
  const chunk=0x8000;
  for(let i=0;i<bytes.length;i+=chunk){
    bin+=String.fromCharCode(...bytes.subarray(i,Math.min(i+chunk,bytes.length)));
  }
  return `data:${mime};base64,${btoa(bin)}`;
}

function externalizeProjectImages(project){
  const clone=deep(project),assets=[],seen=new Map(),keys=new Set(["bgImage","src","suitImage","image"]);
  function walk(obj){
    if(!obj||typeof obj!=="object")return;
    for(const [k,v] of Object.entries(obj)){
      if(keys.has(k) && typeof v==="string" && v.startsWith("data:image/")){
        if(!seen.has(v)){
          const asset=dataUrlToAsset(v);
          if(asset){
            const name=`asset_${String(assets.length+1).padStart(3,"0")}.${asset.ext}`;
            assets.push({name,...asset});
            seen.set(v,name);
          }
        }
        if(seen.has(v)) obj[k]={__pdfAsset:seen.get(v)};
      }else if(v && typeof v==="object"){
        walk(v);
      }
    }
  }
  walk(clone);
  return {project:clone,assets};
}

function hydrateProjectImages(project,attachments){
  const byName=new Map(attachments.map(a=>[a.name,a])),made=new Map();
  function mimeFromName(name){
    const ext=(name.split(".").pop()||"").toLowerCase();
    if(ext==="png")return "image/png";
    if(ext==="jpg"||ext==="jpeg")return "image/jpeg";
    if(ext==="webp")return "image/webp";
    if(ext==="svg")return "image/svg+xml";
    return "application/octet-stream";
  }
  function walk(obj){
    if(!obj||typeof obj!=="object")return;
    for(const [k,v] of Object.entries(obj)){
      if(v && typeof v==="object" && v.__pdfAsset){
        const a=byName.get(v.__pdfAsset);
        if(a){if(!made.has(a.name))made.set(a.name,canonicalImage(bytesToDataUrl(a.data,mimeFromName(a.name))));obj[k]=made.get(a.name)}
      }else if(v && typeof v==="object"){
        walk(v);
      }
    }
  }
  walk(project);
  return project;
}

function showPdfReeditTip(){
  let t=document.querySelector(".pdf-reedit-toast");
  if(!t){t=document.createElement("div");t.className="pdf-reedit-toast";t.textContent="保存したPDFは「PDF読み込み」で再編集できます";document.body.appendChild(t)}
  clearTimeout(showPdfReeditTip.timer);
  requestAnimationFrame(()=>t.classList.add("show"));
  showPdfReeditTip.timer=setTimeout(()=>t.classList.remove("show"),3200);
}
async function buildEditablePdf(){
  if(!window.html2canvas || !window.PDFLib) throw new Error("PDFライブラリを読み込めませんでした。インターネット接続を確認してください。");
  const {PDFDocument}=PDFLib;
  await fontsReady();
  const p=paperMM();
  const ptPerMm=72/25.4;
  const pdf=await PDFDocument.create();

  const staging=document.createElement("div");
  staging.style.position="fixed";staging.style.left="-12000px";staging.style.top="0";
  staging.style.background="#fff";staging.style.zIndex="-1";
  document.body.appendChild(staging);

  try{
    for(const sh of outputSheets()){
      const sheet=makeOutputSheet(sh);
      sheet.style.position="relative";sheet.style.background="#fff";sheet.style.overflow="hidden";
      // Editing-only fold guides must never be rasterized into exported PDFs.
      sheet.querySelectorAll(".fold,.screen-guide").forEach(node=>node.remove());
      staging.appendChild(sheet);

      const canvas=await html2canvas(sheet,{backgroundColor:"#ffffff",scale:2,useCORS:true,logging:false});
      const png=canvas.toDataURL("image/png");
      const img=await pdf.embedPng(png);
      const page=pdf.addPage([p.w*ptPerMm,p.h*ptPerMm]);
      page.drawImage(img,{x:0,y:0,width:p.w*ptPerMm,height:p.h*ptPerMm});
      staging.removeChild(sheet);
    }

    const packed=externalizeProjectImages(getProject());
    const projectBytes=new TextEncoder().encode(JSON.stringify(packed.project));
    await pdf.attach(projectBytes,"card-mock-project.json",{
      mimeType:"application/json",
      description:"Card Mock Maker editable project"
    });
    for(const asset of packed.assets){
      await pdf.attach(asset.bytes,asset.name,{
        mimeType:asset.mime,
        description:"Card Mock Maker image asset"
      });
    }
    pdf.setTitle(sheetTitle||"Card Mock Maker");
    pdf.setSubject("Editable Card Mock Maker PDF");
    pdf.setKeywords(["card-mock-maker","editable-project"]);

    const bytes=await pdf.save();
    const blob=new Blob([bytes],{type:"application/pdf"});
    const a=document.createElement("a");
    a.href=URL.createObjectURL(blob);
    a.download=(sheetTitle||"card-mock")+".pdf";
    a.click();
    setTimeout(()=>URL.revokeObjectURL(a.href),1500);
  }finally{
    staging.remove();
  }
}

function extractPdfAttachments(pdfDoc){
  const {PDFName,PDFDict,PDFArray,PDFStream,decodePDFRawStream}=PDFLib;
  if(!pdfDoc.catalog.has(PDFName.of("Names")))return [];
  const names=pdfDoc.catalog.lookup(PDFName.of("Names"),PDFDict);
  if(!names.has(PDFName.of("EmbeddedFiles")))return [];
  let embedded=names.lookup(PDFName.of("EmbeddedFiles"),PDFDict);
  if(!embedded.has(PDFName.of("Names")) && embedded.has(PDFName.of("Kids"))){
    const kids=embedded.lookup(PDFName.of("Kids"),PDFArray);
    if(kids.size()) embedded=kids.lookup(0,PDFDict);
  }
  if(!embedded.has(PDFName.of("Names")))return [];
  const arr=embedded.lookup(PDFName.of("Names"),PDFArray),out=[];
  for(let i=0;i<arr.size();i+=2){
    const fileName=arr.lookup(i);
    const spec=arr.lookup(i+1,PDFDict);
    const stream=spec.lookup(PDFName.of("EF"),PDFDict).lookup(PDFName.of("F"),PDFStream);
    out.push({name:fileName.decodeText(),data:decodePDFRawStream(stream).decode()});
  }
  return out;
}

el("editablePdfBtn").addEventListener("click",async()=>{
  const btn=el("editablePdfBtn"),old=btn.textContent;
  try{
    btn.disabled=true;btn.textContent="PDF作成中…";
    await buildEditablePdf();
    showPdfReeditTip();
  }catch(e){
    console.error(e);alert(e.message||"PDFの保存に失敗しました。");
  }finally{btn.disabled=false;btn.textContent=old}
});

el("loadPdfBtn").addEventListener("click",()=>el("loadPdf").click());
el("loadPdf").addEventListener("change",async e=>{
  const file=e.target.files[0];if(!file)return;
  try{
    if(!window.PDFLib)throw new Error("PDFライブラリを読み込めませんでした。");
    const bytes=await file.arrayBuffer();
    const pdf=await PDFLib.PDFDocument.load(bytes);
    const atts=extractPdfAttachments(pdf);
    const project=atts.find(x=>x.name==="card-mock-project.json");
    if(!project)throw new Error("このPDFにはCard Mock Makerの編集データがありません。");
    const text=new TextDecoder().decode(project.data);
    const parsed=JSON.parse(text);
    restoreProject(hydrateProjectImages(parsed,atts));
  }catch(err){
    console.error(err);alert(err.message||"PDFを読み込めませんでした。");
  }finally{e.target.value=""}
});

/* ---- 自動保存:このブラウザ内(IndexedDB)に、変更から少しおいて保存。次に開くと続きから ---- */
const AUTOSAVE_DB="card-mock-maker",AUTOSAVE_MS=1200;
let autosaveDb=null,autosaveReady=false,autosaveStopped=false,autosaveFailed=false,autosaveTimer=null,autosaveLastJson=null,autosaveBusy=null;
const autosavedImageIds=new Set();
function idbReq(r){return new Promise((res,rej)=>{r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)})}
function idbDone(tx){return new Promise((res,rej)=>{tx.oncomplete=()=>res();tx.onabort=tx.onerror=()=>rej(tx.error||new Error("transaction failed"))})}
function openAutosaveDb(){
  return new Promise((res,rej)=>{
    if(!window.indexedDB)return rej(new Error("IndexedDB unavailable"));
    const r=indexedDB.open(AUTOSAVE_DB,1);
    r.onupgradeneeded=()=>{const db=r.result;if(!db.objectStoreNames.contains("kv"))db.createObjectStore("kv");if(!db.objectStoreNames.contains("images"))db.createObjectStore("images")};
    r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error);r.onblocked=()=>rej(new Error("IndexedDB blocked"));
  });
}
function scheduleAutosave(){
  if(!autosaveReady||autosaveStopped||autosaveFailed)return;
  clearTimeout(autosaveTimer);autosaveTimer=setTimeout(runAutosave,AUTOSAVE_MS);
}
function writeAutosave(){
  const json=historyState();
  if(json===autosaveLastJson)return Promise.resolve();
  const ids=[...new Set([...json.matchAll(/cmm-img:\/\/([a-z0-9]+)/g)].map(m=>m[1]))];
  const tx=autosaveDb.transaction(["kv","images"],"readwrite"),imgs=tx.objectStore("images");
  ids.forEach(id=>{if(!autosavedImageIds.has(id)){const u=imgUrlById.get(id);if(u)imgs.put(u,id)}});
  tx.objectStore("kv").put({json,ids,savedAt:Date.now(),format:1},"project");
  const keys=imgs.getAllKeys();
  keys.onsuccess=()=>{const keep=new Set(ids);keys.result.forEach(k=>{if(!keep.has(k))imgs.delete(k)})};
  return idbDone(tx).then(()=>{autosavedImageIds.clear();ids.forEach(id=>autosavedImageIds.add(id));autosaveLastJson=json});
}
function runAutosave(){
  clearTimeout(autosaveTimer);autosaveTimer=null;
  if(!autosaveReady||autosaveStopped||autosaveFailed||!autosaveDb)return Promise.resolve();
  const go=()=>writeAutosave().catch(err=>{
    console.warn("autosave failed",err);autosaveFailed=true;
    showAppToast("自動保存できませんでした(ブラウザの保存容量が足りない可能性があります)。こまめに「PDF保存」してください。",{duration:9000});
  });
  autosaveBusy=(autosaveBusy?autosaveBusy.then(go):go()).finally(()=>{});
  return autosaveBusy;
}
function showAppToast(message,{action=null,duration=8000}={}){
  let t=document.querySelector(".app-toast");
  if(!t){t=document.createElement("div");t.className="app-toast";t.setAttribute("role","status");document.body.appendChild(t)}
  t.innerHTML="";const msg=document.createElement("span");msg.textContent=message;t.appendChild(msg);
  if(action){const b=document.createElement("button");b.type="button";b.textContent=action.label;b.addEventListener("click",()=>{t.classList.remove("show");action.run()});t.appendChild(b)}
  const x=document.createElement("button");x.type="button";x.className="app-toast-close";x.setAttribute("aria-label","閉じる");x.textContent="×";x.addEventListener("click",()=>t.classList.remove("show"));t.appendChild(x);
  clearTimeout(showAppToast.timer);requestAnimationFrame(()=>t.classList.add("show"));
  if(duration)showAppToast.timer=setTimeout(()=>t.classList.remove("show"),duration);
}
async function startNewProject(){
  if(!confirm("いまの作業を消して、新しく作りはじめますか？\n(PDF保存していない内容は元に戻せません)"))return;
  autosaveStopped=true;clearTimeout(autosaveTimer);
  try{
    if(autosaveBusy)await autosaveBusy.catch(()=>{});
    if(autosaveDb){const tx=autosaveDb.transaction(["kv","images"],"readwrite");tx.objectStore("kv").clear();tx.objectStore("images").clear();await idbDone(tx)}
  }catch(err){console.warn(err)}
  location.reload();
}
function timeLabel(ms){const d=new Date(ms),p=n=>String(n).padStart(2,"0");const today=new Date().toDateString()===d.toDateString();return (today?"":`${d.getMonth()+1}/${d.getDate()} `)+`${p(d.getHours())}:${p(d.getMinutes())}`}
async function initAutosave(){
  try{
    autosaveDb=await openAutosaveDb();
    const rec=await idbReq(autosaveDb.transaction("kv").objectStore("kv").get("project"));
    const untouched=!undoStack.length&&historyPendingStart===null;
    if(rec&&typeof rec.json==="string"&&untouched){
      const st=autosaveDb.transaction("images").objectStore("images");
      const found=await Promise.all((rec.ids||[]).map(id=>idbReq(st.get(id)).then(u=>[id,u])));
      found.forEach(([id,u])=>{if(typeof u==="string"){internImage(u,id);autosavedImageIds.add(id)}});
      const parsed=JSON.parse(rec.json,unpackImages);
      if((parsed.deck&&parsed.deck.order&&parsed.deck.order.length)||(Array.isArray(parsed.pages)&&parsed.pages.length)){
        applyHistorySnapshot(rec.json);
        initHistory();
        autosaveLastJson=rec.json;
        showAppToast(`前回の続きを開きました(${timeLabel(rec.savedAt||Date.now())}保存)`,{action:{label:"新規",run:startNewProject}});
      }
    }
  }catch(err){console.warn("autosave unavailable",err);autosaveFailed=true}
  autosaveReady=true;
  scheduleAutosave();
}
document.addEventListener("pointerup",()=>scheduleAutosave(),true);
document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="hidden")runAutosave()});
window.addEventListener("pagehide",()=>{runAutosave()});
window.addEventListener("beforeunload",e=>{
  if(autosaveStopped)return;
  if(autosaveReady&&!autosaveFailed){runAutosave();return}
  // 自動保存が使えないときだけ、閉じる前に確認する
  if(undoStack.length||historyPendingStart!==null){e.preventDefault();e.returnValue=""}
});
el("newProjectBtn")?.addEventListener("click",startNewProject);
el("mobileNewProject")?.addEventListener("click",()=>{closeMobilePanel();startNewProject()});

/* 印刷・PDFに出すシートの一覧(両面印刷はページごとにオモテ→ウラの順) */
function outputSheets(){
  const m=layoutMode(),out=[];
  for(let p=0;p<pageCount();p++){
    if(m==="both"){out.push({faces:facesOf(p,"front"),a:"front"});out.push({faces:facesOf(p,"back"),a:"back",back:true})}
    else{const a=m==="fold"?"pairs":"single";out.push({faces:facesOf(p,a),a})}
  }
  return out;
}
function makeOutputSheet(sh){
  const p=paperMM(),sheet=document.createElement("div");
  sheet.className="print-sheet "+(el("paperOrientation").value==="landscape"?"landscape-paper":"portrait-paper");
  sheet.style.width=p.w+"mm";sheet.style.height=p.h+"mm";
  sheet.style.minWidth=p.w+"mm";sheet.style.maxWidth=p.w+"mm";
  sheet.style.minHeight=p.h+"mm";sheet.style.maxHeight=p.h+"mm";
  const title=document.createElement("div");title.className="sheet-title";title.textContent=sh.back?"":sheetTitle;sheet.appendChild(title);
  const sg=document.createElement("div");buildSheet(sg,sh.faces,false,sh.a);sheet.appendChild(sg);
  if(sh.back&&(printSettings.backOffsetX||printSettings.backOffsetY))sg.style.translate=`${Number(printSettings.backOffsetX)||0}mm ${Number(printSettings.backOffsetY)||0}mm`;
  return sheet;
}
function preparePrintPages(){
  const wrap=el("printPages");wrap.innerHTML="";
  outputSheets().forEach(sh=>wrap.appendChild(makeOutputSheet(sh)));
}
function setExactPrintPage(){const p=paperMM(),paperName=el("paperSize").value==="a3"?"A3":"A4",orientation=el("paperOrientation").value;let st=el("printPageStyle");if(!st){st=document.createElement("style");st.id="printPageStyle";document.body.appendChild(st)}st.textContent=`@page{size:${paperName} ${orientation};margin:0}\n@media print{.print-sheet{width:${p.w}mm!important;height:${p.h}mm!important;min-width:${p.w}mm!important;max-width:${p.w}mm!important;min-height:${p.h}mm!important;max-height:${p.h}mm!important}}`}
el("printBtn").addEventListener("click",async()=>{const b=el("printBtn"),t=b.textContent;b.disabled=true;b.textContent="準備中…";try{await fontsReady()}finally{b.disabled=false;b.textContent=t}setExactPrintPage();preparePrintPages();requestAnimationFrame(()=>requestAnimationFrame(()=>window.print()))});



cardOrientation=(el("paperOrientation").value==="portrait")?"landscape":"portrait";
startDeck();
setPaper();renderSheet();syncControls();
initHistory();renderSwatches();
initAutosave();


})();

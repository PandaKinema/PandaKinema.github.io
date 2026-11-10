(() => {
const MM_TO_PX=3.7795275591;
/* 画面の文字は i18n.js が英語に置き換える。alert・confirm・初期値の文字だけはここで訳す */
const T=(s,v)=>window.CMMI18N?CMMI18N.T(s,v):s;

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
const makeTcg=()=>({type:"template",template:"tcg",name:T("カード名"),desc:T("テキスト"),image:null,bgColor:"#ffffff",bgImage:null,bgBorderColor:"#222222",bgBorderWidth:1,bgBorderNone:true,bgBorderAlign:"inside",
  textColor:"#222222",borderColor:"#222222",borderNone:false,panelColor:"#ffffff",horizontalLayout:1,tcgTopHeight:16,tcgMiddleHeight:50,tcgBottomHeight:28,
  nameStyle:{size:SIZE.tcgName,bold:true,italic:false},descStyle:{size:SIZE.tcgDesc,bold:false,italic:false}});
const makeWord=()=>({type:"template",template:"word",main:T("ことば"),mainColor:"#222222",mainStyle:{size:SIZE.word,bold:true,italic:false},bgColor:"#ffffff",bgImage:null,bgBorderColor:"#222222",bgBorderWidth:1,bgBorderNone:true,bgBorderAlign:"inside"});
/* ---- デッキ:カードの一覧(deck.cards)と、印刷する並び(deck.order) ----
   deck.cards[id]={front,back}。deck.order=[id,...] で、同じidが並べば同じカードを複数枚刷る。
   pages は表示用に deck から作り直す配列(中身は各カードの面そのものを指すので、面の中身を直せばカードに反映される)。 */
const MAX_PAGES=25;
let deck={cards:{},order:[]};
let pages=[],currentPage=0,selected=0,sheetTitle="";
let viewSide="front";                 // 両面印刷モードのPC表示:オモテ面/ウラ面
let printSettings={binding:"long",backOffsetX:0,backOffsetY:0};   // binding:プリンタの両面設定(長辺とじ/短辺とじ)
let lastArrangement=null,lastN=null;
function newCardId(){return "c"+Date.now().toString(36)+Math.random().toString(36).slice(2,7)}
function newCardFaces(){return {front:makePlain(),back:makePlain()}}
function addCard(front,back){const id=newCardId(),d=newCardFaces();deck.cards[id]={front:front||d.front,back:back||d.back};return id}

const el=id=>document.getElementById(id);
const paper=el("paper"),grid=el("sheetGrid");

const CARD_SIZES={
  poker:{label:"ポーカー",w:63,h:88},
  bridge:{label:"ブリッジ",w:58,h:89},
  business:{label:"名刺",w:55,h:91},
  yugioh:{label:"遊戯王サイズ",w:59,h:86},
  credit:{label:"クレジット",w:54,h:86},
  half:{label:"ハーフ",w:44,h:63},
  mini:{label:"ミニ",w:41,h:63},
  minieuro:{label:"ミニユーロ",w:44,h:68},
  tarot:{label:"タロット",w:70,h:120},
  square:{label:"スクエア",w:70,h:70}
};
/* 自由な大きさ(mm)。向きは用紙に合わせて回すので、幅≦高さにそろえて持つ */
let customCard={w:63,h:88};
function normCustom(c){const w=Number(c&&c.w),h=Number(c&&c.h);if(!(w>0&&h>0))return {w:63,h:88};return {w:Math.min(w,h),h:Math.max(w,h)}}
function cardMM(){const v=el("cardSize")?.value;if(v==="custom")return {label:"自由",w:customCard.w,h:customCard.h};return CARD_SIZES[v]||CARD_SIZES.poker}
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
/* 両面印刷のウラ面:紙を裏返したとき重なるよう、左右(または上下)を入れ替えた位置に置く。
   紙は「長辺とじ」なら長い辺、「短辺とじ」なら短い辺を軸に裏返る。縦の紙の長辺とじ・横の紙の短辺とじは左右に裏返る */
function backFlipDir(){const land=el("paperOrientation")?.value==="landscape",long=printSettings.binding!=="short";return long!==land?"horizontal":"vertical"}
function backIndex(i){const g=gridRC(),r=Math.floor(i/g.cols),c=i%g.cols;return backFlipDir()==="vertical"?(g.rows-1-r)*g.cols+c:r*g.cols+(g.cols-1-c)}
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
/* ---- 枚数:同じカード(同じid)を並びに何回入れるか。増やすとすぐ後ろに並び、後ろのカードは詰め直す ---- */
function setCardCount(id,n){
  const cur=cardCount(id);n=Math.max(1,Math.round(Number(n)||1));if(n===cur||!deck.cards[id])return false;
  const first=deck.order.indexOf(id),side=slotAt(currentPage,selected).side;
  if(n>cur){
    let add=n-cur,room=MAX_PAGES*cardsPerPage()-deck.order.length;
    // 最後に残っている空のカードは、増やした分だけ詰めて使う(ページ数がむやみに増えないように)
    let trim=0;for(let k=deck.order.length-1;k>deck.order.lastIndexOf(id)&&trim<add;k--){const x=deck.order[k];if(isBlankCard(x)&&cardCount(x)===1)trim++;else break}
    if(add>room+trim){add=room+trim;if(add<=0){alert(T("これ以上カードを増やせません（最大{n}ページ）",{n:MAX_PAGES}));return false}}
    deck.order.splice(deck.order.length-trim,trim);
    deck.order.splice(deck.order.lastIndexOf(id)+1,0,...Array(add).fill(id));
  }else{
    let rm=cur-n;for(let k=deck.order.length-1;k>first&&rm>0;k--)if(deck.order[k]===id){deck.order.splice(k,1);rm--}
  }
  syncPages();selectSlot(first,side);return true;
}
/* 枚数が2枚以上のカードのうち、選んでいる1枚だけを別のカードにする */
function unlinkSelected(){
  const {slot}=slotAt(currentPage,selected),id=deck.order[slot];if(cardCount(id)<2)return;
  deck.order[slot]=cloneCard(deck.cards[id]);syncPages();
}
/* ---- マイテンプレート ----
   deck.templates[tid]={name,front,back,lib}。カードは deck.cards[id].tpl=tid でテンプレートにつながる。
   つながったカードのどれかで見た目(色・大きさ・配置・画像)を変えると、テンプレートと同じテンプレートのカードすべてに反映する。
   文字(と、トレカの絵・画像の面の画像)はカードごと。lib=true は、このブラウザにも保存しているもの */
const CONTENT_KEYS={playing:["number","suit"],tcg:["name","desc","image","imageFit"],word:["main"]};
function faceKindOf(f){return !f?"":f.type==="template"?"t:"+f.template:f.type}
function contentKeys(f){return !f?[]:f.type==="template"?(CONTENT_KEYS[f.template]||[]):f.type==="image"?["src","srcFit"]:[]}
function styleOf(f){
  if(!f)return "";
  const o={...f};contentKeys(f).forEach(k=>delete o[k]);
  ["textBoxes","frameTexts"].forEach(k=>{if(Array.isArray(o[k]))o[k]=o[k].map(x=>{const y={...x};delete y.text;return y})});
  ["optionImages","shapes"].forEach(k=>{if(Array.isArray(o[k]))o[k]=o[k].map(x=>{const y={...x};delete y.count;return y})});   // 個数はカードごと
  return JSON.stringify(o,packImages);
}
/* 見た目は src から、文字は dst のまま(テキストボックスなどは id で対応づける) */
function restyleFace(src,dst){
  const out=deep(src);
  if(dst&&faceKindOf(dst)===faceKindOf(src))contentKeys(src).forEach(k=>{if(dst[k]!==undefined)out[k]=dst[k]===null?null:deep(dst[k])});
  ["textBoxes","frameTexts"].forEach(k=>(out[k]||[]).forEach((x,i)=>{const list=(dst&&dst[k])||[],d=x.id!=null?list.find(y=>y&&y.id===x.id):list[i];if(d&&d.text!==undefined)x.text=d.text}));
  ["optionImages","shapes"].forEach(k=>(out[k]||[]).forEach((x,i)=>{const list=(dst&&dst[k])||[],d=x.id!=null?list.find(y=>y&&y.id===x.id):list[i];if(d)x.count=d.count;else delete x.count}));
  return out;
}
function tplCount(tid){let n=0;for(const id of deck.order)if(deck.cards[id]&&deck.cards[id].tpl===tid)n++;return n}
function cloneCard(c){const id=addCard(deep(c.front),deep(c.back));if(c.tpl)deck.cards[id].tpl=c.tpl;return id}
function newTplId(){return "t"+Date.now().toString(36)+Math.random().toString(36).slice(2,6)}
function uniqueTplName(base){const used=new Set([...Object.values(deck.templates||{}),...myLibrary].map(t=>t.name));if(!used.has(base))return base;for(let i=2;;i++)if(!used.has(`${base} ${i}`))return `${base} ${i}`}
function suggestTplName(card){const f=card&&card.front,k=f&&f.type==="template"?f.template:"";return T(k==="tcg"?"トレカ":k==="playing"?"トランプ":k==="word"?"ワードゲーム":"テンプレート")}
function addTemplate(card,name,lib){deck.templates=deck.templates||{};const tid=newTplId();deck.templates[tid]={name,front:deep(card.front),back:deep(card.back),lib:!!lib};return tid}
/* テンプレートをカードに当てる:見た目はテンプレート、文字はそのカードのまま(空のカードならテンプレートの文字) */
function applyTemplate(tid,id){const t=deck.templates[tid],c=deck.cards[id];c.front=restyleFace(t.front,c.front);c.back=restyleFace(t.back,c.back);c.tpl=tid}
/* 選んでいる面の見た目が変わったら(=見た目を直したら)、同じテンプレートのカードへ広げる */
let tplWatch=null,tplNotice=null;
function propagateTemplateStyle(){
  if(!pages.length)return;
  const ref=slotAt(currentPage,selected),id=deck.order[ref.slot],card=deck.cards[id];if(!card)return;
  const t=card.tpl&&deck.templates&&deck.templates[card.tpl];
  if(card.tpl&&!t)delete card.tpl;
  const src=card[ref.side],key=styleOf(src),prev=tplWatch;tplWatch={id,side:ref.side,key};
  if(!t||!prev||prev.id!==id||prev.side!==ref.side||prev.key===key||key===styleOf(t[ref.side]))return;
  // 面の種類を変えたカードは、別のカードになったものとしてテンプレートから外す
  if(faceKindOf(src)!==faceKindOf(t[ref.side])){delete card.tpl;tplNotice=T("面の種類を変えたので、このカードはテンプレート「{name}」から外れました。",{name:t.name});return}
  t[ref.side]=restyleFace(src,t[ref.side]);
  for(const cid in deck.cards){const c=deck.cards[cid];if(cid!==id&&c.tpl===card.tpl)c[ref.side]=restyleFace(src,c[ref.side])}
  syncPages();
  if(t.lib)scheduleLibrarySync(card.tpl);
}
function startDeck(){deck={cards:{},order:[],templates:{},fmt:2,font:"gothic"};tplWatch=null;startDismissed=false;currentPage=0;selected=0;padOrder();syncPages()}
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
function makeTextBox(i=0){return {id:"tb_"+Date.now()+"_"+Math.random().toString(36).slice(2,7),text:T("テキスト"),style:{size:SIZE.text,bold:false,italic:false,underline:false,color:"#222222",colorNone:false},box:{x:20,y:18+i*16,w:60,h:14},centerSnap:false}}
function ensureFrameTexts(d){if(!Array.isArray(d.frameTexts))d.frameTexts=[];return d.frameTexts}
function makeFrameText(i=0){return {id:"ft_"+Date.now()+"_"+Math.random().toString(36).slice(2,7),text:T("枠つき文字"),style:{size:SIZE.frame,bold:false,italic:false,underline:false,color:"#222222",colorNone:false},borderColor:"#222222",borderNone:false,borderWidth:1,fillColor:"#ffffff",fillNone:false,box:{x:18,y:22+i*14,w:64,h:18},centerSnap:false}}
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
    if(selectable){div.dataset.edit=div.dataset.part="tb:"+item.id;const h=document.createElement("div");h.className="resize-handle";div.appendChild(h);enableGenericTextBox(div,idx,item.id)}
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
    if(selectable){div.dataset.edit=div.dataset.part="ft:"+item.id;const h=document.createElement("div");h.className="resize-handle";div.appendChild(h);enableFrameText(div,idx,item.id)}
    faceEl.appendChild(div);
  });
}
/* ---- 個数:同じ画像・図形を、1個の大きさのままN個並べる(パーツの枠は1個ぶん。中央そろえなら枠を中心に並ぶ) ---- */
const REP_GAP=1.15;   // 1個の大きさに対する間隔
function repCount(item){return clamp(parseInt(item&&item.count)||1,1,20)}
function repCells(item,inner){
  const n=repCount(item);if(n<2)return inner;
  const flow=item.flow||"row-center",col=flow.startsWith("col"),center=flow.endsWith("center"),K=clamp(parseInt(item.wrap)||0,0,20)||n;let h="";
  for(let i=0;i<n;i++){const line=Math.floor(i/K),j=i%K,len=Math.min(K,n-line*K),pos=center?j-(len-1)/2:j,a=pos*REP_GAP*100,b=line*REP_GAP*100;
    h+=`<div class="rep-cell" style="left:${col?b:a}%;top:${col?a:b}%">${inner}</div>`}
  return h;
}
function renderOptionImages(faceEl,d,selectable=false,idx=-1){
  ensureOptionImages(d).forEach((item,n)=>{if(!item.src)return;const b=item.box||{x:30,y:28+n*5,w:40,h:30};const div=document.createElement("div");div.className="option-image"+(selectable?" editable":"")+(repCount(item)>1?" rep":"");div.style.left=b.x+"%";div.style.top=b.y+"%";div.style.width=b.w+"%";div.style.height=b.h+"%";div.style.transform=`rotate(${Number(item.rotation)||0}deg)`;div.innerHTML=repCells(item,`<img src="${item.src}" alt="">`);if(selectable){div.dataset.part="img:"+item.id;div.innerHTML+=`<div class="resize-handle"></div><div class="rotate-handle"></div>`;enableOptionImage(div,idx,item.id)}faceEl.appendChild(div)})
}
function renderShapes(faceEl,d,selectable=false,idx=-1){
  ensureShapes(d).forEach(item=>{const b=item.box||{x:30,y:30,w:38,h:38},div=document.createElement("div");div.className="option-shape"+(selectable?" editable":"");div.style.left=b.x+"%";div.style.top=b.y+"%";div.style.width=b.w+"%";div.style.aspectRatio="1 / 1";
    let tag=item.type==="circle"?'<ellipse cx="50" cy="50" rx="46" ry="46"/>':item.type==="rect"?'<rect x="4" y="4" width="92" height="92"/>':`<polygon points="${shapePoints(item.type,item.points)}"/>`;
    const sw=Math.max(.1,Number(item.borderWidth)||1), align=item.borderAlign||"inside"; let svgStroke=sw*MM_TO_PX; if(align==="inside")svgStroke*=2; else if(align==="outside")svgStroke*=2;
    if(repCount(item)>1)div.classList.add("rep");
    div.innerHTML=repCells(item,`<svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet"><g fill="${item.fillNone?'none':item.fillColor||'#fff'}" stroke="${item.borderNone?'none':item.borderColor||'#222'}" stroke-width="${svgStroke}" vector-effect="non-scaling-stroke">${tag}</g></svg>`)+(selectable?'<div class="resize-handle"></div>':'');
    if(selectable){div.dataset.part="shape:"+item.id;enableShape(div,idx,item.id)}faceEl.appendChild(div)})
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
  node.addEventListener("pointerdown",e=>{if(node.isContentEditable)return;if(e.target!==handle)down(e,"move")});handle.addEventListener("pointerdown",e=>down(e,"resize"));
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
  node.addEventListener("pointerdown",e=>{if(node.isContentEditable)return;if(e.target!==handle)down(e,"move")});handle.addEventListener("pointerdown",e=>down(e,"resize"));
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
    catch(err){console.error(err);alert(T("画像を読み込めませんでした。"))}
    finally{e.target.value=""}
  });
}

/* 面の種類やテンプレートを切り替えても引き継ぐもの(背景・線・オプション) */
function keepCommon(old){
  return {bgColor:old.bgColor||"#ffffff",bgNone:!!old.bgNone,bgImage:old.bgImage||null,bgFit:old.bgFit||null,
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
  const cs=el("cardSize");
  if(cs){const o=cs.querySelector('option[value="custom"]');if(o)o.textContent=`${T("自由")} (${fmtLen(customCard.w,false)}×${fmtLen(customCard.h,false)}${units.len==="mm"?"":" "+LEN_UNITS[units.len].label})`}
  if(cs)[...cs.options].forEach(o=>{const c=CARD_SIZES[o.value];if(!c)return;o.textContent=`${c.label} (${fmtLen(c.w,false)}×${fmtLen(c.h,false)}${units.len==="mm"?"":" "+LEN_UNITS[units.len].label})`});
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
  if(d.suitMode!=="image"&&!d.suit)return "";   // スート「なし」:マークを出さない(数字の位置はそのまま)
  const size=d.suitSize||"medium",count=clamp(Number(d.suitCount)||1,1,5);
  const one=()=>d.suitMode==="image"&&d.suitImage?`<img class="suit-img ${size}" src="${d.suitImage}" alt="">`:`<span class="suit-text ${size}">${esc(d.suit||"")}</span>`;
  return `<span class="suit-stack">${Array.from({length:count},one).join("")}</span>`;
}
function cornerVisible(pos,key){pos=pos||"four";if(pos==="top")return key==="tl"||key==="tr";if(pos==="diagRight")return key==="tr"||key==="bl";if(pos==="diagLeft")return key==="tl"||key==="br";return true}

/* ---- 文字のはみ出し:枠に入りきらない文字は自動で小さくする(作品の設定でオフにできる)。
   小さくしても入らないときは、画面だけ赤い点線で知らせる(印刷・PDF・画像には出ない) ---- */
const FIT_SEL=".tcg-name,.tcg-desc,.word-main,.generic-textbox,.frame-text";
const fitBase=new WeakMap();
const fitCache=new Map();   // 同じ文字・同じ枠・同じ書体なら、合わせた大きさを使い回す(用紙とページ一覧のカードで同じ計算をしない)
function fitTexts(root,mark=true){
  if(!root)return;
  const auto=deck.autoFit!==false;
  const list=[...root.querySelectorAll(FIT_SEL)].filter(n=>!n.isContentEditable);if(!list.length)return;
  // 1) まとめて元の大きさに戻し、つまみを隠す(書き込みだけ)
  const hs=[...root.querySelectorAll(".resize-handle,.rotate-handle")];hs.forEach(h=>h.style.display="none");
  list.forEach(n=>{if(fitBase.has(n))n.style.fontSize=fitBase.get(n);else fitBase.set(n,n.style.fontSize||"")});
  // 2) まとめて読む(レイアウトは1回)
  const items=list.map(n=>{
    if(!n.clientWidth&&!n.clientHeight)return null;   // まだ画面に並んでいない
    const cs=getComputedStyle(n);
    const key=[auto?1:0,n.className.replace(/\b(text-over|part-active|bar-target|inline-editing)\b/g,"").trim(),cs.fontSize,cs.fontFamily,cs.fontWeight,cs.lineHeight,cs.letterSpacing,cs.writingMode,n.clientWidth,n.clientHeight,n.textContent].join("|");
    return {n,key,hit:fitCache.get(key),base:parseFloat(cs.fontSize)||12};
  }).filter(Boolean);
  // 3) はじめて見る組み合わせだけ、実際に入るかを確かめて合わせる
  items.forEach(it=>{
    if(it.hit)return;const n=it.n;
    const over=()=>n.scrollHeight>n.clientHeight+1||n.scrollWidth>n.clientWidth+1;
    let o=over(),fs=null;
    if(o&&auto){let lo=it.base*.4,hi=it.base;for(let i=0;i<8;i++){const mid=(lo+hi)/2;n.style.fontSize=mid+"px";if(over())hi=mid;else lo=mid}fs=lo;n.style.fontSize=lo+"px";o=over()}
    it.hit={fs,o};if(fitCache.size>6000)fitCache.clear();fitCache.set(it.key,it.hit);it.done=true;
  });
  // 4) 使い回しの分を書き込む
  items.forEach(it=>{if(!it.done&&it.hit.fs!=null)it.n.style.fontSize=it.hit.fs+"px";if(mark)it.n.classList.toggle("text-over",it.hit.o)});
  hs.forEach(h=>h.style.display="");
}
let fitQueue=new Set(),fitRaf=0;
function queueFit(faceEl){fitQueue.add(faceEl);if(!fitRaf)fitRaf=requestAnimationFrame(flushFit)}
function flushFit(){fitRaf=0;const q=fitQueue;fitQueue=new Set();q.forEach(f=>{if(f.isConnected)fitTexts(f)});syncOverNote()}
function syncOverNote(){
  const note=el("overNote");if(!note)return;
  const f=document.querySelector(mobileUIActive()?"#mobileCardPair .face.selected":"#sheetGrid .face.selected");
  const o=!!(f&&f.querySelector(".text-over"));note.hidden=!o;
  if(o)note.querySelector("span").textContent=deck.autoFit===false
    ?T("文字が枠からはみ出しています(赤い点線)。文字を減らすか小さくするか、「自動で小さくする」をオンにしてください。")
    :T("文字が枠に入りきりません(赤い点線)。文字を減らすか、枠を大きくしてください。");
  el("overAutoOn").hidden=deck.autoFit!==false;
}
function renderFace(faceEl,d,selectable=false,idx=-1){renderFaceInner(faceEl,d,selectable,idx);queueFit(faceEl)}
/* ---- 画像の位置と大きさ:{x,y}は見せたい場所(0〜100%)、zは拡大(1〜4倍)。切り抜きはいつも枠いっぱい ---- */
const FIT_KEYS={image:"imageFit",src:"srcFit",bg:"bgFit"};
function normFit(f){return {x:clamp(f&&f.x!=null?Number(f.x):50,0,100),y:clamp(f&&f.y!=null?Number(f.y):50,0,100),z:clamp(f&&f.z?Number(f.z):1,1,4)}}
function applyImgFit(img,fit){
  img.style.objectPosition=img.style.transformOrigin=img.style.transform="";
  if(!fit)return;const {x,y,z}=normFit(fit);if(z===1&&x===50&&y===50)return;
  img.style.objectPosition=`${x}% ${y}%`;img.style.transformOrigin=`${x}% ${y}%`;if(z!==1)img.style.transform=`scale(${z})`;
}
function renderFaceInner(faceEl,d,selectable=false,idx=-1){
  faceEl.innerHTML="";
  faceEl.classList.toggle("can-pan",!!selectable&&((d.type==="image"&&!!d.src)||!!d.bgImage));
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
    bg.style.pointerEvents="none";bg.className="face-bg-img";applyImgFit(bg,d.bgFit);
    faceEl.appendChild(bg);
  }

  if(d.type==="plain"){renderGenericTextBoxes(faceEl,d,selectable,idx);return;}
  if(d.type==="image"){
    if(d.src){const img=document.createElement("img");img.src=d.src;img.className="face-src-img";img.style.width="100%";img.style.height="100%";img.style.objectFit="cover";img.style.position="relative";img.style.zIndex="1";applyImgFit(img,d.srcFit);faceEl.appendChild(img)}
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
    const ed=k=>selectable?` data-edit="${k}"`:"";
    wrap.innerHTML=`<div class="tcg-name"${ed("name")} style="${ns.font?`font-family:${fontCss(ns.font)};`:""}font-size:${ns.size||SIZE.tcgName}pt;font-weight:${ns.bold?700:400};font-style:${ns.italic?"italic":"normal"};text-decoration:${ns.underline?"underline":"none"}">${d.name?esc(d.name):'<span class="ph">カード名</span>'}</div>
      <div class="tcg-image"${selectable?' data-drop="image"':""}>${d.image?`<img src="${d.image}">`:'<span class="ph">画像</span>'}</div>
      <div class="tcg-desc"${ed("desc")} style="${ds.font?`font-family:${fontCss(ds.font)};`:""}font-size:${ds.size||SIZE.tcgDesc}pt;font-weight:${ds.bold?700:400};font-style:${ds.italic?"italic":"normal"};text-decoration:${ds.underline?"underline":"none"}">${d.desc?esc(d.desc):'<span class="ph">テキスト</span>'}</div>`;
    {const ti=wrap.querySelector(".tcg-image img");if(ti)applyImgFit(ti,d.imageFit)}
    faceEl.appendChild(wrap);renderGenericTextBoxes(faceEl,d,selectable,idx);return
  }

  if(d.template==="word"){
    const wrap=document.createElement("div");wrap.className="word-card";
    // 縦長のカードは縦書き。ただし日本語を含まない言葉(英単語など)は1文字ずつ縦に並ぶと読みにくいので横書き
    const jp=/[\u3000-\u30ff\u3400-\u9fff\uf900-\ufaff\uff01-\uff9f]/.test(String(d.main??""));
    const main=document.createElement("div");main.className="word-main"+(!isLandscapeCard()&&jp?" vertical":"");if(selectable)main.dataset.edit="main";
    const ms=d.mainStyle||{size:SIZE.word,bold:true,italic:false};main.style.fontSize=(ms.size||SIZE.word)+"pt";if(ms.font)main.style.fontFamily=fontCss(ms.font);main.style.fontWeight=ms.bold?800:400;main.style.fontStyle=ms.italic?"italic":"normal";main.style.textDecoration=ms.underline?"underline":"none";main.style.color=d.mainColorNone?"transparent":(d.mainColor||d.color||"#222222");if(d.main)main.textContent=d.main;else main.innerHTML='<span class="ph">ことば</span>';
    wrap.appendChild(main);faceEl.appendChild(wrap);renderGenericTextBoxes(faceEl,d,selectable,idx);return
  }

  if(d.template==="custom"){
    const wrap=document.createElement("div");wrap.className="custom-card";faceEl.appendChild(wrap);renderGenericTextBoxes(faceEl,d,selectable,idx);return
  }

  const wrap=document.createElement("div");wrap.className="card-template";
  if(d.numberStyle?.font)wrap.style.fontFamily=fontCss(d.numberStyle.font);
  const nc=d.numberColorNone?"transparent":(d.numberColor||d.color||"#d94a4a"),ed=selectable?' data-edit="number"':"";
  wrap.innerHTML=`
    ${cornerVisible(d.cornerPlacement,"tl")?`<div class="corner tl"${ed} style="color:${nc}">${esc(d.number||"")}${renderSuitHTML(d)}</div>`:""}
    ${cornerVisible(d.cornerPlacement,"tr")?`<div class="corner tr"${ed} style="color:${nc}">${esc(d.number||"")}${renderSuitHTML(d)}</div>`:""}
    ${cornerVisible(d.cornerPlacement,"bl")?`<div class="corner bl"${ed} style="color:${nc}">${esc(d.number||"")}${renderSuitHTML(d)}</div>`:""}
    ${cornerVisible(d.cornerPlacement,"br")?`<div class="corner br"${ed} style="color:${nc}">${esc(d.number||"")}${renderSuitHTML(d)}</div>`:""}
    <div class="center-num"${ed} style="color:${nc};font-size:${d.numberStyle?.size||SIZE.number}pt;font-weight:${d.numberStyle?.bold===false?400:800};font-style:${d.numberStyle?.italic?"italic":"normal"};text-decoration:${d.numberStyle?.underline?"underline":"none"}">${esc(d.number||"")}</div>`;
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
    cardSize:el("cardSize").value==="custom-edit"?(el("cardSize").dataset.prev||"poker"):el("cardSize").value,   // 「サイズを入力…」は選んだ瞬間に元へ戻すので記録しない
    customCard,
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
  customCard=normCustom(st.customCard);el("cardSize").value=st.cardSize||"poker";el("cardSize").dataset.prev=el("cardSize").value;relabelLengths();
  el("impositionMode").value=st.impositionMode||"duplex";el("impositionMode").dataset.prev=el("impositionMode").value;cardOrientation=st.cardOrientation||((el("impositionMode").value!=="duplex")?el("paperOrientation").value:(el("paperOrientation").value==="portrait"?"landscape":"portrait"));
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
      const idx=paired?c*2+side:(a==="pairs"?c*2:c),f=document.createElement("div");
      f.className="face"+(selectable&&idx===selected?" selected":"");if(selectable)f.dataset.idx=idx;
      if(selectable&&paired&&idx===selected)f.dataset.sideLabel=T(side===0?"オモテ面":"ウラ面");
      renderFace(f,faces[idx],selectable&&idx===selected,idx);
      if(selectable&&(side===0||!paired)){const n=cardCount(cardIdAt(currentPage,idx));if(n>1){const q=document.createElement("span");q.className="qty-badge";q.textContent="×"+n;f.appendChild(q)}}
      if(selectable) f.addEventListener("click",()=>{if(selected===idx)return;selected=idx;renderSheet();syncControls();inlineHint()});   // 選んであるカードを押しても描き直さない(ダブルクリックで直すため)
      pair.appendChild(f);
    }
    if(paired){const fold=document.createElement("div");fold.className="fold screen-guide";pair.appendChild(fold);}
    container.appendChild(pair);
  }
}

function renderSheet(){
  if(inlineEdit)finishInlineEdit(false);   // 入力中に描き直すときは、打った文字を先に反映
  syncPages();
  propagateTemplateStyle();
  if(tplNotice){showAppToast(tplNotice,{duration:5000});tplNotice=null}
  recordHistory();
  const blank=deck.order.every(isBlankCard);
  ["emptyHint","mobileEmptyHint"].forEach(id=>{if(el(id))el(id).hidden=!blank||!startDismissed});
  syncStartChooser(blank);
  el("sheetTitle").textContent=sheetTitle;
  buildSheet(grid,currentFaces(),true);
  markActivePart();
  setBackOffset(grid,layoutMode()==="both"&&arrangement()==="back");
  el("pageCount").textContent=`${currentPage+1} / ${pages.length}`;
  el("addPage").disabled=pages.length>=MAX_PAGES;
  el("dupPage").disabled=pages.length>=MAX_PAGES;
  el("deletePage").disabled=pages.length<=1;
  throttleSidebar();
  renderMobileCardPreview();
  flushFit();   // 見えている用紙のカードは、描いたその場で文字の大きさを合わせる
  {const d=currentFaces()[selected];if(d)syncImgFit(d)}   // 画像を入れたらすぐ「大きさ・左右・上下」を出す
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
  document.body.classList.remove("m-panel-open","m-panel-full");
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
  dismissStart();   // スマホでパネルを開いたら、最初の画面は閉じて無地から
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
    [[ "mobileFacePanelBody",[".face-section","#imageControls","#faceStyleFold","#faceToolsFold"]],
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
window.matchMedia("(max-width:720px)").addEventListener("change",()=>{cloneControlsForMobile();fitPaper();renderMobileCardPreview()});

/* パネルはカードのすぐ下からタブの上までを使う(狭い画面でも最低220pxは確保) */
function placeMobilePanel(){
  if(!mobileUIActive())return;
  const labels=document.querySelector(".mobile-face-labels"),pair=el("mobileCardPair"),bar=el("mobileQuickBar");
  const sheetFrame=mobileSheetMode?document.querySelector("#mobileSheetView .m-sheet-frame"):null;
  const ref=sheetFrame||((labels&&labels.offsetParent)?labels:pair);if(!ref||!bar)return;
  const barTop=bar.getBoundingClientRect().top;
  const hb=document.querySelector("header")?.getBoundingClientRect().bottom||56;
  const top=document.body.classList.contains("m-panel-full")?Math.round(hb+8):Math.max(56,Math.min(ref.getBoundingClientRect().bottom+8,barTop-8-220));   // 上に引き上げたときは画面いっぱい
  document.documentElement.style.setProperty("--m-panel-top",Math.round(top)+"px");
  document.documentElement.style.setProperty("--m-panel-bottom",Math.round(innerHeight-barTop+8)+"px");
}
window.addEventListener("resize",placeMobilePanel);
/* パネルの上の取っ手:下に引くと閉じる、上に引くと画面いっぱいに広がる(広げたあと下に引くと元の大きさ) */
function setPanelFull(on){document.body.classList.toggle("m-panel-full",!!on);placeMobilePanel()}
document.querySelectorAll(".mobile-tool-panel").forEach(p=>{
  const head=p.querySelector(".mobile-panel-head");if(!head)return;
  const g=document.createElement("div");g.className="m-grab";g.setAttribute("aria-hidden","true");head.prepend(g);
  let st=null;
  head.addEventListener("pointerdown",e=>{if(e.target.closest("button"))return;st={id:e.pointerId,y:e.clientY,t:Date.now(),dy:0};try{head.setPointerCapture(e.pointerId)}catch(_){}});
  head.addEventListener("pointermove",e=>{if(!st||e.pointerId!==st.id)return;st.dy=e.clientY-st.y;p.style.transition="none";p.style.transform=`translateY(${st.dy>0?st.dy:st.dy*.3}px)`});
  const end=e=>{
    if(!st||e.pointerId!==st.id)return;const s=st;st=null;const fast=Date.now()-s.t<260;p.style.transition="transform .18s ease";
    if(s.dy>70||(fast&&s.dy>28)){
      if(document.body.classList.contains("m-panel-full")){setPanelFull(false);p.style.transform=""}
      else{p.style.transform="translateY(105%)";setTimeout(()=>{p.style.transition="";p.style.transform="";closeMobilePanel()},170)}
    }else if(s.dy<-45||(fast&&s.dy<-22)){setPanelFull(true);p.style.transform=""}
    else p.style.transform="";
  };
  head.addEventListener("pointerup",end);head.addEventListener("pointercancel",end);
});

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
  const both=layoutMode()==="both",sa=isPairLayout()?"pairs":(both&&viewSide==="back"?"back":"front");
  if(both){
    const seg=document.createElement("div");seg.className="seg m-view-side";seg.setAttribute("role","group");
    seg.innerHTML=["front","back"].map(v=>`<button type="button" data-view-side="${v}" aria-pressed="${(viewSide==="back")===(v==="back")}">${esc(T(v==="back"?"ウラ面":"オモテ面"))}</button>`).join("");
    seg.addEventListener("click",e=>{const b=e.target.closest("[data-view-side]");if(b){viewSide=b.dataset.viewSide;renderMobileSheet()}});
    host.appendChild(seg);
  }
  const sg=document.createElement("div");buildSheet(sg,facesOf(currentPage,sa),false,sa);sheet.appendChild(sg);
  setBackOffset(sg,sa==="back");
  frame.appendChild(sheet);host.appendChild(frame);
  const slotOf=i=>sa==="back"?backIndex(i):i;
  const cur=arrangement()==="pairs"?Math.floor(selected/2):selected;
  sg.querySelectorAll(".pair").forEach((pair,i)=>{
    if(slotOf(i)===cur)pair.classList.add("m-current");
    pair.addEventListener("click",()=>{const k=slotOf(i);selected=arrangement()==="pairs"?k*2+(sa==="back"?1:selected%2):k;setMobileSheetMode(false);syncControls()});
  });
  // 幅いっぱい、ただし下のバー(パネルを開いていればパネル)にかからない大きさに
  const bar=el("mobileQuickBar"),top=frame.getBoundingClientRect().top;
  const limit=(bar?bar.getBoundingClientRect().top:innerHeight)-(mobilePanelOpen?228:12);
  const k=Math.max(.1,Math.min(host.clientWidth/W,(limit-top)/H));
  sheet.style.transform=`scale(${k})`;frame.style.width=W*k+"px";frame.style.height=H*k+"px";
}
function goToMobilePage(delta){
  if(delta>0&&currentPage>=pages.length-1){if(pages.length<MAX_PAGES){const keep=selected;el("addPage").click();selected=keep;renderSheet();syncControls()}return}
  currentPage=clamp(currentPage+delta,0,pages.length-1);renderSheet();syncControls();
}

function rescaleMobileFaces(){
  sizeOneFace();
  document.querySelectorAll("#mobileCardPair .m-face-inner").forEach(n=>{const w=n.parentElement.clientWidth;if(w){const k=w/parseFloat(n.style.width);n.style.transform=`scale(${k})`;n.style.setProperty("--m-inv",String(1/k))}});
}
/* 1枚の面を、カードの上下の空きに収まるいちばん大きな大きさにする(パネルを開いたら、パネルの上に収まる大きさ) */
function sizeOneFace(){
  const host=el("mobileCardPair");if(!host||!mobileUIActive()||mobileSheetMode)return;
  const f=host.querySelector(".face");if(!f)return;
  const fm=faceMM(),ratio=fm.w/fm.h,vw=document.documentElement.clientWidth;
  const top=host.getBoundingClientRect().top,seg=document.querySelector(".mobile-face-labels");
  const segH=seg&&seg.style.display!=="none"?56:14,barTop=el("mobileQuickBar")?.getBoundingClientRect().top||innerHeight;
  const maxH=mobilePanelOpen?Math.max(130,Math.min(innerHeight*.3,300)):Math.max(160,barTop-top-segH-6);
  const w=Math.min(vw-40,560,maxH*ratio),h=w/ratio;
  f.style.setProperty("width",Math.floor(w)+"px","important");f.style.setProperty("height",Math.floor(h)+"px","important");
}
document.querySelectorAll(".mobile-face-labels [data-side]").forEach(b=>b.addEventListener("click",()=>{
  const side=Number(b.dataset.side);if(arrangement()!=="pairs"||selected%2===side)return;
  selected=Math.floor(selected/2)*2+side;activePart=null;renderSheet();syncControls();
  el("mobileCardPair").querySelector(".face")?.classList.add("flip-in");
}));
/* 左右にスワイプで前後のカードへ(指についてくる。パーツを動かしているときは動かない) */
(()=>{
  const host=el("mobileCardPair");if(!host)return;let sw=null;
  host.addEventListener("pointerdown",e=>{
    if(e.pointerType==="mouse"||!mobileUIActive()||mobileSheetMode)return;
    if(e.target.closest("[data-part],.resize-handle,.rotate-handle,[contenteditable]"))return;
    sw={id:e.pointerId,x:e.clientX,y:e.clientY,t:Date.now(),dx:0,on:false};
  });
  host.addEventListener("pointermove",e=>{
    if(!sw||e.pointerId!==sw.id)return;const dx=e.clientX-sw.x,dy=e.clientY-sw.y;
    if(!sw.on){if(Math.abs(dx)>10&&Math.abs(dx)>Math.abs(dy)*1.3)sw.on=true;else{if(Math.abs(dy)>12)sw=null;return}}
    const total=pages.length*cardsPerPage(),i=mobileCardIndex(),edge=(dx<0&&i>=total-1)||(dx>0&&i<=0);
    sw.dx=dx;host.style.transition="none";host.style.transform=`translateX(${edge?dx*.25:dx}px)`;
  });
  const end=e=>{
    if(!sw||e.pointerId!==sw.id)return;const s=sw;sw=null;if(!s.on)return;
    swipedAt=Date.now();
    const dir=s.dx<0?1:-1,total=pages.length*cardsPerPage(),i=mobileCardIndex(),can=dir>0?i<total-1:i>0;
    const go=can&&(Math.abs(s.dx)>70||(Date.now()-s.t<300&&Math.abs(s.dx)>35));
    host.style.transition="transform .16s ease-in";
    if(!go){host.style.transform="";return}
    host.style.transform=`translateX(${-dir*70}vw)`;
    setTimeout(()=>{host.style.transition="none";host.style.transform=`translateX(${dir*55}vw)`;goToMobileCard(dir);
      requestAnimationFrame(()=>requestAnimationFrame(()=>{host.style.transition="transform .2s cubic-bezier(.2,.8,.3,1)";host.style.transform=""}))},150);
  };
  host.addEventListener("pointerup",end);host.addEventListener("pointercancel",end);
})();
let swipedAt=0;
window.addEventListener("resize",()=>{if(mobileUIActive())rescaleMobileFaces()});
/* 文字を打っているあいだなど、続けて描き直すときは、左のページ一覧は少し待ってからまとめて描く(用紙は毎回すぐ描く) */
let sidebarAt=0,sidebarTimer=null,sidebarSig="";
function throttleSidebar(){
  const now=performance.now(),fm=cardMM(),sig=[pages.length,currentPage,arrangement(),fm.w,fm.h,el("paperSize").value,el("paperOrientation").value,el("impositionMode").value].join("|");
  clearTimeout(sidebarTimer);
  // ページの数や並べ方が変わったときは、すぐ描く
  if(now-sidebarAt>250||sig!==sidebarSig){sidebarAt=now;sidebarSig=sig;renderPageSidebar();return}
  sidebarTimer=setTimeout(()=>{sidebarAt=performance.now();renderPageSidebar();flushFit()},260);
}
function renderMobileCardPreview(){
  if(inlineEdit)finishInlineEdit(false);
  if(!mobileUIActive())return;   // パソコンの画面では隠れているので描かない(スマホの幅になったら描く)
  const host=el("mobileCardPair");if(!host)return;
  const faces=currentFaces(),c=cardMM(),landscape=isLandscapeCard();
  const paired=arrangement()==="pairs";
  // スマホでは、選んでいる面を1枚だけ大きく出す(オモテ・ウラは下の切り替えで)
  host.innerHTML="";host.className="mobile-card-pair one-face single-mode "+(landscape?"mobile-landscape-card":"mobile-portrait-card");
  const indices=[selected];
  indices.forEach(idx=>{const f=document.createElement("div");f.className="face"+(idx===selected?" selected":"");f.dataset.idx=idx;f.style.setProperty("--mobile-card-ratio",landscape?`${c.h}/${c.w}`:`${c.w}/${c.h}`);const fm=faceMM(),inner=document.createElement("div");inner.className="m-face-inner";inner.style.width=fm.w*MM_TO_PX+"px";inner.style.height=fm.h*MM_TO_PX+"px";f.appendChild(inner);renderFace(inner,faces[idx],idx===selected,idx);f.addEventListener("click",()=>{if(selected===idx)return;selected=idx;renderMobileCardPreview();syncControls();inlineHint()});host.appendChild(f)});
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
  {const n=cardCount(deck.order[absolute]);el("mobileCardCount").textContent=`カード ${absolute+1} / ${total}`+(n>1?` ×${n}`:"");}if(el("mobilePageCount"))el("mobilePageCount").textContent=`ページ ${currentPage+1} / ${pages.length}`;
  el("mobilePrevCard").disabled=absolute<=0;
  const atEnd=absolute>=total-1,nb=el("mobileNextCard");
  nb.disabled=atEnd&&pages.length>=MAX_PAGES;nb.textContent=atEnd?"＋":"→";nb.setAttribute("aria-label",atEnd?"ページを追加":"次のカード");nb.classList.toggle("is-add",atEnd);
  const labels=document.querySelector(".mobile-face-labels");if(labels){labels.style.display=paired?"":"none";labels.querySelectorAll("[data-side]").forEach(b=>b.setAttribute("aria-pressed",String(Number(b.dataset.side)===selected%2)))}
  sizeOneFace();rescaleMobileFaces();markActivePart();
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
        <strong>文字${index+1}</strong>
        <button type="button" class="textbox-delete">削除</button>
      </div>
      <input class="tb-text" type="text" value="${esc(item.text||"")}" placeholder="テキスト${index+1}">
      <div class="tool-strip tool-strip-secondary">
        <div class="tool-number-wrap" title="文字サイズ">
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

  el("addTextBox").disabled=items.length>=PART_LIMIT;addDupButtons(list,"tb",items);
}

function renderOptionImageEditors(d){
  const list=el("optionImageList"),items=ensureOptionImages(d);list.innerHTML="";
  items.forEach((item,index)=>{const wrap=document.createElement("div");wrap.className="option-image-editor";wrap.innerHTML=`<div class="option-image-editor-head"><strong>画像${index+1}</strong><button type="button" class="textbox-delete">削除</button></div><div class="option-image-row"><img src="${item.src}" alt=""><label>回転 <input class="option-image-angle" type="number" min="-180" max="180" value="${Number(item.rotation)||0}">°</label></div><label class="checkline" style="margin:6px 0 0"><input class="oi-center" type="checkbox" ${item.centerSnap?"checked":""}>中央にスナップ</label>`;const angle=wrap.querySelector(".option-image-angle"),center=wrap.querySelector(".oi-center"),del=wrap.querySelector(".textbox-delete");angle.oninput=()=>{item.rotation=Number(angle.value)||0;renderSheet()};center.onchange=()=>{item.centerSnap=center.checked;renderSheet()};del.onclick=()=>{items.splice(index,1);renderSheet();syncControls()};list.appendChild(wrap)});el("addOptionImage").disabled=items.length>=5
;addDupButtons(list,"img",items);addRepeatControls(list,"img",items);
}

function renderShapeEditors(d){const list=el('shapeList'),items=ensureShapes(d);list.innerHTML='';items.forEach((item,i)=>{const w=document.createElement('div');w.className='shape-editor';const names={circle:'円',triangle:'三角形',rect:'四角形',polygon:'多角形',star:'星'};w.innerHTML=`<div class="shape-editor-head"><strong>${names[item.type]||'図形'}${i+1}</strong><button class="textbox-delete" type="button">削除</button></div><div class="shape-editor-row">${['polygon','star'].includes(item.type)?`<label>頂点 <input class="shape-points" type="number" min="${item.type==='star'?4:3}" max="12" value="${item.points||5}" style="width:54px"></label>`:''}<div class="tool-color fill-color" title="面色"><input class="shape-fill" type="color" value="${item.fillColor||'#fff'}"></div><div class="tool-color stroke-color" title="線色"><input class="shape-stroke" type="color" value="${item.borderColor||'#222'}"></div><select class="shape-width stroke-width-select"><option value="0.5">0.5 mm</option><option value="0.75">0.75 mm</option><option value="1">1 mm</option><option value="2">2 mm</option><option value="3">3 mm</option></select><select class="shape-align stroke-align-select"><option value="inside">内側</option><option value="center">中央</option><option value="outside">外側</option></select></div>`;const pts=w.querySelector('.shape-points'),fill=w.querySelector('.shape-fill'),stroke=w.querySelector('.shape-stroke'),width=w.querySelector('.shape-width'),align=w.querySelector('.shape-align');width.value=String(item.borderWidth||1);align.value=item.borderAlign||'inside';if(pts)pts.oninput=()=>{item.points=clamp(Number(pts.value)||5,item.type==='star'?4:3,12);renderSheet()};fill.dataset.none=item.fillNone?'1':'0';stroke.dataset.none=item.borderNone?'1':'0';fill.oninput=()=>{item.fillColor=fill.value;item.fillNone=false;renderSheet()};stroke.oninput=()=>{item.borderColor=stroke.value;item.borderNone=false;renderSheet()};fill.addEventListener('colornone',()=>{item.fillNone=true;renderSheet()});stroke.addEventListener('colornone',()=>{item.borderNone=true;renderSheet()});width.onchange=()=>{item.borderWidth=Number(width.value)||1;renderSheet()};align.onchange=()=>{item.borderAlign=align.value;renderSheet()};w.querySelector('.textbox-delete').onclick=()=>{items.splice(i,1);renderSheet();syncControls()};list.appendChild(w);[fill,stroke].forEach(setupColorInput)});addDupButtons(list,"shape",items);addRepeatControls(list,"shape",items);
}

function renderFrameTextEditors(d){
  const list=el("frameTextList"),items=ensureFrameTexts(d);list.innerHTML="";
  items.forEach((item,index)=>{
    const st=item.style||{size:SIZE.frame,bold:false,italic:false,underline:false,color:"#222222",colorNone:false};
    const wrap=document.createElement("div");wrap.className="frame-editor";
    wrap.innerHTML=`<div class="frame-editor-head"><strong>枠つき文字${index+1}</strong><button type="button" class="textbox-delete">削除</button></div>
      <input class="ft-text" type="text" value="${esc(item.text||"")}" placeholder="枠つき文字">
      <div class="tool-strip tool-strip-secondary">
        <div class="tool-number-wrap" title="文字サイズ"><span class="size-icon">A</span><input class="ft-size tool-number" type="number"><span class="unit-suffix"></span></div>
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
  el("addFrameText").disabled=items.length>=PART_LIMIT;addDupButtons(list,"ft",items);
}

function syncControls(){
  const d=currentFaces()[selected];
  el("selectedLabel").textContent=faceName(selected);
  const qid=cardIdAt(currentPage,selected),qn=cardCount(qid);
  el("cardQty").value=qn;el("qtyMinus").disabled=qn<=1;el("unlinkCard").hidden=qn<2;
  {const note=el("qtyNote");note.hidden=qn<2;if(qn>1)note.textContent=T("同じカードが{n}枚あります。どれを直しても全部に反映されます。",{n:qn});}
  // 面の種類「マイテンプレート」:テンプレートにつながっているカード、または選ぼうとしているところ
  const qcard=deck.cards[qid],qtpl=qcard&&qcard.tpl&&deck.templates&&deck.templates[qcard.tpl];
  if(myTplPick&&myTplPick!==qid+":"+slotAt(currentPage,selected).side)myTplPick=null;
  const pickOnly=!!myTplPick;   // 「マイテンプレート」を選んで一覧から選んでいるところ(つながっているカードの付け替えもここから)
  syncMyTplPicker(qcard,qtpl,pickOnly);
  refreshCopyButtonLabels();
  syncDuplexUI();
  // つながっているカードも、面の種類には「トレカ」など中身の種類を出す(つながりは下の一行で伝える)
  el("faceType").value=pickOnly?"mytpl":d.type==="template"?(d.template||"playing"):d.type;
  const templ=d.type==="template"&&!pickOnly;
  el("templateSelector").classList.toggle("hidden",!templ);
  el("playingControls").classList.add("hidden");el("tcgControls").classList.add("hidden");el("wordControls").classList.add("hidden");el("customControls").classList.add("hidden");
  el("imageControls").classList.toggle("hidden",d.type!=="image"||pickOnly);
  el("mobileTemplateHint")?.classList.toggle("hidden",templ);
  el("mobileTemplateBar")?.classList.toggle("hidden",!templ);


  el("suitImageControls").classList.add("hidden");
  syncFaceStyleChip(d);syncImgFit(d);
  if(templ){
    el("templateType").value=d.template||"playing";
    el("tplSectionTitle").textContent=T(TPL_SECTION_TITLES[d.template||"playing"]||"テンプレート");
    if((d.template||"playing")==="playing"){
      el("playingControls").classList.remove("hidden");
      el("numInput").value=d.number??"";el("suitInput").value=d.suit??"●";if(el("suitInput").selectedIndex<0)el("suitInput").value="●";
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
  if(el("autoFit"))el("autoFit").checked=deck.autoFit!==false;
  syncOverNote();
  renderSwatches();
}
function updateSelected(patch){setFaceAt(currentPage,selected,{...currentFaces()[selected],...patch});renderSheet()}

/* ---- カードの上で直接直す ----
   選んだカードの文字は、ダブルクリック(タッチはタップ)でその場で編集できる。Enterで確定、下段のテキストだけは改行できる。
   画像はカードにドラッグ&ドロップ、または⌘V/Ctrl+Vで、選んでいるカードに貼れる。 */
let inlineEdit=null,ptrDown=false,ptrStart=null,ptrType="mouse",inlineRenderWait=false;
const INLINE_PH={name:"カード名",desc:"テキスト",main:"ことば",number:"A"};
document.addEventListener("pointerdown",e=>{ptrDown=true;ptrType=e.pointerType||"mouse";ptrStart={x:e.clientX,y:e.clientY};
  if(inlineEdit&&!inlineEdit.node.contains(e.target))finishInlineEdit()},true);
window.addEventListener("pointerup",()=>{ptrDown=false},true);
window.addEventListener("pointercancel",()=>{ptrDown=false},true);
function inlineList(d,key){return key.startsWith("tb:")?ensureTextBoxes(d):key.startsWith("ft:")?ensureFrameTexts(d):null}
function getInlineText(d,key){const l=inlineList(d,key);if(l)return (l.find(x=>x.id===key.slice(3))||{}).text||"";return d[key]??""}
function setInlineText(d,key,v){const l=inlineList(d,key);if(l){const it=l.find(x=>x.id===key.slice(3));if(it)it.text=v;return}d[key]=v}
function readInline(node){return String(node.innerText??node.textContent??"").replace(/ /g," ").replace(/\r/g,"")}
function caretFromPoint(x,y){
  if(document.caretRangeFromPoint)return document.caretRangeFromPoint(x,y);
  if(document.caretPositionFromPoint){const p=document.caretPositionFromPoint(x,y);if(!p)return null;const r=document.createRange();r.setStart(p.offsetNode,p.offset);r.collapse(true);return r}
  return null;
}
function startInlineEdit(node,pt){
  if(inlineEdit)finishInlineEdit(false);
  const face=node.closest(".face[data-idx]");if(!face)return false;
  const idx=Number(face.dataset.idx),key=node.dataset.edit;
  if(key==="number"&&!node.classList.contains("center-num"))node=face.querySelector(".center-num")||node;   // 隅の数字を押しても、真ん中の数字を直す
  const d=currentFaces()[idx];if(!d||!key)return false;
  if(selected!==idx){selected=idx;syncControls()}
  const multi=key==="desc",before=String(getInlineText(d,key));
  node.querySelectorAll(".resize-handle,.rotate-handle").forEach(h=>h.remove());
  node.textContent=before;
  node.dataset.ph=T(INLINE_PH[key]||"テキスト");
  node.setAttribute("contenteditable","plaintext-only");
  if(node.contentEditable!=="plaintext-only")node.setAttribute("contenteditable","true");
  node.spellcheck=false;node.classList.add("inline-editing");node.classList.toggle("is-empty",!before);
  inlineEdit={node,idx,key,page:currentPage,multi,before};
  node.focus({preventScroll:true});
  const sel=getSelection();sel.removeAllRanges();
  let r=null;
  if(multi&&pt&&before&&before!==T(INLINE_PH[key])){r=caretFromPoint(pt.x,pt.y);if(r&&!node.contains(r.startContainer))r=null}   // 最初から入っている「テキスト」は全部選んで打ち替えやすく
  if(!r){r=document.createRange();r.selectNodeContents(node);if(multi&&before!==T(INLINE_PH[key]))r.collapse(false)}   // 1行のものは全部選んで打ち直しやすく、下段のテキストは末尾へ
  sel.addRange(r);
  node.addEventListener("keydown",inlineKey);
  node.addEventListener("input",inlineInput);
  node.addEventListener("blur",()=>finishInlineEdit(),{once:true});
  ["click","dblclick","pointerdown"].forEach(t=>node.addEventListener(t,e=>{if(node.isContentEditable)e.stopPropagation()}));
  return true;
}
function inlineInput(){const ed=inlineEdit;if(!ed)return;const v=readInline(ed.node);ed.node.classList.toggle("is-empty",!v.trim());const d=pages[ed.page]?.[ed.idx];if(d)setInlineText(d,ed.key,v)}
function inlineKey(e){
  const ed=inlineEdit;if(!ed)return;
  e.stopPropagation();   // ⌘Zは入力中の文字の取り消しに使う(作品全体の「元に戻す」にしない)
  if(e.isComposing||e.keyCode===229)return;
  if(e.key==="Escape"||e.key==="Tab"){e.preventDefault();ed.node.blur();return}
  if(e.key==="Enter"&&(!ed.multi||e.metaKey||e.ctrlKey)){e.preventDefault();ed.node.blur()}
}
/* 確定する。ボタンを押している途中で描き直すとクリックが届かなくなるので、指を離してから描き直す */
function finishInlineEdit(render=true){
  const ed=inlineEdit;if(!ed)return;inlineEdit=null;
  let v=readInline(ed.node);
  v=ed.multi?v.replace(/\n$/,""):v.replace(/\s*\n\s*/g," ").trim();
  ed.node.removeAttribute("contenteditable");ed.node.classList.remove("inline-editing","is-empty");
  ed.node.removeEventListener("keydown",inlineKey);ed.node.removeEventListener("input",inlineInput);
  const d=pages[ed.page]?.[ed.idx];if(d)setInlineText(d,ed.key,v);
  if(!render)return;
  const go=()=>{inlineRenderWait=false;if(inlineEdit)return;renderSheet();syncControls()};
  if(ptrDown){if(!inlineRenderWait){inlineRenderWait=true;window.addEventListener("pointerup",()=>setTimeout(go,0),{once:true})}}
  else go();
}
function editTarget(e){
  const t=e.target&&e.target.isConnected?e.target:document.elementFromPoint(e.clientX,e.clientY);
  const n=t&&t.closest?.("[data-edit]");if(!n)return null;
  const face=n.closest(".face.selected[data-idx]");
  return face&&face.closest("#sheetGrid,#mobileCardPair")?n:null;
}
document.addEventListener("dblclick",e=>{const n=editTarget(e);if(!n||n.isContentEditable)return;e.preventDefault();e.stopPropagation();startInlineEdit(n,{x:e.clientX,y:e.clientY})},true);
/* タッチは、選んであるカードの文字をタップしたら編集(動かしたときは編集しない) */
document.addEventListener("click",e=>{
  if(ptrType==="mouse")return;
  const n=editTarget(e);if(!n||n.isContentEditable)return;
  if(ptrStart&&Math.hypot(e.clientX-ptrStart.x,e.clientY-ptrStart.y)>8)return;
  if(Date.now()-swipedAt<400)return;
  e.preventDefault();e.stopPropagation();startBarEdit(n);
},true);

/* タッチでは、小さなカードの上で直接打つと文字が小さく、iPhoneでは画面が拡大されたままになるので、
   画面の上に大きな入力欄を出して、打った文字をすぐカードに映す */
let barEdit=null,barRaf=0;
const BAR_LABELS={name:"カード名",desc:"テキスト",main:"ことば",number:"数字"};
function barLabelOf(d,key){
  if(key.startsWith("tb:"))return T("文字")+" "+(ensureTextBoxes(d).findIndex(x=>x.id===key.slice(3))+1);
  if(key.startsWith("ft:"))return T("枠つき文字")+" "+(ensureFrameTexts(d).findIndex(x=>x.id===key.slice(3))+1);
  return T(BAR_LABELS[key]||"テキスト");
}
function markBarTarget(){
  if(!barEdit)return;
  const q=barEdit.key==="number"?".center-num":`[data-edit="${CSS.escape(barEdit.key)}"]`;
  document.querySelectorAll(`#sheetGrid .face.selected ${q},#mobileCardPair .face.selected ${q}`).forEach(n=>n.classList.add("bar-target"));
}
function placeBar(){const b=el("textEditBar"),vv=window.visualViewport;if(b&&!b.hidden)b.style.top=(vv?Math.max(0,vv.offsetTop):0)+"px"}
window.visualViewport?.addEventListener("resize",placeBar);window.visualViewport?.addEventListener("scroll",placeBar);
function startBarEdit(node){
  const face=node.closest(".face[data-idx]");if(!face)return;
  const idx=Number(face.dataset.idx),key=node.dataset.edit,d=currentFaces()[idx];if(!d||!key)return;
  if(barEdit)finishBarEdit();
  if(selected!==idx){selected=idx;renderSheet();syncControls()}
  const multi=key==="desc",inp=el("tebInput");
  barEdit={idx,key,page:currentPage,multi,before:String(getInlineText(d,key))};
  el("tebLabel").textContent=barLabelOf(d,key);
  inp.value=barEdit.before;inp.rows=multi?3:1;inp.setAttribute("enterkeyhint",multi?"enter":"done");inp.placeholder=T(INLINE_PH[key]||"テキスト");
  el("textEditBar").hidden=false;document.body.classList.add("teb-open");placeBar();markBarTarget();
  inp.focus({preventScroll:true});   // タップしたその場で呼ぶ(iPhoneでキーボードを出すため)
  if(barEdit.before===T(INLINE_PH[key]||""))inp.select();else{const n=inp.value.length;inp.setSelectionRange(n,n)}
}
function finishBarEdit(){
  const ed=barEdit;if(!ed)return;barEdit=null;cancelAnimationFrame(barRaf);
  const d=pages[ed.page]?.[ed.idx];
  if(d){let v=el("tebInput").value.replace(/\r/g,"");v=ed.multi?v:v.replace(/\s*\n\s*/g," ").trim();setInlineText(d,ed.key,v)}
  el("textEditBar").hidden=true;document.body.classList.remove("teb-open");
  if(document.activeElement===el("tebInput"))el("tebInput").blur();
  renderSheet();syncControls();
}
el("tebInput").addEventListener("input",()=>{
  if(!barEdit)return;const d=pages[barEdit.page]?.[barEdit.idx];if(!d)return;
  let v=el("tebInput").value;if(!barEdit.multi)v=v.replace(/\n/g," ");
  setInlineText(d,barEdit.key,v);
  cancelAnimationFrame(barRaf);barRaf=requestAnimationFrame(()=>{renderSheet();markBarTarget()});
});
el("tebInput").addEventListener("keydown",e=>{
  if(!barEdit||e.isComposing||e.keyCode===229)return;
  if(e.key==="Escape"||(e.key==="Enter"&&(!barEdit.multi||e.metaKey||e.ctrlKey))){e.preventDefault();finishBarEdit()}
});
el("tebInput").addEventListener("blur",()=>setTimeout(()=>{if(barEdit&&document.activeElement!==el("tebInput"))finishBarEdit()},0));
el("tebDone").addEventListener("pointerdown",e=>e.preventDefault());   // 押したときに入力欄からフォーカスが外れないように
el("tebDone").addEventListener("click",finishBarEdit);
let inlineHintShown=false;
function inlineHint(){
  if(inlineHintShown)return;inlineHintShown=true;
  try{if(localStorage.getItem("pk-hint-inline"))return;localStorage.setItem("pk-hint-inline","1")}catch(_){}
  showAppToast(T(ptrType==="mouse"?"カードの文字はダブルクリックで、その場で直せます。画像はカードにドラッグして置けます。":"選んだカードの文字をタップすると、その場で直せます。左右にスワイプすると、前後のカードへ移ります。"),{duration:7000});
}

/* ---- キーボード操作(パソコン) ----
   矢印:となりのカードへ / Enter:選んだカードの文字を直す / Delete:選んだパーツを消す / Esc:パーツの選択をやめる
   ⌘C・⌘V(Ctrl+C・Ctrl+V):面をコピー・貼り付け */
let activePart=null;   // カードの上で最後に触ったパーツ {page,idx,part:"tb:id"など}
function typingIn(t){return !!(t&&t.closest&&t.closest("input,textarea,select,[contenteditable]"))}
function overlayOpen(){return !!document.querySelector(".modal:not([hidden])")||!el("settingsPop").hidden||!el("textEditBar").hidden||!!document.querySelector(".color-popup.open,.color-popup:not([hidden])")}
function markActivePart(){
  document.querySelectorAll(".part-active").forEach(n=>n.classList.remove("part-active"));
  if(activePart&&(activePart.page!==currentPage||activePart.idx!==selected))activePart=null;
  if(activePart){
    const q=`.face.selected [data-part="${CSS.escape(activePart.part)}"]`,ns=document.querySelectorAll(`#sheetGrid ${q},#mobileCardPair ${q}`);
    if(ns.length)ns.forEach(n=>n.classList.add("part-active"));else activePart=null;
  }
  syncPartBar();
}
/* スマホ:カードの上のパーツに触れたら、下に「小さく・大きく・中央へ・削除」を出す(つまみを細かく動かさなくてよいように) */
function syncPartBar(){
  const bar=el("partBar");if(!bar)return;const on=mobileUIActive()&&!!activePart&&!mobileSheetMode;
  bar.hidden=!on;document.body.classList.toggle("part-on",on);
}
function activePartItem(){
  const a=activePart;if(!a)return null;const i=a.part.indexOf(":"),k=a.part.slice(0,i),id=a.part.slice(i+1),d=currentFaces()[selected];
  const list=({tb:ensureTextBoxes,ft:ensureFrameTexts,img:ensureOptionImages,shape:ensureShapes}[k]||(()=>null))(d);
  return list?list.find(x=>x.id===id)||null:null;
}
el("mobileCardPair")?.addEventListener("pointerdown",e=>{
  const p=e.target.closest(".face.selected [data-part]");
  if(p){activePart={page:currentPage,idx:selected,part:p.dataset.part};markActivePart()}
  else if(activePart&&e.target.closest(".face")){activePart=null;markActivePart()}
},true);
el("partBar")?.addEventListener("click",e=>{
  const b=e.target.closest("[data-act]");if(!b)return;const act=b.dataset.act;
  if(act==="done"){activePart=null;markActivePart();return}
  if(act==="delete"){deleteActivePart();return}
  if(act==="dup"){const a=activePart;if(!a)return;const i=a.part.indexOf(":");duplicatePart(a.part.slice(0,i),a.part.slice(i+1));return}
  const item=activePartItem();if(!item)return;const o=item.box||{x:20,y:20,w:60,h:14};
  if(act==="center"){
    const n=repCount(item),flow=item.flow||"row-center",K=clamp(parseInt(item.wrap)||0,0,20)||n;
    const gw=n>1&&flow==="row-start"?(Math.min(n,K)-1)*REP_GAP*o.w+o.w:o.w;   // 左から並べているときは、並び全体を真ん中へ
    item.box={...o,x:50-(n>1&&flow==="row-start"?gw:o.w)/2};
  }
  else{
    let k=act==="bigger"?1.15:1/1.15;k=Math.min(k,100/o.w,100/o.h);if(o.w*k<6)k=6/o.w;
    const w=o.w*k,h=o.h*k,x=clamp(o.x+o.w/2-w/2,0,100-w),y=clamp(o.y+o.h/2-h/2,0,100-h);item.box={...o,x,y,w,h};
  }
  renderSheet();syncControls();
});
el("sheetGrid").addEventListener("pointerdown",e=>{
  const p=e.target.closest(".face.selected [data-part]");
  activePart=p?{page:currentPage,idx:selected,part:p.dataset.part}:null;markActivePart();
},true);
function deleteActivePart(){
  const a=activePart;if(!a)return false;
  const i=a.part.indexOf(":"),k=a.part.slice(0,i),id=a.part.slice(i+1),d=currentFaces()[selected];
  const list=({tb:ensureTextBoxes,ft:ensureFrameTexts,img:ensureOptionImages,shape:ensureShapes}[k]||(()=>null))(d);if(!list)return false;
  const at=list.findIndex(x=>x.id===id);if(at<0)return false;
  list.splice(at,1);activePart=null;renderSheet();syncControls();return true;
}
function moveSelection(key){
  const dir={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[key];
  const faces=[...document.querySelectorAll("#sheetGrid .face[data-idx]")],cur=faces.find(f=>Number(f.dataset.idx)===selected);if(!cur)return;
  const c=cur.getBoundingClientRect(),cx=c.left+c.width/2,cy=c.top+c.height/2;let best=null,bd=Infinity;
  faces.forEach(f=>{if(f===cur)return;const r=f.getBoundingClientRect(),dx=r.left+r.width/2-cx,dy=r.top+r.height/2-cy,along=dx*dir[0]+dy*dir[1];if(along<=4)return;
    const dist=along+(Math.abs(dx*dir[1])+Math.abs(dy*dir[0]))*2;if(dist<bd){bd=dist;best=f}});
  if(best)selected=Number(best.dataset.idx);
  else if(dir[0]+dir[1]>0&&currentPage<pages.length-1){currentPage++;selected=0}       // 最後のカードの先は次のページへ
  else if(dir[0]+dir[1]<0&&currentPage>0){currentPage--;selected=pages[currentPage].length-1}
  else return;
  activePart=null;renderSheet();syncControls();
  document.querySelector("#sheetGrid .face.selected")?.scrollIntoView({block:"nearest",inline:"nearest"});
}
document.addEventListener("keydown",e=>{
  if(e.defaultPrevented||e.isComposing||mobileUIActive()||typingIn(e.target)||inlineEdit||overlayOpen())return;
  const mod=e.metaKey||e.ctrlKey;
  if(!mod&&!e.altKey&&/^Arrow/.test(e.key)){e.preventDefault();moveSelection(e.key);return}
  if(!mod&&e.key==="Enter"){const n=document.querySelector("#sheetGrid .face.selected [data-edit]");if(n){e.preventDefault();startInlineEdit(n)}return}
  if(!mod&&(e.key==="Delete"||e.key==="Backspace")){if(deleteActivePart())e.preventDefault();return}
  if(e.key==="Escape"&&activePart){activePart=null;markActivePart();return}
  if(mod&&!e.shiftKey&&e.key.toLowerCase()==="d"&&activePart){e.preventDefault();const a=activePart,i=a.part.indexOf(":");duplicatePart(a.part.slice(0,i),a.part.slice(i+1));return}
  if(mod&&!e.shiftKey&&e.key.toLowerCase()==="c"&&getSelection().isCollapsed){e.preventDefault();el("copyFace").click();showAppToast(T("この面をコピーしました。ほかの面を選んで ⌘V / Ctrl+V で貼れます。"),{duration:3500})}
});

/* ---- パーツの複製:同じアイコンを並べたいときなどに。1つの面に置けるパーツは種類ごとに12個まで ---- */
const PART_LIMIT=12;
const PART_LISTS={tb:d=>ensureTextBoxes(d),ft:d=>ensureFrameTexts(d),img:d=>ensureOptionImages(d),shape:d=>ensureShapes(d)};
const PART_PREFIX={tb:"tb_",ft:"ft_",img:"oi_",shape:"sh_"};
function partLimitToast(){showAppToast(T("パーツは種類ごとに、1つの面に{n}個まで置けます。",{n:PART_LIMIT}),{duration:3500})}
function duplicatePart(kind,id){
  const d=currentFaces()[selected],list=PART_LISTS[kind]?.(d);if(!list)return false;
  if(list.length>=PART_LIMIT){partLimitToast();return false}
  const i=list.findIndex(x=>x.id===id);if(i<0)return false;
  const c=JSON.parse(JSON.stringify(list[i]));c.id=PART_PREFIX[kind]+Date.now()+"_"+Math.random().toString(36).slice(2,7);
  if(c.box){const b=c.box;c.box={...b,x:b.x+4<=100-b.w?b.x+4:Math.max(0,b.x-4),y:b.y+4<=100-b.h?b.y+4:Math.max(0,b.y-4)}}   // 少しずらして重ねる
  list.splice(i+1,0,c);activePart={page:currentPage,idx:selected,part:kind+":"+c.id};
  renderSheet();syncControls();return true;
}
function fitRepeatToCard(item){
  const o=item.box;if(!o)return;const n=repCount(item),flow=item.flow||"row-center",col=flow.startsWith("col"),K=clamp(parseInt(item.wrap)||0,0,20)||n,len=Math.min(n,K);
  const span=(len-1)*REP_GAP+1,size=col?o.h:o.w,room=92;if(size*span<=room)return;
  const k=room/(size*span),w=o.w*k,h=o.h*k;
  item.box={...o,w,h,x:col?clamp(o.x+o.w/2-w/2,0,100-w):(flow==="row-start"?4:50-w/2),y:col?(flow==="col-start"?4:50-h/2):clamp(o.y+o.h/2-h/2,0,100-h)};
}
function addRepeatControls(list,kind,items){
  [...list.children].forEach((w,i)=>{
    const item=items[i];if(!item||w.querySelector(".part-repeat"))return;
    const n=repCount(item),box=document.createElement("div");box.className="part-repeat";
    box.innerHTML=`<label class="pr-row"><span>${T("個数")}</span><span class="tool-number-wrap"><input class="tool-number pr-n" type="number" min="1" max="20" step="1" value="${n}"></span></label>`+
      `<div class="pr-more"${n>1?"":" hidden"}><select class="pr-flow" aria-label="${T("並べ方")}"><option value="row-center">${T("横に・中央そろえ")}</option><option value="row-start">${T("横に・左から")}</option><option value="col-center">${T("縦に・中央そろえ")}</option><option value="col-start">${T("縦に・上から")}</option></select>`+
      `<label class="pr-row"><span>${T("折り返し")}</span><span class="tool-number-wrap"><input class="tool-number pr-k" type="number" min="0" max="20" step="1" value="${parseInt(item.wrap)||0}"></span><small>${T("個ごと（0はしない）")}</small></label></div>`;
    const head=w.firstElementChild;head.after(box);
    box.querySelector(".pr-flow").value=item.flow||"row-center";
    box.querySelector(".pr-n").addEventListener("change",e=>{
      const before=repCount(item);item.count=clamp(parseInt(e.target.value)||1,1,20);
      if(item.count>before)fitRepeatToCard(item);   // 増やして用紙からはみ出すときは、1個の大きさを小さくして収める
      renderSheet();syncControls();
    });
    box.querySelector(".pr-k").addEventListener("change",e=>{item.wrap=clamp(parseInt(e.target.value)||0,0,20);renderSheet()});
    box.querySelector(".pr-flow").addEventListener("change",e=>{
      // 中央そろえ⇔左から(上から)を切り替えても、並びが今の場所から動かないように基準の位置を合わせる
      const from=item.flow||"row-center",to=e.target.value,o=item.box,n=repCount(item),K=clamp(parseInt(item.wrap)||0,0,20)||n,len=Math.min(n,K);
      if(o&&from.slice(0,3)===to.slice(0,3)&&from!==to){const col=to.startsWith("col"),sz=col?o.h:o.w,shift=(len-1)/2*REP_GAP*sz*(to.endsWith("center")?1:-1);
        item.box=col?{...o,y:clamp(o.y+shift,0,100-o.h)}:{...o,x:clamp(o.x+shift,0,100-o.w)}}
      item.flow=to;fitRepeatToCard(item);renderSheet();
    });
  });
}
function addDupButtons(list,kind,items){
  [...list.children].forEach((w,i)=>{
    const item=items[i],del=w.querySelector(".textbox-delete");if(!item||!del||w.querySelector(".part-dup"))return;
    const b=document.createElement("button");b.type="button";b.className="part-dup";b.textContent=T("複製");b.disabled=items.length>=PART_LIMIT;
    b.addEventListener("click",()=>duplicatePart(kind,item.id));del.parentNode.insertBefore(b,del);
  });
}

/* 画像をカードに置く:TCGの中段は中段の画像、画像の面と無地は面の画像、それ以外は背景 */
function placeImageOnFace(idx,src,zone){
  selected=idx;
  const d=currentFaces()[idx];if(!d)return;
  if(d.type==="template"&&d.template==="tcg"&&zone!=="bg")setFaceAt(currentPage,idx,{...d,image:src,imageFit:null});
  else if(d.type==="image")setFaceAt(currentPage,idx,{...d,src,srcFit:null});
  else if(d.type==="plain")setFaceAt(currentPage,idx,{type:"image",src,...keepCommon(d)});
  else setFaceAt(currentPage,idx,{...d,bgImage:src,bgFit:null});
  renderSheet();syncControls();
}
function dropZoneAt(e){
  const face=e.target.closest?.(".face[data-idx]");
  if(!face||!face.closest("#sheetGrid,#mobileCardPair"))return null;
  const d=currentFaces()[Number(face.dataset.idx)];
  if(d&&d.type==="template"&&d.template==="tcg"){const img=face.querySelector(".tcg-image");const inImg=img&&e.target.closest(".tcg-image");return {face,node:inImg?img:face,zone:inImg?"image":"bg"}}
  return {face,node:face,zone:""};
}
const hasFiles=e=>[...(e.dataTransfer?.types||[])].includes("Files");
let dropTimer=null;
function clearDropMarks(){document.querySelectorAll(".drop-over").forEach(x=>x.classList.remove("drop-over"))}
document.addEventListener("dragover",e=>{
  if(!hasFiles(e))return;
  e.preventDefault();   // カード以外に落としても、ブラウザが画像を開いて作業中の画面から離れないようにする
  const z=dropZoneAt(e);
  document.querySelectorAll(".drop-over").forEach(x=>{if(!z||x!==z.node)x.classList.remove("drop-over")});
  if(z)z.node.classList.add("drop-over");
  e.dataTransfer.dropEffect=z||e.target.closest?.(".canvas-area,.mobile-card-pair")?"copy":"none";
  clearTimeout(dropTimer);dropTimer=setTimeout(clearDropMarks,180);
});
document.addEventListener("drop",async e=>{
  if(!hasFiles(e))return;
  e.preventDefault();clearDropMarks();
  const files=[...e.dataTransfer.files];if(!files.length)return;
  const pdf=files.find(f=>/pdf$/i.test(f.type)||/\.pdf$/i.test(f.name));
  if(pdf&&e.target.closest?.(".canvas-area,.mobile-card-pair,.layout")){   // このツールで保存したPDFは、画面に落とすだけで開ける
    try{const dt=new DataTransfer();dt.items.add(pdf);el("loadPdf").files=dt.files;el("loadPdf").dispatchEvent(new Event("change",{bubbles:true}))}catch(err){console.warn(err)}
    return;
  }
  const z=dropZoneAt(e),img=files.find(f=>/^image\//.test(f.type));
  if(!z||!img)return;
  dismissStart();
  try{placeImageOnFace(Number(z.face.dataset.idx),await readImageFile(img),z.zone)}
  catch(err){console.error(err);alert(T("画像を読み込めませんでした。"))}
});
document.addEventListener("paste",async e=>{
  const t=e.target;
  if(inlineEdit||t.closest?.("input,textarea,select,[contenteditable]")||document.querySelector(".modal:not([hidden])"))return;
  const item=[...(e.clipboardData?.items||[])].find(i=>i.kind==="file"&&/^image\//.test(i.type));
  const file=item&&item.getAsFile();
  if(!file){   // 画像がなければ、⌘C でコピーした面を貼る
    if(faceClipboard&&!mobileUIActive()){e.preventDefault();el("pasteFace").click();showAppToast(T("コピーした面を貼りました。"),{duration:3000})}
    return;
  }
  e.preventDefault();
  try{placeImageOnFace(selected,await readImageFile(file),"");showAppToast(T("画像を選んでいるカードに貼りました。"),{duration:3500})}
  catch(err){console.error(err);alert(T("画像を読み込めませんでした。"))}
});

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
document.querySelectorAll("#mobileTemplateHint [data-kind]").forEach(b=>b.addEventListener("click",()=>{const f=el("faceType");f.value=b.dataset.kind;f.dispatchEvent(new Event("change",{bubbles:true}))}));
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
[el("mobileSheetView")].forEach(area=>{if(!area)return;let sx=null,sy=0;   // カード1枚の表示のスワイプは、指についてくる版(上)で扱う
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
el("cardSize").addEventListener("change",e=>{
  if(e.target.value==="custom-edit"){e.target.value=e.target.dataset.prev||"poker";openSizeModal();return}
  e.target.dataset.prev=e.target.value;resizePagesForLayout();setPaper();syncControls();
});
/* ---- カードの大きさを入力 ---- */
function sizeFit(w,h){
  // 今の用紙・並べ方で何枚入るか(入らなければ0)
  const p=paperMM(),land=isLandscapeCard(),f=land?{w:h,h:w}:{w,h},q=!isPairLayout()?f:(land?{w:f.w,h:f.h*2}:{w:f.w*2,h:f.h});
  return Math.floor(p.w/q.w)*Math.floor(p.h/q.h);
}
function paperLabel(){const a=el("paperSize").value==="a3"?"A3":"A4",land=el("paperOrientation").value==="landscape";return window.CMMI18N&&CMMI18N.lang==="en"?`${a} ${land?"landscape":"portrait"}`:a+(land?"横":"縦")}
function readSizeModal(){const k=LEN_UNITS[units.len].k;return normCustom({w:Number(el("customW").value)*k,h:Number(el("customH").value)*k})}
function syncSizeModal(){
  const k=LEN_UNITS[units.len].k,w=Number(el("customW").value)*k,h=Number(el("customH").value)*k,note=el("sizeNote");
  let ok=w>=15&&h>=15&&w<=297&&h<=297,msg="";
  if(!ok)msg=T("15〜297 mmの大きさにしてください。");
  else{const c=normCustom({w,h}),n=sizeFit(c.w,c.h);ok=n>0;
    msg=n>0?T("{paper}に{n}枚入ります。",{paper:paperLabel(),n})
           :T("この用紙には入りません。用紙の大きさや向き、並べ方を変えてみてください。")}
  note.textContent=msg;note.classList.toggle("bad",!ok);el("sizeOk").disabled=!ok;
}
function openSizeModal(){
  toggleSettings(false);
  const u=LEN_UNITS[units.len];["W","H"].forEach(a=>{const inp=el("custom"+a);inp.step=OFFSET_STEP[units.len]||.1;inp.value=fmtLen(a==="W"?customCard.w:customCard.h,false)});
  document.querySelectorAll("#sizeModal .unit-len-label").forEach(n=>n.textContent=u.label);
  el("sizeModal").hidden=false;syncSizeModal();if(!mobileUIActive()){el("customW").focus();el("customW").select()}
}
function closeSizeModal(){el("sizeModal").hidden=true}
["customW","customH"].forEach(id=>el(id).addEventListener("input",syncSizeModal));
["customW","customH"].forEach(id=>el(id).addEventListener("keydown",e=>{if(e.key==="Enter"&&!el("sizeOk").disabled){e.preventDefault();el("sizeOk").click()}}));
el("sizeOk").addEventListener("click",()=>{
  customCard=readSizeModal();const cs=el("cardSize");cs.value="custom";cs.dataset.prev="custom";
  closeSizeModal();relabelLengths();resizePagesForLayout();setPaper();syncControls();
});
document.querySelectorAll("[data-size-close]").forEach(b=>b.addEventListener("click",closeSizeModal));
el("sizeModal").addEventListener("click",e=>{if(e.target===el("sizeModal"))closeSizeModal()});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!el("sizeModal").hidden)closeSizeModal()});
el("impositionMode").addEventListener("change",e=>{el("paperOrientation").value=optimalPaperOrientationForMode();resizePagesForLayout();e.target.dataset.prev=e.target.value;setPaper();syncControls()});
window.addEventListener("resize",fitPaper);

/* 面の種類は1つのリストで選ぶ(無地・トランプ・トレカ・ワードゲーム・画像・マイテンプレート)。
   以前の「テンプレート」→「種類」の2段階は、ここでまとめて扱う */
const FACE_KINDS=["playing","tcg","word"];
const TPL_SECTION_TITLES={playing:"トランプの数字とマーク",tcg:"トレカの文字と画像",word:"ワードゲームのことば"};
function faceKindValue(d){return d.type==="template"?(d.template||"playing"):d.type}
el("faceType").addEventListener("change",e=>{
  let t=e.target.value;if(t==="template")t="playing";
  const id=cardIdAt(currentPage,selected),c=deck.cards[id];
  if(t==="mytpl"){myTplPick=id+":"+slotAt(currentPage,selected).side;syncControls();return}
  const wasPicking=!!myTplPick;myTplPick=null;
  // 一覧から選ぶのをやめて、いまと同じ種類に戻しただけなら、テンプレートからは外さない
  if(wasPicking&&c&&c.tpl&&t===faceKindValue(currentFaces()[selected])){syncControls();return}
  // マイテンプレートから別の種類へ:テンプレートから外す(同じ種類なら見た目はそのまま)
  if(c&&c.tpl){
    const tp=deck.templates&&deck.templates[c.tpl];delete c.tpl;tplWatch=null;
    if(tp)showAppToast(T("テンプレート「{name}」から外しました",{name:tp.name}),{duration:4000});
    if(t===faceKindValue(currentFaces()[selected])){renderSheet();syncControls();return}
  }
  const keep=keepCommon(currentFaces()[selected]);
  if(FACE_KINDS.includes(t)){
    if(currentFaces()[selected].type==="template"){el("templateType").value=t;el("templateType").dispatchEvent(new Event("change",{bubbles:true}));return}
    setFaceAt(currentPage,selected,{...({playing:makePlaying,tcg:makeTcg,word:makeWord}[t])(),...keep});
  }
  else if(t==="plain")setFaceAt(currentPage,selected,{type:"plain",...keep});
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
  const common={bgColor:keepBg,bgImage:keepBgImage,bgBorderColor:keepBgBorderColor,bgBorderWidth:keepBgBorderWidth,bgBorderNone:keepBgBorderNone,bgBorderAlign:keepBgBorderAlign,textBoxes:keepTextBoxes,frameTexts:keepFrameTexts,optionImages:keepOptionImages};
  if(t==="playing")nextFace={...makePlaying(),...common};
  if(t==="tcg")nextFace={...makeTcg(),...common};
  if(t==="word")nextFace={...makeWord(),...common};
  if(nextFace)setFaceAt(currentPage,selected,Object.assign(nextFace,keep));   // 図形・背景の「なし」も含めて引き継ぐ
  renderSheet();syncControls();
});

["numInput","suitInput","suitSize","suitCount","suitMode","cornerPlacement"].forEach(id=>el(id).addEventListener("input",()=>{
  if(id==="suitInput"&&el("suitInput").value==="")el("suitMode").value="text";   // 「なし」を選んだら、画像のスートもやめる
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
onImagePicked(el("tcgImageInput"),src=>updateSelected({image:src,imageFit:null}));

el("wordMain").addEventListener("input",()=>updateSelected({main:el("wordMain").value}));
el("wordMainColor").addEventListener("input",()=>{const c=el("wordMainColor").value;addRecentColor(c);updateSelected({mainColor:c,mainColorNone:false});renderSwatches()});
["wordMainSize","wordMainBold","wordMainItalic","wordMainUnderline"].forEach(id=>el(id).addEventListener("input",()=>{updateSelected({mainStyle:{...(currentFaces()[selected].mainStyle||{}),size:readSizeInput(el("wordMainSize"),SIZE.word),bold:el("wordMainBold").checked,italic:el("wordMainItalic").checked,underline:el("wordMainUnderline").checked}})}));



el("addTextBox").addEventListener("click",()=>{const d=currentFaces()[selected],items=ensureTextBoxes(d);if(items.length>=PART_LIMIT)return;items.push(makeTextBox(items.length));renderSheet();syncControls()});
el("addFrameText").addEventListener("click",()=>{const d=currentFaces()[selected],items=ensureFrameTexts(d);if(items.length>=PART_LIMIT)return;items.push(makeFrameText(items.length));renderSheet();syncControls()});
document.querySelectorAll(".add-shape").forEach(b=>b.addEventListener("click",()=>{const d=currentFaces()[selected],items=ensureShapes(d);if(items.length>=PART_LIMIT){partLimitToast();return}items.push(makeShape(b.dataset.shape,items.length));renderSheet();syncControls()}));
el("addOptionImage").addEventListener("click",()=>{if(ensureOptionImages(currentFaces()[selected]).length>=PART_LIMIT){partLimitToast();return}el("optionImageInput").click()});
onImagePicked(el("optionImageInput"),src=>{const items=ensureOptionImages(currentFaces()[selected]);if(items.length<PART_LIMIT)items.push(makeOptionImage(src,items.length));renderSheet();syncControls()});

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

onImagePicked(el("faceBgImageInput"),src=>updateSelected({bgImage:src,bgFit:null}));
el("clearFaceBgImage").addEventListener("click",()=>{
  updateSelected({bgImage:null,bgFit:null});
  el("faceBgImageInput").value="";
});

let faceClipboard=null;
function refreshCopyButtonLabels(){
  if(arrangement()==="single"){
    el("copyToPageSide").textContent="このページのカード全部にコピー";
    el("copyToAllPagesSide").textContent="全ページのカード全部にコピー";
  }else if((arrangement()==="pairs"&&selected%2===1)||arrangement()==="back"){
    el("copyToPageSide").textContent="このページのウラ全部にコピー";
    el("copyToAllPagesSide").textContent="全ページのウラ全部にコピー";
  }else{
    el("copyToPageSide").textContent="このページのオモテ全部にコピー";
    el("copyToAllPagesSide").textContent="全ページのオモテ全部にコピー";
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
  const copies=deck.order.slice(p*n,(p+1)*n).map(id=>cloneCard(deck.cards[id]));
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
/* ---- 表から一括作成:テンプレート(トランプ・トレカ・ワードゲーム、マイテンプレート、または選んでいるカード)に、表の1行を1枚のカードとして当てはめる。
   作ったカードはテンプレートでつながるので、あとから見た目をまとめて直せる ---- */
const BULK_ALIASES={
  number:["数字","数","ランク","number","num","rank"],
  suit:["スート","マーク","suit","mark"],
  name:["カード名","名前","名称","タイトル","name","title","cardname"],
  desc:["テキスト","説明","説明文","効果","本文","text","desc","description","effect","rules"],
  main:["ことば","言葉","お題","ワード","word","main"],
  textbox:["文字","テキストボックス","テキスト","textbox","text"],
  frame:["枠つき文字","枠付き文字","枠文字","フレームテキスト","フレーム","frametext","framedtext","frame"],
  qty:["枚数","数量","copies","count","qty","quantity"],
  imgcount:["画像の個数","画像の数","アイコンの数","アイコンの個数","imagecount","iconcount","icons"],
  shapecount:["図形の個数","図形の数","shapecount","shapes"]
};
const BULK_KINDS={playing:{name:"トランプ",make:makePlaying,keys:["number","suit"]},tcg:{name:"トレカ",make:makeTcg,keys:["name","desc"]},word:{name:"ワードゲーム",make:makeWord,keys:["main"]}};
const BULK_EXAMPLES={
  playing:{ja:[["A","♠"],["2","♠"],["3","♠"]],en:[["A","♠"],["2","♠"],["3","♠"]]},
  tcg:{ja:[["ゴブリン","相手の手札を1枚見る。","3"],["スライム","攻撃されたら2枚に分かれる。","2"],["ドラゴン","山札から1枚引く。","1"]],
       en:[["Goblin","Look at one card in an opponent's hand.","3"],["Slime","When attacked, split into two cards.","2"],["Dragon","Draw a card.","1"]]},
  word:{ja:[["りんご"],["自転車"],["図書館"]],en:[["Apple"],["Bicycle"],["Library"]]}
};
/* テンプレートのカードで、文字を入れられる場所の一覧 */
function bulkFields(card){
  const out=[];
  ["front","back"].forEach(side=>{
    const f=card&&card[side];if(!f)return;
    const add=(kind,name,n,set,get)=>out.push({side,kind,name,n,set,get});
    if(f.type==="template"){
      if(f.template==="playing"){add("number","数字",0,(d,v)=>{d.number=v},d=>d.number);add("suit","スート",0,(d,v)=>{d.suit=/^(なし|無し|none|-|ー|—)$/i.test(String(v).trim())?"":v},d=>d.suit||T("なし"))}
      else if(f.template==="tcg"){add("name","カード名",0,(d,v)=>{d.name=v},d=>d.name);add("desc","テキスト",0,(d,v)=>{d.desc=v},d=>d.desc)}
      else if(f.template==="word")add("main","ことば",0,(d,v)=>{d.main=v},d=>d.main);
    }
    (f.textBoxes||[]).forEach((_,i)=>add("textbox","文字",i+1,(d,v)=>{d.textBoxes[i].text=v},d=>d.textBoxes[i].text));
    (f.frameTexts||[]).forEach((_,i)=>add("frame","枠つき文字",i+1,(d,v)=>{d.frameTexts[i].text=v},d=>d.frameTexts[i].text));
    (f.optionImages||[]).forEach((_,i)=>add("imgcount","画像の個数",i+1,(d,v)=>{d.optionImages[i].count=clamp(parseInt(String(v).replace(/[０-９]/g,c=>String.fromCharCode(c.charCodeAt(0)-0xFEE0)))||1,1,20)},d=>String(repCount(d.optionImages[i]))));
    (f.shapes||[]).forEach((_,i)=>add("shapecount","図形の個数",i+1,(d,v)=>{d.shapes[i].count=clamp(parseInt(String(v).replace(/[０-９]/g,c=>String.fromCharCode(c.charCodeAt(0)-0xFEE0)))||1,1,20)},d=>String(repCount(d.shapes[i]))));
  });
  return out;
}
function bulkFieldLabel(x){return T("{side}：{name}",{side:T(x.side==="front"?"オモテ":"ウラ"),name:T(x.name)+(x.n?" "+x.n:"")})}
/* 例の見出し:オモテはそのままの名前、ウラは「ウラ：」をつける(どちらも自動の割り当てで読める) */
function bulkHeadName(x){return x.side==="back"?bulkFieldLabel(x):T(x.name)+(x.n?" "+x.n:"")}
/* 表の読み取り:スプレッドシートから貼り付けた表(タブ区切り)とCSV。"…" で囲んだセルの改行・区切り文字もそのまま */
function parseTable(text,csv){
  text=String(text||"").replace(/^﻿/,"").replace(/\r\n?/g,"\n");   // 改行はLFにそろえる(セルの中の改行も)
  let delim="\t";
  if(!text.includes("\t")){
    const lines=text.split("\n").filter(l=>l.trim()),cnt=l=>(l.match(/,/g)||[]).length;
    if(csv||(lines.length>1&&cnt(lines[0])>0&&lines.every(l=>cnt(l)===cnt(lines[0]))))delim=",";
  }
  const rows=[];let row=[],cell="",q=false;
  for(let i=0;i<text.length;i++){
    const ch=text[i];
    if(q){if(ch==='"'){if(text[i+1]==='"'){cell+='"';i++}else q=false}else cell+=ch;continue}
    if(ch==='"'&&cell===""){q=true;continue}
    if(ch===delim){row.push(cell);cell="";continue}
    if(ch==="\n"){row.push(cell);rows.push(row);row=[];cell="";continue}
    cell+=ch;
  }
  if(cell!==""||row.length){row.push(cell);rows.push(row)}
  return rows.filter(r=>r.some(c=>c.trim()!==""));
}
function normHead(v){return String(v||"").normalize("NFKC").toLowerCase().replace(/[\s_\-・:：()（）「」\[\]]/g,"")}
function splitHead(h){
  let v=normHead(h),side=null;
  const m=v.match(/^(オモテ|おもて|表|front|ウラ|うら|裏|back)/);
  if(m){side=/^(ウラ|うら|裏|back)/.test(m[1])?"back":"front";v=v.slice(m[1].length)}
  const num=(v.match(/(\d+)$/)||[])[1];
  return {side,num,base:num?v.slice(0,-num.length):v};
}
/* 見出しの名前から、どの列をどこに入れるかを決める。見出しが合わなければ左の列から順に */
function bulkAutoMap(fields,headers,useNames){
  const map=fields.map(()=>-1),used=new Set();let qty=-1;
  if(useNames)headers.forEach((h,ci)=>{
    const {side,num,base}=splitHead(h);
    if(!num&&qty<0&&BULK_ALIASES.qty.includes(base)){qty=ci;used.add(ci);return}
    const fi=fields.findIndex((f,k)=>map[k]<0&&(!side||f.side===side)&&BULK_ALIASES[f.kind].includes(base)&&(!num||f.n===+num));
    if(fi>=0){map[fi]=ci;used.add(ci)}
  });
  if(map.every(v=>v<0)){let ci=0;fields.forEach((f,fi)=>{while(used.has(ci))ci++;if(ci<headers.length){map[fi]=ci;ci++}})}
  return {map,qty};
}
/* 見出しからテンプレートを当てる(カード名・テキスト→トレカ、数字・スート→トランプ、ことば→ワードゲーム) */
function bulkGuessKind(headers){
  let best=null,score=0;
  Object.entries(BULK_KINDS).forEach(([k,v])=>{const n=headers.filter(h=>{const {side,base}=splitHead(h);return side!=="back"&&v.keys.some(x=>BULK_ALIASES[x].includes(base))}).length;if(n>score){best=k;score=n}});
  return best;
}
let bulk=null;
function bulkMyTemplate(){const tid=bulk.kind.slice(3);return (deck.templates||{})[tid]||myLibrary.find(x=>x.id===tid)}
function bulkTemplateCard(){
  if(bulk.kind==="selected")return deck.cards[bulk.tpl];
  if(bulk.kind.startsWith("my:")){
    const t=bulkMyTemplate();if(!t){bulk.kind="playing";return bulkTemplateCard()}
    if(!bulk.builtin||bulk.builtin.kind!==bulk.kind)bulk.builtin={kind:bulk.kind,card:{front:deep(t.front),back:deep(t.back)}};
    return bulk.builtin.card;
  }
  if(!bulk.builtin||bulk.builtin.kind!==bulk.kind)bulk.builtin={kind:bulk.kind,card:{front:BULK_KINDS[bulk.kind].make(),back:makePlain()}};
  return bulk.builtin.card;
}
function setBulkKind(kind){if(bulk.kind===kind)return;bulk.kind=kind;bulk.builtin=null;bulk.fields=bulkFields(bulkTemplateCard());bulk.sig=null}
function bulkTable(){
  const rows=parseTable(el("bulkText").value,bulk.csv),head=el("bulkHeader").checked;
  const width=rows.reduce((a,r)=>Math.max(a,r.length),0);
  const headers=Array.from({length:width},(_,i)=>head&&rows[0]&&String(rows[0][i]||"").trim()||T("列{n}",{n:i+1}));
  return {headers,data:head?rows.slice(1):rows,head};
}
function bulkCards(table){
  const tpl=bulkTemplateCard(),out=[];
  table.data.forEach(r=>{
    let n=1;
    if(bulk.qty>=0){const v=String(r[bulk.qty]??"").normalize("NFKC").trim();if(v!==""){n=parseInt(v,10);if(!Number.isFinite(n))n=1}}
    if(n<=0)return;
    const c={front:deep(tpl.front),back:deep(tpl.back)};
    bulk.fields.forEach((f,fi)=>{const ci=bulk.map[fi];if(ci>=0)f.set(c[f.side],String(r[ci]??""))});
    out.push({card:c,n:Math.min(n,999)});
  });
  return out;
}
/* 作ったカードを入れる場所:選んでいるカードがテンプレートならその場所、そうでなければ今あるカードのあと */
function bulkRoom(){
  let order=deck.order.slice(),pos=0;
  if(bulk.kind==="selected"){
    const keep=el("bulkKeep").checked;pos=keep?order.lastIndexOf(bulk.tpl)+1:order.indexOf(bulk.tpl);
    if(!keep)order=order.filter(x=>x!==bulk.tpl);
  }else order.forEach((id,i)=>{if(!isBlankCard(id))pos=i+1});
  let tail=order.length;while(tail>pos&&isBlankCard(order[tail-1]))tail--;   // 後ろの空のカードは詰める
  order=order.slice(0,tail);
  return {order,pos,room:Math.max(0,MAX_PAGES*cardsPerPage()-order.length)};
}
function bulkExample(){
  const lang=window.CMMI18N&&CMMI18N.lang==="en"?"en":"ja",heads=bulk.fields.map(bulkHeadName);let rows;
  if(bulk.kind==="selected"||bulk.kind.startsWith("my:")){const c=bulkTemplateCard();rows=[bulk.fields.map(f=>String(f.get(c[f.side])??"")).concat("1")];heads.push(T("枚数"))}
  else{rows=BULK_EXAMPLES[bulk.kind][lang];if(rows[0].length>heads.length)heads.push(T("枚数"))}
  const cell=v=>/[\t\n"]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;
  return [heads,...rows].map(r=>r.map(cell).join("\t")).join("\n");
}
function openBulk(){
  const id=cardIdAt(currentPage,selected),own=bulkFields(deck.cards[id]).length>0;
  bulk={tpl:id,own,kind:null,auto:!own,csv:false,sig:null,map:[],qty:-1,fields:[]};
  setBulkKind(own?"selected":"playing");
  el("bulkText").value="";el("bulkKeep").checked=false;el("bulkHeader").checked=true;
  toggleSettings(false);closeMobilePanel();
  el("bulkModal").hidden=false;renderBulk();
  if(!mobileUIActive())el("bulkText").focus();
}
function closeBulk(){el("bulkModal").hidden=true;bulk=null}
function renderBulk(){
  if(!bulk)return;
  const table=bulkTable();
  if(bulk.auto&&table.head&&table.data.length){const g=bulkGuessKind(table.headers);if(g)setBulkKind(g)}
  {const box=el("bulkTpl"),selBtn=box.querySelector('[data-tpl="selected"]');box.querySelectorAll(".my-chip").forEach(x=>x.remove());
   allTemplates().forEach(t=>{const b=document.createElement("button");b.type="button";b.className="my-chip";b.dataset.tpl="my:"+t.id;b.textContent="★ "+t.name;box.insertBefore(b,selBtn)})}
  if(bulk.kind.startsWith("my:")&&!bulkMyTemplate())setBulkKind("playing");
  document.querySelectorAll("#bulkTpl [data-tpl]").forEach(b=>{b.setAttribute("aria-pressed",String(b.dataset.tpl===bulk.kind));if(b.dataset.tpl==="selected"){b.disabled=!bulk.own;b.title=bulk.own?"":T("選んでいるカードには文字を入れる場所がありません")}});
  const tplNo=deck.order.indexOf(bulk.tpl)+1;
  el("bulkLead").textContent=bulk.kind==="selected"
    ?T("「カード{n}」の見た目のまま、表の1行を1枚のカードにします。作ったカードは「カード{n}」の場所に並び、同じテンプレートでつながります。",{n:tplNo})
    :bulk.kind.startsWith("my:")
    ?T("マイテンプレート「{name}」で、表の1行を1枚のカードにします。作ったカードは今あるカードのあとに並び、このテンプレートでつながります。",{name:bulkMyTemplate().name})
    :T("{name}の基本の見た目で、表の1行を1枚のカードにします。作ったカードは今あるカードのあとに並びます。作ったカードは同じテンプレートでつながるので、どれか1枚の色などを変えると全部に反映されます。",{name:T(BULK_KINDS[bulk.kind].name)});
  el("bulkKeepRow").hidden=bulk.kind!=="selected";
  el("bulkText").placeholder=T("スプレッドシートやExcelで範囲をコピーして、ここに貼り付けます。1行目は見出し（カード名・テキスト・枚数 など）にします。");
  const sig=bulk.kind+"|"+table.headers.join("\u0001")+"|"+table.head;
  if(sig!==bulk.sig){const a=bulkAutoMap(bulk.fields,table.headers,table.head);bulk.map=a.map;bulk.qty=a.qty;bulk.sig=sig}
  const map=el("bulkMap");map.innerHTML="";
  if(!bulk.fields.length){
    const m=document.createElement("p");m.className="bulk-msg";m.textContent=T("このテンプレートには文字を入れる場所がありません。トランプ・トレカ・ワードゲームか、テキストボックスのあるテンプレートを選んでください。");map.appendChild(m);
  }
  const row=(label,value,none,onChange)=>{
    const l=document.createElement("label");l.className="bulk-map-label";l.textContent=label;
    const sel=document.createElement("select");
    sel.innerHTML=`<option value="-1">${esc(none)}</option>`+table.headers.map((hd,i)=>`<option value="${i}">${esc(hd)}</option>`).join("");
    sel.value=String(value<table.headers.length?value:-1);sel.addEventListener("change",()=>{onChange(Number(sel.value));renderBulk()});
    map.append(l,sel);
  };
  bulk.fields.forEach((f,fi)=>row(bulkFieldLabel(f),bulk.map[fi],T("テンプレートのまま"),v=>{bulk.map[fi]=v}));
  if(bulk.fields.length)row(T("枚数"),bulk.qty,T("すべて1枚"),v=>{bulk.qty=v});
  // 確認:最初の数枚
  const pv=el("bulkPreview");pv.innerHTML="";
  const cards=bulk.fields.length?bulkCards(table):[];
  const total=cards.reduce((a,c)=>a+c.n,0),{room}=bulkRoom();
  if(!cards.length){const m=document.createElement("p");m.className="bulk-msg";m.textContent=T("表を貼り付けると、ここに最初の数枚が表示されます。");pv.appendChild(m)}
  const side=bulk.fields.some((f,fi)=>f.side==="front"&&bulk.map[fi]>=0)||!bulk.fields.some((f,fi)=>bulk.map[fi]>=0)?"front":"back";
  const W=mobileUIActive()?72:84;
  cards.slice(0,6).forEach(c=>{
    const box=faceThumb(c.card[side],W);
    if(c.n>1){const q=document.createElement("span");q.className="bulk-qty";q.textContent="×"+c.n;box.appendChild(q)}
    pv.appendChild(box);
  });
  if(cards.length>6){const m=document.createElement("span");m.className="bulk-more";m.textContent=T("ほか{n}種類",{n:cards.length-6});pv.appendChild(m)}
  let sum=cards.length?T("{n}種類・合計{m}枚のカードを作ります。",{n:cards.length,m:total}):"";
  if(total>room)sum+=" "+T("最大{p}ページのため、{k}枚までしか作れません。",{p:MAX_PAGES,k:room});
  el("bulkSummary").textContent=sum;
  el("bulkApply").disabled=!cards.length||!room;
}
function applyBulk(){
  if(!bulk)return;
  const cards=bulkCards(bulkTable());if(!cards.length)return;
  const {order,pos,room}=bulkRoom(),made=[];
  if(!room)return;
  // 作ったカードをつなぐテンプレート
  let tid;
  if(bulk.kind==="selected"){const sc=deck.cards[bulk.tpl];if(sc.tpl&&deck.templates&&deck.templates[sc.tpl])tid=sc.tpl;else{tid=addTemplate(sc,uniqueTplName(suggestTplName(sc)),false);sc.tpl=tid}}
  else if(bulk.kind.startsWith("my:")){tid=bulk.kind.slice(3);if(!ensureTemplateInDeck(tid))tid=null}
  else tid=addTemplate(bulkTemplateCard(),uniqueTplName(T(BULK_KINDS[bulk.kind].name)),false);
  for(const c of cards){if(made.length>=room)break;const id=addCard(c.card.front,c.card.back);if(tid)deck.cards[id].tpl=tid;for(let i=0;i<c.n&&made.length<room;i++)made.push(id)}
  if(!made.length)return;
  deck.order=order.slice(0,pos).concat(made,order.slice(pos));
  closeBulk();syncPages();selectSlot(pos,"front");renderSheet();syncControls();
  showAppToast(T("{n}枚のカードを作りました",{n:made.length}),{duration:4000});
}
document.querySelectorAll(".open-bulk").forEach(b=>b.addEventListener("click",openBulk));
document.querySelectorAll("[data-bulk-close]").forEach(b=>b.addEventListener("click",closeBulk));
el("bulkTpl").addEventListener("click",e=>{const b=e.target.closest("[data-tpl]");if(!b||!bulk||b.disabled)return;bulk.auto=false;setBulkKind(b.dataset.tpl);renderBulk()});
el("bulkModal").addEventListener("click",e=>{if(e.target===el("bulkModal"))closeBulk()});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&bulk)closeBulk()});
el("bulkText").addEventListener("paste",()=>{if(bulk)bulk.csv=false});
el("bulkText").addEventListener("input",()=>renderBulk());
el("bulkHeader").addEventListener("change",()=>renderBulk());
el("bulkKeep").addEventListener("change",()=>renderBulk());
el("bulkApply").addEventListener("click",applyBulk);
el("bulkExample").addEventListener("click",()=>{
  if(!bulk)return;
  if(el("bulkText").value.trim()&&!confirm(T("貼り付けた内容を例に置き換えますか？")))return;
  bulk.auto=false;el("bulkText").value=bulkExample();el("bulkHeader").checked=true;bulk.csv=false;renderBulk();
});
/* 表のひな形:選んでいるテンプレートに合わせた見出しと例の行を、Excelでも文字化けしないCSVで渡す(書いたらそのまま読み込める) */
function bulkTemplateRows(){
  const lang=window.CMMI18N&&CMMI18N.lang==="en"?"en":"ja",heads=bulk.fields.map(bulkHeadName).concat(T("枚数")),w=heads.length;let rows;
  if(bulk.kind==="selected"||bulk.kind.startsWith("my:")){
    const c=bulkTemplateCard();
    rows=[1,2,3].map(r=>bulk.fields.map(f=>/count$/.test(f.kind)?String(r):String(f.get(c[f.side])??"")).concat("1"));
  }else rows=BULK_EXAMPLES[bulk.kind][lang].map(r=>{const x=r.slice(0,w);while(x.length<w)x.push(x.length===w-1?"1":"");return x});
  return [heads,...rows];
}
el("bulkTemplateDl")?.addEventListener("click",()=>{
  if(!bulk)return;
  const cell=v=>/[",\n\r]/.test(v)?'"'+String(v).replace(/"/g,'""')+'"':v;
  const csv="\ufeff"+bulkTemplateRows().map(r=>r.map(cell).join(",")).join("\r\n")+"\r\n";
  const name=bulk.kind.startsWith("my:")?(bulkMyTemplate()?.name||T("マイテンプレート")):bulk.kind==="selected"?T("選んでいるカード"):T(BULK_KINDS[bulk.kind].name);
  downloadBlob(new Blob([csv],{type:"text/csv;charset=utf-8"}),`${T("表のひな形")}_${String(name).replace(/[\\/:*?"<>|]/g,"_")}.csv`);
  showAppToast(T("表のひな形をダウンロードしました。書いたら「CSVファイルを読み込む」で読み込めます。"),{duration:5000});
});
el("bulkFileBtn").addEventListener("click",()=>el("bulkFile").click());
el("bulkFile").addEventListener("change",async e=>{
  const file=e.target.files[0];e.target.value="";if(!file||!bulk)return;
  try{
    const buf=await file.arrayBuffer();let text;
    try{text=new TextDecoder("utf-8",{fatal:true}).decode(buf)}catch(_){text=new TextDecoder("shift_jis").decode(buf)}   // Excelの日本語CSVはShift_JISのことがある
    el("bulkText").value=text;bulk.csv=!/\.tsv$/i.test(file.name);renderBulk();
  }catch(err){alert(T("CSVファイルを読み込めませんでした。"))}
});
document.addEventListener("cmm-langchange",()=>{if(bulk){bulk.builtin=null;if(bulk.kind!=="selected")bulk.fields=bulkFields(bulkTemplateCard());renderBulk()}});
/* ---- 両面印刷:表示する面・プリンタの両面設定・ウラ面のずれ補正 ---- */
const OFFSET_STEP={mm:.1,cm:.01,inch:.01,pt:.5,px:1};
function syncDuplexUI(){
  const on=layoutMode()==="both";
  el("duplexBar").hidden=!on;
  document.querySelectorAll(".m-duplex-field").forEach(f=>f.hidden=!on);
  if(!on)return;
  document.querySelectorAll("#duplexBar [data-view-side]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.viewSide===(viewSide==="back"?"back":"front"))));
  el("duplexBinding").value=printSettings.binding==="short"?"short":"long";
  ["X","Y"].forEach(a=>{const inp=el("backOffset"+a);inp.step=OFFSET_STEP[units.len]||.1;if(document.activeElement!==inp)inp.value=fmtLen(Number(printSettings["backOffset"+a])||0,false)});
  document.querySelectorAll(".unit-len-label").forEach(n=>n.textContent=LEN_UNITS[units.len].label);
  const lr=backFlipDir()==="horizontal",back=arrangement()==="back";
  const note=back?(lr?"ウラ面は、紙を左右に裏返したとき重なるように、左右を入れ替えて並べています。":"ウラ面は、紙を上下に裏返したとき重なるように、上下を入れ替えて並べています。")
                 :(lr?"ウラ面は、紙を左右に裏返したときオモテと重なる位置に並びます。最初は1枚だけ試し刷りしてください。":"ウラ面は、紙を上下に裏返したときオモテと重なる位置に並びます。最初は1枚だけ試し刷りしてください。");
  document.querySelectorAll(".duplex-note").forEach(n=>n.textContent=T(note));
}
document.querySelectorAll("#duplexBar [data-view-side]").forEach(b=>b.addEventListener("click",()=>{viewSide=b.dataset.viewSide;renderSheet();syncControls()}));
el("duplexBinding").addEventListener("change",e=>{
  const ref=slotAt(currentPage,selected);printSettings.binding=e.target.value;
  syncPages();selected=indexOfSlot(ref.slot,ref.side);renderSheet();syncControls();
});
["X","Y"].forEach(a=>el("backOffset"+a).addEventListener("change",e=>{
  const v=Number(e.target.value);printSettings["backOffset"+a]=Number.isFinite(v)?clamp(+(v*LEN_UNITS[units.len].k).toFixed(2),-20,20):0;
  e.target.blur();renderSheet();syncControls();
}));
/* ---- 枚数の操作 ---- */
function changeQty(n){const id=cardIdAt(currentPage,selected);if(setCardCount(id,n)){renderSheet();syncControls()}else syncControls()}
el("qtyMinus").addEventListener("click",()=>changeQty(cardCount(cardIdAt(currentPage,selected))-1));
el("qtyPlus").addEventListener("click",()=>changeQty(cardCount(cardIdAt(currentPage,selected))+1));
el("cardQty").addEventListener("change",e=>changeQty(e.target.value));
el("unlinkCard").addEventListener("click",()=>{unlinkSelected();renderSheet();syncControls()});
/* ---- 見本:テンプレートとオプションの使い方がわかる4枚 ---- */
function sampleDeck(){
  const back=()=>({...makePlain(),bgColor:"#22384f",bgBorderNone:true,
    frameTexts:[{...makeFrameText(0),text:"SAMPLE",style:{size:16,bold:true,italic:false,underline:false,color:"#22384f",colorNone:false},fillColor:"#f4efe2",borderColor:"#f4efe2",box:{x:15,y:41,w:70,h:18}}],
    shapes:[{...makeShape("star",0),fillColor:"#e4c62a",borderNone:true,box:{x:38,y:12,w:24,h:24*88/63}}]});
  const playing=(num,suit,color)=>({...makePlaying(),number:num,suit,numberColor:color});
  const tcg={type:"template",template:"tcg",name:T("ドラゴン"),desc:T("このカードを出したとき、山札からカードを1枚引く。"),image:null,bgColor:"#3a8dde",bgImage:null,bgBorderColor:"#222222",bgBorderWidth:1,bgBorderNone:true,bgBorderAlign:"inside",
    textColor:"#222222",borderColor:"#22384f",borderNone:false,panelColor:"#ffffff",horizontalLayout:1,tcgTopHeight:16,tcgMiddleHeight:50,tcgBottomHeight:28,
    nameStyle:{size:SIZE.tcgName,bold:true,italic:false},descStyle:{size:SIZE.tcgDesc,bold:false,italic:false},textBoxes:[],frameTexts:[],optionImages:[],shapes:[]};
  const word={type:"template",template:"word",main:T("ことば"),mainColor:"#22384f",mainStyle:{size:SIZE.word,bold:true,italic:false},bgColor:"#f4efe2",bgImage:null,bgBorderColor:"#22384f",bgBorderWidth:2,bgBorderNone:false,bgBorderAlign:"inside",textBoxes:[],frameTexts:[],optionImages:[],shapes:[]};
  const d={cards:{},order:[],templates:{},fmt:2,font:"gothic"};
  [playing("A","♠","#111111"),playing("7","♥","#d94a4a"),tcg,word].forEach(front=>{const id=newCardId();d.cards[id]={front:deep(front),back:back()};d.order.push(id)});
  return d;
}
async function openSample(){
  toggleSettings(false);
  if(!deck.order.every(isBlankCard)){
    if(autosaveFailed||!autosaveDb){if(!confirm(T("いまの作業を見本に置き換えますか？\n(元に戻すときは「取り消し」)")))return}
    else await beginNewProject();   // いまの作品は一覧に残して、見本は新しい作品として開く
  }
  el("paperSize").value="a4";el("paperOrientation").value="landscape";el("cardSize").value="poker";el("impositionMode").value="duplex";cardOrientation="portrait";
  deck=sampleDeck();currentPage=0;selected=0;lastArrangement=null;sheetTitle=T("見本");el("sheetTitleInput").value=sheetTitle;
  closeMobilePanel();setPaper();renderSheet();syncControls();
}
document.querySelectorAll(".open-sample").forEach(b=>b.addEventListener("click",openSample));
/* ---- 最初の画面「何を作る？」:空の作品のときに出す。選ぶと1ページぶんのカードが同じテンプレートでつながって並ぶ ---- */
let startDismissed=false,startSig="";
const START_FACES={playing:()=>makePlaying(),tcg:()=>makeTcg(),word:()=>makeWord(),plain:()=>makePlain()};
function syncStartChooser(blank){
  const box=el("startChooser");if(!box)return;
  const show=blank&&!startDismissed;box.hidden=!show;document.body.classList.toggle("start-open",show);
  if(!show)return;
  // カードの大きさ(見出しの選択と同じもの)
  const src=el("cardSize"),sel=el("startCardSize");
  if(sel.options.length!==src.options.length||[...sel.options].some((o,i)=>o.textContent!==src.options[i].textContent))sel.innerHTML=src.innerHTML;
  sel.value=src.value;
  // 小さな絵は大きさが変わったときだけ描き直す
  const sig=src.value+"|"+cardOrientation+"|"+customCard.w+"x"+customCard.h+"|"+(window.CMMI18N&&CMMI18N.lang);
  if(sig===startSig)return;startSig=sig;
  box.querySelectorAll(".start-tile[data-start]").forEach(t=>{const make=START_FACES[t.dataset.start],art=t.querySelector(".start-art");if(!make||!art)return;art.innerHTML="";art.appendChild(faceThumb(make(),mobileUIActive()?40:64))});
}
const PLAYING_NUMS=["A","2","3","4","5","6","7","8","9","10","J","Q","K"];
function startWith(kind){
  if(kind==="table"){openBulk();return}
  if(kind==="sample"){openSample();return}
  startDismissed=true;
  if(kind!=="plain"){
    const front=START_FACES[kind]();
    const tid=addTemplate({front,back:makePlain()},uniqueTplName(T(BULK_KINDS[kind].name)),false);
    deck.order.slice(0,cardsPerPage()).forEach((id,i)=>{applyTemplate(tid,id);if(kind==="playing")deck.cards[id].front.number=PLAYING_NUMS[i%13]});
    tplWatch=null;currentPage=0;selected=0;
    showAppToast(T("1ページぶん並べました。どれか1枚の色や配置を変えると、全部に反映されます。"),{duration:6000});
  }
  syncPages();renderSheet();syncControls();
}
document.querySelectorAll("#startTiles [data-start]").forEach(b=>b.addEventListener("click",()=>startWith(b.dataset.start)));
function dismissStart(){if(startDismissed)return;startDismissed=true;const blank=deck.order.every(isBlankCard);["emptyHint","mobileEmptyHint"].forEach(id=>{if(el(id))el(id).hidden=!blank});syncStartChooser(blank)}
el("startLater").addEventListener("click",dismissStart);
el("startOpenPdf")?.addEventListener("click",()=>el("loadPdf").click());
/* 以前の版(β)から来た人に、変わったところを伝える(このブラウザでは一度だけ) */
function showBetaNote(hadCustom){
  try{if(localStorage.getItem("pk-beta-note"))return;localStorage.setItem("pk-beta-note","1")}catch(_){}
  el("betaCustomNote").hidden=!hadCustom;el("betaModal").hidden=false;
}
document.querySelectorAll("[data-beta-close]").forEach(b=>b.addEventListener("click",()=>{el("betaModal").hidden=true}));
el("betaModal").addEventListener("click",e=>{if(e.target===el("betaModal"))el("betaModal").hidden=true});
el("startCardSize").addEventListener("change",e=>{const src=el("cardSize");src.value=e.target.value;src.dispatchEvent(new Event("change",{bubbles:true}));syncStartChooser(deck.order.every(isBlankCard))});
document.addEventListener("cmm-langchange",()=>{startSig="";syncStartChooser(deck.order.every(isBlankCard))});
/* ---- フォントの選択 ---- */
document.querySelectorAll("select.font-select[id]").forEach(x=>x.innerHTML=fontOptions(true));
el("autoFit")?.addEventListener("change",e=>{deck.autoFit=e.target.checked;renderSheet();syncControls()});
el("overAutoOn")?.addEventListener("click",()=>{deck.autoFit=true;renderSheet();syncControls()});
if(el("deckFont")){el("deckFont").innerHTML=fontOptions(false);el("deckFont").addEventListener("change",e=>{deck.font=e.target.value;renderSheet();syncControls()})}
[["playingFont","numberStyle"],["tcgNameFont","nameStyle"],["tcgDescFont","descStyle"],["wordMainFont","mainStyle"]].forEach(([id,key])=>el(id)?.addEventListener("change",e=>{
  updateSelected({[key]:{...(currentFaces()[selected][key]||{}),font:e.target.value}});
}));
/* ---- 設定(単位) ---- */
function applyUnits(){saveUnits();relabelLengths(document);updateFit();syncControls()}
if(el("unitLen")){el("unitLen").value=units.len;el("unitLen").addEventListener("change",e=>{units.len=e.target.value;applyUnits()})}
if(el("unitText")){el("unitText").value=units.text;el("unitText").addEventListener("change",e=>{units.text=e.target.value;applyUnits()})}
// ご意見・ご要望フォーム。使っている環境を「ご使用の環境」に入れて開く
const FEEDBACK_FORM="https://docs.google.com/forms/d/e/1FAIpQLSfvJ7wGWu429npbA55X5kqrXcCbYOyQaKBSF5m5vWAtzHPkgQ/viewform";
const FEEDBACK_ENV_ENTRY="entry.628110980";
const APP_VERSION="1.0";
function feedbackEnv(){
  const ua=navigator.userAgent||"";let m,br="その他のブラウザ";
  const touchMac=/Macintosh/.test(ua)&&navigator.maxTouchPoints>1;
  const os=/iPhone/.test(ua)?"iPhone":(/iPad/.test(ua)||touchMac)?"iPad":/Android/.test(ua)?"Android":/Windows/.test(ua)?"Windows":/CrOS/.test(ua)?"ChromeOS":/Mac/.test(ua)?"Mac":/Linux/.test(ua)?"Linux":"その他";
  if((m=ua.match(/Edg(?:A|iOS)?\/(\d+)/)))br="Edge "+m[1];
  else if((m=ua.match(/(?:CriOS|Chrome)\/(\d+)/)))br="Chrome "+m[1];
  else if((m=ua.match(/(?:FxiOS|Firefox)\/(\d+)/)))br="Firefox "+m[1];
  else if(/Safari/.test(ua)&&(m=ua.match(/Version\/(\d+(?:\.\d+)?)/)))br="Safari "+m[1];
  let standalone=false;try{standalone=matchMedia("(display-mode: standalone)").matches||navigator.standalone===true}catch(e){}
  const cards=deck&&deck.order?deck.order.length:0;
  return ["Ver."+APP_VERSION,os,br,"画面 "+innerWidth+"×"+innerHeight,"カード "+cards+"枚",navigator.language||"",standalone?"ホーム画面から":"ブラウザ"].filter(Boolean).join(" / ");
}
function openFeedback(){
  const url=FEEDBACK_FORM+"?usp=pp_url&"+FEEDBACK_ENV_ENTRY+"="+encodeURIComponent(feedbackEnv());
  window.open(url,"_blank","noopener");
  if(typeof toggleSettings==="function")toggleSettings(false);
}
document.addEventListener("click",e=>{if(e.target.closest(".open-feedback")){e.preventDefault();openFeedback()}});
function toggleSettings(force){const pop=el("settingsPop");if(!pop)return;const open=force??pop.hidden;pop.hidden=!open;el("settingsBtn")?.setAttribute("aria-expanded",String(open))}
el("settingsBtn")?.addEventListener("click",e=>{e.stopPropagation();toggleSettings()});
document.addEventListener("click",e=>{const pop=el("settingsPop");if(pop&&!pop.hidden&&!e.target.closest("#settingsPop,#settingsBtn"))toggleSettings(false)});
el("dupPage").addEventListener("click",()=>duplicatePage(currentPage));
el("deletePage").addEventListener("click",()=>deletePage(currentPage));

function getProject(){
  padOrder();
  return {app:"card-mock-maker",version:2,paperSize:el("paperSize").value,paperOrientation:el("paperOrientation").value,cardSize:el("cardSize").value,customCard,impositionMode:el("impositionMode").value,cardOrientation,sheetTitle,printSettings,deck};
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
  const out={cards:{},order:[],templates:{},fmt:2,font:(d&&d.font)||"system"};
  Object.entries((d&&d.templates)||{}).forEach(([tid,t])=>{if(t)out.templates[tid]={name:String(t.name||T("テンプレート")),front:t.front||makePlain(),back:t.back||makePlain(),lib:!!t.lib}});
  (d&&d.order||[]).forEach(id=>{const c=d.cards&&d.cards[id];if(!c)return;if(!out.cards[id]){out.cards[id]={front:c.front||makePlain(),back:c.back||makePlain()};if(c.tpl&&out.templates[c.tpl])out.cards[id].tpl=c.tpl}out.order.push(id)});
  const holders=[...Object.values(out.cards),...Object.values(out.templates)];
  const faces=holders.flatMap(c=>[c.front,c.back]);
  migrateBgBorders(migrateGenericTextBoxes({pages:[faces]}));
  holders.forEach(c=>{const pg=[c.front,c.back];normalizeFaces([pg]);c.front=pg[0];c.back=pg[1]});
  if(!(d&&d.fmt>=2))holders.forEach(c=>{migrateFaceUnits(c.front);migrateFaceUnits(c.back)});
  return out;
}
function restoreProject(p){
  if(!p.deck&&!p.pages)throw new Error("invalid project");
  deck=p.deck?normalizeDeck(deep(p.deck)):deckFromPages(deep(p.pages),p.impositionMode);
  printSettings={binding:"long",backOffsetX:0,backOffsetY:0,...(p.printSettings||{})};delete printSettings.backFlip;
  sheetTitle=p.sheetTitle||"";
  customCard=normCustom(p.customCard);
  el("paperSize").value=p.paperSize||"a4";el("paperOrientation").value=p.paperOrientation||"landscape";el("cardSize").value=CARD_SIZES[p.cardSize]||p.cardSize==="custom"?p.cardSize:"poker";el("cardSize").dataset.prev=el("cardSize").value;relabelLengths();el("impositionMode").value=p.impositionMode||"duplex";el("impositionMode").dataset.prev=el("impositionMode").value;cardOrientation=p.cardOrientation||((el("impositionMode").value!=="duplex")?el("paperOrientation").value:(el("paperOrientation").value==="portrait"?"landscape":"portrait"));el("sheetTitleInput").value=sheetTitle;
  currentPage=0;selected=0;lastArrangement=null;syncPages();setupAllColorInputs();
  tplWatch=null;setPaper();renderSheet();syncControls();
  initHistory();
  importLibraryFromDeck().then(n=>{if(n)showAppToast(T("この作品のマイテンプレートを{n}個、このブラウザに追加しました",{n}),{duration:5000})}).catch(()=>{});
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
/* PDFに描く前に、写真を枠の形に切り抜いた画像へ置き換える
   (html2canvas は object-fit に対応しておらず、写真が引き伸ばされてしまうため) */
async function flattenImagesForRaster(root,scale){
  for(const img of [...root.querySelectorAll("img")]){
    try{
      if(!img.complete)await img.decode().catch(()=>{});
      const fit=getComputedStyle(img).objectFit,w=img.offsetWidth,h=img.offsetHeight;
      if(!w||!h||!img.naturalWidth)continue;
      const c=document.createElement("canvas");c.width=Math.max(1,Math.round(w*scale));c.height=Math.max(1,Math.round(h*scale));
      const ctx=c.getContext("2d");ctx.imageSmoothingQuality="high";
      const iw=img.naturalWidth,ih=img.naturalHeight,bw=c.width,bh=c.height;
      if(fit==="cover"){const k=Math.max(bw/iw,bh/ih),sw=bw/k,sh=bh/k,pos=(getComputedStyle(img).objectPosition||"").split(/\s+/),pct=v=>/%$/.test(v||"")?parseFloat(v)/100:.5;   // 見せる場所(object-position)も写す
        ctx.drawImage(img,(iw-sw)*pct(pos[0]),(ih-sh)*pct(pos[1]),sw,sh,0,0,bw,bh)}
      else if(fit==="contain"||fit==="scale-down"){const k=Math.min(bw/iw,bh/ih,fit==="scale-down"?scale:Infinity),dw=iw*k,dh=ih*k;ctx.drawImage(img,(bw-dw)/2,(bh-dh)/2,dw,dh)}
      else ctx.drawImage(img,0,0,bw,bh);
      // 「.xxx img{…}」のようにタグ名で当たっている配置を引き継ぐため、計算済みの値を写す
      const cs=getComputedStyle(img);c.className=img.className;
      ["position","top","right","bottom","left","margin","display","transform","transformOrigin","borderRadius","zIndex","opacity","verticalAlign","boxSizing"].forEach(k=>{c.style[k]=cs[k]});
      if(c.style.display==="inline")c.style.display="block";
      c.style.width=w+"px";c.style.height=h+"px";
      img.replaceWith(c);
    }catch(err){console.warn(err)}
  }
}
/* html2canvas が描けない指定を、描ける形に置き換える(PDF書き出し用のコピーにだけ行う)
   - 内側の線(inset の box-shadow)→ 枠線を持つ重ね板(そのままだと黒く塗りつぶされる)
   - 縦書き(writing-mode)→ 1文字ずつ縦に並べて描いた画像 */
function fixShadowsForRaster(root){
  root.querySelectorAll("*").forEach(n=>{
    const bs=n.style&&n.style.boxShadow;if(!bs||!/inset/.test(bs))return;
    const parts=bs.split(/,(?![^(]*\))/),keep=[];
    parts.forEach(part=>{
      if(!/inset/.test(part)){keep.push(part);return}
      const cm=part.match(/rgba?\([^)]*\)|#[0-9a-f]{3,8}\b|transparent/i),color=cm?cm[0]:"#222";
      const lens=part.replace(cm?cm[0]:"","").replace("inset","").trim().split(/\s+/).filter(Boolean),spread=lens[3]||"0";
      const o=document.createElement("div");
      o.style.cssText=`position:absolute;inset:0;border:${spread} solid ${color};box-sizing:border-box;pointer-events:none;z-index:60;border-radius:inherit`;
      n.appendChild(o);
    });
    n.style.boxShadow=keep.join(",")||"none";
    if(getComputedStyle(n).position==="static")n.style.position="relative";
  });
}
const V_ROTATE=new Set([..."ー―‐〜～…‥（）「」『』【】〈〉《》［］｛｝()[]{}<>-=~_"]),V_SHIFT=new Set([..."、。，．"]);
function drawVerticalText(el,scale){
  const cs=getComputedStyle(el),w=el.clientWidth,h=el.clientHeight;if(!w||!h)return;
  const size=parseFloat(cs.fontSize)||16,font=`${cs.fontStyle} ${cs.fontWeight} ${size}px ${cs.fontFamily}`,box=el.getBoundingClientRect();
  // ブラウザが縦書きで並べた1文字ずつの位置を測り、その場所に描く(折り返しや中央寄せをそのまま再現)
  const glyphs=[],walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let node;
  while((node=walker.nextNode())){
    const text=node.nodeValue;
    for(let k=0;k<text.length;){
      const cp=text.codePointAt(k),len=cp>0xffff?2:1,ch=text.slice(k,k+len);
      if(ch.trim()){const r=document.createRange();r.setStart(node,k);r.setEnd(node,k+len);const b=r.getBoundingClientRect();if(b.width||b.height)glyphs.push({ch,x:b.left-box.left+b.width/2,y:b.top-box.top+b.height/2})}
      k+=len;
    }
  }
  const c=document.createElement("canvas");c.width=Math.round(w*scale);c.height=Math.round(h*scale);
  const ctx=c.getContext("2d");ctx.scale(scale,scale);ctx.font=font;ctx.fillStyle=cs.color;ctx.textAlign="center";ctx.textBaseline="middle";
  glyphs.forEach(g=>{
    ctx.save();ctx.translate(g.x,g.y);
    if(V_ROTATE.has(g.ch))ctx.rotate(Math.PI/2);
    if(V_SHIFT.has(g.ch))ctx.translate(size*.55,-size*.55);
    ctx.fillText(g.ch,0,0);ctx.restore();
  });
  c.style.cssText="position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none";
  el.style.writingMode="horizontal-tb";el.textContent="";el.appendChild(c);
}
async function prepareForRaster(root,scale){
  await flattenImagesForRaster(root,scale);
  fixShadowsForRaster(root);
  root.querySelectorAll(".word-main.vertical").forEach(e=>{if(getComputedStyle(e).writingMode.startsWith("vertical"))drawVerticalText(e,scale)});
}
/* 約300dpi。ただし端末が扱える大きさ(約1600万画素)を超えないように */
function rasterScale(sheet){const w=sheet.offsetWidth||1,h=sheet.offsetHeight||1;return Math.min(300/96,Math.sqrt(16e6/(w*h)))}
async function buildEditablePdf(){
  if(!window.html2canvas || !window.PDFLib) throw new Error(T("PDFライブラリを読み込めませんでした。インターネット接続を確認してください。"));
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
      staging.appendChild(sheet);fitTexts(sheet,false);

      const scale=rasterScale(sheet),hasPhoto=!!sheet.querySelector("img");
      await prepareForRaster(sheet,scale);
      const canvas=await html2canvas(sheet,{backgroundColor:"#ffffff",scale,useCORS:true,logging:false});
      // 写真があるページはJPEG(軽い)、文字と図形だけならPNG(にじまない)
      const img=hasPhoto?await pdf.embedJpg(canvas.toDataURL("image/jpeg",.92)):await pdf.embedPng(canvas.toDataURL("image/png"));
      canvas.width=canvas.height=0;
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

/* ---- マイテンプレート:このブラウザの保存(IndexedDB)と、一覧の画面 ---- */
const TPL_DB="cmm-templates";let myLibrary=[],libReady=false;
function tplDb(){return new Promise((ok,ng)=>{if(!window.indexedDB)return ng(new Error("IndexedDB unavailable"));const r=indexedDB.open(TPL_DB,1);r.onupgradeneeded=()=>{if(!r.result.objectStoreNames.contains("t"))r.result.createObjectStore("t",{keyPath:"id"})};r.onsuccess=()=>ok(r.result);r.onerror=()=>ng(r.error)})}
async function tplStore(mode,fn){const db=await tplDb();try{return await new Promise((ok,ng)=>{const tx=db.transaction("t",mode),req=fn(tx.objectStore("t"));tx.oncomplete=()=>ok(req&&req.result);tx.onerror=tx.onabort=()=>ng(tx.error)})}finally{db.close()}}
async function loadLibrary(){
  try{const rows=await tplStore("readonly",st=>st.getAll());myLibrary=(rows||[]).map(r=>{const c=JSON.parse(r.card);return {id:r.id,name:r.name,created:r.created||0,front:c.front,back:c.back}}).sort((a,b)=>a.created-b.created);libReady=true}
  catch(err){console.warn(err);myLibrary=[];libReady=false}
}
async function putLibraryItem(item){
  const old=myLibrary.find(x=>x.id===item.id),created=old?old.created:Date.now();
  await tplStore("readwrite",st=>st.put({id:item.id,name:item.name,created,updated:Date.now(),card:JSON.stringify({front:item.front,back:item.back})}));
  const rec={id:item.id,name:item.name,created,front:deep(item.front),back:deep(item.back)};
  if(old)Object.assign(old,rec);else myLibrary.push(rec);
}
async function saveToLibrary(tid){const t=deck.templates&&deck.templates[tid];if(!t)return;await putLibraryItem({id:tid,...t});t.lib=true}
async function removeFromLibrary(tid){await tplStore("readwrite",st=>st.delete(tid));myLibrary=myLibrary.filter(x=>x.id!==tid)}
const libTimers={};
function scheduleLibrarySync(tid){clearTimeout(libTimers[tid]);libTimers[tid]=setTimeout(()=>saveToLibrary(tid).catch(e=>console.warn(e)),800)}
/* 作品を開いたとき:作品の中の「ブラウザに保存」したテンプレートが、このブラウザになければ加える(PDFで別の端末に持っていったとき) */
async function importLibraryFromDeck(){
  if(!libReady)await loadLibrary();if(!libReady)return 0;let n=0;
  for(const [tid,t] of Object.entries(deck.templates||{}))if(t.lib&&!myLibrary.some(x=>x.id===tid)){try{await saveToLibrary(tid);n++}catch(e){console.warn(e)}}
  return n;
}
function allTemplates(){
  const out=Object.entries(deck.templates||{}).map(([id,t])=>({id,name:t.name,front:t.front,back:t.back,inProject:true,lib:!!t.lib&&myLibrary.some(x=>x.id===id)}));
  myLibrary.forEach(x=>{if(!out.some(o=>o.id===x.id))out.push({id:x.id,name:x.name,front:x.front,back:x.back,inProject:false,lib:true})});
  return out;
}
function ensureTemplateInDeck(tid){
  deck.templates=deck.templates||{};if(deck.templates[tid])return true;
  const x=myLibrary.find(y=>y.id===tid);if(!x)return false;
  deck.templates[tid]={name:x.name,front:deep(x.front),back:deep(x.back),lib:true};return true;
}
/* 面の小さな絵(一括作成の確認・テンプレートの一覧) */
function faceThumb(face,W,opt={}){
  const fm=opt.fm||faceMM(),land=opt.land??isLandscapeCard(),k=W/(fm.w*MM_TO_PX),box=document.createElement("div");
  box.className="bulk-thumb "+(land?"landscape-card":"portrait-card")+" card-size-"+(opt.size||el("cardSize").value);
  box.style.width=W+"px";box.style.height=Math.round(fm.h*MM_TO_PX*k)+"px";
  const f=document.createElement("div");f.className="face";f.style.width=fm.w*MM_TO_PX+"px";f.style.height=fm.h*MM_TO_PX+"px";f.style.transform=`scale(${k})`;
  box.appendChild(f);renderFace(f,face||makePlain(),false,-1);return box;
}
/* 面の種類「マイテンプレート」の選択肢(小さな絵と名前) */
let myTplPick=null,myTplSig="";
function syncMyTplPicker(card,t,pickOnly){
  const show=pickOnly;el("myTplPicker").classList.toggle("hidden",!show);
  el("tplStatus").hidden=!t;
  if(t){const n=tplCount(card.tpl);el("tplStatusText").textContent=n>1?T("見た目を変えると、テンプレート「{name}」の{n}枚すべてに反映されます。文字はこのカードだけ。",{name:t.name,n})
    :T("テンプレート「{name}」を使っています。ほかのカードにも使うと、見た目を変えたときに全部に反映されます。",{name:t.name})}
  if(!show)return;
  const items=allTemplates();el("myTplEmpty").hidden=items.length>0;
  const sig=[card&&card.tpl,el("cardSize").value,cardOrientation,window.CMMI18N&&CMMI18N.lang,...items.map(x=>x.id+"="+x.name+"="+styleOf(x.front))].join("|");
  if(sig===myTplSig)return;myTplSig=sig;
  const wrap=el("myTplChoices");wrap.innerHTML="";
  items.forEach(x=>{
    const on=!!(card&&card.tpl===x.id),b=document.createElement("button");b.type="button";b.className="mytpl-choice"+(on?" current":"");b.setAttribute("aria-pressed",String(on));
    b.append(faceThumb(x.front,46));const nm=document.createElement("span");nm.textContent=x.name;b.appendChild(nm);
    b.addEventListener("click",()=>{if(!on)useTemplate(x.id)});wrap.appendChild(b);
  });
}
function openTplModal(){
  toggleSettings(false);closeMobilePanel();el("tplModal").hidden=false;renderTplModal();
  if(!libReady)loadLibrary().then(()=>{if(!el("tplModal").hidden)renderTplModal()});
}
/* テンプレートとして保存(名前をつけるだけの小さな画面) */
function openTplSave(){
  const id=cardIdAt(currentPage,selected),card=deck.cards[id],blank=isBlankCard(id),cur=card&&card.tpl&&deck.templates&&deck.templates[card.tpl];
  toggleSettings(false);
  el("tplName").value=uniqueTplName(suggestTplName(card));el("tplName").disabled=el("tplSaveBtn").disabled=blank;
  el("tplSaveNote").textContent=blank?T("空のカードはテンプレートにできません。カードを作ってから保存してください。")
    :cur?T("このカードはテンプレート「{name}」を使っています。保存すると、新しいテンプレートとして分かれます。",{name:cur.name}):"";
  const th=el("tplSaveThumbs");th.innerHTML="";if(card){th.append(faceThumb(card.front,64));if(!isSingleMode())th.append(faceThumb(card.back,64))}
  el("tplSaveModal").hidden=false;
  if(!blank&&!mobileUIActive()){el("tplName").focus();el("tplName").select()}
}
function closeTplSave(){el("tplSaveModal").hidden=true}
function closeTplModal(){el("tplModal").hidden=true}
function renderTplModal(){
  const id=cardIdAt(currentPage,selected),card=deck.cards[id],cur=card&&card.tpl&&deck.templates&&deck.templates[card.tpl];
  const list=el("tplList");list.innerHTML="";
  const items=allTemplates();
  if(!items.length){const m=document.createElement("p");m.className="tpl-note";m.textContent=T("まだありません。カードの見た目を整えたら、「面」の「テンプレートとして保存」で作れます。");list.appendChild(m)}
  items.forEach(t=>{
    const row=document.createElement("div");row.className="tpl-item"+(cur&&card.tpl===t.id?" current":"");
    const th=document.createElement("div");th.className="tpl-thumbs";th.append(faceThumb(t.front,48));if(!isSingleMode())th.append(faceThumb(t.back,48));
    const info=document.createElement("div");info.className="tpl-info";
    const name=document.createElement("input");name.type="text";name.maxLength=40;name.value=t.name;name.className="tpl-name";name.setAttribute("aria-label",T("テンプレートの名前"));
    name.addEventListener("change",()=>renameTemplate(t.id,name.value));
    const meta=document.createElement("div");meta.className="tpl-meta";
    meta.textContent=[t.inProject?T("この作品で{n}枚",{n:tplCount(t.id)}):T("この作品では未使用"),t.lib?T("ブラウザに保存済み"):T("この作品だけ")].join(" · ");
    const acts=document.createElement("div");acts.className="tpl-acts";
    const btn=(label,fn,cls)=>{const x=document.createElement("button");x.type="button";x.className="mini"+(cls?" "+cls:"");x.textContent=label;x.addEventListener("click",fn);acts.appendChild(x);return x};
    btn(T("選んでいるカードに使う"),()=>useTemplate(t.id));
    if(!t.lib)btn(T("ブラウザにも保存"),async()=>{try{await saveToLibrary(t.id);renderSheet();renderTplModal()}catch(e){alert(T("ブラウザに保存できませんでした。"))}});
    btn(T("削除"),()=>deleteTemplate(t.id),"tpl-del");
    info.append(name,meta,acts);row.append(th,info);list.appendChild(row);
  });
}
async function saveTemplateFromSelected(){
  const id=cardIdAt(currentPage,selected),card=deck.cards[id];if(!card||isBlankCard(id))return;
  const name=el("tplName").value.trim()||uniqueTplName(suggestTplName(card)),tid=addTemplate(card,name,false);
  card.tpl=tid;tplWatch=null;myTplPick=null;
  let msg=T("テンプレート「{name}」を保存しました。面の種類の「マイテンプレート」から使えます。",{name});
  try{await saveToLibrary(tid)}catch(e){console.warn(e);msg=T("ブラウザには保存できませんでした（この作品の中には保存されています）。")}
  closeTplSave();renderSheet();syncControls();showAppToast(msg,{duration:5000});
}
function useTemplate(tid){
  if(!ensureTemplateInDeck(tid))return;
  const id=cardIdAt(currentPage,selected);applyTemplate(tid,id);tplWatch=null;myTplPick=null;
  closeTplModal();syncPages();renderSheet();syncControls();
  showAppToast(T("テンプレート「{name}」を使いました",{name:deck.templates[tid].name}),{duration:4000});
}
async function renameTemplate(tid,v){
  const name=String(v||"").trim();if(!name){renderTplModal();return}
  const t=deck.templates&&deck.templates[tid],x=myLibrary.find(y=>y.id===tid);
  if(t){t.name=name;renderSheet();syncControls()}
  try{if(x)await putLibraryItem({...(t||x),id:tid,name})}catch(e){console.warn(e)}
  renderTplModal();
}
async function deleteTemplate(tid){
  const t=(deck.templates||{})[tid]||myLibrary.find(x=>x.id===tid);if(!t)return;
  const n=deck.templates&&deck.templates[tid]?tplCount(tid):0;
  if(!confirm(n?T("テンプレート「{name}」を削除しますか？\nこの作品の{n}枚はテンプレートから外れます（見た目はそのまま）。",{name:t.name,n}):T("テンプレート「{name}」を削除しますか？",{name:t.name})))return;
  if(deck.templates&&deck.templates[tid]){delete deck.templates[tid];for(const cid in deck.cards)if(deck.cards[cid].tpl===tid)delete deck.cards[cid].tpl}
  try{if(myLibrary.some(x=>x.id===tid))await removeFromLibrary(tid)}catch(e){console.warn(e)}
  tplWatch=null;renderSheet();syncControls();renderTplModal();
}
document.querySelectorAll(".open-tpl").forEach(b=>b.addEventListener("click",openTplModal));
el("tplSaveQuick").addEventListener("click",openTplSave);
document.querySelectorAll("[data-tpl-close]").forEach(b=>b.addEventListener("click",closeTplModal));
document.querySelectorAll("[data-tplsave-close]").forEach(b=>b.addEventListener("click",closeTplSave));
el("tplModal").addEventListener("click",e=>{if(e.target===el("tplModal"))closeTplModal()});
el("tplSaveModal").addEventListener("click",e=>{if(e.target===el("tplSaveModal"))closeTplSave()});
document.addEventListener("keydown",e=>{if(e.key!=="Escape")return;if(!el("tplSaveModal").hidden)closeTplSave();else if(!el("tplModal").hidden)closeTplModal()});
el("tplName").addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.isComposing){e.preventDefault();saveTemplateFromSelected()}});
el("tplSaveBtn").addEventListener("click",saveTemplateFromSelected);
el("tplUnlink").addEventListener("click",()=>{const c=deck.cards[cardIdAt(currentPage,selected)];if(c&&c.tpl){delete c.tpl;tplWatch=null;renderSheet();syncControls()}});
document.addEventListener("cmm-langchange",()=>{if(!el("tplModal").hidden)renderTplModal()});
loadLibrary().then(()=>syncControls());

/* ---- 画像で書き出す:カード1枚ずつのPNGをZIPに ---- */
const CRC_TABLE=(()=>{const t=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0}return t})();
function crc32(u8){let c=0xFFFFFFFF;for(let i=0;i<u8.length;i++)c=CRC_TABLE[(c^u8[i])&255]^(c>>>8);return (c^0xFFFFFFFF)>>>0}
/* 圧縮なし(PNGはもともと圧縮済み)のZIP。ファイル名はUTF-8 */
function makeZip(files){
  const enc=new TextEncoder(),parts=[],central=[],d=new Date();let offset=0;
  const time=(d.getHours()<<11)|(d.getMinutes()<<5)|(d.getSeconds()>>1),date=((d.getFullYear()-1980)<<9)|((d.getMonth()+1)<<5)|d.getDate();
  for(const f of files){
    const name=enc.encode(f.name),data=f.data,crc=crc32(data);
    const lh=new DataView(new ArrayBuffer(30));
    [[0,0x04034b50,4],[4,20,2],[6,0x0800,2],[8,0,2],[10,time,2],[12,date,2],[14,crc,4],[18,data.length,4],[22,data.length,4],[26,name.length,2],[28,0,2]].forEach(([o,v,n])=>n===4?lh.setUint32(o,v,true):lh.setUint16(o,v,true));
    parts.push(lh.buffer,name,data);
    const ch=new DataView(new ArrayBuffer(46));
    [[0,0x02014b50,4],[4,20,2],[6,20,2],[8,0x0800,2],[10,0,2],[12,time,2],[14,date,2],[16,crc,4],[20,data.length,4],[24,data.length,4],[28,name.length,2],[30,0,2],[32,0,2],[34,0,2],[36,0,2],[38,0,4],[42,offset,4]].forEach(([o,v,n])=>n===4?ch.setUint32(o,v,true):ch.setUint16(o,v,true));
    central.push(ch.buffer,name);
    offset+=30+name.length+data.length;
  }
  const size=central.reduce((a,b)=>a+b.byteLength,0),end=new DataView(new ArrayBuffer(22));
  end.setUint32(0,0x06054b50,true);end.setUint16(8,files.length,true);end.setUint16(10,files.length,true);end.setUint32(12,size,true);end.setUint32(16,offset,true);
  return new Blob([...parts,...central,end.buffer],{type:"application/zip"});
}
function downloadBlob(blob,name){const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000)}
function safeFileName(v){return String(v||"").replace(/[\\/:*?"<>|\u0000-\u001f]/g,"_").trim().slice(0,60)}
const canvasBytes=c=>new Promise((ok,ng)=>c.toBlob(b=>b?b.arrayBuffer().then(x=>ok(new Uint8Array(x)),ng):ng(new Error("toBlob")),"image/png"));
/* 1つの面を画像にする(用紙の上と同じ見た目。切り取り線は描かない) */
async function renderFaceCanvas(face,scale,staging){
  const fm=faceMM(),g=document.createElement("div");
  g.className="sheet-grid single-mode export-face "+(isLandscapeCard()?"landscape-card":"portrait-card")+" card-size-"+el("cardSize").value;
  applyCardGeometry(g);
  g.style.setProperty("--pair-w",fm.w+"mm");g.style.setProperty("--pair-h",fm.h+"mm");
  g.style.gridTemplateColumns="var(--face-w)";g.style.gridTemplateRows="var(--face-h)";
  const pair=document.createElement("div");pair.className="pair";const f=document.createElement("div");f.className="face";
  pair.appendChild(f);g.appendChild(pair);staging.appendChild(g);
  try{
    renderFace(f,face,false,-1);fitTexts(g,false);
    await prepareForRaster(g,scale);
    return await html2canvas(f,{backgroundColor:"#ffffff",scale,width:fm.w*MM_TO_PX,height:fm.h*MM_TO_PX,useCORS:true,logging:false});
  }finally{g.remove()}
}
/* 書き出すカード:空のカードは除き、同じカードは1種類にまとめて枚数を数える */
function exportList(){
  const out=[],seen=new Map();
  deck.order.forEach(id=>{if(isBlankCard(id))return;if(seen.has(id)){seen.get(id).n++;return}const it={id,n:1};seen.set(id,it);out.push(it)});
  return out;
}
let exportBusy=false,exportCancel=false;
function exportKind(){return document.querySelector('input[name="exportKind"]:checked')?.value||"cards"}
/* ---- オンライン用の山札:画像(名前はなんでもよく、中身のSHA-256で見分けられる)と、山札のXMLをZIPに ----
   XMLは「山札(card-stack)の中にカード(card)」の形。カードはウラ向きで、オモテ・ウラの画像は画像のSHA-256で指す */
const faceSig=f=>JSON.stringify(f,(k,v)=>k==="id"?undefined:packImages(k,v));
function deckGroups(){
  const mode=el("deckGroup").value,groups=new Map();
  exportList().forEach(it=>{
    const c=deck.cards[it.id];let key="all",name=null;
    if(mode==="tpl"){const t=c.tpl&&deck.templates&&deck.templates[c.tpl];key=t?c.tpl:"_";name=t?t.name:T("そのほか")}
    else if(mode==="back")key=faceSig(isSingleMode()?makePlain():c.back);
    if(!groups.has(key))groups.set(key,{name,items:[]});
    groups.get(key).items.push(it);
  });
  const arr=[...groups.values()],base=sheetTitle||T("山札");
  arr.forEach((g,i)=>{if(!g.name)g.name=arr.length>1?`${base} ${i+1}`:base});
  return arr;
}
/* カードの名前と本文(山札の中のカードの名前・詳細に入れる) */
function cardTexts(card,no){
  const f=card.front||{},texts=[];let name="";
  if(f.type==="template"){
    if(f.template==="tcg"){name=String(f.name||"").trim();if(String(f.desc||"").trim())texts.push(String(f.desc).trim())}
    else if(f.template==="word")name=String(f.main||"").trim();
    else if(f.template==="playing")name=`${f.number??""}${f.suit??""}`.trim();
  }
  [...(f.textBoxes||[]),...(f.frameTexts||[])].forEach(x=>{const v=String(x&&x.text||"").trim();if(v)texts.push(v)});
  if(!name&&texts.length)name=texts.shift().split("\n")[0];
  return {name:(name||T("カード{n}",{n:no})).slice(0,60),detail:texts.join("\n")};
}
const xmlEsc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function stackXml(name,cards,size){
  const card=c=>`<card location.name="table" location.x="0" location.y="0" posZ="0" state="1" rotate="0" owner="" zindex="0"><data name="card"><data name="image"><data type="image" name="imageIdentifier"></data><data type="image" name="front">${c.front}</data><data type="image" name="back">${c.back}</data></data><data name="common"><data name="name">${xmlEsc(c.name)}</data><data name="size">${size}</data></data><data name="detail">${c.detail?`<data type="note" name="${xmlEsc(T("テキスト"))}">${xmlEsc(c.detail)}</data>`:""}</data></data></card>`;
  return `<?xml version="1.0" encoding="UTF-8"?>\n<card-stack location.name="table" location.x="0" location.y="0" posZ="0" rotate="0" zindex="0" owner="" isShowTotal="true"><data name="card-stack"><data name="image"><data type="image" name="imageIdentifier"></data></data><data name="common"><data name="name">${xmlEsc(name)}</data></data><data name="detail"></data></data><node name="cardRoot">${cards.map(card).join("")}</node></card-stack>`;
}
async function sha256Hex(bytes){const h=new Uint8Array(await crypto.subtle.digest("SHA-256",bytes));return [...h].map(b=>b.toString(16).padStart(2,"0")).join("")}
const canvasBlob=(c,type,q)=>new Promise((ok,ng)=>c.toBlob(b=>b?ok(b):ng(new Error("toBlob")),type,q));
/* 1枚2MBまでのツールが多いので、PNGが重いとき(写真など)はJPEGにする */
async function deckImageBytes(c){
  const LIMIT=1.8*1024*1024;
  let b=await canvasBlob(c,"image/png");if(b.size<=LIMIT)return {bytes:new Uint8Array(await b.arrayBuffer()),ext:"png"};
  for(const q of [.9,.8,.7]){b=await canvasBlob(c,"image/jpeg",q);if(b.size<=LIMIT)break}
  return {bytes:new Uint8Array(await b.arrayBuffer()),ext:"jpg"};
}
async function buildDeckZip(staging,progress){
  const groups=deckGroups(),size=Number(el("deckSize").value)||2,fm=faceMM(),scale=(Number(el("deckRes").value)||480)/(fm.w*MM_TO_PX);
  const single=isSingleMode(),cache=new Map(),images=[],xmls=[];
  const faces=new Set();groups.forEach(g=>g.items.forEach(it=>{const c=deck.cards[it.id];faces.add(faceSig(c.front));faces.add(faceSig(single?makePlain():c.back))}));
  const total=faces.size;let done=0;
  const imageId=async face=>{
    const k=faceSig(face);if(cache.has(k))return cache.get(k);
    if(exportCancel)throw new Error("cancel");progress(++done,total);
    const cv=await renderFaceCanvas(face,scale,staging),{bytes,ext}=await deckImageBytes(cv);cv.width=cv.height=0;
    const id=await sha256Hex(bytes);images.push({name:`${String(images.length+1).padStart(3,"0")}.${ext}`,data:bytes});cache.set(k,id);return id;
  };
  let no=0;
  for(const [gi,g] of groups.entries()){
    const cards=[];
    for(const it of g.items){
      const c=deck.cards[it.id],front=await imageId(c.front),back=await imageId(single?makePlain():c.back),tx=cardTexts(c,++no);
      for(let k=0;k<it.n;k++)cards.push({front,back,...tx});
    }
    xmls.push({name:`deck_${gi+1}.xml`,data:new TextEncoder().encode(stackXml(g.name,cards,size))});
  }
  return makeZip([...images,...xmls]);   // 画像を先に(読み込む側が順に読むため)
}
function syncExportUI(msg){
  const list=exportList(),single=isSingleMode(),kind=exportKind();
  el("exportCardsOpts").hidden=kind!=="cards";el("exportDeckOpts").hidden=kind!=="deck";
  el("exportSidesRow").hidden=single;
  let text;
  if(!list.length)text=T("書き出すカードがありません。");
  else if(kind==="deck"){const g=deckGroups(),m=list.reduce((a,x)=>a+x.n,0);text=T("{m}枚のカードで、山札を{s}つ作ります。",{m,s:g.length})}
  else{const sides=single?"front":el("exportSides").value;text=T("{n}種類のカードを書き出します（画像{f}枚）。",{n:list.length,f:list.length*(sides==="both"?2:1)})}
  el("exportSummary").textContent=msg||text;
  el("exportGo").disabled=exportBusy||!list.length;
}
function openExport(){toggleSettings(false);closeMobilePanel();exportCancel=false;el("exportModal").hidden=false;syncExportUI()}
function closeExport(){if(exportBusy){exportCancel=true;return}el("exportModal").hidden=true}
async function runExport(){
  if(exportBusy)return;
  if(!window.html2canvas){alert(T("画像を作るライブラリを読み込めませんでした。インターネット接続を確認してください。"));return}
  const list=exportList();if(!list.length)return;
  exportBusy=true;exportCancel=false;syncExportUI(T("準備中…"));
  const staging=document.createElement("div");staging.style.cssText="position:fixed;left:-12000px;top:0;z-index:-1;background:#fff";document.body.appendChild(staging);
  const base=safeFileName(sheetTitle)||"cards",files=[];
  try{
    await fontsReady();
    if(exportKind()==="deck"){
      const zip=await buildDeckZip(staging,(i,n)=>syncExportUI(T("書き出し中… {i} / {n}",{i,n})));
      downloadBlob(zip,`${base}_deck.zip`);
      exportBusy=false;el("exportModal").hidden=true;
      showAppToast(T("山札のZIPを書き出しました"),{duration:4000});
      return;
    }
    const sides=isSingleMode()?["front"]:el("exportSides").value==="both"?["front","back"]:[el("exportSides").value];
    const scale=Number(el("exportDpi").value)/96,jobs=[];
    list.forEach((it,i)=>sides.forEach(side=>jobs.push({it,i,side})));
    for(let j=0;j<jobs.length;j++){
      if(exportCancel)throw new Error("cancel");
      syncExportUI(T("書き出し中… {i} / {n}",{i:j+1,n:jobs.length}));
      const {it,i,side}=jobs[j],c=await renderFaceCanvas(deck.cards[it.id][side],scale,staging);
      files.push({name:`${String(i+1).padStart(3,"0")}${it.n>1?"_x"+it.n:""}_${side}.png`,data:await canvasBytes(c)});c.width=c.height=0;
    }
    downloadBlob(makeZip(files),`${base}_images.zip`);
    exportBusy=false;el("exportModal").hidden=true;
    showAppToast(T("画像を書き出しました"),{duration:4000});
  }catch(err){
    exportBusy=false;
    if(err&&err.message==="cancel"){el("exportModal").hidden=true}
    else{console.error(err);alert(T("画像の書き出しに失敗しました。"));syncExportUI()}
  }finally{staging.remove();exportBusy=false;if(!el("exportModal").hidden)syncExportUI()}
}
document.querySelectorAll(".open-export").forEach(b=>b.addEventListener("click",openExport));
document.querySelectorAll("[data-export-close]").forEach(b=>b.addEventListener("click",closeExport));
el("exportModal").addEventListener("click",e=>{if(e.target===el("exportModal"))closeExport()});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!el("exportModal").hidden)closeExport()});
document.querySelectorAll('input[name="exportKind"],#exportSides,#exportDpi,#deckGroup,#deckSize,#deckRes').forEach(x=>x.addEventListener("change",()=>syncExportUI()));
el("exportGo").addEventListener("click",runExport);
document.addEventListener("cmm-langchange",()=>{if(!el("exportModal").hidden&&!exportBusy)syncExportUI()});

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
    console.error(e);alert(e.message||T("PDFの保存に失敗しました。"));
  }finally{btn.disabled=false;btn.textContent=old}
});

el("loadPdfBtn").addEventListener("click",()=>el("loadPdf").click());
el("loadPdf").addEventListener("change",async e=>{
  const file=e.target.files[0];if(!file)return;
  try{
    if(!window.PDFLib)throw new Error(T("PDFライブラリを読み込めませんでした。"));
    const bytes=await file.arrayBuffer();
    const pdf=await PDFLib.PDFDocument.load(bytes);
    const atts=extractPdfAttachments(pdf);
    const project=atts.find(x=>x.name==="card-mock-project.json");
    if(!project)throw new Error(T("このPDFにはCard Mock Makerの編集データがありません。"));
    const text=new TextDecoder().decode(project.data);
    const parsed=JSON.parse(text);
    // 以前の版(β)のPDF:作品の形が違う(deckがない)。中身は新しい形に直して開き、変わったところを一度伝える
    const fromBeta=!parsed.deck&&Array.isArray(parsed.pages),hadCustom=fromBeta&&parsed.pages.some(pg=>(pg||[]).some(d=>d&&d.type==="template"&&d.template==="custom"));
    await beginNewProject();   // 読み込んだPDFは新しい作品として開く(いまの作品は一覧に残る)
    restoreProject(hydrateProjectImages(parsed,atts));
    if(fromBeta)showBetaNote(hadCustom);
  }catch(err){
    console.error(err);alert(err.message||T("PDFを読み込めませんでした。"));
  }finally{e.target.value=""}
});

/* ---- 自動保存:このブラウザ内(IndexedDB)に、変更から少しおいて保存。次に開くと続きから ---- */
/* ---- 作品の保存:このブラウザ(IndexedDB)に作品をいくつでも。画像は作品どうしで共有して1つずつ持つ ----
   projects: id → {json(履歴と同じ形), ids(使っている画像)} / meta: id → 一覧に出す情報 / images: 画像id → dataURL / kv: current=開いている作品 */
const AUTOSAVE_DB="card-mock-maker",AUTOSAVE_MS=1200;
let autosaveDb=null,autosaveReady=false,autosaveStopped=false,autosaveFailed=false,autosaveTimer=null,autosaveLastJson=null,autosaveBusy=null;
let currentProjectId=null,currentProjectCreated=0;
const autosavedImageIds=new Set();
function idbReq(r){return new Promise((res,rej)=>{r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)})}
function idbDone(tx){return new Promise((res,rej)=>{tx.oncomplete=()=>res();tx.onabort=tx.onerror=()=>rej(tx.error||new Error("transaction failed"))})}
function openAutosaveDb(){
  return new Promise((res,rej)=>{
    if(!window.indexedDB)return rej(new Error("IndexedDB unavailable"));
    const r=indexedDB.open(AUTOSAVE_DB,2);
    r.onupgradeneeded=()=>{const db=r.result;["kv","images"].forEach(n=>{if(!db.objectStoreNames.contains(n))db.createObjectStore(n)});["projects","meta"].forEach(n=>{if(!db.objectStoreNames.contains(n))db.createObjectStore(n,{keyPath:"id"})})};
    r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error);r.onblocked=()=>rej(new Error("IndexedDB blocked"));
  });
}
function newProjectId(){return "p"+Date.now().toString(36)+Math.random().toString(36).slice(2,6)}
const imgIdsOf=json=>[...new Set([...json.matchAll(/cmm-img:\/\/([a-z0-9]+)/g)].map(m=>m[1]))];
const blankCardOf=c=>!c||(isBlankFace(c.front)&&isBlankFace(c.back));
/* 一覧に出す情報(作品の中身から作る。中身は画像をidにした形のまま) */
function metaFromState(id,st,ids,savedAt,created){
  const d=st.deck||{},order=d.order||[],cards=d.cards||{},first=order.find(k=>!blankCardOf(cards[k]));
  const size=st.cardSize||"poker",base=size==="custom"?normCustom(st.customCard):(CARD_SIZES[size]||CARD_SIZES.poker),land=st.cardOrientation==="landscape";
  return {id,name:st.sheetTitle||"",savedAt,created:created||savedAt,cards:order.filter(k=>!blankCardOf(cards[k])).length,
    preview:first?JSON.stringify(cards[first].front):null,size,fm:land?{w:base.h,h:base.w}:{w:base.w,h:base.h},land,ids};
}
function scheduleAutosave(){
  if(!autosaveReady||autosaveStopped||autosaveFailed)return;
  clearTimeout(autosaveTimer);autosaveTimer=setTimeout(runAutosave,AUTOSAVE_MS);
}
function writeAutosave(){
  const json=historyState();
  if(json===autosaveLastJson)return Promise.resolve();
  if(!currentProjectId){
    if(deck.order.every(isBlankCard)&&!sheetTitle)return Promise.resolve();   // 何も作っていない作品は保存しない(一覧が空の作品で埋まらないように)
    currentProjectId=newProjectId();currentProjectCreated=Date.now();
  }
  const id=currentProjectId,ids=imgIdsOf(json),now=Date.now();
  const tx=autosaveDb.transaction(["kv","images","projects","meta"],"readwrite"),imgs=tx.objectStore("images");
  ids.forEach(i=>{if(!autosavedImageIds.has(i)){const u=imgUrlById.get(i);if(u)imgs.put(u,i)}});
  tx.objectStore("projects").put({id,json,ids,format:2});
  tx.objectStore("meta").put(metaFromState(id,JSON.parse(json),ids,now,currentProjectCreated));
  tx.objectStore("kv").put(id,"current");
  return idbDone(tx).then(()=>{ids.forEach(i=>autosavedImageIds.add(i));autosaveLastJson=json});
}
function runAutosave(){
  clearTimeout(autosaveTimer);autosaveTimer=null;
  if(!autosaveReady||autosaveStopped||autosaveFailed||!autosaveDb)return Promise.resolve();
  const go=()=>writeAutosave().catch(err=>{
    console.warn("autosave failed",err);autosaveFailed=true;
    showAppToast(T("自動保存できませんでした(ブラウザの保存容量が足りない可能性があります)。こまめに「PDF保存」してください。"),{duration:9000});
  });
  autosaveBusy=(autosaveBusy?autosaveBusy.then(go):go()).finally(()=>{});
  return autosaveBusy;
}
/* どの作品も使っていない画像を消す(読み書きを1つの処理で行うので、保存の途中の画像を消すことはない) */
function gcImages(){
  if(!autosaveDb)return Promise.resolve();
  const tx=autosaveDb.transaction(["meta","images"],"readwrite"),metas=tx.objectStore("meta").getAll();
  metas.onsuccess=()=>{
    const keep=new Set();metas.result.forEach(m=>(m.ids||[]).forEach(i=>keep.add(i)));imgIdsOf(historyState()).forEach(i=>keep.add(i));
    const st=tx.objectStore("images"),keys=st.getAllKeys();
    keys.onsuccess=()=>keys.result.forEach(k=>{if(!keep.has(k)){st.delete(k);autosavedImageIds.delete(k)}});
  };
  return idbDone(tx).catch(e=>console.warn(e));
}
/* 以前の版の自動保存(1つだけ)を、作品の1つとして引き継ぐ */
async function migrateOldAutosave(){
  const tx=autosaveDb.transaction(["kv","projects","meta"],"readwrite"),kv=tx.objectStore("kv"),r=kv.get("project");
  r.onsuccess=()=>{
    const old=r.result;if(!old||typeof old.json!=="string")return;
    try{
      const id=newProjectId(),st=JSON.parse(old.json),ids=old.ids||imgIdsOf(old.json),t=old.savedAt||Date.now();
      tx.objectStore("projects").put({id,json:old.json,ids,format:2});
      tx.objectStore("meta").put(metaFromState(id,st,ids,t,t));
      kv.put(id,"current");
    }catch(e){console.warn(e)}
    kv.delete("project");
  };
  await idbDone(tx);
}
async function loadImagesInto(ids){
  const need=(ids||[]).filter(i=>!imgUrlById.has(i));if(!need.length)return;
  const st=autosaveDb.transaction("images").objectStore("images");
  const found=await Promise.all(need.map(i=>idbReq(st.get(i)).then(u=>[i,u])));
  found.forEach(([i,u])=>{if(typeof u==="string"){internImage(u,i);autosavedImageIds.add(i)}});
}
async function loadProject(id){
  const tx=autosaveDb.transaction(["projects","meta"]);
  const [rec,meta]=await Promise.all([idbReq(tx.objectStore("projects").get(id)),idbReq(tx.objectStore("meta").get(id))]);
  if(!rec||typeof rec.json!=="string")return false;
  await loadImagesInto(rec.ids);
  applyHistorySnapshot(rec.json);initHistory();
  currentProjectId=id;currentProjectCreated=meta&&meta.created||Date.now();autosaveLastJson=rec.json;tplWatch=null;myTplPick=null;
  const kv=autosaveDb.transaction("kv","readwrite");kv.objectStore("kv").put(id,"current");await idbDone(kv).catch(()=>{});
  return meta||{savedAt:Date.now()};
}
async function listProjects(){
  if(!autosaveDb)return [];
  const all=await idbReq(autosaveDb.transaction("meta").objectStore("meta").getAll());
  return all.sort((a,b)=>b.savedAt-a.savedAt);
}
/* 新しい作品をはじめる準備:いまの作品を保存して、次に保存するときは新しい作品として保存する */
async function beginNewProject(){
  await runAutosave();
  currentProjectId=null;currentProjectCreated=0;autosaveLastJson=null;
}
function showAppToast(message,{action=null,duration=8000}={}){
  let t=document.querySelector(".app-toast");
  if(!t){t=document.createElement("div");t.className="app-toast";t.setAttribute("role","status");document.body.appendChild(t)}
  t.innerHTML="";const msg=document.createElement("span");msg.textContent=message;t.appendChild(msg);
  if(action){const b=document.createElement("button");b.type="button";b.textContent=action.label;b.addEventListener("click",()=>{t.classList.remove("show");action.run()});t.appendChild(b)}
  const x=document.createElement("button");x.type="button";x.className="app-toast-close";x.setAttribute("aria-label","閉じる");x.textContent="×";x.addEventListener("click",()=>t.classList.remove("show"));t.appendChild(x);
  clearTimeout(showAppToast.timer);requestAnimationFrame(()=>t.classList.add("show"));
  if(duration)showAppToast.timer=setTimeout(()=>t.classList.remove("show"),duration);
  // スマホでは画面のほかの場所に触れたら閉じる(パネルの操作のじゃまにならないように)
  if(mobileUIActive()){const shownAt=Date.now(),off=e=>{if(t.contains(e.target))return;if(Date.now()-shownAt>400)t.classList.remove("show");document.removeEventListener("pointerdown",off,true)};document.removeEventListener("pointerdown",showAppToast.off||off,true);showAppToast.off=off;setTimeout(()=>document.addEventListener("pointerdown",off,true),0)}
}
async function startNewProject(){
  const blank=deck.order.every(isBlankCard)&&!sheetTitle;
  // 保存できない環境では、いまの作業が消えるので確かめる
  if((autosaveFailed||!autosaveDb)&&!blank&&!confirm(T("いまの作業を消して、新しく作りはじめますか？\n(PDF保存していない内容は元に戻せません)")))return;
  toggleSettings(false);closeProjects();closeMobilePanel();
  await beginNewProject();
  sheetTitle="";el("sheetTitleInput").value="";printSettings={binding:"long",backOffsetX:0,backOffsetY:0};
  startDeck();setPaper();renderSheet();syncControls();initHistory();
  if(!blank&&!autosaveFailed&&autosaveDb)showAppToast(T("新しい作品をはじめました。前の作品は「作品の一覧」から開けます。"),{duration:5000});
}
function timeLabel(ms){const d=new Date(ms),p=n=>String(n).padStart(2,"0");const today=new Date().toDateString()===d.toDateString();return (today?"":`${d.getMonth()+1}/${d.getDate()} `)+`${p(d.getHours())}:${p(d.getMinutes())}`}
async function initAutosave(){
  try{
    autosaveDb=await openAutosaveDb();
    await migrateOldAutosave();
    const untouched=!undoStack.length&&historyPendingStart===null;
    if(untouched){
      let id=await idbReq(autosaveDb.transaction("kv").objectStore("kv").get("current"));
      const list=await listProjects();
      if(!list.some(m=>m.id===id))id=list[0]&&list[0].id;
      if(id){
        const meta=await loadProject(id);
        if(meta)showAppToast(T("前回の続きを開きました({t}保存)",{t:timeLabel(meta.savedAt||Date.now())}),{action:{label:T("作品の一覧"),run:openProjects}});
      }
    }
    gcImages();
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
/* ---- 作品の一覧 ---- */
async function openProjects(){
  toggleSettings(false);closeMobilePanel();el("projModal").hidden=false;
  await runAutosave();renderProjects();
}
function closeProjects(){el("projModal").hidden=true}
async function renderProjects(){
  const box=el("projList");box.innerHTML="";
  if(!autosaveDb||autosaveFailed){const m=document.createElement("p");m.className="tpl-note";m.textContent=T("このブラウザでは作品を保存できません。「PDF保存」で保存してください。");box.appendChild(m);return}
  const list=await listProjects();
  if(!list.length){const m=document.createElement("p");m.className="tpl-note";m.textContent=T("まだ保存された作品はありません。カードを作ると、自動でここに保存されます。");box.appendChild(m);return}
  for(const m of list){
    const cur=m.id===currentProjectId,row=document.createElement("div");row.className="proj-item"+(cur?" current":"");
    const th=document.createElement("div");th.className="proj-thumb";
    if(m.preview){try{await loadImagesInto(imgIdsOf(m.preview));th.appendChild(faceThumb(JSON.parse(m.preview,unpackImages),48,{fm:m.fm,land:m.land,size:m.size}))}catch(e){}}
    const info=document.createElement("div");info.className="proj-info";
    const name=document.createElement("input");name.type="text";name.className="tpl-name";name.maxLength=60;name.value=m.name;name.placeholder=T("無題の作品");name.setAttribute("aria-label",T("作品の名前"));
    name.addEventListener("change",()=>renameProject(m.id,name.value));
    const meta=document.createElement("div");meta.className="tpl-meta";meta.textContent=(cur?T("編集中")+" · ":"")+T("カード{n}枚",{n:m.cards})+" · "+timeLabel(m.savedAt);
    const acts=document.createElement("div");acts.className="tpl-acts";
    const btn=(label,fn,cls)=>{const x=document.createElement("button");x.type="button";x.className="mini"+(cls?" "+cls:"");x.textContent=label;x.addEventListener("click",fn);acts.appendChild(x)};
    if(!cur)btn(T("開く"),()=>openProject(m.id),"proj-open");
    btn(T("複製"),()=>duplicateProject(m.id));
    btn(T("削除"),()=>deleteProject(m),"tpl-del");
    info.append(name,meta,acts);row.append(th,info);box.appendChild(row);
  }
}
async function openProject(id){
  await runAutosave();
  const ok=await loadProject(id);closeProjects();
  if(ok)showAppToast(T("「{name}」を開きました",{name:sheetTitle||T("無題の作品")}),{duration:3000});
}
async function renameProject(id,v){
  const name=String(v||"").trim();
  if(id===currentProjectId){sheetTitle=name;el("sheetTitleInput").value=name;renderSheet();await runAutosave();renderProjects();return}
  const tx=autosaveDb.transaction(["projects","meta"],"readwrite"),ps=tx.objectStore("projects"),ms=tx.objectStore("meta");
  const r=ps.get(id);r.onsuccess=()=>{const rec=r.result;if(!rec)return;const st=JSON.parse(rec.json);st.sheetTitle=name;rec.json=JSON.stringify(st);ps.put(rec);
    const q=ms.get(id);q.onsuccess=()=>{if(q.result){q.result.name=name;ms.put(q.result)}}};
  await idbDone(tx).catch(e=>console.warn(e));renderProjects();
}
async function duplicateProject(id){
  if(id===currentProjectId)await runAutosave();
  const tx=autosaveDb.transaction(["projects","meta"],"readwrite"),ps=tx.objectStore("projects"),ms=tx.objectStore("meta");
  const r=ps.get(id),q=ms.get(id);
  q.onsuccess=()=>{const rec=r.result,meta=q.result;if(!rec||!meta)return;
    const nid=newProjectId(),st=JSON.parse(rec.json),now=Date.now();st.sheetTitle=T("{name}のコピー",{name:meta.name||T("無題の作品")});
    const json=JSON.stringify(st);ps.put({id:nid,json,ids:rec.ids,format:2});ms.put(metaFromState(nid,st,rec.ids,now,now));};
  await idbDone(tx).catch(e=>console.warn(e));renderProjects();
}
async function deleteProject(m){
  if(!confirm(T("「{name}」を削除しますか？\n(元に戻せません。必要なら先に開いて「PDF保存」してください)",{name:m.name||T("無題の作品")})))return;
  const tx=autosaveDb.transaction(["projects","meta"],"readwrite");tx.objectStore("projects").delete(m.id);tx.objectStore("meta").delete(m.id);
  await idbDone(tx).catch(e=>console.warn(e));
  if(m.id===currentProjectId){
    currentProjectId=null;autosaveLastJson=null;
    const next=(await listProjects())[0];
    if(next)await loadProject(next.id);
    else{sheetTitle="";el("sheetTitleInput").value="";startDeck();setPaper();renderSheet();syncControls();initHistory()}
  }
  await gcImages();renderProjects();
}
document.querySelectorAll(".open-projects").forEach(b=>b.addEventListener("click",openProjects));
el("projNew").addEventListener("click",startNewProject);
document.querySelectorAll("[data-proj-close]").forEach(b=>b.addEventListener("click",closeProjects));
el("projModal").addEventListener("click",e=>{if(e.target===el("projModal"))closeProjects()});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!el("projModal").hidden)closeProjects()});
document.addEventListener("cmm-langchange",()=>{if(!el("projModal").hidden)renderProjects()});
el("mobileNewProject")?.addEventListener("click",()=>{closeMobilePanel();startNewProject()});

/* ウラ面のずれ補正:CSSの --bx/--by で、シートの中央からずらす */
function setBackOffset(sg,on){
  const x=on?Number(printSettings.backOffsetX)||0:0,y=on?Number(printSettings.backOffsetY)||0:0;
  if(x||y){sg.style.setProperty("--bx",x+"mm");sg.style.setProperty("--by",y+"mm")}else{sg.style.removeProperty("--bx");sg.style.removeProperty("--by")}
}
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
  setBackOffset(sg,!!sh.back);
  return sheet;
}
function preparePrintPages(){
  const wrap=el("printPages");wrap.innerHTML="";
  const m=document.createElement("div");m.style.cssText="position:fixed;left:-12000px;top:0;visibility:hidden";document.body.appendChild(m);
  const sheets=outputSheets().map(sh=>{const x=makeOutputSheet(sh);m.appendChild(x);return x});
  fitTexts(m,false);   // 文字の大きさは、印刷用の用紙を実際に並べて合わせる
  sheets.forEach(x=>wrap.appendChild(x));m.remove();
}
function setExactPrintPage(){const p=paperMM(),paperName=el("paperSize").value==="a3"?"A3":"A4",orientation=el("paperOrientation").value;let st=el("printPageStyle");if(!st){st=document.createElement("style");st.id="printPageStyle";document.body.appendChild(st)}st.textContent=`@page{size:${paperName} ${orientation};margin:0}\n@media print{.print-sheet{width:${p.w}mm!important;height:${p.h}mm!important;min-width:${p.w}mm!important;max-width:${p.w}mm!important;min-height:${p.h}mm!important;max-height:${p.h}mm!important}}`}
el("printBtn").addEventListener("click",async()=>{const b=el("printBtn"),t=b.textContent;b.disabled=true;b.textContent="準備中…";try{await fontsReady()}finally{b.disabled=false;b.textContent=t}setExactPrintPage();preparePrintPages();requestAnimationFrame(()=>requestAnimationFrame(()=>window.print()))});



/* ヘッダーの高さ(タブレット幅で2段になる)を、下の作業エリアの高さの計算に使う */
{const hd=document.querySelector("header"),setH=()=>document.documentElement.style.setProperty("--hdr-h",hd.offsetHeight+"px");setH();if(window.ResizeObserver)new ResizeObserver(()=>{setH();fitPaper()}).observe(hd);}
cardOrientation=(el("paperOrientation").value==="portrait")?"landscape":"portrait";
startDeck();
setPaper();renderSheet();syncControls();
initHistory();renderSwatches();
initAutosave();
/* ---- 言語 ---- */

/* ---- 画像の位置と大きさ:パネルのスライダー、パソコンはカードの上でドラッグしても動かせる ---- */
document.querySelectorAll(".img-fit").forEach(box=>{
  const key=FIT_KEYS[box.dataset.fit];
  box.innerHTML=`<label class="img-fit-row"><span>大きさ</span><input type="range" min="100" max="400" step="5" data-k="z"></label><label class="img-fit-row"><span>左右</span><input type="range" min="0" max="100" step="1" data-k="x"></label><label class="img-fit-row"><span>上下</span><input type="range" min="0" max="100" step="1" data-k="y"></label><div class="img-fit-foot"><span class="img-fit-hint">カードの上でドラッグしても動かせます</span><button type="button" class="mini img-fit-reset">元に戻す</button></div>`;
  box.querySelectorAll("input[type=range]").forEach(r=>r.addEventListener("input",()=>{
    const f=normFit(currentFaces()[selected][key]);f[r.dataset.k]=r.dataset.k==="z"?Number(r.value)/100:Number(r.value);updateSelected({[key]:f});
  }));
  box.querySelector(".img-fit-reset").addEventListener("click",()=>{updateSelected({[key]:null});syncControls()});
});
function syncImgFit(d){
  document.querySelectorAll(".img-fit").forEach(box=>{
    const w=box.dataset.fit,has=w==="image"?!!d.image:w==="src"?(d.type==="image"&&!!d.src):!!d.bgImage;
    box.hidden=!has;if(!has)return;
    const f=normFit(d[FIT_KEYS[w]]);
    [["z",Math.round(f.z*100)],["x",Math.round(f.x)],["y",Math.round(f.y)]].forEach(([k,v])=>{const r=box.querySelector(`[data-k=${k}]`);if(document.activeElement!==r)r.value=v});
  });
}
el("sheetGrid").addEventListener("pointerdown",e=>{
  if(e.pointerType!=="mouse"||e.button!==0||inlineEdit)return;
  const face=e.target.closest(".face.selected[data-idx]");if(!face)return;
  if(e.target.closest(".generic-textbox,.frame-text,.option-image,.option-shape,.resize-handle"))return;
  const d=currentFaces()[Number(face.dataset.idx)];if(!d)return;
  const ti=e.target.closest(".tcg-image");let which=null,box=face,img=null;
  if(ti&&d.image){which="image";box=ti;img=ti.querySelector("img")}
  else if(ti)return;
  else if(d.type==="image"&&d.src){which="src";img=face.querySelector(".face-src-img")}
  else if(d.bgImage){which="bg";img=face.querySelector(".face-bg-img")}
  if(!which||!img||!img.naturalWidth)return;
  const key=FIT_KEYS[which],f0=normFit(d[key]),r=box.getBoundingClientRect();
  const k=Math.max(r.width/img.naturalWidth,r.height/img.naturalHeight),ox=r.width*(f0.z*img.naturalWidth*k/r.width-1),oy=r.height*(f0.z*img.naturalHeight*k/r.height-1);
  if(ox<1&&oy<1)return;   // 枠とぴったり同じ形で拡大もしていないときは、動かす余地がない
  e.preventDefault();
  const x0=e.clientX,y0=e.clientY;let moved=false;
  const move=ev=>{const dx=ev.clientX-x0,dy=ev.clientY-y0;if(!moved&&Math.hypot(dx,dy)<4)return;moved=true;face.classList.add("panning");
    d[key]={...f0,x:ox>=1?clamp(f0.x-dx/ox*100,0,100):f0.x,y:oy>=1?clamp(f0.y-dy/oy*100,0,100):f0.y};applyImgFit(img,d[key])};
  const up=()=>{window.removeEventListener("pointermove",move);window.removeEventListener("pointerup",up);face.classList.remove("panning");if(moved){renderSheet();syncControls()}};
  window.addEventListener("pointermove",move);window.addEventListener("pointerup",up);
});

/* ---- ホーム画面に追加・オフライン:一度開けば、電波がなくても開ける ---- */
if("serviceWorker" in navigator&&(location.protocol==="https:"||location.hostname==="localhost")){
  window.addEventListener("load",()=>navigator.serviceWorker.register("sw.js").catch(err=>console.warn(err)));
  if(matchMedia("(display-mode: standalone)").matches||navigator.standalone)navigator.storage?.persist?.().catch(()=>{});   // ホーム画面から開いたときは、保存した作品が消されにくいように頼んでおく
}
let installPrompt=null;
const isStandalone=()=>matchMedia("(display-mode: standalone)").matches||navigator.standalone===true;
const isIOS=()=>/iPhone|iPad|iPod/.test(navigator.userAgent)||(navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1);
function syncInstallButtons(){const show=!isStandalone()&&(!!installPrompt||isIOS());document.querySelectorAll(".install-btn").forEach(b=>b.hidden=!show)}
window.addEventListener("beforeinstallprompt",e=>{e.preventDefault();installPrompt=e;syncInstallButtons()});
window.addEventListener("appinstalled",()=>{installPrompt=null;syncInstallButtons();showAppToast(T("ホーム画面に追加しました。"),{duration:4000})});
document.querySelectorAll(".install-btn").forEach(b=>b.addEventListener("click",async()=>{
  toggleSettings(false);closeMobilePanel();
  if(installPrompt){const p=installPrompt;installPrompt=null;p.prompt();try{await p.userChoice}catch(_){}syncInstallButtons();return}
  showAppToast(T("Safariの共有ボタン(□に↑)から「ホーム画面に追加」を選んでください。"),{duration:8000});
}));
syncInstallButtons();

/* ---- 指で触る端末では、数字の入力欄の左右に − ＋ を足す(小さな矢印や数字キーの入力をしなくてよいように) ---- */
const coarse=matchMedia("(pointer:coarse)");
function addSteppers(root){
  if(!coarse.matches)return;
  root.querySelectorAll(".tool-number-wrap:not(.has-steps)").forEach(w=>{
    const inp=w.querySelector('input[type=number]');if(!inp)return;w.classList.add("has-steps");
    const mk=(txt,dir,label)=>{const b=document.createElement("button");b.type="button";b.className="num-step";b.textContent=txt;b.setAttribute("aria-label",T(label));
      b.addEventListener("click",()=>{const st=parseFloat(inp.step)||.5,v=(parseFloat(inp.value)||0)+dir*st,mn=inp.min!==""?parseFloat(inp.min):-Infinity,mx=inp.max!==""?parseFloat(inp.max):Infinity;
        inp.value=String(Math.round(clamp(v,mn,mx)*100)/100);inp.dispatchEvent(new Event("input",{bubbles:true}));inp.dispatchEvent(new Event("change",{bubbles:true}))});return b};
    w.insertBefore(mk("−",-1,"小さく"),w.firstChild);w.appendChild(mk("＋",1,"大きく"));
  });
}
addSteppers(document);
new MutationObserver(ms=>{if(!coarse.matches)return;for(const m of ms)for(const n of m.addedNodes)if(n.nodeType===1&&(n.matches?.(".tool-number-wrap")||n.querySelector?.(".tool-number-wrap:not(.has-steps)")))addSteppers(n.parentNode||n)}).observe(document.body,{childList:true,subtree:true});

/* ---- 右のパネル:たたんである「背景とふち」「コピー・テンプレート保存」。開け閉めは覚えておく ---- */
function syncFaceStyleChip(d){
  const chip=el("faceStyleChip");if(!chip)return;
  chip.style.backgroundImage=d.bgImage?`url("${d.bgImage}")`:"";
  chip.style.backgroundColor=d.bgNone?"transparent":(d.bgColor||"#ffffff");
  chip.classList.toggle("none",!!d.bgNone&&!d.bgImage);
  chip.style.boxShadow=d.bgBorderNone?"":`inset 0 0 0 2px ${d.bgBorderColor||"#222"}`;
}
["faceStyleFold","faceToolsFold"].forEach(id=>{
  const f=el(id);if(!f)return;
  try{if(localStorage.getItem("pk-fold-"+id)==="1")f.open=true}catch(_){}
  f.addEventListener("toggle",()=>{try{localStorage.setItem("pk-fold-"+id,f.open?"1":"0")}catch(_){}});
});
el("myTplSaveNow")?.addEventListener("click",()=>{myTplPick=null;openTplSave()});
if(window.CMMI18N){
  CMMI18N.init();
  document.querySelectorAll("[data-lang-btn]").forEach(b=>b.addEventListener("click",()=>CMMI18N.setLang(b.dataset.langBtn)));
  document.addEventListener("cmm-langchange",()=>{relabelLengths();updateFit();renderSheet();syncControls();fitPaper()});
}


})();

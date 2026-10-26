/* カードモックツクール:日本語/英語の切り替え
   画面の日本語をキーにして英語に置き換える。言語はパンダキネマのサイトと同じ「pk-lang」に保存する。
   カードの中身(利用者が入力した文字)は訳さない。未入力の仮表示(.ph)だけは訳す。 */
(function(){
const EN={
  // ---- アプリ全体
  "カードモックツクール":"Card Mock Maker","β":"β","β版":"Beta",
  "パンダキネマのサイトへ":"Go to the Panda Kinema site",
  "履歴":"History","取り消し":"Undo","やり直し":"Redo","取り消し（⌘Z / Ctrl+Z）":"Undo (⌘Z / Ctrl+Z)","やり直し（⇧⌘Z / Ctrl+Y）":"Redo (⇧⌘Z / Ctrl+Y)",
  "用紙サイズ":"Paper size","用紙方向":"Paper orientation","横":"Landscape","縦":"Portrait","カードサイズ":"Card size",
  "面付けモード":"Layout","面付け":"Layout","両面":"Front & back","片面":"Single-sided","両面（折り）":"Front & back (fold)","両面印刷":"Duplex printing",
  "タイトル":"Title","いまの作業を消して新しく始める":"Clear the current work and start over","新規":"New",
  "PDF保存":"Save PDF","PDF読み込み":"Open PDF","印刷":"Print","設定":"Settings","準備中…":"Preparing…","PDF作成中…":"Creating PDF…",
  "長さの単位":"Length unit","文字の単位":"Text unit","級（Q）":"Q (0.25 mm)","基本のフォント":"Default font",
  "単位はこのブラウザに保存されます。基本のフォントは今のデッキの設定です。":"Units are saved in this browser. The default font belongs to the current deck.",
  "言語":"Language","言語 / Language":"Language",
  // ---- ページ
  "ページ":"Pages","ページ追加":"Add page","＋ ページ":"+ Page","ページ複製":"Duplicate page","複製":"Duplicate","ページ削除":"Delete page","削除":"Delete",
  "ページメニュー":"Page menu","ページを追加":"Add page","ページを複製":"Duplicate page","ページを削除":"Delete page",
  "カードをクリックして、右のパネルの「面の種類」から作りはじめます。":"Click a card, then choose a face type in the right panel to start.",
  "下の「面」「テンプレ」から作りはじめます。":"Start from “Face” or “Template” below.",
  "見本を開く":"Open sample","見本":"Sample",
  // ---- スマホ
  "スマホ用ツールバー":"Phone toolbar","面":"Face","テンプレ":"Template","オプション":"Options","用紙":"Paper","メニュー":"Menu",
  "テンプレート":"Template","この面はテンプレートを使っています":"This face uses a template","無地に戻す":"Back to blank",
  "この面はテンプレートを使っていません。テンプレートを使うときは、面の種類を「テンプレート」にします。":"This face doesn't use a template. To use one, set the face type to “Template”.",
  "この面をテンプレートにする":"Use a template on this face","カード":"Card","ファイル":"File",
  "スマホ用カードプレビュー":"Card preview","前のカード":"Previous card","次のカード":"Next card","前のページ":"Previous page","次のページ":"Next page",
  "ページ全体":"Whole page","1枚ずつ":"One by one","オモテ":"Front","ウラ":"Back","オモテ面":"Front","ウラ面":"Back",
  // ---- 面
  "面の種類":"Face type","無地":"Blank","画像":"Image","面色":"Fill","背景の面色":"Background fill","線色":"Stroke","背景の線色":"Background stroke",
  "線の太さ":"Stroke width","背景の線の太さ":"Background stroke width","線幅":"Stroke width","背景の線の位置":"Background stroke position","線の位置":"Stroke position",
  "内側":"Inside","中央":"Center","外側":"Outside","背景画像":"Background image","背景画像を削除":"Remove background image","画像を選ぶ":"Choose image",
  "面をコピー":"Copy face","面をペースト":"Paste face","このページの同じ面にコピー":"Copy to the same side on this page","すべてのページの同じ面にコピー":"Copy to the same side on all pages",
  "この面をこのページの同じ面にコピー":"Copy to the same side on this page","この面をすべてのページの同じ面にコピー":"Copy to the same side on all pages",
  "このページのすべての面にコピー":"Copy to every card on this page","すべてのページのすべての面にコピー":"Copy to every card on all pages",
  "画像を読み込む":"Load image","画像未設定":"No image","画像を読み込めませんでした。":"Couldn't load the image.",
  // ---- テンプレート
  "種類":"Type","トランプ":"Playing card","トレカ":"Trading card","ワードゲーム":"Word game",
  "数字":"Number","数字の大きさ":"Number size","太字":"Bold","斜体":"Italic","下線":"Underline","数字の色":"Number color","フォント":"Font","基本":"Default",
  "スート":"Suit","スートサイズ":"Suit size","小":"S","中":"M","大":"L","スート個数":"Suit count","スートの種類":"Suit style","記号":"Symbol","スートの画像":"Suit image",
  "配置":"Placement","数字とスートの配置":"Number & suit placement","四つ角":"Four corners","上段のみ":"Top only","右対角線":"Diagonal (right)","左対角線":"Diagonal (left)",
  "カード名":"Card name","文字サイズ":"Text size","中段の画像":"Middle image","テキスト":"Text","文字色":"Text color",
  "上下3段":"Three rows","上段＋左右分割":"Top + left/right","上段の高さ":"Top height","上段":"Top","中段の高さ":"Middle height","中段":"Middle","下段の高さ":"Bottom height","下段":"Bottom",
  "フレームの面色":"Frame fill","フレームの線色":"Frame stroke","フレームの線の太さ":"Frame stroke width","フレームの線の位置":"Frame stroke position",
  "ことば":"Word","メイン文字":"Main text",
  // ---- オプション
  "テキストボックス":"Text box","追加":"Add","フレームテキスト":"Framed text","図形":"Shapes","中央にスナップ":"Snap to center","回転":"Rotate","頂点":"Points",
  "円":"Circle","三角形":"Triangle","四角形":"Rectangle","多角形":"Polygon","星":"Star",
  "画像や編集データはブラウザ内で処理され、サーバーへ送信されません。":"Images and your data are processed in your browser and never sent to a server.",
  // ---- 色
  "カラー":"Color","なし":"None","カラーコード":"Color code","基本の色":"Basic colors","使われている色":"Colors in use","まだありません":"None yet",
  // ---- フォント
  "ゴシック":"Sans-serif","明朝":"Serif","丸ゴシック":"Rounded","極太":"Heavy","端末の標準":"System font",
  // ---- カードサイズ名
  "ポーカー":"Poker","ブリッジ":"Bridge","名刺":"Business card","遊戯王サイズ":"Japanese size","クレジット":"Credit card","ハーフ":"Mini",
  // ---- 保存・読み込み・通知
  "保存したPDFは「PDF読み込み」で再編集できます":"You can edit a saved PDF again with “Open PDF”.",
  "PDFライブラリを読み込めませんでした。インターネット接続を確認してください。":"Couldn't load the PDF library. Please check your internet connection.",
  "PDFライブラリを読み込めませんでした。":"Couldn't load the PDF library.",
  "PDFの保存に失敗しました。":"Couldn't save the PDF.","PDFを読み込めませんでした。":"Couldn't open the PDF.",
  "このPDFにはCard Mock Makerの編集データがありません。":"This PDF doesn't contain Card Mock Maker data.",
  "自動保存できませんでした(ブラウザの保存容量が足りない可能性があります)。こまめに「PDF保存」してください。":"Autosave failed (the browser may be out of storage). Please use “Save PDF” often.",
  "閉じる":"Close",
  "いまの作業を消して、新しく作りはじめますか？\n(PDF保存していない内容は元に戻せません)":"Clear the current work and start over?\n(Anything not saved as a PDF can't be restored.)",
  "いまの作業を見本に置き換えますか？\n(元に戻すときは「取り消し」)":"Replace the current work with the sample?\n(Use “Undo” to go back.)",
  // ---- 見本・初期値の文字
  "表示する面":"Side shown","プリンタの両面設定":"Printer duplex setting","長辺とじ":"Flip on long edge","短辺とじ":"Flip on short edge",
  "プリンタの両面印刷の設定と同じものを選びます":"Choose the same setting as your printer's two-sided printing",
  "ウラ面のずれ補正":"Back offset",
  "ウラ面は、紙を左右に裏返したとき重なるように、左右を入れ替えて並べています。":"This is how the backs print: swapped left and right so they line up when the sheet is flipped sideways.",
  "ウラ面は、紙を上下に裏返したとき重なるように、上下を入れ替えて並べています。":"This is how the backs print: swapped top and bottom so they line up when the sheet is flipped top to bottom.",
  "ウラ面は、紙を左右に裏返したときオモテと重なる位置に並びます。最初は1枚だけ試し刷りしてください。":"Backs are placed where they line up with the fronts when the sheet is flipped sideways. Do a single test print first.",
  "ウラ面は、紙を上下に裏返したときオモテと重なる位置に並びます。最初は1枚だけ試し刷りしてください。":"Backs are placed where they line up with the fronts when the sheet is flipped top to bottom. Do a single test print first.",
  "画像で書き出す":"Export images","カード1枚ずつの画像":"One image per card","Tabletop Simulator用":"For Tabletop Simulator",
  "PNG画像をZIPにまとめます。ほかのツールで使ったり、紹介画像にしたり。":"PNG images in a ZIP, for other tools or for showing your cards.",
  "10×7のシート画像とウラ面の画像をZIPにまとめます。カードは枚数ぶん並びます。":"10×7 sheet images and a back image in a ZIP. Each card appears as many times as its copies.",
  "書き出す面":"Sides","解像度":"Resolution","オモテ面とウラ面":"Front and back","書き出す":"Export","つくる":"Create",
  "書き出すカードがありません。":"There are no cards to export.",
  "{m}枚のカードを{s}枚のシートにまとめます。":"{m} cards on {s} sheet(s).",
  "{n}種類のカードを書き出します（画像{f}枚）。":"{n} card designs ({f} images).",
  "準備中…":"Preparing…","書き出し中… {i} / {n}":"Exporting… {i} / {n}","画像を書き出しました":"Images exported",
  "画像の書き出しに失敗しました。":"Couldn't export the images.",
  "画像を作るライブラリを読み込めませんでした。インターネット接続を確認してください。":"Couldn't load the image library. Check your internet connection.",
  "Tabletop Simulator への取り込み方":"Importing into Tabletop Simulator",
  "1. Objects → Components → Cards → Custom Deck を置きます。":"1. Place Objects → Components → Cards → Custom Deck.",
  "2. Face に deck_1.png、Back に back_1.png を選び、「Unique backs」にチェックを入れます。":"2. Choose deck_1.png for Face and back_1.png for Back, and tick \"Unique backs\".",
  "2. Face に deck_1.png、Back に back.png を選びます。":"2. Choose deck_1.png for Face and back.png for Back.",
  "3. Width・Height・Number を下のとおりに入れて Import します。":"3. Enter Width, Height and Number as below, then Import.",
  "deck_{s}.png：Width 10 / Height 7 / Number {n}":"deck_{s}.png: Width 10 / Height 7 / Number {n}",
  "ほかの人と遊ぶときは、画像をSteamクラウドなどにアップロードしてください（TTSの画像選択画面からできます）。":"To play with others, upload the images to the Steam Cloud or similar (you can do this from TTS's image picker).",
  "表から一括作成":"Create from a table","表を貼り付ける":"Paste a table","1行目は見出し":"First row is headers","CSVファイルを読み込む":"Load a CSV file",
  "どの列をどこに入れるか":"Which column goes where","確認":"Check","やめる":"Cancel","作る":"Create",
  "列{n}":"Column {n}","すべて1枚":"1 copy each",
  "選んでいるカード":"Selected card","例を入れる":"Fill in an example",
  "選んでいるカードには文字を入れる場所がありません":"The selected card has nowhere to put text",
  
  
  "スプレッドシートやExcelで範囲をコピーして、ここに貼り付けます。1行目は見出し（カード名・テキスト・枚数 など）にします。":"Copy a range in a spreadsheet or Excel and paste it here. Use the first row for headings (Name, Text, Copies, etc.).",
  "貼り付けた内容を例に置き換えますか？":"Replace what you pasted with the example?",
  
  "表を貼り付けると、ここに最初の数枚が表示されます。":"Paste a table to preview the first few cards here.",
  "ほか{n}種類":"+{n} more","{n}種類・合計{m}枚のカードを作ります。":"Cards to create: {m} (designs: {n})","{side}：{name}":"{side}: {name}",
  "最大{p}ページのため、{k}枚までしか作れません。":"Only {k} will fit (up to {p} pages).","{n}枚のカードを作りました":"Created {n} cards",
  "CSVファイルを読み込めませんでした。":"Couldn't read the CSV file.",
  "テンプレートを選ぶ":"Choose a template","元のカードも残す":"Keep the original card too","テンプレートのまま":"Keep the template's text",
  "「カード{n}」の見た目のまま、表の1行を1枚のカードにします。作ったカードは「カード{n}」の場所に並び、同じテンプレートでつながります。":"Each row becomes one card that looks just like Card {n}. The new cards go where Card {n} is and are linked by the same template.",
  "マイテンプレート「{name}」で、表の1行を1枚のカードにします。作ったカードは今あるカードのあとに並び、このテンプレートでつながります。":"Each row becomes one card using your template \"{name}\". The new cards are added after your existing cards and linked to this template.",
  "{name}の基本の見た目で、表の1行を1枚のカードにします。作ったカードは今あるカードのあとに並びます。作ったカードは同じテンプレートでつながるので、どれか1枚の色などを変えると全部に反映されます。":"Each row becomes one card in the basic {name} style, added after your existing cards. The new cards are linked by one template, so changing the colours etc. on any of them changes them all.",
  "このテンプレートには文字を入れる場所がありません。トランプ・トレカ・ワードゲームか、テキストボックスのあるテンプレートを選んでください。":"This template has nowhere to put text. Choose playing card, trading card, word game, or a template with text boxes.",
  "マイテンプレート":"My templates","選んでいるカードをテンプレートにする":"Make the selected card a template","保存":"Save",
  "テンプレートは作品と一緒に保存されます（PDF保存にも入ります）。「ブラウザに保存」したものは、このブラウザで作るほかの作品でも使えます。":"Templates are saved with your project (and in saved PDFs). Ones saved to the browser can also be used in your other projects in this browser.",
  "テンプレートとして保存":"Save as template","テンプレートから外す":"Unlink from template",
  "テンプレート「{name}」（{n}枚）を使っています。見た目を変えると全部に反映されます。文字はこのカードだけ。":"Uses template \"{name}\" (cards: {n}). Changing the look changes all of them; text changes only this card.",
  "面の種類を変えたので、このカードはテンプレート「{name}」から外れました。":"This card was unlinked from template \"{name}\" because its face type changed.",
  "空のカードはテンプレートにできません。カードを作ってから保存してください。":"An empty card can't be a template. Make the card first, then save it.",
  "このカードはテンプレート「{name}」を使っています。保存すると、新しいテンプレートとして分かれます。":"This card uses template \"{name}\". Saving makes it a separate new template.",
  "まだありません。カードの見た目を整えたら、上で名前をつけて保存します。":"None yet. Once a card looks right, name it above and save it.",
  "テンプレートの名前":"Template name","この作品で{n}枚":"In this project: {n}","この作品では未使用":"Not used in this project",
  "ブラウザに保存済み":"Saved in this browser","この作品だけ":"This project only","選んでいるカードに使う":"Use on selected card","ブラウザにも保存":"Save to browser",
  "ブラウザに保存できませんでした。":"Couldn't save to the browser.",
  "テンプレート「{name}」を削除しますか？\nこの作品の{n}枚はテンプレートから外れます（見た目はそのまま）。":"Delete template \"{name}\"?\nThe {n} cards in this project will be unlinked (they keep their look).",
  "テンプレート「{name}」を削除しますか？":"Delete template \"{name}\"?",
  "テンプレート「{name}」を保存しました":"Saved template \"{name}\"","テンプレート「{name}」を使いました":"Applied template \"{name}\"",
  "ブラウザには保存できませんでした（この作品の中には保存されています）。":"Couldn't save to the browser (it's still saved in this project).",
  "この作品のマイテンプレートを{n}個、このブラウザに追加しました":"Added {n} template(s) from this project to this browser",
  "枚数":"Copies","1枚減らす":"One fewer","1枚増やす":"One more","このカードだけ別にする":"Make this one separate",
  "同じカードが{n}枚あります。どれを直しても全部に反映されます。":"There are {n} copies of this card. Editing any of them changes all.",
  "これ以上カードを増やせません（最大{n}ページ）":"Can't add more cards (up to {n} pages).",
  "ドラゴン":"Dragon","このカードを出したとき、山札からカードを1枚引く。":"When you play this card, draw a card.",
  // ---- メタ
  "カードモックツクール β（改良テスト版） | Card Mock Maker":"Card Mock Maker β (test build)",
};
const PATTERNS=[
  [/^カード(\d+)（ページ内(\d+)）・(オモテ|ウラ)$/,(m)=>`Card ${m[1]} (#${m[2]} on page) · ${m[3]==="オモテ"?"Front":"Back"}`],
  [/^カード(\d+)（ページ内(\d+)）$/,(m)=>`Card ${m[1]} (#${m[2]} on page)`],
  [/^カード (\d+) \/ (\d+)$/,(m)=>`Card ${m[1]} / ${m[2]}`],
  [/^カード (\d+) \/ (\d+) ×(\d+)$/,(m)=>`Card ${m[1]} / ${m[2]} ×${m[3]}`],
  [/^ページ (\d+) \/ (\d+)$/,(m)=>`Page ${m[1]} / ${m[2]}`],
  [/^カード (\d+)〜(\d+)$/,(m)=>`Cards ${m[1]}–${m[2]}`],
  [/^テキストボックス(\d+)$/,(m)=>`Text box ${m[1]}`],[/^フレームテキスト(\d+)$/,(m)=>`Framed text ${m[1]}`],[/^画像(\d+)$/,(m)=>`Image ${m[1]}`],
  [/^テキスト(\d+)$/,(m)=>`Text ${m[1]}`],
  [/^(円|三角形|四角形|多角形|星|図形)(\d+)$/,(m)=>`${({円:"Circle",三角形:"Triangle",四角形:"Rectangle",多角形:"Polygon",星:"Star",図形:"Shape"})[m[1]]} ${m[2]}`],
  [/^(ポーカー|ブリッジ|名刺|遊戯王サイズ|クレジット|ハーフ) \((.+)\)$/,(m)=>`${EN[m[1]]} (${m[2]})`],
  [/^(A[34])(横|縦)に(.+?)×(.+?) (\S+)のカードが(\d+)枚（余白 左右(.+?)・上下(.+?)）。印刷は「実際のサイズ（100%）」で。$/,
    (m)=>`${m[1]} ${m[2]==="横"?"landscape":"portrait"}: ${m[6]} cards of ${m[3]}×${m[4]} ${m[5]} (margins ${m[7]} left/right, ${m[8]} top/bottom). Print at “Actual size (100%)”.`],
  [/^前回の続きを開きました\((.+)保存\)$/,(m)=>`Restored your last session (saved ${m[1]})`],
  [/^×(\d+)$/,(m)=>`×${m[1]}`],
];
const JP=/[぀-ヿ一-鿿！-～]/;
let lang="ja";
function T(s,vars){
  let out=s;
  if(lang==="en"){
    if(Object.prototype.hasOwnProperty.call(EN,s))out=EN[s];
    else for(const [re,fn] of PATTERNS){const m=String(s).match(re);if(m){out=fn(m);break}}
  }
  if(vars)out=out.replace(/\{(\w+)\}/g,(_,k)=>vars[k]??"");
  return out;
}
/* 訳さない場所:カードの中身・印刷用・入力欄 */
const SKIP=".no-i18n,.face,.m-face-inner,.thumb-paper,.print-sheet,#printPages,.m-sheet,#sheetTitle,script,style,textarea";
const originals=new WeakMap();
function translateText(node){
  const v=node.nodeValue;if(!v||!JP.test(v))return;
  const p=node.parentElement;if(!p)return;
  if(p.closest(SKIP)&&!p.closest(".ph"))return;
  const key=v.trim(),t=T(key);if(t===key)return;
  if(!originals.has(node))originals.set(node,v);
  node.nodeValue=v.replace(key,t);
}
const ATTRS=["title","aria-label","placeholder"];
function translateAttrs(elm){
  if(elm.closest&&elm.closest(SKIP)&&!elm.closest(".ph"))return;
  for(const a of ATTRS){
    const v=elm.getAttribute&&elm.getAttribute(a);if(!v||!JP.test(v))continue;
    const t=T(v);if(t===v)continue;
    if(!elm.hasAttribute("data-ja-"+a))elm.setAttribute("data-ja-"+a,v);
    elm.setAttribute(a,t);
  }
}
function applyTo(root){
  if(lang!=="en"||!root)return;
  if(root.nodeType===3){translateText(root);return}
  if(root.nodeType!==1)return;
  translateAttrs(root);
  const w=document.createTreeWalker(root,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT);
  let n;while((n=w.nextNode())){if(n.nodeType===3)translateText(n);else translateAttrs(n)}
}
function restoreAll(){
  const w=document.createTreeWalker(document.body,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT);let n;
  while((n=w.nextNode())){
    if(n.nodeType===3){if(originals.has(n)){n.nodeValue=originals.get(n);originals.delete(n)}}
    else for(const a of ATTRS){const k="data-ja-"+a;if(n.hasAttribute(k)){n.setAttribute(a,n.getAttribute(k));n.removeAttribute(k)}}
  }
}
let observer=null,busy=false;
function observe(){
  if(observer)return;
  observer=new MutationObserver(list=>{
    if(lang!=="en"||busy)return;busy=true;
    try{for(const m of list){
      if(m.type==="childList")m.addedNodes.forEach(applyTo);
      else if(m.type==="characterData")translateText(m.target);
      else if(m.type==="attributes")translateAttrs(m.target);
    }}finally{busy=false}
  });
  observer.observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:ATTRS});
}
function setLang(l,{save=true}={}){
  lang=l==="en"?"en":"ja";
  document.documentElement.lang=lang;
  if(save){try{localStorage.setItem("pk-lang",lang)}catch(e){}}
  if(lang==="en"){applyTo(document.body);document.title=T("カードモックツクール β（改良テスト版） | Card Mock Maker")}
  else{restoreAll();document.title=document.documentElement.dataset.jaTitle||document.title}
  document.querySelectorAll("[data-lang-btn]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.langBtn===lang)));
  document.dispatchEvent(new CustomEvent("cmm-langchange",{detail:{lang}}));
}
function initial(){
  const q=(location.search.match(/[?&]lang=(ja|en)/)||[])[1];let saved=null;
  try{saved=localStorage.getItem("pk-lang")}catch(e){}
  return q||saved||"ja";
}
window.CMMI18N={T,setLang,applyTo,get lang(){return lang},init(){document.documentElement.dataset.jaTitle=document.title;observe();setLang(initial(),{save:false})}};
})();

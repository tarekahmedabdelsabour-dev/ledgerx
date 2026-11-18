(function(){
var D=window.LXD,root=document.documentElement,$=function(i){return document.getElementById(i)};
var UI={ar:{docs:"الدليل",search:"بحث في الدليل",open_app:"فتح النظام",on_page:"في هذه الصفحة",prev:"السابق",next:"التالي",none:"لا توجد نتائج",ph:"اكتب كلمة للبحث...",home:"الرئيسية",welcome:"دليل LedgerX",sub:"كل ما تحتاجه لتشغيل النظام وإدارة شركتك، من الإعداد الأول إلى التقارير."},
en:{docs:"Docs",search:"Search the docs",open_app:"Open the app",on_page:"On this page",prev:"Previous",next:"Next",none:"No results",ph:"Type to search...",home:"Home",welcome:"LedgerX Documentation",sub:"Everything you need to run the system and manage your company, from first setup to reports."}};
var lang="ar";try{lang=localStorage.getItem("lx_docs_lang")||((navigator.language||"").slice(0,2)==="en"?"en":"ar")}catch(e){}
var theme="";try{theme=localStorage.getItem("lx_docs_theme")||""}catch(e){}
if(!theme&&window.matchMedia&&matchMedia("(prefers-color-scheme: dark)").matches)theme="dark";
var flat=[];D.sections.forEach(function(s){s.p.forEach(function(p){flat.push({s:s,p:p})})});
function T(o){return o[lang]||o.ar}
function body(id){var b=(D.body[lang]||{})[id];return b==null?(D.body.ar||{})[id]||"":b}
function esc(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}
function inline(s){
 s=esc(s);var codes=[];
 s=s.replace(/`([^`]+)`/g,function(_,c){codes.push(c);return "\u0001"+(codes.length-1)+"\u0001"});
 s=s.replace(/\*\*([^*]+)\*\*/g,"<b>$1</b>").replace(/\[([^\]]+)\]\(([^)]+)\)/g,function(_,t,u){return '<a href="'+u+'"'+(/^https?:/.test(u)?' target="_blank" rel="noopener"':"")+'>'+t+'</a>'});
 return s.replace(/\u0001(\d+)\u0001/g,function(_,i){return "<code>"+codes[i]+"</code>"})}
function md(src){
 var L=src.replace(/\r/g,"").split("\n"),o=[],i=0,heads=[];
 while(i<L.length){var l=L[i];
  if(/^```/.test(l)){var c=[];i++;while(i<L.length&&!/^```/.test(L[i]))c.push(esc(L[i++]));i++;o.push("<pre><code>"+c.join("\n")+"</code></pre>");continue}
  var h=l.match(/^(#{2,3}) (.*)/);
  if(h){var id="h"+heads.length;heads.push({id:id,lv:h[1].length,t:h[2]});o.push("<h"+h[1].length+' id="'+id+'">'+inline(h[2])+"</h"+h[1].length+">");i++;continue}
  if(/^\|/.test(l)){var rows=[];while(i<L.length&&/^\|/.test(L[i]))rows.push(L[i++]);
   var cells=function(r){return r.replace(/^\||\|$/g,"").split("|").map(function(x){return x.trim()})};
   var t="<table><thead><tr>"+cells(rows[0]).map(function(x){return "<th>"+inline(x)+"</th>"}).join("")+"</tr></thead><tbody>";
   rows.slice(2).forEach(function(r){t+="<tr>"+cells(r).map(function(x){return "<td>"+inline(x)+"</td>"}).join("")+"</tr>"});o.push(t+"</tbody></table>");continue}
  if(/^> /.test(l)){var n=[];while(i<L.length&&/^> /.test(L[i]))n.push(L[i++].slice(2));var w=/^!/.test(n[0]);if(w)n[0]=n[0].slice(1).trim();o.push('<div class="note'+(w?" warn":"")+'">'+inline(n.join(" "))+"</div>");continue}
  if(/^\s*([-*]|\d+\.) /.test(l)){var ord=/^\s*\d+\./.test(l),it=[];while(i<L.length&&/^\s*([-*]|\d+\.) /.test(L[i]))it.push(L[i++].replace(/^\s*([-*]|\d+\.) /,""));o.push("<"+(ord?"ol":"ul")+">"+it.map(function(x){return "<li>"+inline(x)+"</li>"}).join("")+"</"+(ord?"ol":"ul")+">");continue}
  if(!l.trim()){i++;continue}
  var p=[];while(i<L.length&&L[i].trim()&&!/^(#{2,3} |```|\||> |\s*([-*]|\d+\.) )/.test(L[i]))p.push(L[i++]);o.push("<p>"+inline(p.join(" "))+"</p>")}
 return {html:o.join("\n"),heads:heads}}
function href(s,p){return "#/"+s.id+"/"+p.id}
function tree(cur){
 var h="";D.sections.forEach(function(s){var open=cur&&cur.s===s;
  h+='<div class="sec'+(open?" open":"")+'"><button><span>'+esc(T(s.t))+'</span><i>&#9656;</i></button><ul>';
  s.p.forEach(function(p){h+='<li><a href="'+href(s,p)+'"'+(cur&&cur.p===p?' class="on"':"")+">"+esc(T(p.t))+"</a></li>"});h+="</ul></div>"});
 $("tree").innerHTML=h;
 [].forEach.call(document.querySelectorAll(".sec>button"),function(b){b.onclick=function(){b.parentNode.classList.toggle("open")}})}
function home(){
 var h='<h1>'+UI[lang].welcome+'</h1><p class="lead">'+UI[lang].sub+'</p><div class="cards">';
 D.sections.forEach(function(s){h+='<a href="'+href(s,s.p[0])+'"><b>'+esc(T(s.t))+'</b><span>'+esc(T(s.p[0].t))+"</span></a>"});
 $("article").innerHTML=h+"</div>";$("toc").innerHTML="";$("pager").innerHTML="";tree(null);document.title="LedgerX Docs"}
function render(){
 var m=location.hash.match(/^#\/([^\/]+)\/([^\/?]+)/),cur=null;
 if(m)flat.forEach(function(x){if(x.s.id===m[1]&&x.p.id===m[2])cur=x});
 root.lang=lang;root.dir=lang==="ar"?"rtl":"ltr";root.dataset.theme=theme||"light";
 $("lang-btn").textContent=lang==="ar"?"EN":"ع";
 [].forEach.call(document.querySelectorAll("[data-i18n]"),function(e){e.textContent=UI[lang][e.dataset.i18n]});
 $("q").placeholder=UI[lang].ph;
 if(!cur){home();return}
 var r=md(body(cur.p.id)),k=flat.indexOf(cur);
 $("article").innerHTML='<div class="crumbs"><a href="#/">'+UI[lang].home+"</a> / "+esc(T(cur.s.t))+"</div><h1>"+esc(T(cur.p.t))+"</h1>"+r.html;
 $("toc").innerHTML=r.heads.length?"<b>"+UI[lang].on_page+"</b>"+r.heads.map(function(x){return '<a href="#" data-h="'+x.id+'" class="l'+x.lv+'">'+inline(x.t)+"</a>"}).join(""):"";
 [].forEach.call($("toc").querySelectorAll("a"),function(a){a.onclick=function(e){e.preventDefault();$(a.dataset.h).scrollIntoView()}});
 var pg="",pv=flat[k-1],nx=flat[k+1];
 if(pv)pg+='<a href="'+href(pv.s,pv.p)+'"><small>'+UI[lang].prev+"</small>"+esc(T(pv.p.t))+"</a>";
 if(nx)pg+='<a class="next" href="'+href(nx.s,nx.p)+'"><small>'+UI[lang].next+"</small>"+esc(T(nx.p.t))+"</a>";
 $("pager").innerHTML=pg;tree(cur);document.title=T(cur.p.t)+" - LedgerX";
 $("side").classList.remove("show");$("scrim").classList.remove("show");window.scrollTo(0,0);spy()}
function spy(){var hs=[].slice.call($("article").querySelectorAll("h2,h3")),as=$("toc").querySelectorAll("a");
 if(!hs.length)return;var cur=0;hs.forEach(function(h,i){if(h.getBoundingClientRect().top<120)cur=i});
 [].forEach.call(as,function(a,i){a.classList.toggle("on",i===cur)})}
window.addEventListener("scroll",spy);window.addEventListener("hashchange",render);
$("lang-btn").onclick=function(){lang=lang==="ar"?"en":"ar";try{localStorage.setItem("lx_docs_lang",lang)}catch(e){}render()};
$("theme-btn").onclick=function(){theme=(root.dataset.theme==="dark")?"light":"dark";try{localStorage.setItem("lx_docs_theme",theme)}catch(e){}root.dataset.theme=theme};
$("print-btn").onclick=function(){window.print()};
$("menu-btn").onclick=function(){$("side").classList.toggle("show");$("scrim").classList.toggle("show")};
$("scrim").onclick=function(){$("side").classList.remove("show");$("scrim").classList.remove("show")};
/* search */
var idx=null;function build(){idx=flat.map(function(x){return {x:x,t:T(x.p.t),s:T(x.s.t),b:body(x.p.id).replace(/[#`*|>\[\]()-]/g," ")}})}
function search(q){if(!idx)build();q=q.trim().toLowerCase();if(!q)return[];
 return idx.map(function(r){var sc=0,tl=r.t.toLowerCase(),bl=r.b.toLowerCase();
  q.split(/\s+/).forEach(function(w){if(tl.indexOf(w)>-1)sc+=10;if(bl.indexOf(w)>-1)sc+=1;else sc-=100});return {r:r,sc:sc}}).filter(function(z){return z.sc>0}).sort(function(a,b){return b.sc-a.sc}).slice(0,12)}
function openS(){idx=null;$("modal").hidden=false;$("q").value="";$("results").innerHTML="";$("q").focus()}
function closeS(){$("modal").hidden=true}
$("search-btn").onclick=openS;$("modal").onclick=function(e){if(e.target===$("modal"))closeS()};
$("q").oninput=function(){var q=$("q").value,res=search(q),h="";
 if(q.trim()&&!res.length)h='<a><small>'+UI[lang].none+"</small></a>";
 res.forEach(function(z){var r=z.r,b=r.b.replace(/\s+/g," "),w=q.trim().toLowerCase().split(/\s+/)[0],p=b.toLowerCase().indexOf(w),sn=p>-1?b.slice(Math.max(0,p-40),p+90):b.slice(0,110);
  h+='<a href="'+href(r.x.s,r.x.p)+'">'+esc(r.t)+"<small>"+esc(r.s)+" - "+esc(sn)+"</small></a>"});
 $("results").innerHTML=h};
$("results").onclick=function(e){if(e.target.closest("a[href]"))closeS()};
$("q").onkeydown=function(e){if(e.key==="Enter"){var a=$("results").querySelector("a[href]");if(a){location.hash=a.getAttribute("href");closeS()}}};
document.addEventListener("keydown",function(e){if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k"){e.preventDefault();openS()}if(e.key==="Escape")closeS()});
render();
})();

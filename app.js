const baseAPI="https://emsifa.github.io/api-wilayah-indonesia/api";
const proxyFallback="https://api.codetabs.com/v1/proxy?quest=";

btnParse.onclick=parseNIK;
btnClear.onclick=()=>{nik.value="";result.innerHTML="";};

function showLoading(v){loading.style.display=v?"block":"none";}

function parseDateFromNIK(n){
  const t=parseInt(n.slice(6,8));
  const b=parseInt(n.slice(8,10));
  let y=parseInt(n.slice(10,12))+2000;
  if(y>new Date().getFullYear())y-=100;
  return{
    t:t>40?t-40:t,
    b,y,
    g:t>40?"Perempuan":"Laki-laki",
    u:new Date().getFullYear()-y
  };
}

async function fetchJSON(u){
  try{
    const r=await fetch(u);
    if(!r.ok)throw"err";
    return r.json();
  }catch{
    return fetchJSON(proxyFallback+encodeURIComponent(u));
  }
}

async function parseNIK(){
  const v=nik.value.trim();
  if(!/^\d{16}$/.test(v)){
    result.innerHTML='<div class="error">NIK harus 16 digit angka</div>';
    return;
  }

  showLoading(true);
  result.innerHTML="";

  const d=parseDateFromNIK(v);
  const p=await fetchJSON(`${baseAPI}/provinces.json`);
  const prov=p.find(x=>x.id.startsWith(v.slice(0,2)))||{};
  const kab=prov.id?(await fetchJSON(`${baseAPI}/regencies/${prov.id}.json`)).find(x=>x.id.slice(2,4)==v.slice(2,4))||{}:{};
  const kec=kab.id?(await fetchJSON(`${baseAPI}/districts/${kab.id}.json`)).find(x=>x.id.slice(4,6)==v.slice(4,6))||{}:{};

  showLoading(false);

  result.innerHTML=`
    <div class="item"><span>NIK</span><b>${v}</b></div>
    <div class="item"><span>Provinsi</span><b>${prov.name||"-"}</b></div>
    <div class="item"><span>Kabupaten</span><b>${kab.name||"-"}</b></div>
    <div class="item"><span>Kecamatan</span><b>${kec.name||"-"}</b></div>
    <div class="item"><span>Tanggal Lahir</span><b>${d.t}-${d.b}-${d.y}</b></div>
    <div class="item"><span>Jenis Kelamin</span><b>${d.g}</b></div>
    <div class="item"><span>Umur</span><b>${d.u} tahun</b></div>
  `;
}

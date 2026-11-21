"""Florida place data from GeoNames US.txt (download.geonames.org/export/dump/US.zip).
Writes FL entries (pop >= 10,000 get their own page) into content/us_cities.json and
every populated FL place (all cities, towns, villages, CDPs) into content/fl_places_all.json."""
import json, math, re, datetime as dt, geonamescache as g, sys
from zoneinfo import ZoneInfo
ROOT='/home/claude/abdullahshahab-website/'
co={c['fips']:c['name'].replace(' County','') for c in g.GeonamesCache().get_us_counties()}
M=json.load(open(ROOT+'tools/data/fl_metro.json'))
norm=lambda c:c.lower().replace('saint ','st. ').replace('-',' ')
c2m={norm(c):m for m,cs in M.items() for c in cs}
FLNB=json.load(open(ROOT+'tools/data/fl_nb.json')); nbn={n.lower() for v in FLNB.values() for n in v}
def d(a,b,c,e): return math.hypot((a-c)*111,(b-e)*111*math.cos(math.radians(a)))
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower().replace('st.','saint').replace('.','')).strip('-')
def tz(t):
    z=ZoneInfo(t); k=ZoneInfo('Asia/Karachi'); o=[]
    for m in (1,7):
        x=dt.datetime(2026,m,15,12); o.append(int((x.replace(tzinfo=k).utcoffset()-x.replace(tzinfo=z).utcoffset()).total_seconds()//3600))
    return {'America/New_York':'Eastern','America/Chicago':'Central'}.get(t,t), min(o), max(o)
P=[]
for line in open('/tmp/work/US.txt',encoding='utf-8'):
    p=line.rstrip('\n').split('\t')
    if p[10]!='FL' or p[6]!='P' or p[7] not in ('PPL','PPLA','PPLA2','PPLL'): continue
    pop=int(p[14] or 0)
    if pop<=0 or p[1].lower() in nbn: continue
    P.append({'name':p[1].replace('Saint Petersburg','St. Petersburg'),'county':co.get('12'+p[11],''),'pop':pop,'lat':float(p[4]),'lon':float(p[5]),'tz':p[17],'seat':p[7] in ('PPLA','PPLA2')})
P.sort(key=lambda x:-x['pop'])
seen=set(); allp=[]
for x in P:
    k=(x['name'],x['county'])
    if k in seen: continue
    seen.add(k); allp.append(x)
old={c['slug']:c for c in json.load(open(ROOT+'content/us_cities.json')) if c['state']=='FL'}
pages=[]; used=set()
big=[x for x in allp if x['pop']>=5000]
for x in big:
    s=slug(x['name'])
    if s in used: s=slug(x['name']+' '+x['county'])
    used.add(s); x['slug']=s
    zn,lo,hi=tz(x['tz'])
    near=sorted([y for y in big if y is not x],key=lambda y:d(x['lat'],x['lon'],y['lat'],y['lon']))[:8]
    near=[y['name'] for y in near if d(x['lat'],x['lon'],y['lat'],y['lon'])<30]
    pages.append({"name":x['name'],"state":"FL","state_name":"Florida","slug":s,"state_slug":"florida","pop":x['pop'],
      "county":x['county'],"metro":c2m.get(norm(x['county']),""),"seat":x['seat'],"lat":x['lat'],"lon":x['lon'],"tz":zn,"off_lo":lo,"off_hi":hi,
      "near":near,"nb":(old.get(s) or {}).get('nb') or FLNB.get(x['name'],[])})
allc=[c for c in json.load(open(ROOT+'content/us_cities.json')) if c['state']!='FL']+pages
json.dump(allc,open(ROOT+'content/us_cities.json','w'),indent=0,ensure_ascii=False)
json.dump([{"name":x['name'],"county":x['county'],"pop":x['pop'],"slug":x.get('slug'),"seat":x['seat'],"tz":tz(x['tz'])[0]} for x in allp],open(ROOT+'content/fl_places_all.json','w'),indent=0,ensure_ascii=False)
print(len(pages),'FL pages;',len(allp),'FL places;',len({x['county'] for x in allp}),'counties; no-metro',sum(1 for c in pages if not c['metro']))
missing=[s for s in old if s not in used]; print('old FL slugs not kept:',missing)

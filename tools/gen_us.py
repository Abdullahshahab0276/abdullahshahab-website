import geonamescache as g, csv, math, json, re, datetime as dt
from zoneinfo import ZoneInfo
gc=g.GeonamesCache(min_city_population=15000)
ALL=[x for x in gc.get_cities().values() if x['countrycode']=='US']
EXCL={"Meads","East Independence","West Raleigh","East Chattanooga","New South Memphis","East Hampton","North Stamford","North Peoria","South Boston","Deer Valley","Maryvale","Tempe Junction","Chinatown","Koreatown","Alhambra|AZ","Tri-Cities","Borough Park","Bushwick","East Flatbush","East New York","Gravesend","Harlem","Sheepshead Bay","Upper West Side","Washington Heights","East Harlem","Sunset Park","Astoria","Corona|NY","Elmhurst|NY","Jamaica|NY","Hollywood|CA","Paradise|NV","Spring Valley|NV","Enterprise|NV","Sunrise Manor|NV"}
REN={"Lexington-Fayette":"Lexington","Metairie Terrace":"Metairie","New York City":"New York City","Saint Paul":"St. Paul"}
states={s['code']:s['name'] for s in gc.get_us_states().values()}
states['DC']='District of Columbia'
K=[r for r in csv.DictReader(open('/tmp/work/data/us_cities.csv'))]
def d(a,b,c,e): return math.hypot((a-c)*111,(b-e)*111*math.cos(math.radians(a)))
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower().replace('st.','saint').replace('.','')).strip('-')
def tzinfo(tz):
    z=ZoneInfo(tz); k=ZoneInfo('Asia/Karachi')
    offs=[]
    for m in (1,7):
        t=dt.datetime(2026,m,15,12)
        offs.append(int((t.replace(tzinfo=k).utcoffset()-t.replace(tzinfo=z).utcoffset()).total_seconds()//3600))
    names={'America/New_York':'Eastern','America/Detroit':'Eastern','America/Indiana/Indianapolis':'Eastern','America/Kentucky/Louisville':'Eastern','America/Chicago':'Central','America/Denver':'Mountain','America/Boise':'Mountain','America/Phoenix':'Mountain (no daylight saving)','America/Los_Angeles':'Pacific','America/Anchorage':'Alaska','Pacific/Honolulu':'Hawaii'}
    return names.get(tz, tz.split('/')[-1].replace('_',' ')), min(offs), max(offs)
NB=json.load(open('/tmp/work/nb_us.json'))
for st,fn in [('TX','/tmp/work/tx_nb.json'),('FL','/tmp/work/fl_nb.json')]:
    try:
        for k,v in json.load(open(fn)).items(): NB[f"{st}|{k}"]=v
    except FileNotFoundError: pass
cities=[]
for x in ALL:
    if x['population']<100000: continue
    nm=x['name']; st=x['admin1code']
    if nm in EXCL or f"{nm}|{st}" in EXCL: continue
    nm=REN.get(nm,nm)
    cand=[r for r in K if r['STATE_CODE']==st]
    county=""
    if cand:
        best=min(cand,key=lambda r:d(x['latitude'],x['longitude'],float(r['LATITUDE']),float(r['LONGITUDE'])))
        county=best['COUNTY'].replace('Miami-dade','Miami-Dade').replace('Saint ','St. ')
    kn={r['CITY'].lower() for r in cand}
    near=sorted([y for y in ALL if y['admin1code']==st and y is not x and y['name'].lower() in kn and y['population']>=25000 and y['name'] not in EXCL and f"{y['name']}|{st}" not in EXCL and d(x['latitude'],x['longitude'],y['latitude'],y['longitude'])<45],key=lambda y:-y['population'])[:8]
    if nm=='New York City': county='the five boroughs (New York, Kings, Queens, Bronx and Richmond counties)'
    zn,lo,hi=tzinfo(x['timezone'])
    cities.append({"name":nm,"state":st,"state_name":states.get(st,st),"slug":slug(nm),"state_slug":slug(states.get(st,st)),
        "pop":x['population'],"county":county,"lat":x['latitude'],"lon":x['longitude'],"tz":zn,"off_lo":lo,"off_hi":hi,
        "near":[REN.get(y['name'],y['name']) for y in near],"nb":NB.get(f"{st}|{nm}",[])})
# dedupe by state+slug
seen={}; out=[]
for c in sorted(cities,key=lambda c:-c['pop']):
    k=(c['state'],c['slug'])
    if k in seen: continue
    seen[k]=1; out.append(c)
json.dump(out,open('/home/claude/abdullahshahab-website/content/us_cities.json','w'),indent=0,ensure_ascii=False)
import collections
print(len(out),'cities in',len({c['state'] for c in out}),'states'); print(collections.Counter(c['tz'] for c in out))
print([ (c['name'],c['state'],c['off_lo'],c['off_hi'],c['county'],c['near'][:3]) for c in out[:6]])

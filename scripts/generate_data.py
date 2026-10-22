"""Generates the synthetic Lakeshore Provisions dataset into ../data. Seeded, so output is reproducible."""
import numpy as np, pandas as pd, os, random
rng = np.random.default_rng(42); random.seed(42)
import pathlib
OUT = str(pathlib.Path(__file__).resolve().parent.parent / "data"); os.makedirs(OUT, exist_ok=True)

# ---------- Regions ----------
regions = pd.DataFrame([
    ("R1","Chicago Metro","IL"),("R2","Northwest Indiana","IN"),
    ("R3","Milwaukee & SE Wisconsin","WI"),("R4","Central Illinois","IL"),
    ("R5","Michigan West","MI")], columns=["region_id","region_name","state"])
region_weight = {"R1":0.38,"R2":0.17,"R3":0.18,"R4":0.15,"R5":0.12}

# ---------- Sales reps ----------
first = ["Maria","James","Priya","Kevin","Aisha","Tom","Daniel","Rachel","Luis","Megan","Andre","Sofia"]
last  = ["Gonzalez","O'Brien","Patel","Nguyen","Johnson","Kowalski","Murphy","Chen","Ramirez","Schultz","Washington","Rossi"]
rep_regions = ["R1","R1","R1","R1","R2","R2","R3","R3","R4","R4","R5","R5"]
hire = ["2018-03-12","2020-07-01","2019-11-04","2025-02-17","2017-05-22","2021-09-13",
        "2016-01-11","2022-04-04","2019-06-24","2023-08-14","2020-02-03","2024-10-07"]
reps = pd.DataFrame({"rep_id":[f"SR{100+i}" for i in range(12)],
    "rep_name":[f"{a} {b}" for a,b in zip(first,last)],
    "region_id":rep_regions,"hire_date":hire})
# Story: SR103 (Kevin Nguyen) hired Feb 2025, Chicago - ramps up. SR105 (Tom Kowalski) NW Indiana underperforms.

# ---------- Products ----------
cats = {
 "Dairy":[("Whole Milk 1 Gal (6pk)",21.5),("2% Milk 1 Gal (6pk)",20.9),("Shredded Mozzarella 5lb",17.8),("Cheddar Block 10lb",38.4),("Butter Solids 36ct",112.0),("Heavy Cream 1/2 Gal (6pk)",42.0),("Greek Yogurt 32oz (6pk)",27.5),("Sour Cream 5lb",12.9)],
 "Meat & Poultry":[("Chicken Breast IQF 40lb",118.0),("Ground Beef 80/20 10lb",52.0),("Italian Beef Sliced 10lb",79.0),("Pork Shoulder 20lb",61.0),("Bacon Layflat 15lb",84.0),("Polish Sausage 10lb",46.0),("Turkey Breast Deli 2x9lb",88.0),("Chicken Wings 40lb",131.0)],
 "Seafood":[("Atlantic Salmon Fillet 10lb",142.0),("Cod Loins 10lb",115.0),("Shrimp 21/25 2lb (5pk)",96.0),("Lake Perch Fillet 5lb",89.0),("Tilapia Fillet 10lb",58.0)],
 "Produce":[("Romaine Hearts 24ct",34.0),("Yellow Onions 50lb",24.5),("Russet Potatoes 50lb",26.0),("Roma Tomatoes 25lb",31.0),("Lemons 115ct",38.0),("Mixed Greens 3lb (4pk)",29.5),("Green Peppers 1-1/9 Bu",33.0),("Avocados Hass 48ct",54.0)],
 "Frozen":[("French Fries 6x5lb",36.0),("Pizza Dough Balls 60ct",41.0),("Vanilla Ice Cream 3 Gal",29.0),("Mixed Vegetables 12x2.5lb",39.0),("Breaded Cheese Curds 4x3lb",57.0),("Tater Tots 6x5lb",38.5)],
 "Dry Goods":[("All-Purpose Flour 50lb",23.0),("Penne Pasta 2x10lb",19.5),("Long Grain Rice 50lb",34.0),("Tomato Sauce #10 (6ct)",28.0),("Canola Oil 35lb",44.0),("Sugar Granulated 50lb",36.0),("Giardiniera Hot 1 Gal (4ct)",48.0)],
 "Beverages":[("Bottled Water 16oz (24pk)",6.2),("Cold Brew Concentrate 1 Gal (2pk)",38.0),("Orange Juice 1/2 Gal (8pk)",27.0),("Lemonade Mix 6x1 Gal",22.0),("Coffee Ground 2.5oz (42ct)",44.0)],
 "Paper & Disposables":[("To-Go Container 9x9 (200ct)",39.0),("Napkins Dinner (3000ct)",31.0),("Nitrile Gloves L (1000ct)",48.0),("Foil Sheets 12x10.75 (500ct)",21.0),("Paper Cups 16oz (1000ct)",42.0)],
}
supplier = {"Dairy":"Prairie Farms Co-op","Meat & Poultry":"Midwest Protein Partners","Seafood":"Great Lakes Seafood Supply","Produce":"Heartland Fresh Produce","Frozen":"NorthStar Frozen Foods","Dry Goods":"Lakeview Pantry Wholesale","Beverages":"Lakeview Pantry Wholesale","Paper & Disposables":"Windy City Packaging"}
margin = {"Dairy":0.18,"Meat & Poultry":0.22,"Seafood":0.26,"Produce":0.24,"Frozen":0.28,"Dry Goods":0.30,"Beverages":0.33,"Paper & Disposables":0.35}
rows=[]; i=1000
for c,items in cats.items():
    for n,p in items:
        rows.append((f"P{i}",n,c,supplier[c],p,round(p*(1-margin[c]),2))); i+=1
products = pd.DataFrame(rows,columns=["product_id","product_name","category","supplier","list_price","unit_cost"])
salmon_id = products.loc[products.product_name.str.startswith("Atlantic Salmon"),"product_id"].item()

# ---------- Customers ----------
seg_types = ["Independent Restaurant","Restaurant Group","Hotel","Hospital/Healthcare","School/University","Caterer","Grocery/Deli"]
seg_w = [0.40,0.12,0.08,0.08,0.10,0.12,0.10]
pre = ["Lakeside","Maple","Northside","Hometown","Union","Riverside","Golden","Prairie","Oak Street","West Loop","Harbor","Lincoln","Iron","Redline","Bluebird","Copper","Second City","Fulton","Cedar","Southport","Midway","Pilsen","Wicker","Logan","Bridgeport","Heritage","Summit","Lantern","Crescent","Elmwood"]
suf = {"Independent Restaurant":["Grill","Kitchen","Bistro","Tavern","Diner","Taqueria","Pizzeria","Eatery"],
       "Restaurant Group":["Hospitality Group","Restaurant Group","Dining Co."],
       "Hotel":["Hotel","Inn & Suites","Lodge"],"Hospital/Healthcare":["Medical Center","Health System","Senior Living"],
       "School/University":["College Dining","School District","Academy"],"Caterer":["Catering","Events & Catering"],
       "Grocery/Deli":["Market","Deli","Fresh Market"]}
cities = {"R1":["Chicago","Evanston","Oak Park","Naperville","Schaumburg","Skokie","Cicero","Aurora"],
          "R2":["Gary","Hammond","Merrillville","Valparaiso","Crown Point"],
          "R3":["Milwaukee","Kenosha","Racine","Waukesha"],
          "R4":["Peoria","Bloomington","Champaign","Springfield"],
          "R5":["Grand Rapids","Kalamazoo","Holland","Muskegon"]}
N_CUST=420; cust=[]; used=set()
for k in range(N_CUST):
    r = rng.choice(list(region_weight), p=list(region_weight.values()))
    s = rng.choice(seg_types, p=seg_w)
    while True:
        nm = f"{random.choice(pre)} {random.choice(suf[s])}"
        if nm not in used: used.add(nm); break
    since = pd.Timestamp("2015-01-01")+pd.Timedelta(days=int(rng.integers(0,3500)))
    cust.append((f"C{5000+k}",nm,s,r,random.choice(cities[r]),since.date()))
customers = pd.DataFrame(cust,columns=["customer_id","customer_name","segment","region_id","city","customer_since"])
# The big NW Indiana account that churns in 2026
big = customers.index[customers.region_id=="R2"][0]
customers.loc[big,["customer_name","segment","city"]] = ["Calumet Regional Health System","Hospital/Healthcare","Merrillville"]
big_id = customers.loc[big,"customer_id"]
# customer size weights (pareto)
cw = np.minimum(rng.pareto(1.6,N_CUST)+1, 25)
cw[big] = cw.sum()*0.012
customers["_w"]=cw
# assign rep from region (new rep SR103 only gets customers from 2025)
def pick_rep(reg): return rng.choice(reps.loc[reps.region_id==reg,"rep_id"].values)
customers["rep_id"]=[pick_rep(r) for r in customers.region_id]
customers.loc[big,"rep_id"]="SR105"

# ---------- Orders ----------
dates = pd.date_range("2024-10-01","2026-09-30",freq="D")
orders=[]; oid=100001
seas_month = {1:0.85,2:0.88,3:0.97,4:1.0,5:1.07,6:1.13,7:1.15,8:1.12,9:1.03,10:1.0,11:1.02,12:1.06}
cat_seas = {"Frozen":{6:1.35,7:1.45,8:1.35,12:0.8,1:0.75},"Produce":{6:1.2,7:1.25,8:1.2},"Beverages":{6:1.3,7:1.4,8:1.3},"Seafood":{2:1.4,3:1.5}}  # Lent
probs = customers._w.values/customers._w.sum()
cust_idx = np.arange(N_CUST)
prod_by_cat = products.groupby("category").product_id.apply(list).to_dict()
price = products.set_index("product_id").list_price.to_dict()
pcat = products.set_index("product_id").category.to_dict()
cat_pref = {"Independent Restaurant":{"Meat & Poultry":3,"Produce":3,"Dairy":2,"Frozen":2,"Dry Goods":2,"Paper & Disposables":2,"Seafood":1,"Beverages":1},
            "Restaurant Group":{"Meat & Poultry":3,"Produce":3,"Dairy":2,"Frozen":2,"Dry Goods":2,"Paper & Disposables":2,"Seafood":2,"Beverages":1},
            "Hotel":{"Beverages":3,"Dairy":2,"Produce":2,"Meat & Poultry":2,"Seafood":2,"Dry Goods":1,"Frozen":1,"Paper & Disposables":1},
            "Hospital/Healthcare":{"Dairy":3,"Produce":3,"Dry Goods":2,"Meat & Poultry":2,"Paper & Disposables":3,"Beverages":2,"Frozen":1,"Seafood":0.5},
            "School/University":{"Frozen":3,"Dairy":3,"Dry Goods":3,"Paper & Disposables":2,"Meat & Poultry":2,"Produce":1,"Beverages":2,"Seafood":0.3},
            "Caterer":{"Meat & Poultry":3,"Seafood":2,"Produce":3,"Paper & Disposables":3,"Dairy":1,"Dry Goods":1,"Frozen":1,"Beverages":2},
            "Grocery/Deli":{"Dairy":3,"Meat & Poultry":3,"Beverages":2,"Produce":2,"Dry Goods":2,"Frozen":1,"Seafood":1,"Paper & Disposables":1}}
crec = [r for r in customers.itertuples()]
for d in dates:
    if d.weekday()==6: continue
    base = 20 if d.weekday()<5 else 7
    yr_growth = 1+0.08*((d-dates[0]).days/365)
    n = rng.poisson(base*seas_month[d.month]*yr_growth)
    for _ in range(n):
        ci = rng.choice(cust_idx,p=probs); c = crec[ci]
        cid = c.customer_id; reg = c.region_id; seg=c.segment; rep=c.rep_id
        # schools quiet in summer
        if seg=="School/University" and d.month in (6,7,8) and rng.random()<0.75: continue
        # big account churns after March 2026
        if cid==big_id and d>=pd.Timestamp("2026-04-01"): continue
        # NW Indiana broader softness in 2026
        if reg=="R2" and d.year==2026 and rng.random()<0.15: continue
        # SR103 starts Mar 2025: before that, his customers go to SR100
        if rep=="SR103" and d<pd.Timestamp("2025-03-01"): rep="SR100"
        # Michigan West growth
        if reg=="R5" and rng.random() < max(0,0.35-0.35*((d-dates[0]).days/730)): continue
        pref = cat_pref[seg]; cl=list(pref); w=np.array([pref[x]*cat_seas.get(x,{}).get(d.month,1) for x in cl],dtype=float); w/=w.sum()
        nlines = int(rng.integers(1,6)) if cid!=big_id else int(rng.integers(4,9))
        chosen=set()
        for ln in range(nlines):
            cat = rng.choice(cl,p=w); pid = random.choice(prod_by_cat[cat])
            if pid in chosen: continue
            chosen.add(pid)
            qty = int(max(1,rng.gamma(2.0, 4 if cid!=big_id else 12)))
            p = price[pid]
            if cat=="Dairy" and d>=pd.Timestamp("2026-01-01"):
                p*=1.09; qty=max(1,int(qty*0.85))   # dairy price hike -> volume drop
            elif d>=pd.Timestamp("2025-10-01"): p*=1.03
            disc = rng.choice([0,0,0,0,0.02,0.05,0.10],p=[.4,.15,.1,.1,.1,.1,.05])
            if cw[ci]>8: disc=max(disc,0.05)
            status="Delivered"
            rr = 0.17 if (pid==salmon_id and d>=pd.Timestamp("2025-06-01")) else 0.02
            u=rng.random()
            if u<rr: status="Returned"
            elif u<rr+0.015: status="Cancelled"
            if d>=pd.Timestamp("2026-09-26") and rng.random()<0.6: status = rng.choice(["Pending","Shipped"])
            ship = d + pd.Timedelta(days=int(rng.choice([1,1,1,2,2,3,4,6],)))
            orders.append([f"SO-{oid}",ln+1,d.date(),ship.date() if status!="Cancelled" else None,cid,pid,rep,qty,round(p,2),disc,status])
        oid+=1
fact = pd.DataFrame(orders,columns=["order_id","line_number","order_date","ship_date","customer_id","product_id","rep_id","quantity","unit_price","discount_pct","status"])
# renumber lines
fact["line_number"]=fact.groupby("order_id").cumcount()+1

# ---------- Targets (monthly quota per rep) ----------
fact["_rev"]=fact.quantity*fact.unit_price*(1-fact.discount_pct)
ok = fact[fact.status!="Cancelled"].copy()
ok["month"]=pd.to_datetime(ok.order_date).dt.to_period("M")
book = customers.set_index("customer_id").rep_id
ok["owner"]=ok.customer_id.map(book)
by_owner = ok.groupby(["owner","month"])._rev.sum()
by_rep = ok.groupby(["rep_id","month"])._rev.sum()
months = sorted(ok.month.unique())
tg=[]
for rep in reps.rep_id:
    for per in months:
        if rep=="SR103":
            if per<pd.Period("2025-03","M"): continue
            t = by_owner.get(("SR103",per-12),0)*1.10 if per>=pd.Period("2025-10","M") else by_rep.get((rep,per),0)*rng.uniform(0.86,0.97)
        elif per>=pd.Period("2025-10","M"):
            t = by_owner.get((rep,per-12),0)*(1.05 if rep=="SR105" else 1.07)
        else:
            t = by_rep.get((rep,per),0)*rng.uniform(0.94,1.08)
        tg.append((rep,per.to_timestamp().date(),int(round(t,-2))))
targets = pd.DataFrame(tg,columns=["rep_id","month_start","revenue_target"])
targets = targets[targets.revenue_target>0]
fact = fact.drop(columns="_rev")

# ---------- Deliberate messiness (for Power Query cleaning) ----------
# 1) exact duplicate rows (~0.4%)
dup = fact.sample(frac=0.004,random_state=1); fact = pd.concat([fact,dup]).sort_values(["order_date","order_id","line_number"]).reset_index(drop=True)
# 2) missing rep on some lines
fact.loc[fact.sample(frac=0.006,random_state=2).index,"rep_id"]=None
# 3) status casing / whitespace inconsistencies
idx=fact.sample(frac=0.01,random_state=3).index
fact.loc[idx,"status"]=fact.loc[idx,"status"].map(lambda s: random.choice([s.upper(),s.lower(),f" {s} "]))
# 4) a few negative / zero quantities (data entry errors)
fact.loc[fact.sample(n=25,random_state=4).index,"quantity"]=0
# 5) customer city/name whitespace & casing; segment variants
cidx=customers.sample(frac=0.05,random_state=5).index
customers.loc[cidx,"city"]=customers.loc[cidx,"city"].str.upper()
customers.loc[customers.sample(frac=0.03,random_state=6).index,"customer_name"]+= "  "
customers.loc[customers.sample(frac=0.04,random_state=7).index,"segment"]=customers.segment.map({"Independent Restaurant":"Indep. Restaurant","Restaurant Group":"Rest. Group"}).fillna(customers.segment)
customers=customers.drop(columns="_w")

fact.to_csv(f"{OUT}/fact_order_lines.csv",index=False)
customers.to_csv(f"{OUT}/dim_customers.csv",index=False)
products.to_csv(f"{OUT}/dim_products.csv",index=False)
reps.to_csv(f"{OUT}/dim_sales_reps.csv",index=False)
regions.to_csv(f"{OUT}/dim_regions.csv",index=False)
targets.to_csv(f"{OUT}/fact_sales_targets.csv",index=False)
print(len(fact), fact.order_id.nunique(), len(customers), len(products), len(targets))
print("big",big_id,"salmon",salmon_id)

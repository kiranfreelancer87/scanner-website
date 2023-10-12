import pymongo
s = [1,2,3,4,5,6,7,8,9,0]
print(s[-4:-2])
inst = "AXISBANK"
cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
db = cl.zerodha
mw = ['MONTHLY','WEEKLY']
final_data = {"MONTHLY":{},"WEEKLY":{}}
final_dict = {"MONTHLY":{"CE":[],"PE":[]},"WEEKLY":{"CE":[],"PE":[]}}
for m in mw:
  tmp_dict = {m:{"CE":[],"PE":[]}}
  table = db[inst+m]
  result_ce = list(table.find({"side":"CE"},{'_id': 0}))
  result_pe = list(table.find({"side":"PE"},{'_id': 0}))
  try:
   maxCE = max(result_ce, key=lambda x:x['oi'])
   maxPE = max(result_pe, key=lambda x:x['oi'])
  except :
   continue
  print(maxPE['strike'],maxCE['strike'])
  ce_up = sorted(result_ce, key=lambda d: d['strike'])
  pe_up = sorted(result_pe, key=lambda d: d['strike'])
  c_above = []
  c_below = []
  p_above= []
  p_below = []
  for c in ce_up:
     if (c['strike']) < maxCE['strike']:
         c_above.append(c)
     elif (c['strike']) >= maxCE['strike']:
         c_below.append(c)
  for c in pe_up:
     if (c['strike']) < maxPE['strike']:
         p_above.append(c)
     elif (c['strike']) >= maxPE['strike']:
         p_below.append(c)
  for p in c_above[-15:]:
     tmp_dict[m]["CE"].append([p['strike'],p['oi']])
  for p in c_below[:15]:
     tmp_dict[m]["CE"].append([p['strike'],p['oi']])
  for p in p_above[-15:]:
     tmp_dict[m]["PE"].append([p['strike'],p['oi']])
  for p in p_below[:15]:
     tmp_dict[m]["PE"].append([p['strike'],p['oi']])
  strikes = set()
  for lst in tmp_dict[m]['CE']:
    strikes.add(lst[0])
  for lst in tmp_dict[m]['PE']:
    strikes.add(lst[0])
  for strike in strikes:
     final_data[m][strike] = {}
  print(strikes)
  strikes = (sorted(strikes, reverse=True))
  for rce in result_ce:
     if rce['strike'] in strikes :
       final_data[m][rce['strike']]['CE'] = rce['oi']
  for rpe in result_pe:
      if rpe['strike'] in strikes :
       final_data[m][rpe['strike']]['PE'] = rpe['oi']
print(final_data)

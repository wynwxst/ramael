import ramael
import os

def cli():
  from flags import Flags
  import sys
  f = Flags(sys.argv)
  fla = f.flag
  if fla in ["-r","request"]:
    fl = f.arg
    url = f.args[0]
    f.args.remove(url)
    a = {}
    op = ["h","p"]
    for item in f.args:
      item = item.split(":")
      a[item[0]] = item[1]
    for item in op:
      if item not in a:
        a[item] = {}

    r = spyrael.request(fl.upper(),url=url,headers=a["h"],params=a['p'])
    if "o" in a:
      of = a["o"]
      os.system(f"touch {of}")
      f = open(of,"w")
      f.write(r.text)
    else:
      print(r.text)
    
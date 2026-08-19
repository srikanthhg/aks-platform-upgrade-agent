#!/usr/bin/env python3
import argparse,json,requests
def main():
 p=argparse.ArgumentParser();p.add_argument('--base-url',required=True);p.add_argument('--api-key',required=True);a=p.parse_args();results=[]
 for path in ('/health','/ready','/diagnostics'):
  r=requests.get(a.base_url.rstrip('/')+path,timeout=20);results.append({'path':path,'status_code':r.status_code})
 print(json.dumps(results,indent=2));return 0 if all(x['status_code']==200 for x in results) else 1
if __name__=='__main__':raise SystemExit(main())

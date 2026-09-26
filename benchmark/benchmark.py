#!/usr/bin/env python3
import argparse, concurrent.futures, json, statistics, time, urllib.request
PAYLOAD={"state":"A customer reports that the same order was charged twice.","questions":{"team":{"type":"choice","instructions":"Which team should handle this request?","criteria":{"billing":"Billing and payment disputes","shipping":"Shipping and delivery","access":"Account access and login"}}}}

def once(url):
    req=urllib.request.Request(url.rstrip("/")+"/v1/decide",data=json.dumps(PAYLOAD).encode(),headers={"Content-Type":"application/json"},method="POST")
    start=time.perf_counter()
    with urllib.request.urlopen(req,timeout=120) as response: response.read()
    return (time.perf_counter()-start)*1000

def pct(values,p):
    ordered=sorted(values); return ordered[min(len(ordered)-1,max(0,round((len(ordered)-1)*p)))]

def main():
    p=argparse.ArgumentParser(); p.add_argument("--url",default="http://127.0.0.1:8000"); p.add_argument("--requests",type=int,default=100); p.add_argument("--concurrency",type=int,default=2); p.add_argument("--warmup",type=int,default=5); a=p.parse_args()
    for _ in range(a.warmup): once(a.url)
    start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.concurrency) as pool: lat=list(pool.map(lambda _:once(a.url),range(a.requests)))
    elapsed=time.perf_counter()-start
    print(json.dumps({"requests":a.requests,"concurrency":a.concurrency,"elapsed_seconds":round(elapsed,3),"requests_per_second":round(a.requests/elapsed,3),"latency_ms":{"mean":round(statistics.mean(lat),2),"p50":round(pct(lat,.5),2),"p95":round(pct(lat,.95),2),"p99":round(pct(lat,.99),2),"min":round(min(lat),2),"max":round(max(lat),2)}},indent=2))
if __name__=="__main__": main()

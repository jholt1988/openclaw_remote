#!/usr/bin/env python3
"""Lightweight static frontend/backend contract probe for Keyring OS admin vs tenant_portal_backend.
No repo mutation; reads TS/TSX files and prints a markdown-ish matrix."""
from __future__ import annotations
import os,re
FR='keyring-os/apps/admin/src'
BE='pms-master/tenant_portal_backend/src'

def files(root):
  for d,_,fs in os.walk(root):
    for f in fs:
      if f.endswith(('.ts','.tsx')):
        yield os.path.join(d,f)

def clean(p):
  p=p.strip()
  p=re.sub(r'\$\{[^}]+\}', ':param', p)
  p=p.split('?')[0]
  # Template expressions appended directly to a path segment are usually query builders,
  # e.g. `/reporting/rent-roll${buildQuery(...)}`. They should not create a route segment.
  p=re.sub(r'(?<!/):param(?:\)\})?$', '', p)
  p=re.sub(r'//+','/',p)
  return p.rstrip('/') or '/'

def templ(p):
  p=clean(p)
  p=re.sub(r'/[0-9a-fA-F-]{8,}(?=/|$)','/:id',p)
  p=re.sub(r'/\d+(?=/|$)','/:id',p)
  return p

front=[]
for p in files(FR):
  s=open(p,errors='ignore').read()
  for m in re.finditer(r"(?:fetch|api)(?:<[^>]+>)?\s*\(\s*([`'\"])(.*?)\1",s,re.S):
    raw=m.group(2)
    if raw.startswith('http'): continue
    if raw.startswith('/'):
      front.append((templ(raw),p))
  for m in re.finditer(r"fetch\s*\(\s*`\$\{[^}]+\}([^`]*)`",s):
    raw=m.group(1)
    if raw.startswith('/'):
      front.append((templ(raw),p))
# de-dupe
seen=set(); front2=[]
for path,src in front:
  k=(path,src)
  if k not in seen:
    seen.add(k); front2.append(k)
front=front2

routes=[]
for p in files(BE):
  s=open(p,errors='ignore').read()
  ctrls=[]
  for m in re.finditer(r"@Controller\(([^)]*)\)",s):
    arg=m.group(1)
    vals=re.findall(r"['\"]([^'\"]*)['\"]",arg)
    ctrls.extend(vals or [''])
  if not ctrls: continue
  for m in re.finditer(r"@(Get|Post|Put|Patch|Delete)\(([^)]*)\)",s):
    meth=m.group(1).upper(); arg=m.group(2)
    vals=re.findall(r"['\"]([^'\"]*)['\"]",arg) or ['']
    for c in ctrls:
      for v in vals:
        path=clean('/'+c+'/'+v)
        path=re.sub(r':[A-Za-z_][A-Za-z0-9_]*', ':param', path)
        routes.append((path,meth,p))
rpaths={r[0] for r in routes}

def variants(fp):
  ps={fp}
  if fp.startswith('/api/v2/'):
    ps.add('/api/'+fp[len('/api/v2/'):])
    ps.add('/'+fp[len('/api/v2/'):])
  if fp.startswith('/api/'):
    ps.add('/'+fp[len('/api/'):])
  else:
    ps.add('/api'+fp)
  return ps

def matched(fp):
  vs=variants(fp)
  hits=[]
  for rp,m,src in routes:
    if rp in vs:
      hits.append((rp,m,src))
  return hits

print('# Static Contract Probe Output')
print(f'Frontend call sites: {len(front)}; Backend route declarations: {len(routes)}')
print('\n## Potential misses')
miss=[]
for fp,src in sorted(front):
  if fp.startswith('/api/auth/'): continue # Next proxy path
  if '/app/api/v2/' in src or '/app/api/auth/' in src: continue # proxy internals construct backend URLs dynamically
  h=matched(fp)
  if not h:
    miss.append((fp,src))
    print(f'- `{fp}` from `{src}`')
print(f'\nMiss count: {len(miss)}')
print('\n## Direct matches / prefix-compatible')
for fp,src in sorted(front):
  h=matched(fp)
  if h:
    hs=', '.join(sorted({x[1]+' '+x[0] for x in h})[:4])
    print(f'- `{fp}` -> {hs}')

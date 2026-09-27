"""Check public Drive inventory, sizes and Zstandard magic without downloading bulk data."""
import argparse
import concurrent.futures as cf
import datetime
import html.parser
import json
from pathlib import Path
import re
import urllib.request

HERE=Path(__file__).resolve().parent
FOLDER='1F8wvIRqL3pdB34db-llz0YjnIbFbRg9Y'

class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__();self.current=None;self.items={}
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            url=dict(attrs).get('href','')
            match=re.match(r'https://drive\.google\.com/file/d/([-\w]+)/view',url)
            self.current=[match.group(1),''] if match else None
    def handle_data(self,text):
        if self.current is not None:self.current[1]+=text
    def handle_endtag(self,tag):
        if tag=='a' and self.current is not None:
            file_id,name=self.current;name=name.strip()
            if name in self.items and self.items[name]!=file_id:
                raise ValueError('Duplicate public filename: '+name)
            self.items[name]=file_id;self.current=None

def probe(row,file_id):
    url=f'https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t'
    request=urllib.request.Request(url,headers={'Range':'bytes=0-3'})
    with urllib.request.urlopen(request,timeout=45) as response:
        content_range=response.headers.get('Content-Range','')
        size=int(content_range.rsplit('/',1)[-1]) if '/' in content_range else int(response.headers.get('Content-Length','-1'))
        if response.status not in (200,206) or size!=row['bytes'] or response.read(4)!=bytes.fromhex('28b52ffd'):
            raise ValueError('Public shard size/format mismatch: '+row['asset'])
    return dict(file=row['asset'],drive_file_id=file_id,bytes=size,status='ANONYMOUS_RANGE_PASS')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--update-manifest',action='store_true',help='Maintainer operation: update confirmed public file IDs')
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    manifest=HERE/'DATA_MANIFEST.json';data=json.loads(manifest.read_text());parser=Links()
    with urllib.request.urlopen('https://drive.google.com/embeddedfolderview?id='+FOLDER,timeout=45) as response:
        parser.feed(response.read().decode())
    present=[r for r in data['rows'] if r['asset'] in parser.items]
    missing=[r['asset'] for r in data['rows'] if r['asset'] not in parser.items]
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda row:probe(row,parser.items[row['asset']]),present))
    complete=len(results)==96 and not missing
    report=dict(status='PASS' if complete else 'UPLOAD_INCOMPLETE',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                authenticated=False,public_folder_url='https://drive.google.com/drive/folders/'+FOLDER,
                verified_file_sizes_and_magic=len(results),expected_files=96,missing=missing,files=results,
                scope='Anonymous listing, exact byte size and four-byte Zstandard magic. Full-file SHA256 is checked by data.py when downloading.')
    if args.update_manifest:
        for row in data['rows']:
            if row['asset'] in parser.items:
                row['drive_file_id']=parser.items[row['asset']]
                row['url']='https://drive.google.com/file/d/'+row['drive_file_id']+'/view'
        data['distribution'].update(status='PUBLIC_ALL_FILES_RANGE_VERIFIED' if complete else 'PUBLIC_FOLDER_UPLOAD_IN_PROGRESS',
                                    public_folder_url=report['public_folder_url'],confirmed_data_files=len(results),expected_data_files=96,
                                    checked_utc=report['checked_utc'],note=report['scope'])
        manifest.write_text(json.dumps(data,indent=2)+'\n')
    if args.report:args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('files','missing')}),flush=True)
    if missing:print('Missing shards:',len(missing));raise SystemExit(2)

if __name__=='__main__':main()

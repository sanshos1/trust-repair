import json,re,secrets,time
from pathlib import Path
from genlayer_py import create_client,create_account
from genlayer_py.chains import studionet
R=Path(__file__).parents[1];E=(R.parents[3]/'accounts.env').read_text();key=re.search(r'^ACCOUNT_3_GENLAYER_PRIVATE_KEY="?([^"\r\n]+)',E,re.M).group(1).strip();owner=create_account(account_private_key=key);roles=[create_account(account_private_key='0x'+secrets.token_hex(32)) for _ in range(3)];clients=[create_client(chain=studionet,account=x) for x in [owner]+roles];addr='0x4Fa21Bc6b939F6357F7cA92538C6FB8bB9A0FcD9';item='LIVE-'+str(int(time.time()));base='bd27a4a';urls=[f'https://github.com/sanshos1/trust-repair/raw/{base}/evidence/incident.txt',f'https://raw.githubusercontent.com/sanshos1/trust-repair/{base}/evidence/archive-restored.txt',f'https://cdn.jsdelivr.net/gh/sanshos1/trust-repair@{base}/evidence/correction-published.txt'];tx=[]
def send(cl,fn,args):
 h=cl.write_contract(address=addr,function_name=fn,args=args);r=cl.wait_for_transaction_receipt(transaction_hash=h,status='FINALIZED',retries=180,interval=5000);assert r.get('status_name')=='FINALIZED';tx.append(h)
send(clients[0],'open_case',[item,roles[0].address,roles[1].address,roles[2].address,'A release removed public accessibility records.',['Restore the public archive','Publish a durable correction'],urls[0],3600]);send(clients[1],'accept_plan',[item]);send(clients[2],'witness_remedy',[item,0,urls[1]]);send(clients[3],'witness_remedy',[item,1,urls[2]]);print(json.dumps({'id':item,'state':'RESTORED','transactions':tx}),flush=True)

import json,re
from pathlib import Path
from genlayer_py import create_client,create_account
from genlayer_py.chains import studionet
R=Path(__file__).parents[1];E=(R.parents[3]/'accounts.env').read_text(encoding='utf-8');v=lambda n:re.search(rf'^{n}="?([^"\r\n]+)',E,re.M).group(1).strip()
def f(x):
 if isinstance(x,dict):
  if x.get('contract_address'):return x['contract_address']
  for y in x.values():
   z=f(y)
   if z:return z
 if isinstance(x,list):
  for y in x:
   z=f(y)
   if z:return z
a=create_account(account_private_key=v('ACCOUNT_3_GENLAYER_PRIVATE_KEY'));c=create_client(chain=studionet,account=a);h=c.deploy_contract(code=(R/'contracts/contract.py').read_text(encoding='utf-8'),args=[]);r=c.wait_for_transaction_receipt(transaction_hash=h,status='FINALIZED',retries=180,interval=5000);print(json.dumps({'contract':f(r),'tx':h,'wallet':a.address,'status':r.get('status_name')}),flush=True)

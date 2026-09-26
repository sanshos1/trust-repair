from conftest import CONTRACT
def setup(vm,deploy,a,b,c,d):
 vm.warp('2035-01-01T00:00:00+00:00');vm.sender=a;x=deploy(CONTRACT);vm.mock_web(r'incident\.example',{'status':200,'body':'Original incident: public records removed.'});x.open_case('case-7','0x'+b.hex(),'0x'+c.hex(),'0x'+d.hex(),'A release removed public accessibility records.',['Restore the public archive','Publish a durable correction'],'https://incident.example/original',3600);return x
def mock(vm,host):
 vm.mock_web(r'incident\.example',{'status':200,'body':'Original incident: public records removed.'});vm.mock_web(host.replace('.','\\.'),{'status':200,'body':'Remedy completed with public verification.'});vm.mock_llm(r'.*TrustRepair milestone check.*','{"complete":true}')
def test_two_witnesses_restore(direct_vm,direct_deploy,direct_accounts):
 x=setup(direct_vm,direct_deploy,*direct_accounts[:4]);direct_vm.sender=direct_accounts[1];x.accept_plan('case-7');direct_vm.sender=direct_accounts[2];mock(direct_vm,'one.example');x.witness_remedy('case-7',0,'https://one.example/proof');direct_vm.sender=direct_accounts[3];mock(direct_vm,'two.example');x.witness_remedy('case-7',1,'https://two.example/proof');assert x.get_case('case-7')['state']=='RESTORED'
def test_witnesses_must_alternate(direct_vm,direct_deploy,direct_accounts):
 x=setup(direct_vm,direct_deploy,*direct_accounts[:4]);direct_vm.sender=direct_accounts[1];x.accept_plan('case-7');direct_vm.sender=direct_accounts[2];mock(direct_vm,'one.example');x.witness_remedy('case-7',0,'https://one.example/proof');mock(direct_vm,'two.example')
 with direct_vm.expect_revert('alternating witness'):x.witness_remedy('case-7',1,'https://two.example/proof')
def test_four_remedies_restore_with_alternating_witnesses(direct_vm,direct_deploy,direct_accounts):
 direct_vm.warp('2035-01-01T00:00:00+00:00');direct_vm.sender=direct_accounts[0];x=direct_deploy(CONTRACT);direct_vm.mock_web(r'incident\.example',{'status':200,'body':'Original incident: public records removed.'});x.open_case('case-8','0x'+direct_accounts[1].hex(),'0x'+direct_accounts[2].hex(),'0x'+direct_accounts[3].hex(),'A release removed public accessibility records.',['Restore archive','Publish correction','Notify readers','Preserve audit trail'],'https://incident.example/original',3600);direct_vm.sender=direct_accounts[1];x.accept_plan('case-8')
 for i,host in enumerate(('one.example','two.example','three.example','four.example')):
  direct_vm.sender=direct_accounts[2] if i%2==0 else direct_accounts[3];mock(direct_vm,host);x.witness_remedy('case-8',i,'https://'+host+'/proof')
 assert x.get_case('case-8')['state']=='RESTORED' and x.get_case('case-8')['next_remedy']==4
def test_incident_mutation_is_rejected(direct_vm,direct_deploy,direct_accounts):
 x=setup(direct_vm,direct_deploy,*direct_accounts[:4]);direct_vm.sender=direct_accounts[1];x.accept_plan('case-7');direct_vm.sender=direct_accounts[2];direct_vm.clear_mocks();direct_vm.mock_web(r'incident\.example',{'status':200,'body':'MUTATED incident record'});direct_vm.mock_web(r'one\.example',{'status':200,'body':'Remedy completed.'})
 with direct_vm.expect_revert('incident baseline changed'):x.witness_remedy('case-7',0,'https://one.example/proof')
def test_forged_incident_digest_rejected(direct_vm,direct_deploy,direct_accounts):
 x=setup(direct_vm,direct_deploy,*direct_accounts[:4]);mock(direct_vm,'one.example');result=x._check(x.cases['CASE-7'],0,'https://one.example/proof');assert direct_vm.run_validator(leader_result=result);forged=dict(result);forged['incident_digest']='0'*64;assert not direct_vm.run_validator(leader_result=forged)

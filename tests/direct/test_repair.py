from conftest import CONTRACT
def setup(vm,deploy,a,b,c,d):
 vm.warp('2035-01-01T00:00:00+00:00');vm.sender=a;x=deploy(CONTRACT);x.open_case('case-7','0x'+b.hex(),'0x'+c.hex(),'0x'+d.hex(),'A release removed public accessibility records.',['Restore the public archive','Publish a durable correction'],'https://incident.example/original',3600);return x
def mock(vm,host):
 vm.mock_web(r'incident\.example',{'status':200,'body':'Original incident: public records removed.'});vm.mock_web(host.replace('.','\\.'),{'status':200,'body':'Remedy completed with public verification.'});vm.mock_llm(r'.*TrustRepair milestone check.*','{"complete":true,"incident_preserved":true}')
def test_two_witnesses_restore(direct_vm,direct_deploy,direct_accounts):
 x=setup(direct_vm,direct_deploy,*direct_accounts[:4]);direct_vm.sender=direct_accounts[1];x.accept_plan('case-7');direct_vm.sender=direct_accounts[2];mock(direct_vm,'one.example');x.witness_remedy('case-7',0,'https://one.example/proof');direct_vm.sender=direct_accounts[3];mock(direct_vm,'two.example');x.witness_remedy('case-7',1,'https://two.example/proof');assert x.get_case('case-7')['state']=='RESTORED'
def test_witness_cannot_repeat(direct_vm,direct_deploy,direct_accounts):
 x=setup(direct_vm,direct_deploy,*direct_accounts[:4]);direct_vm.sender=direct_accounts[1];x.accept_plan('case-7');direct_vm.sender=direct_accounts[2];mock(direct_vm,'one.example');x.witness_remedy('case-7',0,'https://one.example/proof');mock(direct_vm,'two.example')
 with direct_vm.expect_revert('fresh witness'):x.witness_remedy('case-7',1,'https://two.example/proof')
def test_forged_preservation_rejected(direct_vm,direct_deploy,direct_accounts):
 x=setup(direct_vm,direct_deploy,*direct_accounts[:4]);mock(direct_vm,'one.example');result=x._check(x.cases['CASE-7'],0,'https://one.example/proof');assert direct_vm.run_validator(leader_result=result);forged=dict(result);forged['incident_preserved']=False;assert not direct_vm.run_validator(leader_result=forged)


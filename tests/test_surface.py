from pathlib import Path
T=Path('contracts/contract.py').read_text(encoding='utf-8');P=Path('docs/index.html').read_text(encoding='utf-8')
def test_surface():
 for n in ('open_case','accept_plan','witness_remedy','close_partial','get_case'):assert 'def '+n in T and n in P
 assert "status:'FINALIZED'" in P and 'id="kintsugiBowl"' in P and 'id="remedyDrawer"' in P

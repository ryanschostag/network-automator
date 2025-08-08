
import pytest
from pathlib import Path
import network_auditor


@pytest.fixture(autouse=True, scope='module')
def auditor():
    auditor = network_auditor.NetworkAuditor()
    yield auditor

def test_compare_with_golden(monkeypatch, auditor):
    test_config = """version 15.2
hostname TEST-ROUTER
!
"""
    
    golden_path = network_auditor.os.path.join(
        auditor.template_directory,
        'test_golden.txt'
    )
    monkeypatch.setattr(auditor, 'golden_file', golden_path)
    Path(auditor.template_directory).mkdir(exist_ok=True)
    with open(auditor.golden_file, 'w') as f:
        f.write("""version 15.2
hostname GOLDEN-ROUTER
!
""")
    diff = auditor.compare_with_golden(test_config)
    assert any('hostname' in line for line in diff)
    network_auditor.os.remove(golden_path)

def test_generate_report(auditor):
    diff = ['-hostname GOLDEN-ROUTER\n', '+hostname TEST-ROUTER\n']
    report_path = auditor.generate_report('test-device', diff)
    assert Path(report_path).exists()
    with open(report_path, 'r') as f:
        content = f.read()
        assert 'hostname' in content

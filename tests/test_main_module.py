import runpy

def test_main_module_invokes_run(monkeypatch):
    called = {}
    def fake_run(argv=None):
        called['args'] = argv
    monkeypatch.setattr('fueltracker.main.run', fake_run)
    runpy.run_module('fueltracker.__main__', run_name='__main__')
    assert called.get('args') is None

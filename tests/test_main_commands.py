from pathlib import Path

import pytest

from fueltracker import main
from src.services import StorageService


def test_migrate_command(monkeypatch, tmp_path):
    called = {}

    def fake_upgrade(path: Path) -> None:
        called['path'] = path

    monkeypatch.setattr(main, '_upgrade_to_head', fake_upgrade)
    monkeypatch.setenv('DB_PATH', str(tmp_path / 'db.sqlite'))

    main.run(['migrate'])

    assert called.get('path') == tmp_path / 'db.sqlite'


def test_backup_command(monkeypatch, tmp_path, capsys):
    called = {}

    def fake_backup(self: StorageService):
        called['called'] = True
        return tmp_path / 'backup.db'

    monkeypatch.setenv('DB_PATH', str(tmp_path / 'db.sqlite'))
    monkeypatch.setattr(StorageService, 'auto_backup', fake_backup)

    main.run(['backup'])

    out = capsys.readouterr().out.strip()
    assert called.get('called')
    assert out.endswith('backup.db')


def test_sync_command(monkeypatch, tmp_path):
    called = {}

    def fake_sync(self: StorageService, backup_dir: Path, cloud_dir: Path) -> None:
        called['args'] = (backup_dir, cloud_dir)

    monkeypatch.setenv('DB_PATH', str(tmp_path / 'db.sqlite'))
    monkeypatch.setenv('FT_CLOUD_DIR', str(tmp_path / 'cloud'))
    monkeypatch.setattr(Path, 'home', lambda: tmp_path)
    monkeypatch.setattr(StorageService, 'sync_to_cloud', fake_sync)

    main.run(['sync'])

    expected = (tmp_path / '.fueltracker' / 'backups', tmp_path / 'cloud')
    assert called.get('args') == expected

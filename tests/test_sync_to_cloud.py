from src.services import StorageService


def test_sync_to_cloud(tmp_path):
    db_path = tmp_path / "fuel.db"
    storage = StorageService(db_path=db_path)

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    files = []
    for i in range(3):
        f = backup_dir / f"b{i}.db"
        content = f"data{i}"
        f.write_text(content)
        files.append((f, content))

    cloud_dir = tmp_path / "cloud"
    assert not cloud_dir.exists()

    storage.sync_to_cloud(backup_dir, cloud_dir)

    assert cloud_dir.is_dir()
    for src, content in files:
        dest = cloud_dir / src.name
        assert dest.exists()
        assert dest.read_text() == content

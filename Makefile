lock:
	pip-compile --resolver backtracking pyproject.toml -o requirements.lock

.PHONY: lock


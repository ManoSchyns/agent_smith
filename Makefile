PYTHON = uv run python
EXAMPLE = agent_example "Creer moi une  qui dit hello world" "gemini-3.1-flash-lite" "https://generativelanguage.googleapis.com"


all: install

install:
	uv sync

run:
	$(PYTHON) src $(EXAMPLE)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".venv" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	flake8 .
	mypy . \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

.PHONY: all install clean lint run
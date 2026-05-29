.PHONY: db smoke reported test serve queue

db:
	python3 scripts/create_demo_db.py --fresh

smoke:
	python3 -m unittest discover tests/smoke

reported:
	python3 -m unittest discover tests/reported

test: smoke

serve:
	python3 -m mosaic_demo.web --db data/mosaic_demo.sqlite3 --port 8000

queue:
	python3 scripts/print_queue.py --sort sla


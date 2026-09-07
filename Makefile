.PHONY: setup baseline reproduce test regression synthesis
setup:
	python3 scripts/setup.py
	docker build -t simt-differential:dev .
	bash scripts/container.sh bash scripts/build.sh
test:
	python3 scripts/review_evidence.py
	python3 -m unittest discover -s tests -v
	python3 scripts/verify_evidence.py
baseline:
	python3 scripts/setup.py --baseline
	bash scripts/container.sh bash scripts/build.sh --baseline
reproduce:
	bash scripts/container.sh python3 scripts/reproduce.py
regression:
	bash scripts/container.sh bash -lc 'cd build32 && ../vendor/vortex/configure --xlen=32 --tooldir=/workspace/tools && ./ci/regression.sh --test sync_semantics'
synthesis:
	bash scripts/container.sh bash scripts/synthesize.sh

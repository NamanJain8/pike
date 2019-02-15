all:
	scripts/run.sh

clean:
	scripts/clean.sh
	rm -f tests/output2/out*

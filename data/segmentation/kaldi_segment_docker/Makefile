help: # List all commands
	grep -E '.+:.*\s#' Makefile | sed 's/:.*#/: /'

build: # Build docker container
	docker image build --tag asr/kaldi_vosk_base kaldi_vosk_base/ && \
	docker image build --tag asr/kaldi_segment .

clean: # delete docker container
	docker image rm asr/kaldi_segment

dev: # Run shell in docker container, for development
	docker run --rm -it -v "${PWD}/:/workdir/" asr/kaldi_segment bash


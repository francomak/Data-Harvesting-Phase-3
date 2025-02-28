## Description
This directory contains scripts for phone alignment, and phone and word recognition of audio using Kaldi.

The tools in this directory requires initialisation with data from the Sadilar website in order to function. Read README.resources.md on how to do this.

A dockerfile is provided containing Kaldi and other dependencies necessary for the scripts to run. The container can be managed with the Makefile in the root of this folder.

## Installation
To build the docker container:

```sh
make build
```

To run a shell in the docker container:

```sh
make dev
```

Within the docker container, the current working directory is mounted as "/workdir/". You may therefore run the rest of the scripts in the bin directory in order to perform phone alignment and other tasks.

The phone alignment functionality is based on the Kaldi wallstreet recipe, modified to allow out-of-tree building.

To configure a build directory in order to perform recognition functionality using Kaldi:

```sh
bin/setup.sh <destination directory> <language code>
```

Where language code is one of the languages preconfigured within phone_align/data_template and phone_align/exp_base. Destination directory is the directory where you want to perform your Kaldi tasks, it will be created.

Once you have your out-of-tree build directory, you may use the scripts in the bin directory to perform phone alignment, phone and word recognition, and other tasks.

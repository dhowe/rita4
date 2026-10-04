#!/bin/bash

# run from root dir of repo, e.g. $./scripts/generate-docs.sh

pushd docs/docgen >/dev/null

# compile grammar if needed (via ant)
[ ! -f ./bin/docgen/MakeDocs.class ] && echo "...compiling" && ant build

# generate the documentation
java -classpath ./bin:./lib/core3.5.3.jar docgen.MakeDocs "$@"

popd >/dev/null

#!/bin/bash

path=$1
oldrev=$2
newrev=$3

TEMPDIR="tmp/pep257/`date +%s%N`"
COMMAND=`basename ${path}`

files=`git diff --name-only ${oldrev}...${newrev}`

for file in ${files}; do
    object=`git ls-tree --full-name -r ${newrev} | egrep "(\s)${file}\$" | awk '{ print $3 }'`
    if [ -z ${object} ]; then continue; fi
    mkdir -p "${TEMPDIR}/`dirname ${file}`" &> /dev/null
    git cat-file blob ${object} > ${TEMPDIR}/${file}
done;

# Change the filename here if your flake8 configuration
# has a different name.
cp ${path} ${TEMPDIR}/${COMMAND}
cd ${TEMPDIR}

find -name "*.py" -not -path "*migrations*" | xargs python ${COMMAND}

cd -
rm -rf ${TEMPDIR} &> /dev/null

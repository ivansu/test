#!/bin/bash

# Massage the @@ counts so they are usable
function prep1() {
   cat | awk -F',' 'BEGIN { convert = 0; }
       /^@@ / { convert=1; }
       /^/  { if ( convert == 1 ) { print $1,$2,$3;
              } else { print $0;
              }
              convert=0;
             }'
}

# Extract all new changes added with the line count
function prep2() {
  cat | awk 'BEGIN { display=0; line=0; left=0; out=1}
     /^@@ / { out=0; inc=0; line=$4; line--; display=line; left=line;        }
     /^[-]/   { left++; display=left; inc=0; }
     /^[+]/   { line++; display=line; inc=0; }
     /^[-+][-+][-+] / { out=0; inc=0; }
     /^\+\+\+ / { file=$2; }
     /^/    { 
               line += inc;
               left += inc;
               display += inc;
               if ( out == 1 ) {
                   print file":"display$0;
               } else {
                   print $0;
               }
               out = 1;
               inc = 1;
               display = line;
            }'
}  

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

find -name "*.py" -not -path "*migrations*" | xargs python ${COMMAND} 2> ./violations
sed -i '$!N;s/\n/ /' ./violations
git diff -U0 ${oldrev}...${newrev} | prep1 | prep2 | sed "s/^b\//.\//" | grep --only-matching "^./\(\S\)\++" | sed "s/+$/ /" > ./filter
grep -f ./filter ./violations

cd -
rm -rf ${TEMPDIR} &> /dev/null

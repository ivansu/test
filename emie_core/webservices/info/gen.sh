#!/bin/sh

PROJECTS_PATH=/home/danil/projects

cd $PROJECTS_PATH/edu/src/web_edu/emie_core/webservices/info/
python $PROJECTS_PATH/m3/src/m3/contrib/soap/wsdl2py.py -b ./info.wsdl
cp $PROJECTS_PATH/edu/src/web_edu/emie_core/webservices/info/SchoolInfoService_types.py $PROJECTS_PATH/edu-portal/src/edu_portal/core/school/soap/info/
cp $PROJECTS_PATH/edu/src/web_edu/emie_core/webservices/info/SchoolInfoService_client.py $PROJECTS_PATH/edu-portal/src/edu_portal/core/school/soap/info/
echo "Все пучком, жми ентер для выхода"
read a
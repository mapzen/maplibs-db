#!/bin/sh

SED=`which sed`
PYTHON=`which python`
UUID=`which uuid`
MYSQL=`which mysql`

WHOAMI=`${PYTHON} -c 'import os, sys; print os.path.realpath(sys.argv[1])' $0`
BIN=`dirname ${WHOAMI}`
PROJECT=`dirname ${BIN}`

DBNAME='maplibs'
USERNAME='maplibs'

PASSWORD=`${UUID} | ${SED} s/-//g`

TMP="/tmp/${DBNAME}.sql"

if [ -f ${TMP} ]
then
    rm ${TMP}
fi

touch ${TMP}

echo "DROP DATABASE IF EXISTS ${DBNAME};" >> ${TMP}
echo "DROP USER '${USERNAME}'@'localhost';" >> ${TMP}
echo "FLUSH PRIVILEGES;" >> ${TMP}

# Note: the bit about dropping the user and then recreating does not
# appear to be working even all the documentation says to do this. I
# do not understand... (20150730/thisisaaronland)

echo "CREATE DATABASE ${DBNAME};" >> ${TMP}
echo "CREATE user '${USERNAME}'@'localhost' IDENTIFIED BY '${PASSWORD}';" >> ${TMP}
echo "GRANT SELECT,UPDATE,DELETE,INSERT ON ${DBNAME}.* TO '${USERNAME}'@'localhost' IDENTIFIED BY '${PASSWORD}';" >> ${TMP}
echo "FLUSH PRIVILEGES;" >> ${TMP}

echo "USE ${DBNAME};" >> ${TMP};

for f in `ls -a ${PROJECT}/schema/*.schema`
do
    echo "" >> ${TMP}
    cat $f >> ${TMP}
done

${MYSQL} -u root -p < /tmp/${DBNAME}.sql

# unlink ${TMP}

echo ${PASSWORD} > ${PROJECT}/password.txt

echo "wrote password for db user '${USERNAME}' to ${PROJECT}/password.txt"
exit

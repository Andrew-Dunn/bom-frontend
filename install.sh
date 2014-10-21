#!/bin/bash

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root through sudo." 1>&2
   exit 1
fi

RUNASUSER="sudo -u $SUDO_USER"
RUNASPOSTGRES="sudo -u postgres"

yum -y install postgresql postgresql-devel postgresql-server

# Don't bother if python is already installed.
if [ ! -x python27/bin/python2.7 ]; then
    $RUNASUSER bash <<FIN
wget https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz
tar -xzf Python-2.7.8.tgz
rm Python-2.7.8.tgz
FIN

    pushd Python-2.7.8

    $RUNASUSER bash <<FIN
./configure --prefix=$PWD/../python27
make
make install
FIN

    popd

    rm -rf Python-2.7.8
fi

EC2RC=$(eval echo "~${SUDO_USER}/ec2rc.sh")
if [ ! -f $EC2RC ]; then
    echo "ec2rc.sh not found in user's home directory."
    exit 2
fi
source $EC2RC

if [ ! -x /usr/bin/s3fs ]; then
    yum -y install git make gcc gcc-c++ pkgconfig libstdc++-devel curl curlpp curlpp-devel curl-devel libxml2 libxml2* libxml2-devel openssl-devel mailcap
    yum -y remove fuse fuse* fuse-devel
 
    $RUNASUSER bash <<EOF
wget http://iweb.dl.sourceforge.net/project/fuse/fuse-2.X/2.9.3/fuse-2.9.3.tar.gz
tar -xzf fuse-2.9.3.tar.gz*
rm -f fuse-2.9.3.tar.gz*
mv fuse-2.9.3 fuse
EOF
 
    cd fuse
 
    $RUNASUSER bash <<EOF
./configure --prefix=/usr
make
EOF
 
    make install
    ldconfig
    modprobe fuse
    cd ..
    rm -rf fuse
 
    $RUNASUSER bash <<EOF
git clone https://github.com/s3fs-fuse/s3fs-fuse.git
EOF
 
    cd s3fs-fuse
 
    $RUNASUSER bash <<EOF
export PKG_CONFIG_PATH=/usr/lib/pkgconfig:/usr/lib64/pkgconfig/
./autogen.sh
./configure --prefix=/usr
make
EOF
 
    make install
    cd ..
    rm -rf s3fs-fuse
 
    mkdir -p $PWD/datafiles
    chown $SUDO_UID:$SUDO_GID $PWD/datafiles
 
    echo "user_allow_other" > /etc/fuse.conf
 
    $RUNASUSER bash <<EOF
cat > dev/mount_nectar.sh <<EOI
#!/bin/bash
/usr/bin/s3fs data $PWD/datafiles -o url="$S3_URL" -o use_path_request_style -o allow_other -o uid=$SUDO_UID -o gid=$SUDO_GID
EOI
 
cat > dev/unmount_nectar.sh <<EOI
#!/bin/bash
fusermount -u $PWD/datafiles
EOI
 
chmod +x dev/mount_nectar.sh
chmod +x dev/unmount_nectar.sh
 
./dev/mount_nectar.sh
echo "Data storage has been mounted to '$PWD/datafiles'"
EOF
fi

export PATH=$PWD/python27/bin:$PATH

# Install python setuptools.
wget https://bootstrap.pypa.io/ez_setup.py -O - | python2.7

rm setuptools-7.0.zip

# Install pip
wget https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py -O - | python2.7

# Install virtualenv
pip2.7 install virtualenv

virtualenv env
source ./env/bin/activate
cat dev/requirements.txt | xargs -L1 pip2.7 install
deactivate

$RUNASUSER bash <<FIN
gunzip -dc $(ls dev/bom_*.sql.gz -1 | sort | tail -1) > dump.sql
FIN

mkdir -p /usr/local/pgsql/data
touch postgres.log
chown postgres /usr/local/pgsql
chown postgres /usr/local/pgsql/data
chown postgres postgres.log

OLDDIR=$PWD

cd /usr/local/pgsql

$RUNASPOSTGRES bash <<FIN
if [ "$(ls -A /usr/local/pgsql/data)" ]; then
    echo "Database data directory already initialised."
else
    initdb -D /usr/local/pgsql/data
fi
nohup postgres -D /usr/local/pgsql/data >$PWD/postgres.log 2>&1 &

createuser -P -s -e bom
createdb --encoding=UNICODE bom -O bom
FIN

cp $OLDDIR/dump.sql /usr/local/pgsql/dump.sql
rm $OLDDIR/dump.sql
chown postgres:postgres /usr/local/pgsql/dump.sql

$RUNASPOSTGRES bash <<FIN
psql -d bom -U bom -f /usr/local/pgsql/dump.sql
FIN

cd $OLDDIR
cp dev/sample_settings.py bom/settings.py

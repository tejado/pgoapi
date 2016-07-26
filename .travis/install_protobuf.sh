#!/bin/bash
set -o errexit

cd $SRCDIR
PROTOBUF=protobuf-2.4.1
ARCHIVE=$PROTOBUF.tar.gz

if [ -d $DIR ]
then
    echo "Protobuf already cached. Skipping compilation and installation."
    exit 0
fi

wget https://protobuf.googlecode.com/files/$ARCHIVE
tar -xzvf $ARCHIVE
pushd $PROTOBUF
./configure --prefix=$PREFIX
make
make install
popd

#!/bin/bash
cd $SRCDIR
wget https://protobuf.googlecode.com/files/protobuf-2.4.1.tar.gz
tar -xzvf protobuf-2.4.1.tar.gz
pushd protobuf-2.4.1 && ./configure --prefix=$PREFIX && make && make install && popd

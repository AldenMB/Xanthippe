#! /bin/bash
gcc shift_register_read.c -lbcm2835 -Wall -O3 -fPIC -shared -o shift.so

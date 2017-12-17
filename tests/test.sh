for i in $(find /cygdrive/c/src/cs/cdb/trunk/src/ /cygdrive/c/src/cs/cdb/trunk/cdb/python/cdb -name "*.py" -o -name "*.cc" -o -name "*.c"); do
    bin/python3 -m cui_source $i > test.cc
    output=$(diff --strip-trailing-cr test.cc "$i")
    if [ -n "$output" ]
        then echo $i
    fi
done

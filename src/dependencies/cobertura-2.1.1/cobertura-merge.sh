BASEDIR=`dirname $0`
java -cp $BASEDIR/cobertura-2.1.1.jar:$BASEDIR/lib/asm-5.0.1.jar:$BASEDIR/lib/asm-tree-5.0.1.jar:$BASEDIR/lib/asm-commons-5.0.1.jar:$BASEDIR/lib/slf4j-api-1.7.5.jar:$BASEDIR/lib/logback-core-1.0.13.jar:$BASEDIR/lib/logback-classic-1.0.13.jar:$BASEDIR/lib/oro-2.0.8.jar net.sourceforge.cobertura.merge.MergeMain $*

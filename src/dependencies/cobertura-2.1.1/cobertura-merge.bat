@echo off

REM
REM Grab the directory where this script resides, for use later
REM
set COBERTURA_HOME=%~dp0

REM
REM Read all parameters into a single variable using an ugly loop
REM
set CMD_LINE_ARGS=%1
if ""%1""=="""" goto doneStart
shift
:getArgs
if ""%1""=="""" goto doneStart
set CMD_LINE_ARGS=%CMD_LINE_ARGS% %1
shift
goto getArgs
:doneStart

java -cp "%COBERTURA_HOME%cobertura-2.1.1.jar;%COBERTURA_HOME%lib\asm-5.0.1.jar;%COBERTURA_HOME%lib\asm-tree-5.0.1.jar;%COBERTURA_HOME%lib\asm-commons-5.0.1.jar;%COBERTURA_HOME%lib\slf4j-api-1.7.5.jar;%COBERTURA_HOME%lib\logback-core-1.0.13.jar;%COBERTURA_HOME%lib\logback-classic-1.0.13.jar;%COBERTURA_HOME%lib\oro-2.0.8.jar" net.sourceforge.cobertura.merge.MergeMain %CMD_LINE_ARGS%

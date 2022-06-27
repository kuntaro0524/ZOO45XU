#!/bin/csh
git add ./*.py *zoo*sh LargeHolder/*.py *.com *.sh *.csh README.md 
git add `find ./Libs/ -name '*.py'`
git add `find ./KUMAGUI/ -name '*.py'`
git add `find ./ZOOGUI/ -name '*.py'`

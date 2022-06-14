#!/bin/csh
/oys/xtal/cctbx/snapshots/dials-v1-8-3-dev/build/bin2/kamo.auto_multi_merge \
  csv=automerge_pattern1.csv \
  workdir=$PWD \
  prefix=merge_pattern1_ \
  cell_method=reindex \
  merge.max_clusters=100 \
  merge.d_min_start=1.5 \
  merge.clustering=cc \
  merge.cc_clustering.min_cmpl=95 \
  merge.cc_clustering.min_redun=10 \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \

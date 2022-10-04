/oys/xtal/cctbx/snapshots/dials-v1-8-3-dev/build/bin2/kamo.auto_multi_merge \
  csv=sample2.csv \
  workdir=$PWD \
  prefix=merge_11 \
  cell_method=reindex \
  merge.max_clusters=15 \
  merge.d_min_start=2.5 \
  merge.clustering=cc \
  merge.cc_clustering.min_acmpl=90 \
  merge.cc_clustering.min_aredun=2 \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \
#  unit_cell="63     48    342     90     90.65  90.00" space_group=p2


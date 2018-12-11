#! /bin/bash
work_dir='KEGG/files' # set your own files directory

filename=$1
bactname=$2

# for weighted graph, use ./bin/convert -i graph/graph.txt -o blabla.bin -w -r -n 20000
convert -i ${work_dir}/${filename} -o ${work_dir}/graph_${bactname}.bin -r -n 20000
# for weighted graph use ./bin/community graph.bin -l -1 -w graph.weights > graph.tree
community ${work_dir}/graph_${bactname}.bin -l -1 -v > ${work_dir}/graph_${bactname}.tree 2> ${work_dir}/M_${bactname}.txt
hierarchy ${work_dir}/graph_${bactname}.tree > ${work_dir}/hier_${bactname}.txt

level=`grep -i Number ${work_dir}/hier_${bactname}.txt|cut -c 19`
level=`bc <<EOF
$level - 1
EOF`
echo " > Highest level: $level"

hierarchy ${work_dir}/graph_${bactname}.tree -l $level > ${work_dir}/partition_${bactname}.txt

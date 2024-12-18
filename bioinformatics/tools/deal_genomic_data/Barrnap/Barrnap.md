## Barrnap介绍   

## Barrnap的使用     

barrnap --kingdom bac --threads 8 --outseq bac_rRNA.fasta --quiet examples/bacteria.fna > bac_rRNA.gff3







- -kingdom：物种类型，bac代表细菌，arc代表古菌，euk代表真核生物，mito代表后生动物线粒体






- -threads：并行的线程数，此处为8      
- -outseq：输出识别到的rRNA序列      
- -quiet：输入文件，DNA fasta序列                

## 预测类型

Barrnap支持以下类型的rRNA的预测：      

bacteria (5S,23S,16S)      

archaea (5S,5.8S,23S,16S)      

metazoan mitochondria (12S,16S)      

eukaryotes (5S,5.8S,28S,18S)        
## 预测结果

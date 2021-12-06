for i in $(seq 1 27); do
	tmp="test1_bbr_10ms_"
	fx="_.log"
	filename="${tmp}${i}${fx}" 
	cat ${filename} | grep -Po '[0-9.]*(?= Mbits/sec)' | tail -2 | head -1 >> test1_bbr_10ms.dat
done

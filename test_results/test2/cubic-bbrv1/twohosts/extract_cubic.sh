for i in $(seq 1 28); do
	tmp="bbr_h13_"
	fx="_.log"
	filename="${tmp}${i}${fx}" 
	cat ${filename} | grep -Po '[0-9.]*(?= Mbits/sec)' | tail -2 | head -1 >> bbr1_2.dat
done

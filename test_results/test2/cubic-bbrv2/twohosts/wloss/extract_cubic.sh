for i in $(seq 1 34); do
	tmp="bbr2_h12_"
	fx="_.log"
	filename="${tmp}${i}${fx}" 
	cat ${filename} | grep -Po '[0-9.]*(?= Mbits/sec)' | tail -2 | head -1 >> bbr2_1.dat
done

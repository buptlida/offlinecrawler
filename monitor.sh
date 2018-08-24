num=`ps -ef | grep genrentinfo.py | grep -v grep |wc -l`
if [ $num -ne 1 ];then
  cd python
  python3 -u genrentinfo.py >> monitor.log 2>&1 &  
  echo 1
fi

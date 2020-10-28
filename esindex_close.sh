#!/bin/bash

ES_URL='http://localhost:9200'
KIBANA_URL='http://localhost:5601'

function ES_CLOSE {
  echo -en "CLOSE ES Index $1 "
  curl -X POST http://localhost:9200/$1/_close
  echo ""
}
function ES_DELETE {
  echo -en "DELETE ES Index $1 "
  curl -XDELETE http://localhost:9200/$1
  echo ""
}


#第1个参数为索引名称。
function OP_KIBANA {
  OP_STATUS=$(curl -sX GET ${KIBANA_URL}/api/saved_objects/index-pattern/${1})
  if [[ "$OP_STATUS" =~ 'Not Found' ]];then
    echo -en "ADD ES Index $1 "
    curl -sX POST ${KIBANA_URL}/api/saved_objects/index-pattern/${1} -H 'kbn-xsrf: true' -H 'Content-Type: application/json' -d "{\"attributes\":{\"title\":\"${1}_*\",\"timeFieldName\":\"@timestamp\"}}"
    echo ""
  fi
}


#第1个参数为close或delete，第2个参数为要进行操作的天数。
function OP_ES {
  SAVE_DAY=$(date -d "-${2} days" "+%Y-%m-%d")
  if [ "${1}" == "close" ];then
    INDEXS=$(curl -sX GET "${ES_URL}/_cat/indices?v"|egrep -v 'kibana|monitoring'|grep ' open '|awk '{print $3}')
  else
    INDEXS=$(curl -sX GET "${ES_URL}/_cat/indices?v"|egrep -v 'kibana|monitoring'|grep ' close '|awk '{print $3}')
  fi

  for index in ${INDEXS};do
    INDEX_NAME=$(echo ${index}|awk -F'_' '{print $1}')
    #判断在kibana中是否存在Index Patterns，没有则创建。
    [[ $1 == "close" ]] && OP_KIBANA ${INDEX_NAME}
    INDEX_DAY=$(echo ${index}|awk -F'_' '{print $NF}')
    NUMBER=$((($(date +%s -d ${INDEX_DAY//./-}) - $(date +%s -d ${SAVE_DAY}))/(24*60*60)))
    if [ ${NUMBER} -lt 0 ]; then
      [[ $1 == "close" ]] && ES_CLOSE $index || ES_DELETE $index
    fi
  done
}


# 关闭5天以前的ES索引
OP_ES close 0
# 删除15天以前的ES索引
OP_ES delete 20


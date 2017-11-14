#-*- coding: utf-8 -*-

import socket
import titlelist

######################## get_ip ##################################
# get_ip ) 목적지 주소와 소켓을 연결하고, 해당 커넥트 정보로부터
#		자신의 IP 주소를 획득하고 return.
#
# param )
#	addr : 목적지 ip 주소
#

#def get_ip(addr):
#	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#	s.connect((addr, 514))
#	return s.getsockname()[0]

	
######################## formatting ##############################
# param )
#	formats : config.json에서 설정된 포맷
#	title : 각 범주 안에서 Code에 배정되는 log 제목
#
#	index : 각 범주를 구분하는 index
#		0: 관리자설정, 1: 장비관리, 2: 시스템접근제어, 3: 단말자산
#		4: 성능분석, 5: 과다패킷검출, 6: 사용자인증
#
#	raw_data : 각 field 별 값이 입력된 log 리스트
#	

def formatting(formats, title, index, raw_data):
	format_data = []

	for form in formats:
		if form == "Category":
			format_data.append(titlelist.category[index])
		elif form == "LogTitle":
			format_data.append(title[str(raw_data['Code'])])
		else:
			try:
				if type(raw_data[form]) != type(str):
					format_data.append(str(raw_data[form]))
				else:
					format_data.append(raw_data[form])
			except:
				if type(form) != type(str):
					format_data.append(str(form))
				else:
					format_data.append(form)

	return format_data
	
##################################################################

import json
import utility
import pymysql
import datetime
import threading
import time
import queue
import logging
import logging.handlers
import titlelist

############### Log Class ################

class LogManager(threading.Thread):
	__time = 0

	def __init__(self, current):
		threading.Thread.__init__(self)
		self.__time = current

	def run(self):
		seq = 0 
		prev_time = self.__time
		current_time = datetime.datetime.now()
		db = pymysql.connect("localhost", "root", "ipplus", "DBN_IPPlus")
		curs = db.cursor()

		while True:
			if seq is 7:
				seq = 0
				db.close()

				time.sleep(1)
				prev_time = current_time
				current_time = datetime.datetime.now()
				
				db = pymysql.connect("localhost", "root", "ipplus", "DBN_IPPlus")
				curs = db.cursor()

			if seq is 0 or seq is 6:
				sql = """select * from """ + titlelist.table_list[seq] + """ where EventTime >= '""" + prev_time.strftime('%Y-%m-%d %H:%M:%S') + """' and EventTime < '""" + current_time.strftime('%Y-%m-%d %H:%M:%S') + """'"""
			else:
				sql = """select * from """ + titlelist.table_list[seq] + """ where AlarmTime >= '""" + prev_time.strftime('%Y-%m-%d %H:%M:%S') + """' and AlarmTime < '""" + current_time.strftime('%Y-%m-%d %H:%M:%S') + """'"""

			curs.execute(sql)
			rows = curs.fetchall()
			seq += 1

			if not rows:  # rows is None:
				continue
			else:
				for row in rows: 
					temp = list(row)
					temp.insert(0, seq-1)
					row = tuple(temp)
					formatQueue.put(row)
		db.close()	

##################################################

################ Format Class ####################

class FormatManager(threading.Thread):
	__data = () 
	__delimiter = ""

	def run(self):
		logger = logging.getLogger("logform")
		logger.setLevel(logging.INFO)

		#fileHandler = logging.FileHandler('./log/formatter.log')    # this line is able to overlap. so don't use this command at loop.

		config = GetConfigure()
		title = GetTitle()

		config.setConf()
		title.setTitle()

		formats = config.getFormats()
		self.__delimiter = config.getDelimiter()
		destip = config.getIP()
		destport = config.getPort()
		#local = utility.get_ip(destIP) 

		admin_log = title.getAdmin()
		device_log = title.getDevice()
		system_log = title.getSystem()
		terminal_log = title.getTerminal()
		traffic_log = title.getTraffic()
		overpacket_log = title.getOverPacket()
		user_log = title.getUser()

		handler = logging.handlers.SysLogHandler(address = (destip,destport))

		while True:
			if formatQueue.qsize() is 0:
				time.sleep(1) # This line is needed for decreasing cpu time
				continue
			
			self.__data = list(formatQueue.get())
			index = self.__data.pop(0)

			if index == 0:
				admin_data = {'UID':self.__data[0], 'EventGroup':self.__data[1], 'Code':self.__data[2], 'DatailCode':self.__data[3], 'EventTime':self.__data[4].strftime('%Y-%m-%d %H:%M:%S'),
				'ConsoleIP':self.__data[5], 'UserID':self.__data[6], 'AgentIP':self.__data[7], 'AgentMACU':self.__data[8], 'AgentMACL':self.__data[9], 'LanID':self.__data[10], 'TargetIP':self.__data[11],
				'TargetIP2':self.__data[12], 'TargetMACU':self.__data[13], 'TargetMACL':self.__data[14], 'TargetName':self.__data[15], 'LoginID':self.__data[16], 'Description':self.__data[17],
				'Recognized':self.__data[18]}

				msg = self.__delimiter.join(utility.formatting(formats["T_UserEvent"], admin_log, 0, admin_data))

			elif index == 1:
				device_data = {'UID':self.__data[0], 'Code':self.__data[1], 'AlarmType':self.__data[2], 'AlarmTime':self.__data[3].strftime('%Y-%m-%d %H:%M:%S'), 'TargetIP':self.__data[4], 'TargetName':self.__data[5],
				'SystemType':self.__data[6], 'Description':self.__data[7], 'Recognized':self.__data[8]}

				msg = self.__delimiter.join(utility.formatting(formats["T_Alarm_System"], device_log, 1, device_data))

			elif index == 2:
				system_data = {'UID':self.__data[0], 'Code':self.__data[1], 'AlarmType':self.__data[2], 'AlarmTime':self.__data[3].strftime('%Y-%m-%d %H:%M:%S'), 'MonitoringMode':self.__data[4],
				'AgentMACU':self.__data[5], 'AgentMACL':self.__data[6], 'AdaptorName':self.__data[7], 'TargetIP':self.__data[8], 'TargetMACU':self.__data[9], 'TargetMACL':self.__data[10], 'TargetName':self.__data[11],
				'TargetGroup':self.__data[12], 'PolicyIP':self.__data[13], 'PolicyMACU':self.__data[14], 'PolicyMACL':self.__data[15], 'VAgentGroupID1':self.__data[16], 'VAgentGroupID2':self.__data[17],
				'VAgentGroupID3':self.__data[18], 'VAgentGroupName1':self.__data[19], 'VAgentGroupName2':self.__data[20], 'VAgentGroupName3':self.__data[21], 'Description':self.__data[22],
				'Recognized':self.__data[23], 'UserField1':self.__data[24], 'UserField2':self.__data[25], 'UserField3':self.__data[26], 'UserField4':self.__data[27],'UserField5':self.__data[28],
				'UserField6':self.__data[29],'UserField7':self.__data[30], 'UserField8':self.__data[31], 'UserField9':self.__data[32], 'UserField10':self.__data[33], 'UserField11':self.__data[34],
				'UserField12':self.__data[35], 'UserField13':self.__data[36],'UserField14':self.__data[37], 'UserField15':self.__data[38], 'UserField16':self.__data[39], 'UserField17':self.__data[40],
				'UserField18':self.__data[41], 'UserField19':self.__data[42],'UserField20':self.__data[43]}

				msg = self.__delimiter.join(utility.formatting(formats["T_Alarm_IP"], system_log, 2, system_data))

			elif index == 3:
				terminal_data = {'UID':self.__data[0], 'AlarmTime':self.__data[1].strftime('%Y-%m-%d %H:%M:%S'), 'AlarmType':self.__data[2], 'Code':self.__data[3], 'DetailCode':self.__data[4],
				'SystemID':self.__data[5], 'UserID':self.__data[6], 'IP1':self.__data[7], 'MACU1':self.__data[8], 'MACL1':self.__data[9], 'IP2':self.__data[10], 'MACU2':self.__data[11], 'MACL2':self.__data[12],
				'IP3':self.__data[13], 'MACU3':self.__data[14], 'MACL3':self.__data[15], 'IP4':self.__data[16], 'MACU4':self.__data[17], 'MACL4':self.__data[18], 'IP5':self.__data[19], 'MACU5':self.__data[20],
				'MACL5':self.__data[21], 'GroupID0':self.__data[22], 'GroupID1':self.__data[23], 'GroupID2':self.__data[24], 'GroupID3':self.__data[25], 'GroupID4':self.__data[26], 'GroupID5':self.__data[27],
				'GroupID6':self.__data[28], 'GroupID7':self.__data[29], 'GroupID8':self.__data[30], 'GroupID9':self.__data[31], 'GroupName0':self.__data[32], 'GroupName1':self.__data[33], 'GroupName2':self.__data[34],
				'GroupName3':self.__data[35], 'GroupName4':self.__data[36], 'GroupName5':self.__data[37], 'GroupName6':self.__data[38], 'GroupName7':self.__data[39], 'GroupName8':self.__data[40],
				'GroupName9':self.__data[41], 'Description':self.__data[42]}

				msg = self.__delimiter.join(utility.formatting(formats["T_Alarm_PC"], terminal_log, 3, terminal_data))

			elif index == 4:
				traffic_data = {'UID':self.__data[0], 'AlarmTime':self.__data[1].strftime('%Y-%m-%d %H:%M:%S'), 'TargetIP':self.__data[2], 'IfIndex':self.__data[3], 'CurrentValue':self.__data[4], 'Threshold':self.__data[5],
				'MaxSpeed':self.__data[6], 'Code':self.__data[7], 'Recognized':self.__data[8]}

				msg = self.__delimiter.join(utility.formatting(formats["T_Alarm_Traffic"], traffic_log, 4, traffic_data))

			elif index == 5:
				overpacket_data = {'UID':self.__data[0], 'AlarmTime':self.__data[1].strftime('%Y-%m-%d %H:%M:%S'), 'TargetIP':self.__data[2], 'IfIndex':self.__data[3], 'CurrentValue':self.__data[4], 'Threshold':self.__data[5],
				'Code':self.__data[6], 'Recognized':self.__data[7]}

				msg = self.__delimiter.join(utility.formatting(formats["T_Alarm_WDI"], overpacket_log, 5, overpacket_data))

			elif index == 6:
				user_data = {'EventID':self.__data[0], 'Code':self.__data[1], 'EventTime':self.__data[2].strftime('%Y-%m-%d %H:%M:%S'), 'UserID':self.__data[3], 'UserName':self.__data[4], 'Jumin':self.__data[5],
				'Position_1':self.__data[6], 'Position_2':self.__data[7], 'Position_3':self.__data[8], 'UserWorkGroup':self.__data[9], 'FirstRegisterationDay':self.__data[10], 'ComputerName':self.__data[11],
				'ComputerWorkGroup':self.__data[12], 'Description':self.__data[13], 'RemoteIP':self.__data[14], 'EventType':self.__data[15], 'FromWeb':self.__data[16], 'Rank':self.__data[17], 'TelNum':self.__data[18],
				'CellPhone':self.__data[19], 'Email':self.__data[20], 'ReservedField1':self.__data[21], 'ReservedField2':self.__data[22], 'ReservedField3':self.__data[23], 'ReservedField4':self.__data[24],
				'ReservedField5':self.__data[25], 'NASName':self.__data[26], 'NASShortname':self.__data[27], 'NASMAC':self.__data[28]}

				msg = self.__delimiter.join(utility.formatting(formats["T_UA_UserEvent"], user_log, 6, user_data))

			form = '%(message)s'
			formatter = logging.Formatter(form)
			handler.setFormatter(formatter)
			#fileHandler.setFormatter(formatter)

			logger.addHandler(handler)
			#logger.addHandler(fileHandler)
			logger.info(msg)
##################################################

################# Config Class ###################

class GetConfigure():
	__formats = {} 
	__ip = '0.0.0.0'
	__port = 0 
	__delimiter = ""

	def setConf(self):
		with open('config.json') as config_file:
			data = json.load(config_file)

		self.__ip = data["Destination"]["IP"]
		self.__port = data["Destination"]["Port"]
		self.__delimiter = data["Delimiter"][0]
		self.__formats = data["Format"]

	def getFormats(self):
		return self.__formats
	def getIP(self):
		return self.__ip
	def getPort(self):
		return self.__port
	def getDelimiter(self):
		return self.__delimiter

##################################################

################## Title Class ###################

class GetTitle():
	__Title = {}

	def setTitle(self):
		with open('loginfo.json') as title_file:
			self.__Title = json.load(title_file)

	def getAdmin(self):
		return self.__Title["Admin Configuration"]
	def getDevice(self):
		return self.__Title["Device Management"]
	def getSystem(self):
		return self.__Title["System Access Control"]
	def getTerminal(self):
		return self.__Title["Terminal Asset"]
	def getTraffic(self):
		return self.__Title["Performance Analysis"]
	def getOverPacket(self):
		return self.__Title["Over-Packet Detection"]
	def getUser(self):
		return self.__Title["User Authentication"]

##################################################
formatQueue = queue.Queue(100)

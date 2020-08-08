from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator
from java.util import List, ArrayList
import random

class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
	def registerExtenderCallbacks(self, callbacks):
		self._callbacks = callbacks
		self._helpers = callbacks.getHelpers()
		callbacks.registerIntruderPayloadGeneratorFactory(self)
		return
		 
	@staticmethod	
	def getGeneratorName():
		return "BHP Payload Generator"
	
	def createNewInstance(self, attack):
		return BHPFuzzer(self, attack)
		
class BHPFuzzer(IIntruderPayloadGenerator):
	def __init__(self, extender, attack):
		self._extender = extender
		self._helpers = extender._helpers
		self._attack = attack
		self.max_payloads = 1000
		self.num_payloads = 0
		return
	
	def hasMorePayloads(self):
		if self.num_payloads == self.max_payloads:
			return False
		else:
			return True
	
	def getNextPayload(self, current_payload):
		payload = "".join(chr(x) for x in current_payload)
		payload = self.mutate_payload(payload)
		self.num_payloads += 1
		return payload
	
	def reset(self):
		self.num_payloads = 0
		return
		
	@staticmethod
	def mutate_payload(original_payload):
		picker = random.randint(1, 3)
		offset = random.randint(0, len(original_payload) - 1)
		payload = original_payload[:offset]
		if picker == 1:
			payload += "'"
		
		if picker == 2:
			payload += "<script>alert('BHP!');</script>"
		
		if picker == 3:
			chunk_length = random.randint(len(payload[offset:]), len(payload) - 1)
			repeater = random.randint(1, 10)
			for i in range(repeater):
				payload += original_payload[offset:offset + chunk_length]
		
		payload += original_payload[offset:]
		return payload

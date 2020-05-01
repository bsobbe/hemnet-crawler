
class Decoder:
	def decodeEmail(encodedString):
	    r = int(encodedString[:2],16)
	    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
	    return email


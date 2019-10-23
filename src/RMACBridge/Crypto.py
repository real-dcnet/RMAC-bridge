from cryptography.fernet import Fernet

class Crypto:
	def __init__(self, key_file):
		with open(key_file, "rb") as open_file:
			self.key = open_file.read()
			self.f = Fernet(self.key)

	def encrypt(self, plaintext):
		return self.f.encrypt(plaintext)
	
	def decrypt(self, ciphertext):
		return self.f.decrypt(ciphertext)


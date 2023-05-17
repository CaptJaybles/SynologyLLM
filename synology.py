import json

class OutgoingWebhook(object):

	def __init__(self, data, token, verbose=False):
		""" Initiate the object. """
		self.__client_token     = None
		self.__server_token     = data['token']
		self.__user_id 		= data['user_id']
		self.__username 	= data['username']
		self.__post_id 		= data['post_id']
		self.__timestamp 	= data['timestamp']
		self.__text 		= data['text']

	def __str__(self):
		""" Define how the print() method should print the object. """
		object_type = str(type(self))
		return object_type + ": " + str(self.as_dict())

	def __repr__(self):
		""" Define how the object is represented when output to console. """

		class_name     	= type(self).__name__
		client_token   	= f"client_token = '{self.client_token}'"
		server_token   	= f"server_token = '{self.server_token}'"
		user_id        	= f"user_id = {self.user_id}"
		username       	= f"username = '{self.username}'"
		post_id        	= f"post_id = {self.post_id}"
		timestamp      	= f"timestamp = {self.timestamp}"
		text           	= f"text = '{self.text}'"


		return f"{class_name}({client_token}, {server_token}, {user_id}, {username}, {post_id}, {timestamp}, {text}, )"

	def as_dict(self):
		""" Return the object properties in a dictionary. """
		return {
			'client_token': self.client_token,
			'server_token': self.server_token,
			'user_id': self.user_id,
			'username': self.username,
			'post_id': self.post_id,
			'timestamp': self.timestamp,
			'text': self.text,
		}

	def authenticate(self, token):
		""" Compare the client and server API token. """
		self.__client_token = token
		return token == self.__server_token

	def createResponse(self, text, file_url=None):
		""" Send a text message to the channel associated with the token. """
		payload = {
			"text": text,
			"user_id": self.__user_id
		}
		
		# Check if there is a URL to include in the request
		if file_url:
			payload['file_url'] = file_url

		return json.dumps(payload)

	@property
	def client_token(self):
		return self.__client_token

	@property
	def server_token(self):
		return self.__server_token

	@property
	def user_id(self):
		return self.__user_id

	@property
	def username(self):
		return self.__username

	@property
	def post_id(self):
		return self.__post_id

	@property
	def timestamp(self):
		return self.__timestamp

	@property
	def text(self):
		return self.__text
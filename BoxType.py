class BoxType:
	def __init__(self, name, freq, dest):
		self.name = name
		self.frequency = freq
		self.destinations = dest
		self.location = [0,0]
		self.groupedPalletLocations = []

	#Get/Sets
	def GetName(self):
		return self.name
	def SetName(self, newName):
		self.name = newName
	def GetFrequency(self):
		return self.frequency
	def SetFrequency(self,newFreq):
		self.frequency = newFreq
	def GetDestinations(self):
		return self.destinations
	def SetDestination(self, newDest):
		self.destinations = newDest
	def GetLocation(self):
		return self.location
	def SetLocation(self, newLoc):
		self.location = newLoc
	def GetGroupedPalletLocations(self):
		return self.groupedPalletLocations
	def SetGroupedPalletLocations(self, newLoc):
		self.groupedPalletLocations = newLoc

	def PrintData(self):
		print("BOXTYPE\nName: " + str(self.name))
		print("Frequency: " + str(self.frequency) + " per day")
		print("Destination: chute " + str(self.destinations))

class Zone:
	def __init__(self, name, dtc):
		self.name = name
		self.distanceToCenter = dtc

	#Get/Sets
	def GetCenterDistance(self):
		return self.distanceToCenter
	def SetCenterDistance(self, newDist):
		self.distanceToCenter = newDist
	def GetName(self):
		return self.name
	def SetName(newName):
		self.name = newName

	def PrintData(self):
		print("ZONE\nName: ", self.name + 1)
		print("Distance to center: " + str(self.distanceToCenter))
import math as m

class PalletLocation:
	def __init__(self, zone, wwd, subZone, positionNumber, loc):
		self.zone = zone
		self.subZone = subZone
		self.positionNumber = positionNumber
		self.position = str(chr(self.zone.GetName() + 66)) + " - " + str(self.positionNumber) + "-" + str(self.subZone)
		self.walkWayDistance = wwd
		self.distances = []
		self.currentPallet = 0
		self.location = loc

		for chute in range(0,16,1): #for each chute assign distances
			zoneDist = zone.GetCenterDistance()
			chuteDist = self.GetChuteDistance(chute + 1)

			if (zoneDist * chuteDist > 0):
				self.distances += [self.walkWayDistance + m.fabs(zoneDist - chuteDist)]
			else:
				self.distances += [self.walkWayDistance + m.fabs(zoneDist) + m.fabs(chuteDist)]

	#Get/Sets
	def GetZone(self):
		return self.zone
	def SetZone(self, newZone):
		self.zone = newZone
	def GetSubZone(self):
		return self.subZone
	def GetPosition(self):
		return self.positionNumber
	def GetWalkWayDistance(self):
		return self.walkWayDistance
	def SetWalkWayDistance(self, newWWD):
		self.walkWayDistance = newWWD
	def GetDistances(self):
		return self.distances
	def SetDistances(self, newDistances):
		self.distances = newDistances

	#Occupational Functions
	def SetCurrentPallet(self, newPallet):
		self.currentPallet = newPallet
	def GetCurrentPallet(self):
		return self.currentPallet
	def GetLocation(self):
		return self.location

	def GetHealth(self):
		if (self.currentPallet != 0):
			accum = 0
			# Adds the weighted average of the distances to each destination chute
			#for i in range(0,len(self.currentPallet.GetDestinations()),1):
			#	accum += self.distances[i] * self.currentPallet.GetDestinations()[i]

			groupedPalletLocations = self.currentPallet.GetGroupedPalletLocations()
			# Adds the distance from like pallets 
			for i in range(0, len(groupedPalletLocations), 1):
				xComp = (self.GetLocation()[0] - groupedPalletLocations[i][0]) ** 2
				yComp = (self.GetLocation()[1] - groupedPalletLocations[i][1]) ** 2
				accum += m.sqrt(xComp + yComp) ** 2
		else:
			return 0

		return accum * self.currentPallet.GetFrequency()

	def GetTravelDistance(self):
		accum = 0
		if (self.currentPallet != 0):
			for i in range(0,len(self.currentPallet.GetDestinations()),1):
				accum += self.distances[i] * self.currentPallet.GetDestinations()[i]
			return accum
		else:
			return 0

	def PrintData(self):
		if (self.currentPallet != 0):
			print("\nPosition: ", self.position)
			#print("WalkWayDistance: ", round(self.walkWayDistance))
			print("Current pallet occupying: ", self.currentPallet.GetName())
			print("Destination: ",self.currentPallet.GetDestinations())
			print("Distance: ", self.distances[self.currentPallet.GetDestinations()[0]])
			#for i in range(0, len(self.distances),1):
			#	print("Distance ",i,"is ",self.distances[i])

	def GetChuteDistance(self, chute):
		if (chute == 1):
			return 31
		elif (chute == 2):
			return 31
		elif (chute == 3):
			return 15
		elif (chute == 4):
			return 15
		elif (chute == 5):
			return 8
		elif (chute == 6):
			return 8
		elif (chute == 7):
			return -8
		elif (chute == 8):
			return -8
		elif (chute == 9):
			return -23
		elif (chute == 10):
			return -23
		elif (chute == 11):
			return -31
		elif (chute == 12):
			return -31
		elif (chute == 13):
			return -48
		elif (chute == 14):
			return -48
		elif (chute == 15):
			return 56
		elif (chute == 16):
			return 56 
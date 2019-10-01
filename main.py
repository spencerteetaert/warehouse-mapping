from Zone import Zone
from BoxType import BoxType
from PalletLocation import PalletLocation
import math as m
import random as r
import time
import copy
import csv
import datetime
import os
import sys

### Display toggles ###
printInitZoneStatus = False
printInitPalletLocationsStatus = False
printImportBoxTypeStatus = False
printEvolveStatus = True

### Other Parameters ###
fileName = 'data.csv'

#proposed layout - 5
def Main():
	for i in range(0,5,1):

		#[Gens, Epochs, BatchSize, Mutation Threshold]
		evolutionSettings = [1, 1000, 5, 2]

		#Distance the end of each zone is to the reference point
		dtc = [50.88, 33.37, 16.17, 0, -16.05, -32.7, -48.95, 33.37]

		#Initializes the box room
		zones = InitZones(dtc)
		palletLocations = InitPalletLocations(zones)
		boxTypes = ImportBoxTypeData()
		otherData = []
		#otherData = [Average init health, Best Health]

		#Runs the evolution algorithm 
		if (len(palletLocations) >= len(boxTypes)):
			print("Timer started")
			startTime = time.time()
			[palletLocations, otherData] = Optimize(palletLocations, boxTypes, evolutionSettings)
			endTime = time.time()
			print("Evolution time: ",round(endTime - startTime, 3),"s")

			evolutionSettings += [otherData[1]]

			ExportResults(palletLocations, i+1, evolutionSettings)
			#PrintEvolutionResults(palletLocations, otherData)
		else:
			print("ERR: Too many pallets for map")

####################
### ML Functions ###
####################

def Optimize(palletLocations, boxTypes, evolutionSettings):
	### Evolution Parameters ###
	maxJumpSize = 1
	staleEpoch = 0

	#Prints Evolution Parameters
	if (printEvolveStatus):
		print("Beginning Evolution with the Following Parameters...")
		print("Generations: ",evolutionSettings[0])
		print("Epochs: ",evolutionSettings[1])
		print("Batch Sizes: ",evolutionSettings[2])
		print("Mutation Threshold: ",evolutionSettings[3],"%")

	#Init 
	generationResults = []
	epochResults = []
	batchResults = []
	currentPalletLocations = palletLocations
	boxData = boxTypes
	results = [0, float("inf"), currentPalletLocations]
	initTravelAccum = 0

	toggle = 0
	#Results Structure: 
		#results = [null, best gen health, best gen data, [gen], [gen], [gen]]
		#gen = [null, best epoch health, best epoch data, [epoch], [epoch], [epoch]]
		#epoch = [null, best of batch health, best batch data, [batch], [batch], [batch]]

	for gen in range(0, evolutionSettings[0], 1):
		if (printEvolveStatus):
			print("Starting Generation ",gen+1,"...")
		#Each generation begins with a random assignment of pallet locations
		currentPalletLocations = ClearPallets(currentPalletLocations)
		currentPalletLocations = RandomizePallets(currentPalletLocations, boxData)
		currentPalletLocations = RefreshGroupedPalletLocations(currentPalletLocations)
		#r.shuffle(currentPalletLocations)
		epochResults = [0, GetLayoutHealth(currentPalletLocations), currentPalletLocations]
		staleEpoch = 0
		maxJumpSize = 1

		if (printEvolveStatus):
			randomTravel = GetLayoutTravelDistance(epochResults[2])
			randomHealth = epochResults[1]
			initTravelAccum += randomTravel
			print("   Generation Starting Distance: ", randomTravel)
			print("   Generation Starting Health: ", randomHealth)

		toPrint = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
		for epo in range(0, evolutionSettings[1], 1):
			if (round(epo/evolutionSettings[1]*100) in toPrint):
				print("\t\t",toPrint[0], "%")
				toPrint = toPrint[1:]

			batchResults = [0, epochResults[1], epochResults[2]]
			if ((epo - staleEpoch > evolutionSettings[1] / 50) & (epo % 10 == 0)):
				maxJumpSize += 1
				if maxJumpSize > len(palletLocations):
					maxJumpSize = len(palletLocations)
			elif ((maxJumpSize > 1) & (epo % 10 == 0)):
				maxJumpSize = 1

			#Each epoch will take the "current best" and run random mutations on it
			for bat in range(0, evolutionSettings[2], 1):
				#Each batch will be random mutations of the current epoch
				#The best batch, providing it is better than the current epoch, will become the new epoch

				#1: Generates a mutated layout of the current best layout from this generation
				mutatedSet = Evolve(copy.deepcopy(batchResults[2]), evolutionSettings[3], maxJumpSize)

				mutatedHealth = GetLayoutHealth(mutatedSet)
				
				#2: Checks if the new mutated set is the best set of the batch so far. 
				#   If it is, sets the top health and the layout to be the batch results[0:1]
				if (mutatedHealth < batchResults[1]):
					staleEpoch = epo
					batchResults[0] = bat + 3
					batchResults[1] = mutatedHealth

				#3: Keeps record of every mutated set, for retrieval later
				batchResults += [copy.deepcopy(mutatedSet)]

			#4: Sets the new winning set at the end of the batch
			batchResults[2] = copy.deepcopy(batchResults[batchResults[0]])

			#5: If the best of the batch is better than the best of the epoch, it replaces it. 
			if (batchResults[1] < epochResults[1]):
				epochResults[1] = batchResults[1] 
				epochResults[2] = copy.deepcopy(batchResults[2])

		#7: If the best of the finish generation is the best of all generations, it replaces it here
		if (epochResults[1] < results[1]):
			results[1] = epochResults[1]
			results[2] = copy.deepcopy(epochResults[2])
			# ret = epochResults[2]
			print("   #New Generation Win:",GetLayoutTravelDistance(results[2]))
			
		if (printEvolveStatus):
			print("   Winning Generation Distance: ", GetLayoutTravelDistance(results[2]))
			#print("   Winning Generation Health: ", GetLayoutHealth(ret))
			print("   Winning Generation Health: ", results[1])

	return [results[2], [initTravelAccum / evolutionSettings[0], GetLayoutTravelDistance(results[2])]]

def Evolve(currentPalletLocations, mutationThreshold, maxJumpSize):
	#Mutation algorithm randomly siwtched pallets up or down in order by one place
	for i in range(0, len(currentPalletLocations)-maxJumpSize, 1):
		rand = r.randint(0,99)
		jump = r.randint(0,maxJumpSize)
		#Half the valid pallets to switch upwards in order
		if (rand < mutationThreshold/2): 
			temp = currentPalletLocations[i].GetCurrentPallet()
			currentPalletLocations[i].SetCurrentPallet(currentPalletLocations[i+jump].GetCurrentPallet())
			currentPalletLocations[i+jump].SetCurrentPallet(temp)
		#Other half of pallets to switch downward in order
		elif (rand < mutationThreshold): 
			temp = currentPalletLocations[i+jump].GetCurrentPallet()
			currentPalletLocations[i+jump].SetCurrentPallet(currentPalletLocations[i].GetCurrentPallet())
			currentPalletLocations[i].SetCurrentPallet(temp)

	currentPalletLocations = RefreshGroupedPalletLocations(currentPalletLocations)

	return currentPalletLocations

def RandomizePallets(currentPalletLocations, boxData):
	availableIndices = []
	for i in range(0, len(currentPalletLocations),1):
		availableIndices += [i]

	for i in range(0, len(boxData), 1):
		if (len(availableIndices) == 0):
			print("ERR: Not enough room for the pallets requested")
			break
		#Generates random indices to pull available positions from
		placement = r.randint(0,len(availableIndices)-1)
		#Sets random empty pallet space to the box type
		currentPalletLocations[availableIndices[placement]].SetCurrentPallet(boxData[i])
		#Remove taken position from the avaialable indices list
		availableIndices = availableIndices[:placement] + availableIndices[placement+1:]

	return currentPalletLocations

def GetLayoutHealth(currentPalletLocations):
	#Returns the health of the entire layout
	accum = 0
	for i in range(0, len(currentPalletLocations), 1):
		accum += currentPalletLocations[i].GetHealth()
	return accum 

def GetLayoutTravelDistance(currentPalletLocations):
	accum = 0
	for i in range(0, len(currentPalletLocations), 1):
		accum += currentPalletLocations[i].GetTravelDistance()
	return accum

######################
### Init Functions ###
######################

def RefreshGroupedPalletLocations(palletLocations):
	visited = []
	# goes through each pallet space
	for i in range(0, len(palletLocations), 1):
		currentPallet = palletLocations[i].GetCurrentPallet()
		# If pallet space is not empty
		if (currentPallet != 0):
			palletType = currentPallet.GetName()
			# If we haven't already checked this pallet type
			if (palletType not in visited):
				indeces = []
				locations = []
				for j in range(0, len(palletLocations), 1):
					otherPallet = palletLocations[j].GetCurrentPallet()
					if (otherPallet != 0):
						otherPalletType = otherPallet.GetName()
						# Finds all other pallets of same type
						if (palletType == otherPalletType):
							locations += [palletLocations[j].GetLocation()]
							indeces += [j]
				# Sets each pallet of that type 
				for k in range(0, len(indeces), 1):
					palletLocations[indeces[k]].GetCurrentPallet().SetGroupedPalletLocations(locations)
				visited += [palletType]
	return palletLocations

def ClearPallets(palletLocations):
	#if (printEvolveStatus):
	#	print("Clearing pallet locations...")
	for i in range(0, len(palletLocations),1):
		palletLocations[i].SetCurrentPallet(0)
	return palletLocations

def InitZones(dtc):
	if (printInitZoneStatus):
		print("\nInitializing Zones...")
	ret = []
	for i in range(0,len(dtc),1):
		ret += [Zone(i, dtc[i])]
		if (printInitZoneStatus):
			print("New Zone Added")
			ret[len(ret)-1].PrintData()
	return ret

def InitPalletLocations(zones):
	if (printInitPalletLocationsStatus):
		print("\nInitializing Pallet Locations...")
	#zone distance to first pallet (from CAD):
	# 2 - 12.28, 3 - 16.44, 4 - 12.28, 5 - 12.28, 6 - 12.28, 7 - 8.11, 8 - 0, 9 - 71.16

	ret = []
	#Zone 2:
	zone = 0
	up = 1
	down = 1
	for i in range(2,12,1):
		ret += [PalletLocation(zones[zone], 12.28 + i*4.17,'N',up, [4.17*(i+3),4.17*27])]
		up += 1
	for i in range(0,12,1):
		ret += [PalletLocation(zones[zone], 12.28 + i*4.17,'S',down,[4.17*(i+3),4.17*24])]
		down += 1

	if (printInitPalletLocationsStatus):
		print("Zone " + str(zone + 1) + " added")

	#Zone 3:
	zone = 1
	up = 1
	down = 1
	filt = [6]
	for i in range(0,11,1):
		if i not in filt:
			ret += [PalletLocation(zones[zone], 16.44 + i*4.17,'N',up, [4.17*(i+4), 4.17*23])]
			ret += [PalletLocation(zones[zone], 16.44 + i*4.17,'S',down, [4.17*(i+4), 4.17*20])]
			up += 1
			down += 1
	if (printInitPalletLocationsStatus):
		print("Zone " + str(zone + 1) + " added")

	#Zone 4:
	zone = 2
	up = 1
	down = 1
	filt1 = [0, 12, 13]
	filt2 = [12, 13]
	for i in range(0,23,1):
		if i not in filt1:
			ret += [PalletLocation(zones[zone], 12.28 + i*4.17, 'N', up, [4.17*(i+3), 4.17*19])]
			ret += [PalletLocation(zones[zone], 12.28 + i*4.17, 'S', down, [4.17*(i+3), 4.17*16])]
			down += 1
			up += 1
		elif i not in filt2:
			ret += [PalletLocation(zones[zone], 12.28 + i*4.17, 'S', down, [4.17*(i+3), 4.17*16])]
			down += 1
		
	if (printInitPalletLocationsStatus):
		print("Zone " + str(zone + 1) + " added")

	#Zone 5:
	zone = 3
	up = 1
	down = 1
	filt1 = [12, 13]
	filt2 = [12, 13, 22]
	for i in range(0,23,1):
		if i not in filt2:
			ret += [PalletLocation(zones[zone], 12.28 + i*4.17, 'N', up, [4.17*(i+3), 4.17*15])]
			ret += [PalletLocation(zones[zone], 12.28 + i*4.17, 'S', down, [4.17*(i+3), 4.17*12])]
			up += 1
			down += 1
		elif i not in filt1:
			ret += [PalletLocation(zones[zone], 12.28 + i*4.17, 'N', up, [4.17*(i+3), 4.17*15])]
			up += 1

	if (printInitPalletLocationsStatus):
		print("Zone " + str(zone + 1) + " added")

	#Zone 6:
	zone = 4
	up = 1
	down = 1
	filt1 = [0, 7, 12, 13, 15]
	filt2 = [13, 14]
	for i in range(0,22,1):
		if i not in filt1:
			ret += [PalletLocation(zones[zone], 12.28 + i*4.17,'N',up, [4.17*(i+3), 4.17*11])]
			up += 1
		if i not in filt2:
			ret += [PalletLocation(zones[zone], 12.28 + i*4.17,'S',down, [4.17*(i+3), 4.17*8])]
			down += 1
	if (printInitPalletLocationsStatus):
		print("Zone " + str(zone + 1) + " added")

	#Zone 7:
	zone = 5
	up = 1
	down = 1
	filt = [0,2]
	for i in range(0,8,1):
		if i not in filt:
			ret += [PalletLocation(zones[zone], 8.11 + i*4.17,'N',up, [4.17*(i+2), 4.17*7])]
			up += 1
		ret += [PalletLocation(zones[zone], 8.11 + i*4.17,'S',down, [4.17*(i+2), 4.17*4])]
		down += 1
		
	if (printInitPalletLocationsStatus):
		print("Zone " + str(zone + 1) + " added")

	#Zone 8:
	zone = 6
	up = 1
	down = 1
	filt1 = [0, 1]
	filt2 = [9]
	for i in range(0,10,1):
		if i not in filt1:
			ret += [PalletLocation(zones[zone], i*4.17,'N', up, [4.17*i, 4.17*3])]
			up += 1
		if i not in filt2:
			ret += [PalletLocation(zones[zone], i*4.17,'S', down, [4.17*i, 0])]
			down += 1
	if (printInitPalletLocationsStatus):
		print("Zone " + str(zone + 1) + " added")

	#Zone 9:
	zone = 7
	up = 1
	for i in range(-2,8,1):
		ret += [PalletLocation(zones[zone], 71.16 + m.fabs(i*4.17), '', up, [4.17*17, 4.17*(i+21)])]
		up += 1
	if (printInitPalletLocationsStatus):
		print("Zone " + str(zone + 1) + " added")

	return ret

def ImportBoxTypeData():
	if (printImportBoxTypeStatus):
		print("\nImporting data from " + fileName + "...")
	#Opens a read-only CSV file under the given filename
	file = open(fileName, 'r', encoding='utf-8-sig')
	ret = []
	#Skips the first line (titles)
	file.readline()

	#['name', demand, chute 1 demand, chute 2, chute 3..., chute 16]

	while True:
		line = file.readline().split(",")
		if (line[0] == 'x'):
			break
		if (printImportBoxTypeStatus):
			print("==New Box Type Found")
		productName = line[0]
		chuteFrequencies = []
		toAdd = []
		freq = int(line[1])

		#Runs through each possible chute location and finds the frequency and number of locations each box has
		for i in range(2,18,1):
			chuteFrequencies += [float(line[i].rstrip("\n"))]
		for i in range(0, freq, 1): 
			ret += [BoxType(productName, freq, chuteFrequencies)]
			if (printImportBoxTypeStatus):
				ret[len(ret)-1].PrintData()
		#ret += [toAdd]
	return ret

def ExportResults(palletLocations, run, evolutionSettings):
	data = []
	health = str(round(evolutionSettings[4]))
	evolutionS = 'g'+str(evolutionSettings[0])+'-e'+str(evolutionSettings[1])+'-b'+str(evolutionSettings[2])+'-m'+str(evolutionSettings[3])
	exportName = 'map-v' + str(run) +' ('+health+ ').csv'
	directory = evolutionS
	if not os.path.exists(directory):
		os.makedirs(directory)
	with open(directory + "\\" + exportName,'w', newline='') as writeFile:
		writer = csv.writer(writeFile)
		writer.writerow(["Zone","Side","Position","Box Type","Box Destination"])

		for i in range(0, len(palletLocations),1):
			toAdd = []
			toAdd += [chr(palletLocations[i].GetZone().GetName() + 66)]
			toAdd += [palletLocations[i].GetSubZone()]
			toAdd += [palletLocations[i].GetPosition()]
			try:
				toAdd += [palletLocations[i].GetCurrentPallet().GetName()]
				toAdd += [palletLocations[i].GetCurrentPallet().GetDestinations()]
			except:
				toAdd += [0, 0]
			data += [toAdd]
		
		writer.writerows(data)

#######################
### Other Functions ###
#######################

def PrintData(inp):
	for i in range(0,len(inp),1):
		inp[i].PrintData()

def PrintEvolutionResults(palletLocations, otherData):
	print("Evolution algorithm completed...")
	print("Average starting distance:",otherData[0])
	print("Optimized distance:",otherData[1])
	print("A", round((1 - otherData[1]/otherData[0])*100), "% increase in efficiency was achieved") 
	print("The final recommended locations are: ")
	for i in range(0, len(palletLocations),1):
		palletLocations[i].PrintData()

	return 0

Main()
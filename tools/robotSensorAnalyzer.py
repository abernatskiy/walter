import matplotlib.pyplot as plt

def plot_encephalogram(sensorData):
	nrobots = len(sensorData)

	fig, axes = plt.subplots(nrows=nrobots)

	slabels = ['proximityR', 'proximityT', 'proximityP', 'light', 'adhesive', 'tether']

	for axid in range(nrobots):
		for ts in sensorData[axid]:
			axes[axid].plot(ts)
			if axid == nrobots-1:
				axes[axid].legend(slabels)

	plt.show()

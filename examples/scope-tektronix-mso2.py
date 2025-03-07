from benchtop.scope import *

# connect to the oscillscope
scope = MSO2("my.scope.local")
scope.set_timeout(10.0)

scope.reset()

# set horizontal scale
scope.set_horizontal_scale(scale=200e-6)

# enable channels and set vertical scale
scope[MSO2.Channel.CH1].enable()
scope[MSO2.Channel.CH2].enable()

scope[MSO2.Channel.CH1].set_vertical_scale(scale=500e-3)
scope[MSO2.Channel.CH2].set_vertical_scale(scale=500e-3)

# configure trigger
scope.set_trigger(0.5,
        channel=MSO2.Channel.CH1,
        edge=MSO2.TriggerEdge.RISING,
        coupling=MSO2.TriggerCoupling.DC
        )

# set acquisition mode to average over 42 samples
scope.set_acquisition_mode(MSO2.AcquisitionMode.AVERAGE, n=42)

# run and stop after a single acquisition
scope.run(single=True)
scope.sync()

# retrieve waveforms from the oscillscope
data = scope.get_waveforms()

# plot waveforms
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.gca()

for channel in [MSO2.Channel.CH1, MSO2.Channel.CH2]:
    ax.plot(data[channel.value]["x"] * 1e6, data[channel.value]["y"], label=channel.value)

ax.set_xlabel("time / μs")
ax.set_ylabel("voltage / V") # y label

ax.legend(loc="upper right")

fig.savefig("test.pdf")

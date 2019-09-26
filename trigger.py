import nidaqmx as ni

# with ni.Task() as task:
#     task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
#     task.read()

#detect NIDAQ boards
system = ni.system.System.local()

device = system.devices['PCI6036']
channel = device.ai_physical_chans['ai0']

with ni.Task() as task:
    task.di_channels.add_di_chan('PCI6036/port0/line0')
    print(task.read(number_of_samples_per_channel=5))

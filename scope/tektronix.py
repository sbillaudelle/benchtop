import enum
from typing import Optional

import numpy as np
import pyvisa as visa

# TODO:
# scope.handle.write("horizontal:position 0")
# scope.handle.write("CH1:offset 0e-3")

class MSO2:
    class Channel(enum.Enum):
        CH1 = "CH1"
        CH2 = "CH2"
        CH3 = "CH3"
        CH4 = "CH4"

    class TriggerEdge(enum.Enum):
        RISING = "rise"
        FALLING = "fall"
        EITHER = "EITHER"

    class TriggerCoupling(enum.Enum):
        DC = "dc"
        HFReject = "hfrej"
        LFReject = "lfrej"

    class AcquisitionMode(enum.Enum):
        SAMPLE = "sample"
        PEAKDETECT = "peakdetect"
        HIRES = "hires"
        AVERAGE = "average"
        ENVELOPE = "envelope"
    
    def __init__(self, address):
        self.resource_manager = visa.ResourceManager()
        self.handle = self.resource_manager.open_resource(f"TCPIP0::{address}::inst0::INSTR")

    def set_timeout(self, timeout: float=1.0):
        self.handle.timeout = timeout * 1000  # convert to ms

    def reset(self):
        self.handle.write("*rst")

    def sync(self):
        self.handle.query("*opc?")


    def autoset(self):
        self.handle.write("autoset execute")


    def set_trigger(self,
                    level: float=0.0,
                    channel: Channel=Channel.CH1,
                    edge: TriggerEdge=TriggerEdge.RISING,
                    coupling: TriggerCoupling=TriggerCoupling.DC
                    ):
        self.handle.write(f"trigger:A:edge:source {channel.value}")
        self.handle.write(f"trigger:A:level:{channel.value} {level}")
        self.handle.write(f"trigger:A:edge:slope {edge.value}")
        self.handle.write(f"trigger:A:edge:coupling:{channel.value} {coupling.value}")

    def set_horizontal_scale(self,
                             scale: Optional[float] = None,
                             record_length: Optional[int] = None,
                             sample_rate: Optional[int] = None
                             ):
        if scale is not None:
            if record_length is not None or sample_rate is not None:
                raise ValueError("You can eiher set the scale parameter (automatic mode) or record_length and sample_rate (manual mode)")

            self.handle.write("horizontal:mode auto")
            self.handle.write(f"horizontal:mode:scale {scale}")
        elif record_length is not None and sample_rate is not None:
            self.handle.write("horizontal:mode manual")
            self.handle.write(f"horizontal:mode:samplerate {sample_rate}")
            self.handle.write(f"horizontal:mode:recordlength {record_length}")
        else:
            raise ValueError("You have to specify either the scale or sample_rate and record_length")
    
    def set_acquisition_mode(self,
                             mode: AcquisitionMode = AcquisitionMode.SAMPLE,
                             n: Optional[int] = None
                             ):
        self.handle.write(f"acquire:mode {mode.value}")

        if mode == self.__class__.AcquisitionMode.AVERAGE:
            if n is None:
                raise ValueError("When enabling the AVERAGE acquisition mode, the number of samples to average over has to be provided")
            self.handle.write(f"acquire:numavg {n}")
        elif mode == self.__class__.AcquisitionMode.ENVELOPE:
            if n is None:
                raise ValueError("When enabling the envelope acquisition mode, the number of samples to average over has to be provided")
            self.handle.write(f"acquire:numenv {n}")
        else:
            if n is not None:
                raise ValueError("Number of samples to average over can only be specified in the average or envelope acquisition modes")

    def run(self, single: bool=False):
        if single:
            self.handle.write('acquire:stopafter SEQUENCE')
        self.handle.write('acquire:state RUN')

    def stop(self):
        self.handle.write('acquire:state STOP')

    def get_waveforms(self, resolution: int=16):
        available_waveforms = [s.strip() for s in self.handle.query("data:source:available?").split(",")]

        data = {}

        for source in available_waveforms:
            self.handle.write(f"wfmoutpre:bit_nr {resolution}")
            
            self.handle.write("data:encdg RIBINARY")
            self.handle.write(f"data:source {source}")
            self.handle.write(f"data:start 1")
            end = int(self.handle.query("horizontal:mode:recordlength?"))
            self.handle.write("data:stop {}".format(end))

            # query data
            if resolution == 8:
                data_type = "b"
            elif resolution == 16:
                data_type = "h"
            else:
                raise ValueError("Only valid resolutions are 8 or 16 bit")

            bin_wave = self.handle.query_binary_values('curve?', datatype=data_type, container=np.array, is_big_endian=True)
            number_of_samples = bin_wave.size

            # retrieve scaling factors
            tscale = float(self.handle.query('wfmpre:xincr?'))
            tstart = float(self.handle.query('wfmpre:xzero?'))
            vscale = float(self.handle.query('wfmpre:ymult?')) # volts / level
            voff = float(self.handle.query('wfmpre:yzero?')) # reference voltage
            vpos = float(self.handle.query('wfmpre:yoff?')) # reference position (level)

            total_time = tscale * number_of_samples
            tstop = tstart + total_time
            scaled_time = np.linspace(tstart, tstop, num=number_of_samples, endpoint=False)
            
            unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
            scaled_wave = (unscaled_wave - vpos) * vscale + voff
            
            stacked = np.vstack([scaled_time, scaled_wave])

            data[source] = stacked.T.ravel().view([("x", stacked.dtype), ("y", stacked.dtype)])
        
        return data


    def __getitem__(self, key):
        class ChannelProxy:
            def __init__(self, identifier, handle):
                self.identifier = identifier
                self.handle = handle

            def enable(self):
                self.handle.write(f"select:{self.identifier.value} on")
        
            def disable(self):
                self.handle.write(f"select:{self.identifier.value} off")
    
            def set_vertical_scale(self, scale: float):
                self.handle.write(f"{self.identifier.value}:scale {scale}")
 
        return ChannelProxy(key, self.handle)


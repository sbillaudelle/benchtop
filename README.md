# benchtop 🎛️

*Benchtop* is a rather minimalistic collection of Python wrappers for [PyVISA](https://pyvisa.readthedocs.io/)-compatible lab equipment.
It attempts to provide a streamlined, Python-first interface for reproducible and remote experimentation with oscilloscopes, source measure units, and other measurement devices.

## Installation

To install *benchtop* from source, please execute

```bash
$ python setup.py install
```

*Benchtop*'s dependency `pyvisa` requires an additional backend that has to be installed separately.
Here, we recommend `pyvisa-py`.

## Examples

Please find a set of example scripts in the `examples` folder.

## List of supported devices
*Benchtop* is growing with the needs of its contributors.
Feel free to request or contribute support for new features or devices, and to report issues.

Currently, *benchtop* supports the following devices:

- Tektronix MSO2-series oscilloscopes
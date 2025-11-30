# GR-RFHS

GNU Radio OOT Modules used to run RF Hackers Sanctuary SDR Capture the flag challenges.

## Modules

### LRS Pager Data Source

This block generates manchester encoded data packets for LRS pagers. It is based on Tony Tiger's script and Dan's edits for RFHS.

### Morse Code Data Source

This block generates Morse Code characters. It uses the Paris standard for Words per minute (WPM). It is based on Russ's code.

### ASK Data Source

This block generates binary data at a specified baud rate for the Amplitude Shift Keying challenge. It is based on Russ's code.
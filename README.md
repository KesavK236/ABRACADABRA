# ABRACADABRA
Axon Binary Reading Analyzer Capable of Analyzing Data as an Axon Binary Reading Analyzer

## Description

An application that uses a python script to automate data extraction of electrophysiological parameters from Axon Binary Files.

## Getting Started

### Installing

* Download the ABRACADABRA from the box folder
* It should contain 3 files: ABF Analyzer Icon.ico, ABRACADABRA.exe, and README.md.
* note this will only work on a windows system.

### Executing program

* Before running the program, double check the box folder to see if there is a new version, I will be updating the program once every week or two. If in doubt, download it again.
* You can run the program by running the ABRACADABRA application inside of the ABRACADABRA Folder

* the ABRACADABRA window will open
* Do not full screen the window

* Inside the ABRACADABRA window, you can select the abf file corresponding to a protocol by clicking the "change file" button and selecting the desired file in the file explorer that pops up
* If you want to only analyze one protocol, only select the file for the desired protocol.
* You can remove a file from the analysis list by clickin the "Clear File" button to the left of the unwanted protocol.
* The default dV/dt for the analyzer is 5 mV/ms. This can be changed to any integer between 1 and 100 using the scroll box.
* Once you do this for all six protocols, name the output file in the text entry at the bottom. 
* You can then click the "enter" button to run the program
* The extracted data will populate in the in an excel file that will automatically open. You can also find all outputed files and images in a newly made folder made in the same folder with the ABRACADABRA application
* You can either close the program or change the files to analyze your next data set

### Converting ABF files to NWB files
* You can begin the conversion to NWB files by clicking the "Convert to NWB file" checkbox
* A set of text entries will appear for you to fill in the appropriate information for the NWB metadata
* If a format example is in the label, please match that format to ensure proper conversion.
* After running the analysis, the "bulk_abf_nwb_converter.xlsx" file will be populated with the inputed meta data
* The actual conversion will be done by a seperate script overnight due to conversion times and compilation issues.

## Help

* Slack me (@Kesav Kothapalli) me the issue you're having to the best of your ability. Also send me the files you inputed into the program and any files that were outputed. Screenshots are greatly appreciated. I will try to respond with a fix as soon as possible.

## Authors

Kesav Kothapalli

## Version History

* Beta 0.9
    * Beta Release

## Acknowledgments

Based on the following packages
* [pyABF]- by Scott W Harden(https://swharden.com/pyabf/)

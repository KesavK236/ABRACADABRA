# ABRACADABRA
Axon Binary Reading Analyzer Capable of Analyzing Data as an Axon Binary Reading Analyzer

## Description

An application that uses a Python script to automate data extraction of electrophysiological parameters from Current Clamp Axon Binary Files.

## Getting Started

### Installing

* Clone the repository

### Executing program

* You can run the program either through terminal or your desired IDE

* Inside the ABRACADABRA window, you can select the ABF file corresponding to a protocol by clicking the "change file" button and selecting the desired file in the file explorer that pops up
* If you want to analyze only one protocol, select the file for the desired protocol.
* You can remove a file from the analysis list by clicking the "Clear File" button to the left of the unwanted protocol.
* The default dV/dt for the analyzer is 5 mV/ms. This can be changed to any integer between 1 and 100 using the scroll box or by typing it.
* Once you do this for your desired protocols, name the output folders in the text entry at the bottom. 
* If unsure if the program is calculating the correct threshold voltage, you can manually check the threshold value by selecting the "Verify Threshold Value?" check box
    * This button will open up 2 windows. One is a graph of the selected sweep with a green dot marking the selected threshold value. The other is a window that controls whether to change the threshold value. You can select a specific time window to check for a threshold voltage. If the selected sweep does not appear to have an action potential, you can look at the next sweep. If the threshold appears correct, you can press the "Threshold is Correct!" button.
* You can then click the "enter" button to run the program
* The extracted data will populate in an Excel file that will automatically open. You can also find all outputted files and images in a newly made folder (the name is "inputted name" + _outputs) made in the folder with the ABRACADABRA application
* You can either close the program or change the files to analyze your next data set

### Converting ABF files to NWB files
* You can begin the conversion to NWB files by clicking the "Convert to NWB file" checkbox
* A set of text entries will appear for you to fill in the appropriate information for the NWB metadata
* If a format example is in the label, please match that format to ensure proper conversion.
* After running the analysis, the "bulk_abf_nwb_converter.xlsx" file will be populated with the inputted metadata
* The actual conversion will be done by a separate script overnight due to conversion times and compilation issues.

## Help

* Slack me (@Kesav Kothapalli) me the issue you're having to the best of your ability. Also, send me the files you inputted into the program and any files that were outputted. Screenshots are greatly appreciated. I will try to respond with a fix as soon as possible.

## Authors

Kesav Kothapalli

## Version History

* 1.0
    * Initial  Release
* 1.1
    * Fixed input resistance units
    * Added warning messages for potentially incorrect analysis
    * Added a threshold visualizer so user can verify threshold during analysis
    * Changes Voltage sag to Sag peak, delta sag, and sag ratio
    * Changed falling phase to be from peak to ahp
    * Added AP count visualizer so users can verify AP counts

## Acknowledgments

Based on the following packages
* [pyABF]- by Scott W Harden(https://swharden.com/pyabf/)

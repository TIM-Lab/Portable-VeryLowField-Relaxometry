# Portable-VeryLowField-Relaxometry

## Abstract

Skeletal muscle T2 is a key biomarker for evaluating inflammation, edema, and fat infiltration, but portable single-sided NMR devices often suffer from signal interference caused by the superficial subcutaneous fat layer. To solve this, we developed a portable single-sided NMR device built with a barrel and bar permanent magnet architecture that projects a magnetic field into tissue. A surface meander gradient coil driven by a modified CPMG sequence actively dephases superficial spins, suppressing fat signals to isolate the underlying muscle response.

We validated the system through phantom studies, in vivo experiments on swine, and ex vivo measurements on excised tissue. Operating with the active gradient successfully eliminated subcutaneous fat contribution, yielding muscle T2 values that matched ex vivo measurements. This fat-suppression technique offers an adaptable approach for single-sided NMR designs, opening up new opportunities for point-of-care muscle evaluation and clinical applications.

This work is under review for publication in _Magnetic Resonance in Medicine_.

## Code

This repository provides example code to visualize in vivo data acquired with the single-sided NMR device from an animal study, as well as the code to simulate the B0 characteristics of the single-sided NMR relaxometry device.

For the simulation code, run "Fig4_Simulations_singleSided_magnet_TIM.py". Make sure to install all dependencies with their specified versions using "requirements.txt". Note that this code requires the magpylib package to run (more information: https://magpylib.readthedocs.io/en/stable/). The code was tested on Python 3.11.

## Contact

Arian Mollajafari Sohi (amollaja@purdue.edu)
Hazar Benan Unal (hunal@purdue.edu)

# b2_drought
Biosphere2 Drought Experiment

## overview
This repository contains all useful information for the data management of the Biosphere 2 drought project.

The folder /scripts contains scripts for the creation and management of the B2 drought datasets. The chosen system is the document-based database MongoDB. Loading scripts are grouped by experiment type.
The folder /vocabulary contains the controlled vocabulary for the experiment.

## Data model
The conceptual datamodel takes into account two main types of experiments : ponctual and continuous experimentation.

![Alt text](datamodel/conceptual_datamodel.jpg?raw=true "Title")

A denormalization was performed on the conceptual model to match a document-based modelisation. 
This document-based model is defined by two main collections "Experiments" and "Samples". Note that a sample can be in fact a sub-sample from a parent sample (Tree structure).

![Alt text](datamodel/document_datamodel.jpg?raw=true "Title")

# Text Spotting dataset creator

[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

Tool to help creating a dataset for text spotting task. 

# Main Features!

  - GUI support
  - Use Tesseract-ocr to support initial text spotting
  
# Installation:
To use the tool, you have to install tesseract-ocr. For Windows OS, you have to copy the exe path to line #15 of the code. 

Use pip install -r requirement.txt to install the tool requirements.  It's better to use Anaconda environment. 

# Usage
The image you want to tag must be in "images" folder. When loading the application, the user will see the images sequentially and will be able to select the text regions by mouse. 
When the text is selected, Tesseract will try to predict the text and write it into a text box. Then, you have to press "save" to save the output into a json file. 

The tool will generate a JSON file with the same name of the image and save it in "done_json" folder. 

Each time the tool loads, it loads all the bbox found in the JSON if exists. 

Don't worry if you commited a mistakes. you can correct it by:
- close the image
- correct the JSON
- load the image again [DO NOT correct JSON while the image is open, the result won't be saved!]

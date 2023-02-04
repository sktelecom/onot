# onot

onot is a tool that automatically creates open source software notices based on SPDX documents.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install onot
```

or you can install latest verson from source code. 

```bash
git clone https://github.com/sktelecom/onot.git ~/onot
cd ~/onot; python setup.py install
```

## Usage

1. Prepare your input file. The input file is an [Excel format SPDX document](./sample/SPDXRdfExample-v2.1.xlsx), and refer to the next page for [how to prepare it](./docs/how_to_prepare.md).

2. Run onot command with two arguments. 
   - `-i` or `--input` : SPDX document in Excel format containing open source information to be included in the OSS notice
   - `-o` or `--output_format` : File type of OSS notice to be generated (`html` or `text`)
   - Sample output : [output/OSS_Notice_SPDX-Tools-v2.0_20221009_180948.html](https://sktelecom.github.io/compliance/OSS_Notice_Sample_Application_20221011_140301.html)

```python
onot --input sample/SPDXRdfExample-v2.3.xlsx --output_format html
```

## Test

```python
python -m unittest
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)
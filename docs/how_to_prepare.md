# How to prepare

## SPDX document

Please fill in the necessary information in the Excel file in SPDX format. Download and use the sample here. : [SPDXRdfExample-v2.1.xlsx](../sample/SPDXRdfExample-v2.1.xlsx)

The required input sheets and columns are as follows.

1. `Document Info`

In the `Document Info` sheet, the following columns should be filled.

- `Document Name` : Enter the name of the product.
- `Creator` : Enter your company name and email address. 
  - ex: SK Telecom (opensource@sk.com)

2. `Package Info`

In the `Package Info` sheet, the following columns should be filled.

- `Package Name`
- `Package Version`
- `Package Download Location`
- `License Concluded`
  - Note: 
    - The license name must be the same as the [SPDX Identifier](https://spdx.org/licenses/).
    - If the license is not in SPDX, define the identifier in the `Extracted License Info` sheet and add the license text to the `Extracted Text` column.
- `Package Copyright Text`
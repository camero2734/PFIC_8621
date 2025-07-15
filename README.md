# Form 8621 Filler

This program fills out IRS Form 8621, specifically for Mark-to-Market (MTM) elections.

## Getting started
For each PFIC you'd like to generate a form for, create a `REFERENCE_ID.xlsx` file in the `inputs` folder, based on the `f8621.xlsx` template. It is recommended to use the e.g. ticker for an ETF as the reference id.

Example:
```bash
cp ./f8621.xlsx ./inputs/vwce.xlsx # Fund 1
cp ./f8621.xlsx ./inputs/spyy.xlsx # Fund 2
```

Now you need to fill out the XLSX files with the relevant data for each fund. The program will read these files and generate a filled-out Form 8621 PDF for each.

## Filling out the form

### Lot Details
For each transaction made, you need to fill out the lot details in the `Lot Details` sheet of the XLSX file. This includes:
- Date of acquisition
- Price per share at acquisition (in local currency)
- Total amount paid (in local currency)
- Exchange rate on purchase date (e.g. EUR to USD)

If the share lot was sold, you also need to fill out the sale details:
- Date of sale
- Price per share at sale (in local currency)
- Exchange rate on sale date (e.g. EUR to USD)

If it wasn't sold, leave the sale details blank.

### EOY Details
In the `EOY Details` sheet, you need to fill out for each year:
- The year
- The FMV of the a share of the PFIC on December 31st (in local currency)
- The exchange rate on December 31st (e.g. EUR to USD)

### PFIC Details
In the `PFIC Details` sheet, you need to fill out:
- The name of the PFIC (e.g. Vanguard FTSE All-World UCITS ETF)
- The address of the PFIC (you can find this in the Prospectus by searching for "Registered Office")
- The reference ID
  - Recommended to use the ticker name, like VWCE or SPYY
  - Can be whatever you want, but must be consistent year-to-year

## Running the program
To run the program, first install `uv` by following the instructions in the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

Next, install the dependencies:
```bash
uv install
```

Finally, run the program:
```bash
uv run f8621_filler.py
```

This will ask you several questions in the terminal:
1. Name of the Shareholder (that's you!)
2. Identifying number (SSN or ITIN)
3. City, State, ZIP, Country (e.g. Amsterdam 1012AB, Netherlands)
4. Address (e.g. Some Street 123)
5. Tax year, just the last 2 digits (e.g. 19 for 2019)

That's all of the data needed. It will then generate a PDF for each PFIC in the `outputs` folder, named `REFERENCE_ID.pdf`. For example, if you have `vwce.xlsx` and `spyy.xlsx` in the `inputs` folder, it will generate:
- `outputs/vwce.pdf`
- `outputs/spyy.pdf`

You can then include these with your tax return.
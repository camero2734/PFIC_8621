# Form 8621 Filler

This program fills out IRS Form 8621, specifically for Mark-to-Market (MTM) elections.

<img width="500" alt="image" src="https://github.com/user-attachments/assets/970426a5-dd5a-46a1-a0a0-97e6c16de4f6" />

---

> [!CAUTION]
> This tool does not provide not tax advice, cannot be guaranteed to generate a compliant output, and is not responsible for any errors in the generated forms. It is your responsibility to ensure that the filled-out forms are correct and compliant with IRS regulations. Consult a tax professional if needed.

## Getting started
For each PFIC you'd like to generate a form for, copy the `f8621.xlsx` template file into the `inputs` folder and rename it to something meaningful (e.g. the reference ID of the PFIC).

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

If you only sold part of the lot, you need to split it into two separate rows with the same acquisition date: one for the sold part and one for the remaining part. The remaining part should have the sale details left blank.

### EOY Details
In the `EOY Details` sheet, you need to fill out for each year:
- The year
- The FMV of a share of the PFIC on December 31st (in local currency)
- The exchange rate on December 31st (e.g. EUR to USD)

### PFIC Details
In the `PFIC Details` sheet, you need to fill out:
- The name of the PFIC (e.g. Vanguard FTSE All-World UCITS ETF)
- The address of the PFIC (you can usually find this in the Prospectus by searching for "Registered Office")
- The reference ID
  - Recommended to use the ticker name, like VWCE or SPYY, without any special characters
  - Can be whatever you want, but must be consistent year-to-year
  - From the IRS:
    > The reference ID number must be alphanumeric [A-Z, 0-9] and no special characters or spaces are permitted. The length of a given reference ID number is limited to 50 characters.

## Running the program
To run the program, first install `uv` by following the instructions in the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

Next, install the dependencies:
```bash
uv install
```

Finally, run the program:
```bash
uv run main.py
```

This will ask you several questions in the terminal:
1. Name of the Shareholder (that's you!)
2. Identifying number (SSN or ITIN)
3. City, State, ZIP, Country (e.g. Amsterdam 1012AB, Netherlands)
4. Address (e.g. Some Street 123)
5. Tax year, just the last 2 digits (e.g. 19 for 2019)

That's all of the data needed. It will then generate a PDF for each PFIC in the `outputs/YEAR` folder, named `REFERENCE_ID.pdf`. For example, if you have `vwce.xlsx` and `spyy.xlsx` in the `inputs` folder, and run the program for 2025, it will generate:
- `outputs/2025/vwce.pdf`
- `outputs/2025/spyy.pdf`

import pdfrw
from reportlab.pdfgen import canvas
import subprocess
import tkinter
import os
import sys
import pandas as pd
import numpy as np

exec(open(r'8621_xy_coordinates.py').read())


def create_overlay(path):
    """
    Create the data that will be overlayed on top
    of the form that we want to fill
    """
    number_of_lots = 5
    data_dict, file_dict = create_gui()
    tax_year=2000+int(data_dict["Tax year"])
    df_lot = pd.read_excel(file_dict['file'],sheet_name = 'Lot Details')
    df_eoy = pd.read_excel(file_dict['file'],sheet_name = 'EOY Details')
    number_of_lots = len(df_lot.index)
    print(df_lot)
    c = canvas.Canvas(path)
    coordinates = get_coordinates()
    add_personal_info(c,coordinates,data_dict)
    add_pfic_info(c,coordinates,data_dict)
    add_part_1(c,coordinates,data_dict,df_lot, df_eoy,tax_year)
    add_part_2(c,coordinates,data_dict)
    for lot in range(number_of_lots):
        if not add_part_4(c,coordinates,df_lot,df_eoy,lot,tax_year):
            number_of_lots=number_of_lots-1
    c.save()
    return number_of_lots

def add_personal_info(c,coordinates,data_dict):
    keys = ['Name of shareholder', 'Identifying Number', 'Address', 'City, State, Zip, Country', 'Tax year', 'Type of Shareholder']
    for key in keys:
        c.drawString(coordinates[key][0],coordinates[key][1], data_dict[key])

    c.drawString(196, 627, u'\u2713') # type of shareholder

def add_pfic_info(c,coordinates,data_dict):
    keys = ['Name of PFIC', 'PFIC Address', 'PFIC Reference ID']
    for key in keys:
        c.drawString(coordinates[key][0],coordinates[key][1], data_dict[key])

def add_part_1(c,coordinates,data_dict, df_lot, df_eoy,current_year):
    part_1_dict = {}
    part_1_dict['Date of Aquision'] = 'Multiple'
    part_1_dict['Number of Shares'] = 0
    part_1_dict["Amount of 1291"] = ''
    part_1_dict["Amount of 1293"] = ''
    part_1_dict['Descrition of each class of shares']='Class A'
    for lot in range(len(df_lot.index)):
        # Check if lot was sold and get last price and ER
        if np.isnan(df_lot["Price per share: Sale"][lot]):
            price_aquisition = df_lot['Price per share: Acquisition'][lot]
            cost_aquisition = df_lot['Cost: Acquisition'][lot]
            part_1_dict['Number of Shares'] = part_1_dict['Number of Shares'] + cost_aquisition/price_aquisition

    last_er = df_eoy[df_eoy['Year']==current_year]["Exchange Rate"].values[0]
    last_price = df_eoy[df_eoy['Year']==current_year]["Price"].values[0]
    part_1_dict['Amount of 1296']= round(part_1_dict["Number of Shares"]*last_price/last_er)


    for key in part_1_dict.keys():
        c.drawString(coordinates[key][0],coordinates[key][1], '{}'.format(part_1_dict[key]))

    value_of_pfic = part_1_dict['Amount of 1296']
    if (value_of_pfic>0) and (value_of_pfic<=50000):
        c.drawString(79.2, 373.5, u'\u2713') # value of pfic
    elif (value_of_pfic>50000) and (value_of_pfic<=100000):
        c.drawString(151.2, 373.5, u'\u2713') # value of pfic
    elif (value_of_pfic>100000) and (value_of_pfic<=150000):
        c.drawString(245, 373.5, u'\u2713') # value of pfic
    elif (value_of_pfic>150000) and (value_of_pfic<=200000):
        c.drawString(345.6, 373.5, u'\u2713') # value of pfic
    else:
        c.drawString(199, 362, '{}'.format(value_of_pfic)) # value of pfic

    # Check marks
    c.drawString(79.2, 290, u'\u2713') # type of PFIC type c


def add_part_2(c,coordinates,data_dict):
    c.drawString(52.4, 205.5, u'\u2713') # Part II election to MTM PFIC stock

def add_part_4(c,coordinates,df_lot,df_eoy,lot,current_year):
    etf_dict = {}
    # Get info about origianl aquisition
    year_of_aqiusition = df_lot['Date: Acquisition'][lot].year
    price_aquisition = df_lot['Price per share: Acquisition'][lot]
    cost_aquisition = df_lot['Cost: Acquisition'][lot]
    er_of_aqiusition   = df_lot['Exchange Rate: Acquisition'][lot]

    print(df_lot)

    number_of_shares = cost_aquisition/price_aquisition
    original_basis = cost_aquisition/er_of_aqiusition

    # Get last year's basis
    if current_year > year_of_aqiusition:
        prev_year_er = df_eoy[df_eoy['Year']==current_year-1]["Exchange Rate"].values[0]
        prev_year_price = df_eoy[df_eoy['Year']==current_year-1]["Price"].values[0]
        adjusted_basis = round(number_of_shares*prev_year_price/prev_year_er)
    else:
        adjusted_basis =  round(original_basis)


    # Check if lot was sold and get last price and ER
    if np.isnan(df_lot["Price per share: Sale"][lot]):
        print("no sale")
        last_er = df_eoy[df_eoy['Year']==current_year]["Exchange Rate"].values[0]
        last_price = df_eoy[df_eoy['Year']==current_year]["Price"].values[0]
        fmv_dollars = round(number_of_shares*last_price/last_er)
        print("Last ER={}, Last Price={}".format(last_er,last_price))
        print("FMV={}, Adjusted Basis={}".format(fmv_dollars,adjusted_basis))

        etf_dict['10a'] = fmv_dollars
        etf_dict['10b'] = adjusted_basis
        etf_dict['10c'] = etf_dict['10a'] - etf_dict['10b']
        if etf_dict['10c']<0:
            if adjusted_basis > original_basis:
                unreversed_inclusions = round(adjusted_basis - original_basis)
                if unreversed_inclusions>(-1*etf_dict['10c']):
                    loss_from_ten_c = etf_dict['10c']
                else:
                    loss_from_ten_c = -1*unreversed_inclusions
                etf_dict['11'] = unreversed_inclusions
                etf_dict['12'] = loss_from_ten_c
                print("12:  Include {} as an ordinary loss on your tax return".format(etf_dict['12']))
            else:
                etf_dict['11'] = ''
                etf_dict['12'] = ''
        else:
            etf_dict['11'] = ''
            etf_dict['12'] = ''
            print("10c: Add gain of {} to your ordinary income".format(etf_dict['10c']))
        etf_dict['13a'] = ''
        etf_dict['13b'] = ''
        etf_dict['13c'] = ''
        etf_dict['14a'] = ''
        etf_dict['14b'] = ''
        etf_dict['14c'] = ''

    else:
        print("sale")
        last_er = df_lot['Exchange Rate: Sale'][lot]
        last_price = df_lot['Price per share: Sale'][lot]
        year_of_sale = df_lot['Date: Sale'][lot].year
        if year_of_sale<current_year:
            return False
        fmv_dollars = round(number_of_shares*last_price/last_er)
        print("Last ER={}, Last Price={}".format(last_er,last_price))
        print("FMV={}, Adjusted Basis={}".format(fmv_dollars,adjusted_basis))
        etf_dict['13a'] = round(fmv_dollars)
        etf_dict['13b'] = round(adjusted_basis)
        etf_dict['13c'] = etf_dict['13a'] - etf_dict['13b']
        if etf_dict['13c']<0:
            if adjusted_basis > original_basis:
                unreversed_inclusions = round(adjusted_basis - original_basis)
                if unreversed_inclusions>(-1*etf_dict['13c']):
                    loss_from_thirteen_c = etf_dict['13c']
                else:
                    loss_from_thirteen_c = -1*unreversed_inclusions
                etf_dict['14a'] = unreversed_inclusions
                etf_dict['14b'] = loss_from_thirteen_c
                etf_dict['14c'] = ''
                print('14b: Enter {} as an ordinary loss'.format(etf_dict['14b']))
            else:
                etf_dict['14a'] = 0
                etf_dict['14b'] = 0
                etf_dict['14c'] = etf_dict['13c']
                print("14c: Include {} on tax return according to the rules generally applicable for losses provided elsewhere in the Code and regulations".format(etf_dict['14c']))
        else:
            etf_dict['14a'] = ''
            etf_dict['14b'] = ''
            etf_dict['14c'] = ''
            print("13c: Add gain of {} to your ordinary income".format(etf_dict['13c']))
        etf_dict['10a'] = ''
        etf_dict['10b'] = ''
        etf_dict['10c'] = ''
        etf_dict['11'] = ''
        etf_dict['12'] = ''

    c.showPage()
    for key in etf_dict.keys():
        if key in coordinates:
            c.drawString(coordinates[key][0],coordinates[key][1], '{}'.format(etf_dict[key]))
        else:
            print(f"Warning: {key} not found in coordinates dictionary. Skipping.")
    return True


def merge_pdfs(pdf_1, pdf_2, output):
    """
    Merge the specified fillable form PDF with the
    overlay PDF and save the output
    """
    form = pdfrw.PdfReader(pdf_1)
    olay = pdfrw.PdfReader(pdf_2)

    for form_page, overlay_page in zip(form.pages, olay.pages):
        merge_obj = pdfrw.PageMerge()
        overlay = merge_obj.add(overlay_page)[0]
        pdfrw.PageMerge(form_page).add(overlay).render()

    writer = pdfrw.PdfWriter()
    writer.write(output, form)

def split(path, page, output):
    pdf_obj = pdfrw.PdfReader(path)
    total_pages = len(pdf_obj.pages)

    writer = pdfrw.PdfWriter()

    if page <= total_pages:
        writer.addpage(pdf_obj.pages[page])

    writer.write(output)

def concatenate(paths, output):
    writer = pdfrw.PdfWriter()

    for path in paths:
        reader = pdfrw.PdfReader(path)
        writer.addpages(reader.pages)

    writer.write(output)

def create_full_8621(path,number_of_page_2,output):
    orig_path = path + '.pdf'
    page_1_path = path + 'page1.pdf'
    page_2_path = path + 'page2.pdf'
    split(orig_path,0,page_1_path)
    split(orig_path,1,page_2_path)
    concatenate([page_1_path,page_2_path],output)
    for page in range(number_of_page_2-1):
        concatenate([output,page_2_path],output)

def create_gui():
    data_dict = {}
    file_dict = {}

    print("Enter the following details:")

    # data_dict['Name of shareholder'] = input("Name of shareholder: ")
    # data_dict['Identifying Number'] = input("Identifying Number (e.g., SSN): ")
    # data_dict['City, State, Zip, Country'] = input("City, State, Zip, Country: ")
    # data_dict['Address'] = input("Address: ")
    # data_dict['Tax year'] = input("Tax year (last two digits): ")
    # data_dict['Type of Shareholder'] = '\u2713'  # assuming always an individual
    # data_dict['Name of PFIC'] = input("Name of PFIC: ")
    # data_dict['PFIC Address'] = input("PFIC Address: ")
    # pfic_id = input("PFIC Reference ID: ")
    # data_dict['PFIC Reference ID'] = pfic_id

    # Placeholder values:
    data_dict['Name of shareholder'] = 'John Doe'
    data_dict['Identifying Number'] = '123-45-6789'
    data_dict['City, State, Zip, Country'] = 'Anytown, ST 12345'
    data_dict['Address'] = '123 Main St'
    data_dict['Tax year'] = '25'
    data_dict['Type of Shareholder'] = '\u2713'  # assuming always an individual
    data_dict['Name of PFIC'] = 'vwce'
    data_dict['PFIC Address'] = '456 Market St'
    pfic_id = 'vwce'
    data_dict['PFIC Reference ID'] = pfic_id

    default_path = f"./{pfic_id}.xlsx"
    file_input = input(f"Path to Excel file [default: {default_path}]: ").strip()
    file_dict = {'file': file_input if file_input else default_path}
    return data_dict, file_dict


def main():
    path = r'{}'
    form = "f8621"
    FORM_TEMPLATE_PATH = path.format(form) + '.pdf'
    FORM_FULL_PATH     = path.format(form) +'_full.pdf'
    FORM_OVERLAY_PATH = path.format(form) +'_overlay.pdf'
    FORM_OUTPUT_PATH = path.format(form) + '_filled_by_overlay.pdf'

    number_of_lots = create_overlay(FORM_OVERLAY_PATH)
    create_full_8621(form,number_of_lots,FORM_FULL_PATH)
    merge_pdfs(FORM_FULL_PATH,
               FORM_OVERLAY_PATH,
               FORM_OUTPUT_PATH)

    print(f"Form filled and saved to {FORM_OUTPUT_PATH}")


main()

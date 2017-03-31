import pandas as pd
from selenium import webdriver


def get_dengov_url(address_='10737', street_loc_ ='E', \
                   street_='26th', street_type_='Ave'):
    ''' Takes in address parameters to set up urls from which to scrape
        info property tax records from Denver County on denver.gov.
    '''

    # If doesn't have a N/S/E/W before street name and no street type
    #   (St, Ave, Blvd), set url with below format
    if street_loc_ == '-' and street_type_ == '-':
        request_format = 'https://www.denvergov.org/property?q=[address]%20[street]'
        report_url = request_format.\
                     replace('[address]', str(address_)).\
                     replace('[street]', street_)
    # If address just doesn't have N/S/E/W before street name, set
    #   url as below format
    elif street_loc_ == '-':
        request_format = 'https://www.denvergov.org/property?q=[address]%20[street]%20[typeStreet]'
        report_url = request_format.\
                     replace('[address]', str(address_)).\
                     replace('[street]', street_).\
                     replace('[typeStreet]', street_type_)

    # If address just doesn't have street type, set url as below format
    elif street_type_ == '-':
        request_format = 'https://www.denvergov.org/property?q=[address]%20[street_loc]%20[street]'
        report_url = request_format.\
                     replace('[address]', str(address_)).\
                     replace('[street_loc]', street_loc_).\
                     replace('[street]', street_)
    # Else use the usual format in which the address contains a street location (N/S/E/W) and a street type (St, Ave, Blvd)
    else:
        request_format = 'https://www.denvergov.org/property?q=[address]%20[street_loc]%20[street]%20[typeStreet]'
        report_url = request_format.\
                     replace('[address]', str(address_)).\
                     replace('[street_loc]',street_loc_).\
                     replace('[street]', street_).\
                     replace('[typeStreet]', street_type_)

    print report_url
    return report_url

def get_total_address(address='10737', street_loc ='E',\
                      street='26th', street_type='Ave'):
    ''' Takes in address parameters and outputs the concatanated
        address for input into link of property tax record to be
        clicked on using Selenium.
    '''
    total_address = address + " " + street_loc + " " + street + " " + street_type
    total_address.replace('.', '').replace('  ', ' ').upper()
    return total_address

def scrape_denvergov_proptax_records(df):
    ''' Takes in DataFrame as input, containing addresses, and updates and
          returns the DataFrame populated with additional information about
          the property.
    '''
    for i in range(len(df)):
        # Set fields for address from DataFrame data
        address = str(df['address'][i])
        street_loc = df['street_loc'][i]
        street = df['street'][i]
        street_type = df['street_type'][i]
        # Setting url for property tax record page for address,
        #   getting from get_dengov_url function
        url = get_dengov_url(address, street_loc, street, street_type)

        # Setting concatanated address for input to link to be clicked
        #   on by Selenium to bring up page with details of property
        #   tax record
        total_address = get_total_address(address, street_loc, street, street_type)

        # Setting up Selenium webdriver using Chrome browser
        path_to_chromedriver = '/home/griggs/chromedriver'
        browser = webdriver.Chrome(executable_path = \
                                   path_to_chromedriver)

        # Getting list of addresses that aren't able to get property
        #   tax record for
        bad_addresses = []

        # If the property tax record exists, scrape information
        try:
            # Opening up browser for property tax record of address
            browser.get(url)
            # Scraping parcel number, owner, co-owner, year assessed, accessed
            #   value, actual value, and property type of address (Residential,
            #   Industrial, etc.)
            parcel_number = browser.find_element_by_xpath('//*[@id="results_table"]/tbody/tr[2]/td[2]').get_attribute('innerHTML')
            owner = browser.find_element_by_xpath('//*[@id="results_table"]/tbody/tr[2]/td[3]').get_attribute('innerHTML')
            co_owner = browser.find_element_by_xpath('//*[@id="results_table"]/tbody/tr[2]/td[4]').get_attribute('innerHTML')
            year_assessed = browser.find_element_by_xpath('//*[@id="results_table"]/tbody/tr[2]/td[5]').get_attribute('innerHTML')
            assessed_value = browser.find_element_by_xpath('//*[@id="results_table"]/tbody/tr[2]/td[6]').get_attribute('innerHTML')
            actual_value = browser.find_element_by_xpath('//*[@id="results_table"]/tbody/tr[2]/td[7]').get_attribute('innerHTML')
            property_type = browser.find_element_by_xpath('//*[@id="results_table"]/tbody/tr[2]/td[8]').get_attribute('innerHTML')

            # Clicking on link to details for property tax record
            browser.find_element_by_xpath('//a[@class="search-result-link"][contains(text(), total_address)]').click()

            # Scraping property style (One-Story, Two-Story, etc.), sq. footage,
            #   number of bedrooms, lot size, year built, number of bathrooms,
            #   basement sq. footage and how much of that is finished, and what
            #   the property is zoned as
            house_type = browser.find_element_by_xpath('//*[@id="property_summary"]/div/div[2]/table/tbody/tr[1]/td[2]').get_attribute('innerHTML')
            # Scraping sq. footage of property
            sqft = browser.find_element_by_xpath('//*[@id="property_summary"]/div/div[2]/table/tbody/tr[1]/td[4]').get_attribute('innerHTML')
            bedrooms = browser.find_element_by_xpath('//*[@id="property_summary"]/div/div[2]/table/tbody/tr[2]/td[2]').get_attribute('innerHTML')
            lot_size = browser.find_element_by_xpath('//*[@id="property_summary"]/div/div[2]/table/tbody/tr[4]/td[2]').get_attribute('innerHTML')
            year_built = browser.find_element_by_xpath('//*[@id="property_summary"]/div/div[2]/table/tbody/tr[5]/td[2]').get_attribute('innerHTML')
            baths = browser.find_element_by_xpath('//*[@id="property_summary"]/div/div[2]/table/tbody/tr[2]/td[4]').get_attribute('innerHTML')
            basement_sqft_and_finished = browser.find_element_by_xpath('//*[@id="property_summary"]/div/div[2]/table/tbody/tr[3]/td[4]').get_attribute('innerHTML')
            zoned_as = browser.find_element_by_xpath('//*[@id="property_summary"]/div/div[2]/table/tbody/tr[4]/td[4]').get_attribute('innerHTML')


            # Outputting address and property info to the screen
            print total_address, property_type, house_type, sqft + " sqft"

            # Copying scraped information to the DataFrame
            df['parcel_number'][i] = str(parcel_number)
            df['owner'][i] = str(owner).replace('  ', '')
            if str(co_owner).replace(" ", "") != '':
                df['co_owner'][i] = str(co_owner)
            df['year_assessed'][i] = int(year_assessed)
            df['assessed_value'][i] = int(str(assessed_value).replace("$", "")\
                                                             .replace(",", ""))
            df['actual_value'][i] = int(str(actual_value).replace("$", "") \
                                                         .replace(",", ""))
            df['property_type'][i] = str(property_type).replace('  ', '')
            df['house_type'][i] = str(house_type)
            df['sqft'][i] = int(sqft)
            df['bedrooms'][i] = int(bedrooms)
            df['lot_size'][i] = int(str(lot_size).replace(",", ""))
            df['year_built'][i] = int(year_built)
            df['baths'][i] = str(baths)
            df['basement_sqft_and_finished'][i] = \
                                                str(basement_sqft_and_finished)
            df['zoned_as'][i] = str(zoned_as)

            # Closing the browser
            browser.close()

        # If the property tax record does not exists, print error
        #   message. The addresses with missing data will be
        #   investigated further.
        except:
            print "Unexpected error for address", total_address

    return df


if __name__ == '__main__':
    ''' Read in file containing these columns:
    address:        address number, INT
    street_loc:     N/S/E/W, STRING
    street:         street name, STRING
    street_type:    St, Ave, Blvd, etc., STRING
    parcel_number:  Parcel number or property, STRING (init w/ '-')
    owner:          Owner of property, STRING (init w/ '-')
    co_owner:       Co-owner of property, STRING (init w/ '-')
    year_assessed:  Year of property tax assessment, INT (init w/ 0)
    assessed_value: Assessed value of property, INT (init w/ 0)
    actual_value:   Actual value of property, INT (init w/ 0)
    property_type:  Property use type (Residential, Industrial, etc.), STRING
                    (init w/ '-')
    house_type:     Type of property (One-story, Two-Story, etc.), STRING
                    (init w/ '-')
    sqft:           Square footage of building, INT (init w/ 0)
    bedrooms:       Number of bedrooms, INT (init w/ 0)
    lot_size:       Square footage of lot, INT (init w/ 0)
    year_built:     Year structure built, INT (init w/ 0)
    baths:          Number of bathrooms, STRING (init w/ '-')
    basement_sqft_and_finished  Square footage of basement and how much of that
                    square footage is finished, STRING (init w/ '-')
    zoned_as        Zoning code, STRING (init w/ '-')
    '''
    com_2016 = pd.read_csv('test.csv')
    com_2016.fillna('-', inplace=True)

    # Scrape data from denver.gov property tax records and save to DataFrame
    com_2016 = scrape_denvergov_proptax_records(com_2016)

    # Outputting DataFrame to csv file with updated information
    com_2016.to_csv("com_test_2016.csv")

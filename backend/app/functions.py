import pandas as pd
import numpy as np
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

def get_dominant_font(characters_details):
  """Function that get font details for each character in line and return font that dominates if the font size of all characters is the same
  
  Parameters
  ----------
  characters_details : dataframe
      Table with character details (columns 'FontName', 'FontSize', 'FontSColor') for each character in text line

  Returns
  -------
  characters_details : dataframe
      Table with character details (columns 'FontName', 'FontSize', 'FontSColor') where FontName was changed to most common font name, if font size is the same as most common font size
  """

  # Making sure that any character details are in table
  if characters_details.shape[0] > 0:

    # Getting most common character details
    common_font, common_size, common_scolor = characters_details.value_counts().index[0]

    # Overwritting font if size is the same as the rest of text
    characters_details.loc[(characters_details['FontSize'] == common_size) & (characters_details['FontName'] != common_font), 'FontName'] = common_font

  return characters_details

def get_lines_details(page):
  """Function that iterate over each char in each line of each text element on page to establish font style of every line 
  
  Parameters
  ----------
  page : pdfminer.layout.LTPage
      Page with text elements

  Returns
  -------
  line_details : dataframe
      Table with line details (columns 'FontName', 'FontSize', 'FontSColor')
  """

  # Letters and numbers from ascii code - important for char details determination
  important_characters = (list(range(48, 57+1))+list(range(65, 90+1))+list(range(97, 122+1)))

  # Table for line's details 
  line_details = pd.DataFrame()

  # Iterating over text containers in page
  for element in page:
      if isinstance(element, LTTextContainer):

        # Verifying if text container has any text in it
        text = element.get_text().replace('\t','').replace('\n','')
        if len(text)>0:

          # Iterating over every line in text container
          for text_line in element:
            if isinstance(text_line, LTTextLine):

              # Table for character's details
              characters_details = pd.DataFrame()

              # Iterating over every char in line container
              for character in text_line:
                if isinstance(character, LTChar):
                  
                  # Verifying if char has good length 
                  ## Warning! Some letters from other languages can have different length - that cases can be ignored
                  if len(character._text) == 1:
                    # Verifying if char is among important characters
                    ## Warning! Some chars as bullets can negatively affect line details determination
                    if ord(character._text) in important_characters:

                      # Appending character details of char to table
                      character_details = {'FontName':character.fontname,
                                          'FontSize' : round(character.size,2),
                                          'FontSColor' : [str(character.graphicstate.ncolor)]}
                      characters_details = pd.concat([characters_details, pd.DataFrame(character_details)])

              # Dropping duplicates
              characters_details = characters_details.drop_duplicates()
              # Modifying fonts in case of not common exceptions
              characters_details = get_dominant_font(characters_details)

              # Appending line details to table
              new_row = {'ElementText':[text_line.get_text().replace('\t','').replace('\n','')],
                        'FontName':[str(set(characters_details['FontName'].values))],
                        'FontSize':[str(set(characters_details['FontSize'].values))],
                        'FontSColor':[str(set(characters_details['FontSColor'].values))]
                        }
              line_details = pd.concat([line_details, pd.DataFrame(new_row)], ignore_index=True)

  return line_details

def group_lines_into_page(line_details):
  """Function that merge lines into elements if adjacent lines of text have the same style
  
  Parameters
  ----------
  line_details : dataframe
      Table with line details (columns 'FontName', 'FontSize', 'FontSColor')

  Returns
  -------
  page_details : dataframe
      Table with page details (columns 'FontName', 'FontSize', 'FontSColor')
  """

  # We start section grouping from the first element
  page_details = line_details.loc[[0]].copy()

  for i in range(1, line_details.shape[0]):
    if ((line_details.loc[i,'FontName'] == line_details.loc[i-1,'FontName']) &
        (line_details.loc[i,'FontSize'] == line_details.loc[i-1,'FontSize']) &
        (line_details.loc[i,'FontSColor'] == line_details.loc[i-1,'FontSColor'])):
      # If row has the same parameters as previous row, we append text to previous row's text
      page_details.iloc[-1]['ElementText'] = page_details.iloc[-1]['ElementText'] + ' ' + line_details.loc[i,'ElementText']
    else:
      # If row has different parameters than previous row we just rewrite it
      page_details = pd.concat([page_details, line_details.loc[[i]]], ignore_index = True)

  return page_details

def get_page_number(page_details):
  """Function that try to find page number based on elements on page.
     Numeric element is searched among bottom and top elements with common fontsize.
  
  Parameters
  ----------
  page_details : dataframe
      Table with page details (columns 'FontName', 'FontSize', 'FontSColor')

  Returns
  -------
  page_details : dataframe
      Table with page details and with additional column 'PageNumber' if page number was found. 
      Also with deleted element with page number.
  """

  page_number = np.nan

  # Iterating over elements
  for i in range(int(page_details.shape[0]/2)):

    # Verifying if page number exist in the footer
    if page_details.iloc[-(i+1)]['FontSize'] == page_details.iloc[-1]['FontSize']:
      if str(page_details.iloc[-(i+1)]['ElementText']).rstrip().isnumeric():
        page_number = page_details.iloc[-(i+1)]['ElementText'].rstrip()

    # Verifying if page number exist in the header
    if page_details.iloc[i]['FontSize'] == page_details.iloc[0]['FontSize']:
      if str(page_details.iloc[i]['ElementText']).rstrip().isnumeric():
        page_number = page_details.iloc[i]['ElementText'].rstrip()

  # If page number was not found
  if page_number != None:
    page_details['PageNumber'] = page_number
    # Excluding element with page number from paragraphs
    page_details = page_details[page_details.index != page_number]

  return page_details
import pandas as pd
import numpy as np
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine


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
  lines_details = pd.DataFrame()

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
              char_details = pd.DataFrame()

              # Iterating over every char in line container
              for character in text_line:

                new_row = {'Char' : [character], 
                           'FontName': [np.nan],
                           'FontSize' : [np.nan],
                           'FontSColor' : [np.nan]}
                
                if isinstance(character, LTChar):
                  
                  # Verifying if char has good length 
                  ## Warning! Some letters from other languages can have different length - that cases can be ignored
                  if len(character._text) == 1:
                    # Verifying if char is among important characters
                    ## Warning! Some chars as bullets can negatively affect line details determination
                    if ord(character._text) in important_characters:

                      # Appending character details of char to table
                      new_row['FontName'] = character.fontname
                      new_row['FontSize'] = round(character.size,2)
                      new_row['FontSColor'] = str(character.graphicstate.ncolor)
                      
                char_details = pd.concat([char_details, pd.DataFrame(new_row)], ignore_index = True)
                
              # Grouping characters
              char_details = char_details[~char_details['FontName'].isna()].reset_index().drop(columns='index')
              line_details = group_characters_into_lines(char_details)

              # Making sure that any details were returned
              if line_details.shape[0] > 0:

                # Appending line details to table
                lines_details = pd.concat([lines_details, line_details], ignore_index=True)

  return lines_details

def group_characters_into_lines(char_details):
  """Function that merge characters into lines if adjacent characters of text have the same style
  
  Parameters
  ----------
  char_details : dataframe
      Table with character details (columns 'FontName', 'FontSize', 'FontSColor')

  Returns
  -------
  line_details : dataframe
      Table with line details (columns 'FontName', 'FontSize', 'FontSColor')
  """
  # Converting chars to text
  char_details['ElementText'] = [x.get_text() for x in char_details['Char']]
  char_details = char_details[['ElementText', 'FontName', 'FontSize', 'FontSColor']].copy()
  # Forward fill for chars that do not have font details
  for col in ['FontName','FontSize', 'FontSColor']:
    char_details[col] = char_details[col].ffill()

  # We start section grouping from the first element
  line_details = char_details.loc[[0]].copy()

  for i in range(1, char_details.shape[0]):
    if ((char_details.loc[i,'FontName'] == char_details.loc[i-1,'FontName']) &
        (char_details.loc[i,'FontSize'] == char_details.loc[i-1,'FontSize']) &
        (char_details.loc[i,'FontSColor'] == char_details.loc[i-1,'FontSColor'])):
      # If row has the same parameters as previous row, we append text to previous row's text
      line_details.iloc[-1, 0] = line_details.iloc[-1, 0] + char_details.loc[i, 'ElementText']
    else:
      # If row has different parameters than previous row we just rewrite it
      line_details = pd.concat([line_details, char_details.loc[[i]]], ignore_index = True)

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
      page_details.iloc[-1, 0] = page_details.iloc[-1, 0] + ' ' + line_details.loc[i,'ElementText']
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
  # Index of row with page number
  n = np.nan

  # Iterating over elements
  for i in range(int(page_details.shape[0]/2)):

    # Verifying if page number exist in the footer
    if page_details.iloc[-(i+1)]['FontSize'] == page_details.iloc[-1]['FontSize']:
      if str(page_details.iloc[-(i+1)]['ElementText']).rstrip().isnumeric():
        page_number = page_details.iloc[-(i+1)]['ElementText'].rstrip()
        n = page_details.shape[0] - (i+1)

    # Verifying if page number exist in the header
    if page_details.iloc[i]['FontSize'] == page_details.iloc[0]['FontSize']:
      if str(page_details.iloc[i]['ElementText']).rstrip().isnumeric():
        page_number = page_details.iloc[i]['ElementText'].rstrip()
        n = i

  # If page number was not found
  if page_number != None:
    page_details['PageNumber'] = page_number
    # Excluding element with page number from paragraphs
    page_details = page_details[page_details.index != n]

  return page_details

def get_main_font_among_pages(all_pages):
  """Function that establish paragraph font details based on occurence of every font details among chars
  
  Parameters
  ----------
  all_pages : list
      List of tables with page details (columns 'FontName', 'FontSize', 'FontSColor')

  Returns
  -------
  main_paragraph_font : dataframe
      Table with main paragraph font details
  """
  # Contacting all pages
  pages_text = pd.DataFrame()
  for page_text in all_pages:
      pages_text = pd.concat([pages_text, page_text], ignore_index = True)

  # Making column with number of char in each element
  pages_text['ElementTextLength'] = [len(el) for el in pages_text['ElementText']]

  # Counting occurence of every font details among characters
  style_occurance = pages_text.groupby(['FontName','FontSize','FontSColor'])['ElementTextLength'].sum()
  style_occurance = style_occurance.reset_index().sort_values('ElementTextLength', ascending = False)

  # Choosing most frequent font details as main paragraph details
  main_paragraph_font = style_occurance.iloc[0]

  return main_paragraph_font

def get_footer_and_header(all_pages):
  """Function that establish header and footer based on font size
  
  Parameters
  ----------
  all_pages : list
      List of tables with page details (columns 'FontName', 'FontSize', 'FontSColor')

  Returns
  -------
  all_pages : dataframe
      List of tables with page details with additional columns 'Header', 'Footer'
  """

  # Getting main paragraph font details
  main_paragraph_font = get_main_font_among_pages(all_pages)

  # Iterating over pages
  for pg in range(len(all_pages)):

      page_details = all_pages[pg]

      # Iterating over top n rows with font size smaller than main paragrapg font size
      n = np.nan
      for i in range(int(page_details.shape[0])):

          if (page_details.iloc[i]['FontSize'] < (main_paragraph_font['FontSize'])): n = i
          else: break
      
      # Checking if any row was classified as header
      page_details['Header'] = np.nan
      if n >= 0:
          # Saving header value in column
          page_details['Header'] = ' '.join(page_details.iloc[:n+1]['ElementText'].values)
          # Limiting table to rows that are not header
          page_details = page_details.iloc[n+1:].copy()

      # Iterating over bottom n rows with font size smaller than main paragrapg font size
      n = np.nan
      for i in range(int(page_details.shape[0])):

          if (page_details.iloc[-(i+1)]['FontSize'] < (main_paragraph_font['FontSize'])): n = i
          else: break

      # Checking if any row was classified as footer
      page_details['Footer'] = np.nan
      if n >= 0:
          # Saving footer value in column
          page_details['Footer'] = ' '.join(page_details.iloc[-(n+1):]['ElementText'].values)
          # Limiting table to rows that are not footer
          page_details = page_details.iloc[:-(n+1)].copy()

      # Overwritting page table in list
      all_pages[pg] = page_details

  return all_pages
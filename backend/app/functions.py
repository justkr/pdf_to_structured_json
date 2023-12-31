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
                

              # Making sure that any details were returned
              if char_details.shape[0] > 0:

                # Grouping characters
                line_details = group_characters_into_lines(char_details)
                line_details = line_details[~line_details['FontName'].isna()].reset_index().drop(columns='index')
                line_details['ElementText'] = line_details['ElementText'].str.rstrip()
                line_details['ElementText'] = [repr(x)[1:-1].replace('\\x','').replace('\\t','').replace('\\n','') for x in line_details['ElementText'] ]

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
  line_details['ElementText'] = line_details['ElementText']

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
  style_occurance = style_occurance.drop(columns=['ElementTextLength'])
  # Choosing most frequent font details as main paragraph details
  main_paragraph_font = style_occurance.iloc[0]

  return main_paragraph_font

def get_footer_and_header(all_pages):
  """Function that establish header and footer based on font size. It also search for page number in footer/header and return page number as column 'PageNumber'
  
  Parameters
  ----------
  all_pages : list
      List of tables with page details (columns 'FontName', 'FontSize', 'FontSColor')

  Returns
  -------
  all_pages_modified : dataframe
      List of tables with page details with additional columns 'Header', 'Footer' and 'PageNumber'
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

  # Joining pages together
  pages_text = pd.DataFrame()
  for page_text in all_pages:
      pages_text = pd.concat([pages_text, page_text], ignore_index = True)

  # Preparing joined pages for page number search
  pages_text['PageNumber'] = None
  pages_text['Header'] = pages_text['Header'].astype(str)
  pages_text['Footer'] = pages_text['Footer'].astype(str)
  pages_text = pages_text[['ElementText', 'FontName', 'FontSize', 'FontSColor',
                          'OperationalPageNumber', 'Header', 'Footer', 'PageNumber']].copy()

  # Iterating over elements to see if there are any numbers in footer and header
  for i, row in pages_text.iterrows():
      numbersh = [str(x) for x in row['Header'] if str(x).isdigit()]
      numbersf = [str(x) for x in row['Footer'] if str(x).isdigit()]
      if len(numbersh + numbersf) > 0: pages_text.loc[i, 'PageNumber'] = ''.join(numbersh + numbersf)

  # Calculating difference between found numbers and operational page number
  pages_text['PageDifference'] = [int(po) - int(p) if p != None else None for po, p in zip(pages_text['OperationalPageNumber'],pages_text['PageNumber'])]

  # At lease 50% of pages have to have page number filled, otherwise PageNumber will not be filled
  na_fillout = pages_text['PageDifference'].isna().sum() / pages_text['PageDifference'].shape[0]
  if na_fillout <= 0.5:
    # Most common difference (to make sure that some deviations do not impact page number)
    difference_pages = pages_text['PageDifference'].value_counts().index[0]
    # Calculating PageNumber
    pages_text['PageNumber'] = pages_text['OperationalPageNumber'] - difference_pages
    pages_text.loc[pages_text['PageNumber'] <=0, 'PageNumber'] = np.nan
     
  # Pages modification - adding PageNumber
  all_pages_modified = []
  for i in range(len(all_pages)):
      pg = all_pages[i]
      pg = pg.merge(pages_text[['OperationalPageNumber', 'PageNumber']].drop_duplicates(), on = ['OperationalPageNumber'], how='left')
      all_pages_modified.append(pg)

  return all_pages_modified

def get_structure(all_pages):
  """Function that establish if element is 'Header' or 'Text
  
  Parameters
  ----------
  all_pages : list
      List of tables with page details (columns 'FontName', 'FontSize', 'FontSColor')

  Returns
  -------
  all_pages_modified : dataframe
      List of tables with page details with additional column 'Structure'
  """

  # Joining all pages together to findout style of sections in the whole document
  pages_text = pd.DataFrame()
  for page_text in all_pages:
      pages_text = pd.concat([pages_text, page_text], ignore_index = True)

  # Determining what style occures the most often in document
  main_paragraph_font = get_main_font_among_pages(all_pages)

  # Calculating proportion of every style occurance
  pages_text['ElementTextLength'] = [len(x) for x in pages_text['ElementText']]
  style = pages_text.groupby(['FontName', 'FontSize', 'FontSColor'])['ElementTextLength'].sum().reset_index()
  style['ElementTextLength'] = style['ElementTextLength'] / pages_text['ElementTextLength'].sum()

  # Element that are long are usually not headers, so they have the structure 'Text' assigned
  long_texts = pages_text[pages_text['ElementTextLength'] > 100][['FontName', 'FontSize', 'FontSColor']].drop_duplicates()
  long_texts['Structure'] = 'Text'
  style = style.merge(long_texts, on = ['FontName', 'FontSize', 'FontSColor'], how = 'left').drop_duplicates()
  style = style.sort_values('ElementTextLength', ascending=False)

  # Not frequent elements are converted to standard text
  style.loc[style['ElementTextLength'] <= 0.001, 'Structure'] = 'Text'

  # Determining if font is bolded or have different color than standard text
  style['Bold'] = [1 if ('bold' in nm.lower() and 'semibold' not in nm.lower()) else 0 for nm in style['FontName']]
  style['Colored']= [1 if c != main_paragraph_font['FontSColor'] else 0 for c in style['FontSColor']]

  # If element is not bolded and size is around main size, we assume that structure is 'Text'
  style.loc[(abs(style['FontSize'] -  main_paragraph_font['FontSize']) <= 1) &
            (style['Bold'] == 0), 'Structure'] = 'Text'

  # If font size is smaller than main font and text is not bolded or colored, we assign it as 'Text'
  style.loc[(style['FontSize'] < main_paragraph_font['FontSize']) &
            (style['Bold'] == 0) & (style['Colored'] == 0), 'Structure'] = 'Text'

  # All the other styles have 'Header' structure
  style.loc[style['Structure'] != 'Text', 'Structure'] = 'Header'

  # Merging style details (col 'Structure') to list of page details
  all_pages_modified = []

  for i in range(len(all_pages)):
      pg = all_pages[i]
      pg = pg.merge(style[['FontName','FontSize','FontSColor','Structure']], on = ['FontName','FontSize','FontSColor'], how='left')
      all_pages_modified.append(pg)
        
  return all_pages_modified
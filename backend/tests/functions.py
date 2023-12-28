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
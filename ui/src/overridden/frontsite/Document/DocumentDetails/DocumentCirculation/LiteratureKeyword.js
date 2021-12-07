import _isEmpty from 'lodash/isEmpty';

export const LiteratureKeyword = ({ keywords }) => {
  // hides the keyword sources
  const keywordsIsEmpty = _isEmpty(keywords);

  if (keywordsIsEmpty) return null;

  const keywordValues = keywords.map(keyword => keyword?.value);
  return keywordValues.join(';  ');
};

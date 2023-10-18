import { vocabularyApi } from "@inveniosoftware/react-invenio-app-ils";

export const IS_LOADING = "fetchIdentifiers/IS_LOADING";
export const SUCCESS = "fetchIdentifiers/SUCCESS";
export const HAS_ERROR = "fetchIdentifiers/HAS_ERROR";

const createQueryPromise = (type) => {
  const query = vocabularyApi.query().withType(type).qs();

  return vocabularyApi.list(query);
};

const serializer = (hit) => ({
  value: hit.metadata.key,
  text: hit.metadata.text,
  url_path: hit.metadata?.data?.url_path,
});

const query = async () => {
  const {
    data: { hits: identifierQuery },
  } = await createQueryPromise("identifier_scheme");
  const {
    data: { hits: alternativeIdentifierQuery },
  } = await createQueryPromise("alternative_identifier_scheme");

  const combinedHits = identifierQuery.concat(alternativeIdentifierQuery);

  return combinedHits.map(serializer);
};

const identifierCache = () => {
  let value = null;

  return {
    set: (valueToSet) => (value = valueToSet),
    get: () => value,
  };
};

const cache = identifierCache();

export const fetchVocabularyIdentifiers = () => {
  return async (dispatch) => {
    dispatch({ type: IS_LOADING });

    const fetchedVocabularyIdentifiers = cache.get();

    try {
      if (fetchedVocabularyIdentifiers) {
        dispatch({
          type: SUCCESS,
          payload: fetchedVocabularyIdentifiers,
        });
      } else {
        const queries = await query();

        cache.set(queries);

        dispatch({
          type: SUCCESS,
          payload: queries,
        });
      }
    } catch (error) {
      dispatch({ type: HAS_ERROR, payload: error });
    }
  };
};

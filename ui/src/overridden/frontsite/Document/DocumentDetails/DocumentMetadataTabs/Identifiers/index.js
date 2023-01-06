import { connect } from "react-redux";
import { fetchVocabularyIdentifiers } from "./actions";
import { Identifiers as IdentifiersComponent } from "./Identifiers";

const mapDispatchToProps = (dispatch) => ({
  fetchVocabularyIdentifiers: () => dispatch(fetchVocabularyIdentifiers()),
});

const mapStateToProps = (state) => ({
  vocabularyIdentifiers: state.vocabularyIdentifiers.data,
  loading: state.vocabularyIdentifiers.isLoading,
  error: state.vocabularyIdentifiers.error,
});

export const Identifiers = connect(
  mapStateToProps,
  mapDispatchToProps
)(IdentifiersComponent);

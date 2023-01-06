import { connect } from "react-redux";
import { eitemDetailsModalClose, openEitemDetailsModal } from "./actions";
import EitemDetailsModalComponent from "./EitemImportDetailsModal";

const mapDispatchToProps = (dispatch) => ({
  modalClose: () => dispatch(eitemDetailsModalClose()),
  modalOpen: (eitemReport) => dispatch(openEitemDetailsModal(eitemReport)),
});

const mapStateToProps = (state) => {
  return {
    eitemReport: state.eitemDetailsModal.eitemReport,
    open: state.eitemDetailsModal.open,
  };
};

export const EitemImportDetailsModal = connect(
  mapStateToProps,
  mapDispatchToProps
)(EitemDetailsModalComponent);

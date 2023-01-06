import { connect } from "react-redux";
import { openJsonModal } from "../JsonViewModal/actions";
import { seriesDetailsModalClose, openSeriesDetailsModal } from "./actions";
import SeriesDetailsModalComponent from "./SeriesImportDetailsModal";

const mapDispatchToProps = (dispatch) => ({
  modalClose: () => dispatch(seriesDetailsModalClose()),
  modalOpen: (seriesReport) => dispatch(openSeriesDetailsModal(seriesReport)),
  jsonModalOpen: (title, json) => dispatch(openJsonModal(title, json)),
});

const mapStateToProps = (state) => {
  return {
    seriesReport: state.seriesDetailsModal.seriesReport,
    open: state.seriesDetailsModal.open,
  };
};

export const SeriesImportDetailsModal = connect(
  mapStateToProps,
  mapDispatchToProps
)(SeriesDetailsModalComponent);

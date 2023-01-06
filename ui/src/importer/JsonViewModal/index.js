import { connect } from "react-redux";
import { jsonModalClose, openJsonModal } from "./actions";
import JsonViewModalComponent from "./JsonViewModal";

const mapDispatchToProps = (dispatch) => ({
  onCloseHandler: () => dispatch(jsonModalClose()),
  jsonModalOpen: (title, json) => dispatch(openJsonModal(title, json)),
});

const mapStateToProps = (state) => {
  return {
    title: state.jsonModal.title,
    jsonData: state.jsonModal.json,
    open: state.jsonModal.open,
  };
};

export const JsonViewModal = connect(
  mapStateToProps,
  mapDispatchToProps
)(JsonViewModalComponent);

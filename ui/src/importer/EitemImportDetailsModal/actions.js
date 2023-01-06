export const EITEM_DETAILS_MODAL_OPEN = "eitemDetailsModal/OPEN";
export const EITEM_DETAILS_MODAL_CLOSE = "eitemDetailsModal/CLOSE";

export const openEitemDetailsModal = (seriesReport) => {
  return async (dispatch) => {
    dispatch({
      type: EITEM_DETAILS_MODAL_OPEN,
      eitemReport: seriesReport,
    });
  };
};

export const eitemDetailsModalClose = () => {
  return async (dispatch) => {
    dispatch({
      type: EITEM_DETAILS_MODAL_CLOSE,
    });
  };
};

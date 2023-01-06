export const SERIES_DETAILS_MODAL_OPEN = "seriesDetailsModal/OPEN";
export const SERIES_DETAILS_MODAL_CLOSE = "seriesDetailsModal/CLOSE";

export const openSeriesDetailsModal = (seriesReport) => {
  return async (dispatch) => {
    dispatch({
      type: SERIES_DETAILS_MODAL_OPEN,
      seriesReport: seriesReport,
    });
  };
};

export const seriesDetailsModalClose = () => {
  return async (dispatch) => {
    dispatch({
      type: SERIES_DETAILS_MODAL_CLOSE,
    });
  };
};

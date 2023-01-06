export const JSON_MODAL_OPEN = "detailsModal/OPEN";
export const JSON_MODAL_CLOSE = "detailsModal/CLOSE";

export const openJsonModal = (title = null, json = null) => {
  return async (dispatch) => {
    dispatch({
      type: JSON_MODAL_OPEN,
      json: json,
      title: title,
    });
  };
};

export const jsonModalClose = () => {
  return async (dispatch) => {
    dispatch({
      type: JSON_MODAL_CLOSE,
    });
  };
};

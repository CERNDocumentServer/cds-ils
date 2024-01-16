import React from "react";
import { config } from "../../config";

export const formatPrice = (price, includeCurrency = true) => {
  if (!price) return null;

  const options =
    price.currency && includeCurrency
      ? {
          style: "currency",
          currency: price.currency,
        }
      : {
          maximumFractionDigits: 2,
        };

  return new Intl.NumberFormat(config.APP.i18n.priceLocale, options).format(
    price.value
  );
};

import React from "react";
import PropTypes from "prop-types";

const Card = ({ text }) => <div className="sortable-card">{text}</div>;

Card.propTypes = {
    text: PropTypes.string.isRequired,
};

export default Card;

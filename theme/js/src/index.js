import "./theme.scss";

// Anchors for headers

import AnchorJS from "anchor-js";
const anchors = new AnchorJS();

anchors.options = {
    placement: "right",
    // visible: "always",
    icon: "#",
};

anchors.add(
    "article.post h1:not(.no-anchor), article.post h2:not(.no-anchor), article.post h3"
);

// Medium Zoom: zoom images on click

import mediumZoom from "medium-zoom";

mediumZoom("article.post img", {
    background: "#1a1a1a",
    scrollOffset: 0,
    margin: 30,
});

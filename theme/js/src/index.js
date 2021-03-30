import "./index.scss";

// Anchors for headers
anchors.options = {
    placement: "right",
    // visible: "always",
    icon: "»",
};
anchors.add(
    "article.post h1:not(.no-anchor), article.post h2:not(.no-anchor), article.post h3"
);

// Images zoom on click
const zoomDefault = mediumZoom("article.post img", {
    background: "#1a1a1a",
    scrollOffset: 0,
    margin: 30,
});

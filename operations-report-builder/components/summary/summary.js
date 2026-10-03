/* Anime.js 4.5.0, served locally. No uploaded cell contents enter this iframe. */
(() => {
    "use strict";
    const container = document.getElementById("summary");
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    let animation = null;
    let previous = null;
    let frameHeight = 0;

    function send(type, fields = {}) {
        // Streamlit's v1 component protocol. Only messages from our parent are read.
        window.parent.postMessage({ isStreamlitMessage: true, type, ...fields }, "*");
    }

    function resize() {
        const height = Math.ceil(container.getBoundingClientRect().height);
        if (height > 0 && height !== frameHeight) {
            frameHeight = height;
            send("streamlit:setFrameHeight", { height });
        }
    }

    function stopMotion() {
        if (animation) animation.cancel();
        animation = null;
        for (const node of container.children) {
            node.style.opacity = "1";
            node.style.transform = "none";
        }
    }

    function render(items) {
        const signature = JSON.stringify(items);
        if (signature === previous) {
            resize();
            return;
        }
        stopMotion();
        const nodes = items.map((item) => {
            const section = document.createElement("section");
            section.className = item.warning ? "stat warning" : "stat";
            for (const field of ["value", "label", "detail"]) {
                const text = document.createElement("p");
                text.className = field;
                text.textContent = String(item[field] ?? "");
                section.appendChild(text);
            }
            return section;
        });
        container.replaceChildren(...nodes);
        previous = signature;
        resize();
        if (!preference.matches && window.anime && nodes.length) {
            // Final counts are readable immediately; we never count from zero.
            const { animate, stagger } = window.anime;
            animation = animate(nodes, {
                opacity: [0.65, 1],
                translateY: [6, 0],
                duration: 220,
                delay: stagger(25),
                ease: "outQuad",
                onComplete: () => { animation = null; },
            });
        }
    }

    window.addEventListener("message", (event) => {
        if (event.source !== window.parent || event.data?.type !== "streamlit:render") return;
        const items = event.data.args?.items;
        if (Array.isArray(items)) render(items);
    });
    preference.addEventListener("change", () => { if (preference.matches) stopMotion(); });
    window.addEventListener("pagehide", stopMotion);
    window.addEventListener("resize", resize);
    new ResizeObserver(resize).observe(container);
    send("streamlit:componentReady", { apiVersion: 1 });
})();
